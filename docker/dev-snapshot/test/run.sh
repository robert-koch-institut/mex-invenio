#!/usr/bin/env bash
# End-to-end test of the developer snapshot image against synthetic data.
#
# 1. starts a throwaway Postgres standing in for staging
# 2. creates the MEx schema and seeds it from test/testdata.ndjson,
#    plus planted personal data in descriptions, history, drafts and auxiliary tables
# 3. runs the snapshot image with SKIP_UPLOAD=1
# 4. restores the result and fails if any planted value survives
#
# Needs Docker and the project's pipenv environment. Uses its own Docker network,
# container names and port, and never touches the regular docker-services stack.
# Usage: docker/dev-snapshot/test/run.sh [--keep] [--out <dir>]
#   --keep  keep the test database container
#   --out   copy mex.dump and manifest.json to <dir>, e.g. to try restore.sh --file
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../../.." && pwd)"
NET=mex-dev-snapshot-test
DB=mex-dev-snapshot-test-db
PORT=5441
IMAGE=mex-dev-snapshot:test
WORK="$(mktemp -d)"
chmod 777 "$WORK"  # the image runs as the postgres user

KEEP=""
OUT=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --keep) KEEP="--keep"; shift ;;
        --out) OUT="$(realpath -m "$2")"; shift 2 ;;
        *) echo "unknown argument: $1" >&2; exit 2 ;;
    esac
done
cleanup() {
    if [[ "$KEEP" != "--keep" ]]; then
        docker rm -f "$DB" >/dev/null 2>&1 || true
        docker network rm "$NET" >/dev/null 2>&1 || true
    fi
    rm -rf "$WORK"
}
trap cleanup EXIT

echo "== building $IMAGE"
docker build -q -t "$IMAGE" "$HERE/.." >/dev/null

echo "== starting synthetic 'staging' database"
docker network create "$NET" >/dev/null 2>&1 || true
docker rm -f "$DB" >/dev/null 2>&1 || true
docker run -d --name "$DB" --network "$NET" -p "127.0.0.1:$PORT:5432" \
    -e POSTGRES_USER=mex -e POSTGRES_PASSWORD=mex -e POSTGRES_DB=mex postgres:17 >/dev/null
until docker exec "$DB" pg_isready -U mex -q; do sleep 1; done

echo "== creating schema and seeding (takes a few minutes)"
cd "$REPO"
export INVENIO_SQLALCHEMY_DATABASE_URI="postgresql+psycopg2://mex:mex@127.0.0.1:$PORT/mex"
# Everything except Postgres points nowhere, so nothing reaches a real service.
export INVENIO_SEARCH_HOSTS="['127.0.0.1:1']"
export INVENIO_CACHE_TYPE=simple
export INVENIO_CELERY_BROKER_URL=memory:// INVENIO_BROKER_URL=memory://
export INVENIO_CELERY_RESULT_BACKEND=cache+memory://
export INVENIO_RATELIMIT_STORAGE_URL=memory://
export INVENIO_ACCOUNTS_SESSION_REDIS_URL=redis://127.0.0.1:1/0
export INVENIO_CACHE_REDIS_URL=redis://127.0.0.1:1/0
export INVENIO_COMMUNITIES_IDENTITIES_CACHE_REDIS_URL=redis://127.0.0.1:1/0
pipenv run invenio db create >/dev/null 2>&1
pipenv run python -I "$HERE/seed.py" "$HERE/testdata.ndjson" \
    app_data/vocabularies/resource_types.yaml 2>&1 | grep -v -i "warning\|declare_namespace\|Loading .env"
docker exec -i "$DB" psql -U mex -q -v ON_ERROR_STOP=1 < "$HERE/seed_aux.sql"

# Values that must not survive: planted personal data plus samples of the seeded data.
docker exec "$DB" psql -U mex -X -tA -c "
    (SELECT json->'custom_fields'->'mex:email'->>0 FROM rdm_records_metadata
      WHERE json->'custom_fields' ? 'mex:email' LIMIT 20)
    UNION ALL
    (SELECT json->'custom_fields'->'mex:fullName'->>0 FROM rdm_records_metadata
      WHERE json->'custom_fields'->'mex:fullName'->>0 LIKE '% %' LIMIT 20)
    UNION ALL SELECT unnest(ARRAY['alice.mueller@rki.de', 'bob.schmidt@example.org',
        'erika.musterfrau@rki.de', 'requester@uni-berlin.de', 'draft.only@rki.de',
        '198.51.100.7', '203.0.113.5', '030 18754 0', 'secret-access-token'])" > "$WORK/forbidden.txt"

echo "== running snapshot image"
docker run --rm --network "$NET" -v "$WORK:/k" -v "$WORK:/work/out-host" \
    -e INVENIO_DB_HOST="$DB" -e INVENIO_DB_PORT=5432 -e INVENIO_DB_USER=mex \
    -e INVENIO_DB_PASSWORD=mex -e INVENIO_DB_NAME=mex \
    -e SNAPSHOT_SALT="test-salt-0123456789abcdef0123456789abcdef" \
    -e SKIP_UPLOAD=1 \
    --entrypoint bash "$IMAGE" -c '/opt/dev-snapshot/snapshot.sh && cp /work/out/* /work/out-host/'

echo "== scanning the snapshot"
docker run --rm -v "$WORK:/k" --entrypoint bash "$IMAGE" -c '
    set -e
    pg_restore -f /tmp/plain.sql /k/mex.dump
    leaks=0
    while read -r v; do
        [ -z "$v" ] && continue
        if grep -qiF -- "$v" /tmp/plain.sql; then echo "LEAK: ${v:0:4}***"; leaks=$((leaks + 1)); fi
    done < /k/forbidden.txt
    if grep -qiE "snapshot_tmp|pgcrypto" /tmp/plain.sql; then echo "LEAK: snapshot_tmp/pgcrypto in dump"; leaks=$((leaks + 1)); fi
    echo "checked $(grep -c . /k/forbidden.txt) values, $leaks leak(s)"
    [ "$leaks" -eq 0 ]'
cat "$WORK/manifest.json"
if [[ -n "$OUT" ]]; then
    mkdir -p "$OUT"
    cp "$WORK/mex.dump" "$WORK/manifest.json" "$OUT/"
    echo "== copied mex.dump and manifest.json to $OUT"
fi
echo "== PASS"
