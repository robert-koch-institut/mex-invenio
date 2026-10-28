#!/usr/bin/env bash
# Build a pseudonymised developer snapshot of the MEx staging database and upload it.
# Staging runs the same code and imports the same MEx data as production, so the
# snapshot matches what developers run locally while still holding real personal data.
#
#   staging DB --pg_dump (read-only user)--> scratch Postgres in this container
#     --> sanitise.sql --> verify.sql --> pg_dump --> S3 upload
#
# The raw staging data only ever exists inside the scratch database, which lives
# in $WORK_DIR (an emptyDir in Kubernetes) and is discarded with the pod. If
# verify.sql finds anything, the script exits non-zero before dumping.
#
# Required environment:
#   SOURCE_DATABASE_URL   staging DB: postgresql://user:pass@host:5432/db (read-only user)
#   SNAPSHOT_SALT         >= 32 chars; keep it stable so pseudonyms stay stable
#   S3_ENDPOINT_URL       e.g. https://s3.de-north-2.psmanaged.com
#   S3_BUCKET
#   S3_ACCESS_KEY_ID      write access (PutObject) is enough
#   S3_SECRET_ACCESS_KEY
# Optional:
#   S3_REGION             default: us-east-1
#   S3_PREFIX             default: snapshots
#   ALLOW_EMAILS          comma-separated functional addresses allowed to remain
#   APP_IMAGE             Invenio image the staging site runs (recorded in the manifest)
#   WORK_DIR              default: /work
#   SKIP_UPLOAD           set to 1 to stop after dumping (for local testing)
set -euo pipefail

: "${SOURCE_DATABASE_URL:?}" "${SNAPSHOT_SALT:?}"
if [[ "${SKIP_UPLOAD:-0}" != "1" ]]; then
    : "${S3_ENDPOINT_URL:?}" "${S3_BUCKET:?}" "${S3_ACCESS_KEY_ID:?}" "${S3_SECRET_ACCESS_KEY:?}"
fi
S3_REGION="${S3_REGION:-us-east-1}"
S3_PREFIX="${S3_PREFIX:-snapshots}"
WORK_DIR="${WORK_DIR:-/work}"
SQL_DIR="$(cd "$(dirname "$0")" && pwd)"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"

log() { echo "$(date -u +%H:%M:%S) $*" >&2; }

# --- scratch Postgres, Unix socket only ------------------------------------
export PGDATA="$WORK_DIR/pgdata" PGHOST="$WORK_DIR/socket" PGUSER=snapshot PGDATABASE=snapshot
mkdir -p "$PGHOST"
log "initialising scratch database"
initdb --username="$PGUSER" --auth=trust --encoding=UTF8 >/dev/null
pg_ctl --wait --log="$WORK_DIR/postgres.log" \
    -o "-c listen_addresses='' -c unix_socket_directories='$PGHOST' -c fsync=off -c full_page_writes=off" start >/dev/null
trap 'pg_ctl --mode=immediate stop >/dev/null 2>&1 || true' EXIT
createdb "$PGDATABASE"

# --- copy staging into scratch (streamed, never written to disk as a dump) ---
log "copying staging database"
pg_dump --dbname="$SOURCE_DATABASE_URL" --format=custom --no-owner --no-privileges \
    | pg_restore --dbname="$PGDATABASE" --no-owner --no-privileges --exit-on-error

# --- pseudonymise and verify -------------------------------------------------
log "sanitising"
psql -X -q -v ON_ERROR_STOP=1 -v salt="$SNAPSHOT_SALT" -f "$SQL_DIR/sanitise.sql"
log "verifying"
psql -X -q -v ON_ERROR_STOP=1 -v allow_emails="${ALLOW_EMAILS:-}" -f "$SQL_DIR/verify.sql"

# --- dump, describe ---------------------------------------------------------
OUT="$WORK_DIR/out"
mkdir -p "$OUT"
log "dumping"
pg_dump --format=custom --no-owner --no-privileges --file="$OUT/mex.dump"

q() { psql -X -tA -c "$1"; }
SHA256="$(sha256sum "$OUT/mex.dump" | cut -d' ' -f1)"
cat > "$OUT/manifest.json" <<EOF
{
  "created_at": "$TIMESTAMP",
  "file": "mex.dump",
  "sha256": "$SHA256",
  "size_bytes": $(stat -c %s "$OUT/mex.dump"),
  "postgres_server_version": "$(q 'SHOW server_version')",
  "alembic_versions": $(q "SELECT coalesce(json_agg(version_num ORDER BY version_num), '[]') FROM alembic_version"),
  "app_image": "${APP_IMAGE:-unknown}",
  "counts": {
    "records": $(q 'SELECT count(*) FROM rdm_records_metadata'),
    "record_versions": $(q 'SELECT count(*) FROM rdm_records_metadata_version'),
    "drafts": $(q 'SELECT count(*) FROM rdm_drafts_metadata WHERE json IS NOT NULL')
  }
}
EOF
log "snapshot ready: $(du -h "$OUT/mex.dump" | cut -f1)"

if [[ "${SKIP_UPLOAD:-0}" == "1" ]]; then
    log "SKIP_UPLOAD=1, leaving files in $OUT"
    exit 0
fi

# --- upload (PutObject only: works with a write-only key) ------------------------
put() {  # put <local file> <key> <content type>
    curl --fail --silent --show-error --retry 3 \
        --aws-sigv4 "aws:amz:${S3_REGION}:s3" \
        --user "${S3_ACCESS_KEY_ID}:${S3_SECRET_ACCESS_KEY}" \
        -H "x-amz-content-sha256: $(sha256sum "$1" | cut -d' ' -f1)" \
        -H "Content-Type: $3" \
        --upload-file "$1" \
        "${S3_ENDPOINT_URL%/}/${S3_BUCKET}/$2"
}
KEY="${S3_PREFIX}/${TIMESTAMP}"
log "uploading to ${S3_BUCKET}/${KEY}/"
put "$OUT/mex.dump" "${KEY}/mex.dump" application/octet-stream
put "$OUT/manifest.json" "${KEY}/manifest.json" application/json
# Written last, so it only ever points at a complete snapshot.
printf '{"latest": "%s/"}\n' "$KEY" > "$OUT/latest.json"
put "$OUT/latest.json" "${S3_PREFIX}/latest.json" application/json
log "done"
