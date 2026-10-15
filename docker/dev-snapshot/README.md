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
    ──▶ sanitise.sql ──▶ verify.sql ──▶ pg_dump ──▶ age-encrypt ──▶ S3 bucket
```

- Raw staging data only exists inside the job's scratch database, which is
  deleted with the pod. The staging dump is streamed straight into it and never
  written to disk as a file.
- `verify.sql` scans **every** text and JSON column. The job fails, and nothing is
  uploaded, if it finds anything that should not be there.
- The upload is encrypted to the developers' [age](https://age-encryption.org) public
  keys, so the bucket never holds readable data.

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
| File storage location | local path instead of the staging bucket |

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
| `AGE_RECIPIENTS_FILE` | developers' age public keys, one per line |
| `S3_ENDPOINT_URL`, `S3_BUCKET`, `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY` | a write-only (PutObject) key is enough |
| `S3_REGION`, `S3_PREFIX` | optional; default `us-east-1`, `snapshots` |
| `ALLOW_EMAILS` | optional comma-separated functional addresses that may remain (e.g. `mex@rki.de`) |
| `APP_IMAGE` | optional; the Invenio image staging runs, recorded in the manifest |
| `SKIP_UPLOAD=1` | stop after encrypting; files stay in `/work/out` |

Build with the staging PostgreSQL major version:

```bash
docker build --build-arg PG_MAJOR=14 -t mex-dev-snapshot docker/dev-snapshot
```

The job's working directory `/work` needs room for two copies of the database (an
`emptyDir` with a size limit in Kubernetes). The image runs as the `postgres` user (uid 999).

## Bucket layout

```
snapshots/<timestamp>/mex.dump.age    encrypted pg_dump (custom format)
snapshots/<timestamp>/manifest.json   sha256, size, alembic revisions, app image, counts
snapshots/latest.json                 {"latest": "snapshots/<timestamp>/"}, written last
```

## Testing

`test/run.sh` builds the image, seeds a throwaway database from
`site/mex_invenio/scripts/testdata.ndjson` (plus planted personal data in descriptions,
history, drafts and auxiliary tables), runs the job with `SKIP_UPLOAD=1`, decrypts the
result and fails if any planted or sampled value survives. It uses its own container,
network and port (5441) and takes about 10 minutes, mostly seeding.

```bash
docker/dev-snapshot/test/run.sh          # add --keep to keep the test database
```
