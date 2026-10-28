# Developer database snapshots

Pseudonymised copies of the **staging** database for local development
([#215](https://github.com/robert-koch-institut/mex-invenio/issues/215)). Unlike a fresh
import, a snapshot includes the version history of every record and loads in minutes.

Snapshots are taken from staging, not production. Staging runs the same code as
`develop` and imports the same MEx data feed as production, so the database schema
matches what developers run locally. The data is still real, so it is pseudonymised
before it leaves the cluster.

## How it works

The image in this directory runs as a scheduled job next to staging:

```
staging DB ──pg_dump (read-only user)──▶ scratch Postgres inside the job
    ──▶ sanitise.sql ──▶ verify.sql ──▶ pg_dump ──▶ S3 bucket
```

- Raw staging data only exists inside the job's scratch database, which is
  deleted with the pod. The staging dump is streamed straight into it and never
  written to disk as a file.
- `verify.sql` scans **every** text and JSON column. The job fails, and nothing is
  uploaded, if it finds anything that should not be there.
- The upload is not encrypted, so the bucket must stay private, readable only by
  developers. Pseudonymisation is not complete (see Known limitations), so treat a
  snapshot as internal data.

## What is changed

Replacements are deterministic: an HMAC of the original value with a secret salt. The
same person gets the same pseudonym across record versions, drafts and snapshots, as
long as the salt stays the same.

| Data | Treatment |
|---|---|
| `mex:fullName`, `mex:givenName`, `mex:familyName` | `Person 1a2b3c4d`, `Given …`, `Family …` |
| `mex:email`, and any email address anywhere in a record | `user-<hash>@example.invalid` |
| Phone numbers after Tel/Telefon/Phone/Fax/Mobil…, or in `+49 …` form | `[phone removed]` |
| Full names of Person records appearing in any other record text | the same `Person …` pseudonym |
| `mex:orcidId`, `mex:isniId` on Person records | fake identifiers in the same format |
| Person and ContactPoint titles (copies of name/email) | recomputed from the pseudonyms |
| All of the above in current records, **record history** and drafts | as above |
| User accounts | kept for references; email `user<id>@example.invalid`, no password/username/profile |
| Sessions, login info, OAuth links/tokens, access-request tokens, secret links, audit logs, job runs, webhooks | emptied |
| Client IP addresses on SQLAlchemy-Continuum transactions | removed |

## Known limitations

- **Names of people who are not Person records**, written in free text (e.g. "Ansprechperson:
  Dr. Erika Musterfrau" in a description), are not detected. Email addresses and phone
  numbers in the same text are.
- Phone numbers written without a keyword or `+` prefix (e.g. a bare `030 1234567`) are
  not detected; a general digit pattern would destroy dates and identifiers.
- An organisation name containing a Person record's full name is pseudonymised too.
- Fake ORCIDs have the right format but an invalid checksum.

## Configuration

| Variable | |
|---|---|
| `SOURCE_DATABASE_URL` | the staging database, `postgresql://user:pass@host:5432/db`; a read-only user is enough |
| `SNAPSHOT_SALT` | at least 32 characters; keep it stable and never share it |
| `S3_ENDPOINT_URL`, `S3_BUCKET`, `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY` | a write-only (PutObject) key is enough |
| `S3_REGION`, `S3_PREFIX` | optional; default `us-east-1`, `snapshots` |
| `ALLOW_EMAILS` | optional comma-separated functional addresses that may remain (e.g. `mex@rki.de`) |
| `APP_IMAGE` | optional; the Invenio image staging runs, recorded in the manifest |
| `SKIP_UPLOAD=1` | stop after dumping; files stay in `/work/out` |

Build with the staging PostgreSQL major version:

```bash
docker build --build-arg PG_MAJOR=14 -t mex-dev-snapshot docker/dev-snapshot
```

The job's working directory `/work` needs room for two copies of the database (an
`emptyDir` with a size limit in Kubernetes). The image runs as the `postgres` user (uid 999).

## Bucket layout

```
snapshots/<timestamp>/mex.dump        pg_dump (custom format)
snapshots/<timestamp>/manifest.json   sha256, size, alembic revisions, app image, counts
snapshots/latest.json                 {"latest": "snapshots/<timestamp>/"}, written last
```

## Restoring a snapshot locally

`restore.sh` replaces your local database with the latest snapshot. It **drops** the
local `mex-invenio` database and all search indices.

1. Ask for a read-only key to the snapshot bucket and put it in `.env.snapshot` in the
   repository root (gitignored):
   ```bash
   S3_ENDPOINT_URL=https://...
   S3_BUCKET=...
   S3_ACCESS_KEY_ID=...
   S3_SECRET_ACCESS_KEY=...
   ```
2. Start the services with `docker compose up -d`.
3. Run `docker/dev-snapshot/restore.sh`.

The script:
1. downloads the latest snapshot into `tmp/dev-snapshot/` and checks it against the
   manifest's sha256. A snapshot that was already downloaded is reused.
2. restores it into the `db` service.
3. runs `invenio alembic upgrade`, since staging may be behind your checkout.
4. flushes Redis, then recreates the search indices and custom fields.
5. reindexes everything. Indexing runs in the script, so no Celery worker is needed.
6. creates a local admin, because imported users have no passwords.

Set `LOCAL_ADMIN_EMAIL` and `LOCAL_ADMIN_PASSWORD` to choose the admin's login.
Otherwise it is `admin@example.org` with a generated password, printed at the end.
Use `--file path/to/mex.dump` to restore a dump you already have; a `manifest.json`
next to it is checked if present. Use `--yes` to skip the confirmation.

Staging's `SECRET_KEY` and password salt are not needed. Everything that depends on
them (password hashes, encrypted OAuth tokens, secret links) is removed by
`sanitise.sql`. To log in as an imported user, set a password for them in
`invenio shell` with `invenio_accounts.utils.hash_password`.

## Testing

`test/run.sh` builds the image, seeds a throwaway database from
`site/mex_invenio/scripts/testdata.ndjson` (plus planted personal data in descriptions,
history, drafts and auxiliary tables), runs the job with `SKIP_UPLOAD=1`, restores the
result and fails if any planted or sampled value survives. It uses its own container,
network and port (5441) and takes about 10 minutes, mostly seeding.

```bash
docker/dev-snapshot/test/run.sh          # add --keep to keep the test database
```
