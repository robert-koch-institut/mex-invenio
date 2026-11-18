#!/usr/bin/env bash
# Replace the local development database with the latest developer snapshot.
#
#   S3 bucket --download + sha256 check--> pg_restore into the docker-compose db
#     --> alembic upgrade --> reindex --> local admin user
#
# Run from anywhere in the repository, with the docker-compose services up
# (docker compose up -d). This DROPS the local mex-invenio database and search
# indices. Snapshots are pseudonymised (see README.md) but still internal data.
#
# S3 settings are read from the environment, or from .env.snapshot in the
# repository root if it exists (gitignored):
#   S3_ENDPOINT_URL, S3_BUCKET, S3_ACCESS_KEY_ID, S3_SECRET_ACCESS_KEY (read access)
#   S3_REGION             default: us-east-1
#   S3_PREFIX             default: snapshots
# Optional:
#   LOCAL_ADMIN_EMAIL     default: admin@example.org
#   LOCAL_ADMIN_PASSWORD  default: generated and printed at the end
#
# Usage: docker/dev-snapshot/restore.sh [--file <mex.dump>] [--target <name>] [--yes]
#   --file    restore a dump you already have; its manifest.json is used if next to it
#   --target  restore into database <name> with search index prefix "<name>-" instead,
#             leaving the regular database, indices and Redis alone. Stop any local
#             Celery worker first: it would take the reindexing jobs from the queues.
#   --yes     do not ask for confirmation
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
cd "$REPO"

DUMP=""
TARGET=""
ASSUME_YES=0
while [[ $# -gt 0 ]]; do
    case "$1" in
        --file) DUMP="$(realpath "$2")"; shift 2 ;;
        --target) TARGET="$2"; shift 2 ;;
        --yes) ASSUME_YES=1; shift ;;
        *) echo "unknown argument: $1" >&2; exit 2 ;;
    esac
done

log() { echo "== $*" >&2; }
die() { echo "error: $*" >&2; exit 1; }

if [[ -f .env.snapshot ]]; then
    set -a; source .env.snapshot; set +a
fi
S3_REGION="${S3_REGION:-us-east-1}"
S3_PREFIX="${S3_PREFIX:-snapshots}"
ADMIN_EMAIL="${LOCAL_ADMIN_EMAIL:-admin@example.org}"
ADMIN_PASSWORD="${LOCAL_ADMIN_PASSWORD:-$(head -c 12 /dev/urandom | base64 | tr -d '/+=')}"
DB_USER=mex-invenio
DB_NAME=mex-invenio
INDICES="all search indices"
if [[ -n "$TARGET" ]]; then
    [[ "$TARGET" != "$DB_NAME" ]] || die "--target must differ from $DB_NAME"
    DB_NAME="$TARGET"
    INDICES="the '$TARGET-' search indices"
    export INVENIO_SQLALCHEMY_DATABASE_URI="postgresql+psycopg2://$DB_USER:$DB_USER@localhost/$DB_NAME"
    export INVENIO_SEARCH_INDEX_PREFIX="$TARGET-"
fi

json_get() { python3 -c 'import json, sys; print(json.load(open(sys.argv[1]))[sys.argv[2]])' "$1" "$2"; }
dc() { docker compose "$@"; }

for service in db cache mq search; do
    [[ -n "$(dc ps -q --status running "$service")" ]] \
        || die "docker compose service '$service' is not running (docker compose up -d)"
done

# --- fetch the snapshot ---------------------------------------------------------
get() {  # get <key> <local file>
    curl --fail --silent --show-error --retry 3 \
        --aws-sigv4 "aws:amz:${S3_REGION}:s3" \
        --user "${S3_ACCESS_KEY_ID}:${S3_SECRET_ACCESS_KEY}" \
        -H "x-amz-content-sha256: UNSIGNED-PAYLOAD" \
        --output "$2" \
        "${S3_ENDPOINT_URL%/}/${S3_BUCKET}/$1"
}

if [[ -z "$DUMP" ]]; then
    : "${S3_ENDPOINT_URL:?}" "${S3_BUCKET:?}" "${S3_ACCESS_KEY_ID:?}" "${S3_SECRET_ACCESS_KEY:?}"
    mkdir -p tmp/dev-snapshot
    get "${S3_PREFIX}/latest.json" tmp/dev-snapshot/latest.json
    KEY="$(json_get tmp/dev-snapshot/latest.json latest)"
    DIR="tmp/dev-snapshot/$(basename "$KEY")"
    mkdir -p "$DIR"
    get "${KEY%/}/manifest.json" "$DIR/manifest.json"
    DUMP="$REPO/$DIR/mex.dump"
    if [[ -f "$DUMP" ]] && [[ "$(sha256sum "$DUMP" | cut -d' ' -f1)" == "$(json_get "$DIR/manifest.json" sha256)" ]]; then
        log "using already downloaded $DIR"
    else
        log "downloading $KEY"
        get "${KEY%/}/mex.dump" "$DUMP"
    fi
fi
[[ -f "$DUMP" ]] || die "no such file: $DUMP"

MANIFEST="$(dirname "$DUMP")/manifest.json"
if [[ -f "$MANIFEST" ]]; then
    [[ "$(sha256sum "$DUMP" | cut -d' ' -f1)" == "$(json_get "$MANIFEST" sha256)" ]] \
        || die "$DUMP does not match the sha256 in $MANIFEST"
    log "snapshot from $(json_get "$MANIFEST" created_at), staging image $(json_get "$MANIFEST" app_image)"
else
    log "no manifest.json next to $DUMP, skipping the checksum"
fi

if [[ "$ASSUME_YES" != "1" ]]; then
    read -r -p "This replaces the local '$DB_NAME' database and $INDICES. Continue? [y/N] " answer
    [[ "$answer" == [yY]* ]] || exit 1
fi

# --- database ---------------------------------------------------------------------
log "restoring database"
dc exec -T db dropdb --username="$DB_USER" --if-exists --force "$DB_NAME"
dc exec -T db createdb --username="$DB_USER" --owner="$DB_USER" "$DB_NAME"
dc exec -T db pg_restore --username="$DB_USER" --dbname="$DB_NAME" \
    --no-owner --no-privileges --exit-on-error < "$DUMP"

# Staging may be behind this checkout; a snapshot ahead of it needs a newer checkout.
log "applying database migrations"
pipenv run invenio alembic upgrade \
    || die "alembic upgrade failed; if the snapshot is newer than this checkout, pull develop and retry"

# Sessions and cached objects belong to the previous database's users.
if [[ -z "$TARGET" ]]; then
    dc exec -T cache redis-cli FLUSHALL >/dev/null
fi

# --- search -----------------------------------------------------------------------
log "recreating search indices"
pipenv run invenio index destroy --yes-i-know
pipenv run invenio index init
pipenv run invenio rdm-records custom-fields init
pipenv run invenio communities custom-fields init

log "reindexing (takes a while)"
pipenv run python "$HERE/post_restore.py"

# --- local admin --------------------------------------------------------------------
# Imported users have no passwords, so nobody could log in otherwise.
log "creating local admin $ADMIN_EMAIL"
pipenv run invenio users create "$ADMIN_EMAIL" --password "$ADMIN_PASSWORD" --active --confirm
pipenv run invenio access allow administration-access user "$ADMIN_EMAIL"

log "done. Log in as $ADMIN_EMAIL / $ADMIN_PASSWORD"
