# Image for the developer snapshot CronJob (see README.md in this directory).
# PG_MAJOR must match the staging PostgreSQL major version: pg_dump needs to be at
# least the server's version, and the scratch database restores the dump.
ARG PG_MAJOR=14
FROM postgres:${PG_MAJOR}-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

COPY sanitise.sql verify.sql snapshot.sh /opt/dev-snapshot/
RUN chmod 0755 /opt/dev-snapshot/snapshot.sh \
    && mkdir -p /work && chown postgres:postgres /work

# initdb refuses to run as root.
USER postgres
WORKDIR /work
ENTRYPOINT ["/opt/dev-snapshot/snapshot.sh"]
