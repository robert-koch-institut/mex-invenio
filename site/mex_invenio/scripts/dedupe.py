"""Remove duplicate records: MEx identifiers that have more than one parent.

An import that fails to find a record it already created makes a second parent
for the same MEx identifier. That happened when an initial import was restarted
without skipping the records already imported, and when the existing-record
lookup failed during an import.

For each such identifier the earliest-created parent is kept and the others are
deleted, with their versions, drafts, PIDs, empty file buckets and search
documents. A duplicate is only deleted if it has a single version (no import has
updated it since) and the kept parent has a published latest version; anything
else is reported and left alone.

Run with the CLI command (dry run unless --commit is given):

        $ invenio mex dedupe-records [--created-after ...] [--commit]
"""

import json
import logging
import os.path
from collections import Counter
from dataclasses import dataclass
from datetime import datetime

from flask import current_app
from invenio_db import db
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_search import current_search_client
from invenio_search.utils import build_alias_name
from sqlalchemy import text

logger = logging.getLogger(__name__)

RECORDS = "rdm_records_metadata"
DRAFTS = "rdm_drafts_metadata"
PARENTS = "rdm_parents_metadata"
VERSIONS_STATE = "rdm_versions_state"
PIDS = "pidstore_pid"
BUCKETS = "files_bucket"

# Foreign keys into the deleted rows that are deleted along with them. A row
# referencing a duplicate through any other foreign key (files, communities,
# quotas, ...) stops the purge, as the duplicate is then more than a bare copy.
DELETED_REFERENCES = {
    (RECORDS, "parent_id"),
    (RECORDS, "bucket_id"),
    (RECORDS, "media_bucket_id"),
    (DRAFTS, "parent_id"),
    (DRAFTS, "bucket_id"),
    (DRAFTS, "media_bucket_id"),
    (VERSIONS_STATE, "parent_id"),
    (VERSIONS_STATE, "latest_id"),
    (VERSIONS_STATE, "next_draft_id"),
}


@dataclass
class Duplicate:
    """A parent to delete, with the parent kept for the same MEx identifier."""

    mex_id: str
    parent_id: str
    kept_parent_id: str
    record_type: str
    created: datetime


@dataclass
class Plan:
    """Duplicates to delete, and those found but left alone."""

    identifiers: int
    duplicates: list[Duplicate]
    refused: list[tuple[Duplicate, str]]
    outside_window: int


def find_duplicates(
    created_after: datetime | None = None, created_before: datetime | None = None
) -> Plan:
    """Find duplicated MEx identifiers and decide which parents to delete.

    Only duplicates whose first version was created within the window are
    candidates for deletion; the kept parent may be from any time.
    """
    rows = db.session.execute(
        text(f"""
            SELECT json->'custom_fields'->>'mex:identifier' AS mex_id,
                   parent_id::text,
                   min(created) AS first_created,
                   count(*) AS versions,
                   bool_or(is_latest_published) AS has_published_latest,
                   min(json->'metadata'->'resource_type'->>'id') AS record_type
            FROM (
                SELECT r.*,
                       r.id = vs.latest_id AND r.deletion_status = 'P'
                           AS is_latest_published
                FROM {RECORDS} r
                LEFT JOIN {VERSIONS_STATE} vs ON vs.parent_id = r.parent_id
                WHERE json->'custom_fields'->>'mex:identifier' IN (
                    SELECT json->'custom_fields'->>'mex:identifier'
                    FROM {RECORDS}
                    WHERE json->'custom_fields'->>'mex:identifier' IS NOT NULL
                    GROUP BY 1
                    HAVING count(DISTINCT parent_id) > 1
                )
            ) r
            GROUP BY 1, 2
        """)  # noqa: S608
    ).fetchall()

    parents_by_mex_id: dict[str, list] = {}
    for row in rows:
        parents_by_mex_id.setdefault(row.mex_id, []).append(row)

    duplicates, refused, outside_window = [], [], 0
    for mex_id, parents in parents_by_mex_id.items():
        kept, *others = sorted(parents, key=lambda p: (p.first_created, p.parent_id))
        for parent in others:
            duplicate = Duplicate(
                mex_id=mex_id,
                parent_id=parent.parent_id,
                kept_parent_id=kept.parent_id,
                record_type=parent.record_type,
                created=parent.first_created,
            )
            if (created_after and parent.first_created < created_after) or (
                created_before and parent.first_created >= created_before
            ):
                outside_window += 1
            elif parent.versions > 1:
                refused.append(
                    (
                        duplicate,
                        f"updated since it was created ({parent.versions} versions)",
                    )
                )
            elif not kept.has_published_latest:
                refused.append(
                    (duplicate, "kept parent has no published latest version")
                )
            else:
                duplicates.append(duplicate)

    return Plan(len(parents_by_mex_id), duplicates, refused, outside_window)


def _ids(sql: str, **params) -> list[str]:
    return [str(r[0]) for r in db.session.execute(text(sql), params).fetchall()]


def _rows_owned(parent_ids: list[str]) -> dict[str, list[str]]:
    """IDs of the rows owned by the given parents, by table."""
    params = {"parents": parent_ids}
    records = _ids(
        f"SELECT id FROM {RECORDS} WHERE parent_id = ANY(CAST(:parents AS uuid[]))",  # noqa: S608
        **params,
    )
    drafts = _ids(
        f"SELECT id FROM {DRAFTS} WHERE parent_id = ANY(CAST(:parents AS uuid[]))",  # noqa: S608
        **params,
    )
    buckets = _ids(
        f"""
        SELECT bucket FROM (
            SELECT bucket_id AS bucket, parent_id FROM {RECORDS}
            UNION SELECT media_bucket_id, parent_id FROM {RECORDS}
            UNION SELECT bucket_id, parent_id FROM {DRAFTS}
            UNION SELECT media_bucket_id, parent_id FROM {DRAFTS}
        ) b
        WHERE bucket IS NOT NULL AND parent_id = ANY(CAST(:parents AS uuid[]))
        """,  # noqa: S608
        **params,
    )
    pids = _ids(
        f"SELECT id FROM {PIDS} WHERE object_uuid = ANY(CAST(:objects AS uuid[]))",  # noqa: S608
        objects=records + drafts + parent_ids,
    )
    return {
        RECORDS: records,
        DRAFTS: drafts,
        PARENTS: parent_ids,
        PIDS: pids,
        BUCKETS: buckets,
    }


def _version_tables() -> list[str]:
    """History tables (SQLAlchemy-Continuum) of the deleted tables that exist."""
    candidates = [f"{t}_version" for t in (RECORDS, DRAFTS, PARENTS)]
    return _ids(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = current_schema() AND table_name = ANY(:tables)",
        tables=candidates,
    )


def _unexpected_references(owned: dict[str, list[str]]) -> dict[str, int]:
    """Rows referencing the deleted rows through foreign keys not deleted with them."""
    foreign_keys = db.session.execute(
        text("""
            SELECT DISTINCT kcu.table_name, kcu.column_name, ccu.table_name, col.udt_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu
              ON tc.constraint_name = ccu.constraint_name
            JOIN information_schema.columns col
              ON col.table_name = kcu.table_name AND col.column_name = kcu.column_name
            WHERE tc.constraint_type = 'FOREIGN KEY' AND ccu.table_name = ANY(:tables)
        """),
        {"tables": list(owned)},
    ).fetchall()

    found = {}
    for table, column, referenced, column_type in foreign_keys:
        ids = owned[referenced]
        if (table, column) in DELETED_REFERENCES or not ids:
            continue
        count = db.session.execute(
            text(
                f"SELECT count(*) FROM {table} "  # noqa: S608
                f"WHERE {column} = ANY(CAST(:ids AS {column_type}[]))"
            ),
            {"ids": ids},
        ).scalar()
        if count:
            found[f"{table}.{column}"] = count
    return found


def _registered_dois(pids: list[str]) -> int:
    if not pids:
        return 0
    return db.session.execute(
        text(
            f"SELECT count(*) FROM {PIDS} "  # noqa: S608
            "WHERE id = ANY(CAST(:pids AS integer[])) AND pid_type = 'doi' AND status = 'R'"
        ),
        {"pids": pids},
    ).scalar()


def _search_aliases() -> list[str]:
    return [
        build_alias_name(cls.index.search_alias)
        for cls in (
            current_rdm_records_service.record_cls,
            current_rdm_records_service.draft_cls,
        )
    ]


def _delete_batch(owned: dict[str, list[str]], version_tables: list[str]) -> None:
    """Delete one batch of duplicates from the search index, then the database.

    The search documents go first: if the database deletion then fails, the
    duplicates are still found on a re-run and their deletion completes.
    """
    documents = owned[RECORDS] + owned[DRAFTS]
    for alias in _search_aliases():
        current_search_client.delete_by_query(
            index=alias,
            body={"query": {"ids": {"values": documents}}},
            conflicts="proceed",
            refresh=True,
        )

    def delete(table, column, ids, id_type="uuid"):
        if ids:
            db.session.execute(
                text(
                    f"DELETE FROM {table} "  # noqa: S608
                    f"WHERE {column} = ANY(CAST(:ids AS {id_type}[]))"
                ),
                {"ids": ids},
            )

    delete(VERSIONS_STATE, "parent_id", owned[PARENTS])
    for table in version_tables:
        delete(table, "id", owned[RECORDS] + owned[DRAFTS] + owned[PARENTS])
    delete(RECORDS, "id", owned[RECORDS])
    delete(DRAFTS, "id", owned[DRAFTS])
    delete(PIDS, "id", owned[PIDS], id_type="integer")
    delete(PARENTS, "id", owned[PARENTS])
    delete(BUCKETS, "id", owned[BUCKETS])
    db.session.commit()


def _import_in_progress() -> bool:
    state_file = os.path.join(
        current_app.config.get("S3_DOWNLOAD_FOLDER", "s3_downloads"), ".import_state"
    )
    try:
        with open(state_file) as f:
            return json.load(f).get("status") == "in_progress"
    except (OSError, ValueError):
        return False


def dedupe_records(
    created_after: datetime | None = None,
    created_before: datetime | None = None,
    batch_size: int = 500,
    commit: bool = False,
    output: str | None = None,
    echo=print,
) -> bool:
    """Find duplicate parents and, with commit, delete them in batches.

    Returns False if the purge was stopped before deleting anything.
    """
    if _import_in_progress():
        echo("An import is in progress (.import_state). Stop it before deduplicating.")
        return False

    plan = find_duplicates(created_after, created_before)
    duplicates = plan.duplicates

    echo(f"MEx identifiers with more than one parent: {plan.identifiers}")
    echo(f"Duplicates outside the creation window, left alone: {plan.outside_window}")
    echo(f"Duplicates refused, left alone: {len(plan.refused)}")
    for duplicate, reason in plan.refused[:20]:
        echo(f"  {duplicate.mex_id} parent {duplicate.parent_id}: {reason}")
    echo(f"Duplicates to delete: {len(duplicates)}")
    if not duplicates:
        return True

    echo(f"  by type: {dict(Counter(d.record_type for d in duplicates).most_common())}")
    echo(
        f"  created: {min(d.created for d in duplicates)} "
        f"to {max(d.created for d in duplicates)}"
    )
    if output:
        with open(output, "w") as f:
            f.writelines(
                f"{d.parent_id} {d.kept_parent_id} {d.mex_id}\n" for d in duplicates
            )
        echo(f"  list written to {output} (duplicate parent, kept parent, identifier)")

    version_tables = _version_tables()
    batches = [
        [d.parent_id for d in duplicates[i : i + batch_size]]
        for i in range(0, len(duplicates), batch_size)
    ]

    # Check every batch before deleting any, so a purge either runs or doesn't.
    totals: Counter = Counter()
    for parent_ids in batches:
        owned = _rows_owned(parent_ids)
        unexpected = _unexpected_references(owned)
        if unexpected:
            echo(f"Stopped: duplicates are referenced from {unexpected}.")
            return False
        if _registered_dois(owned[PIDS]):
            echo("Stopped: duplicates have registered DOIs.")
            return False
        totals.update({table: len(ids) for table, ids in owned.items()})
    db.session.rollback()

    echo(f"Rows to delete: {dict(totals)} (and their history in {version_tables})")
    if not commit:
        echo("Dry run: nothing deleted. Re-run with --commit to delete.")
        return True

    for number, parent_ids in enumerate(batches, start=1):
        _delete_batch(_rows_owned(parent_ids), version_tables)
        logger.info(f"Deleted batch {number} of {len(batches)}.")
        echo(
            f"Deleted batch {number} of {len(batches)} ({len(parent_ids)} duplicates)."
        )

    echo(f"Deleted {len(duplicates)} duplicates.")
    return True
