"""Re-index records whose search documents disagree with the database.

Each version of a record has its own search document, with versions.is_latest
telling whether it is the latest version. When a new version is published, the
older versions have to be re-indexed too, to lose that flag. Imports run with
indexing disabled and index afterwards, and records they leave out keep stale
documents:

- an older version still indexed as the latest: /records/mex/<id> can open it,
  showing the "newer version" banner on what looks like the current record
- a latest version not indexed as the latest: the record is missing from search

This finds both by comparing the latest-version documents in the search index with
the latest published versions in the database, and re-indexes them.

Run with the CLI command (dry run unless --commit is given):

        $ invenio mex reindex-stale [--commit]
"""

import logging
from collections import Counter

from celery import current_app as current_celery_app
from invenio_db import db
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_search import current_search_client
from invenio_search.utils import build_alias_name
from opensearchpy.helpers import BulkIndexError, scan
from sqlalchemy import text

logger = logging.getLogger(__name__)

# More rounds than this without the queue emptying means something else is holding
# or re-adding messages; stop rather than loop forever.
MAX_EMPTY_ROUNDS = 3


def find_stale_and_missing() -> tuple[set[str], set[str]]:
    """Record IDs indexed as latest but not latest in the database (stale), and
    latest published in the database but not indexed as latest (missing)."""
    service = current_rdm_records_service
    alias = build_alias_name(service.record_cls.index.search_alias)
    indexed_latest = {
        hit["_id"]
        for hit in scan(
            current_search_client,
            index=alias,
            query={"query": {"term": {"versions.is_latest": True}}},
            _source=False,
        )
    }
    latest = {
        str(row[0])
        for row in db.session.execute(
            text("""
                SELECT vs.latest_id FROM rdm_versions_state vs
                JOIN rdm_records_metadata r ON r.id = vs.latest_id
                WHERE r.deletion_status = 'P'
            """)
        )
    }
    db.session.rollback()
    return indexed_latest - latest, latest - indexed_latest


def _queued() -> int:
    """Messages waiting in the record indexer's bulk queue."""
    indexer = current_rdm_records_service.indexer
    with current_celery_app.pool.acquire(block=True) as conn:
        return indexer.mq_queue(conn.default_channel).queue_declare(passive=True)[1]


def _process_queue(echo) -> None:
    """Process the bulk queue until it is empty.

    Each process_bulk_queue call takes a limited number of messages, and messages
    of records that fail to dump are rejected without being counted, so the queue
    length rather than the returned count decides when it is done.
    """
    indexer = current_rdm_records_service.indexer
    empty_rounds = 0
    while _queued():
        try:
            indexed, failed = indexer.process_bulk_queue()
        except BulkIndexError as e:
            indexed, failed = 0, len(e.errors)
            logger.error(f"Bulk indexing errors: {e.errors[:5]}")
        echo(f"  indexed {indexed}, failed {failed}, still queued {_queued()}")
        empty_rounds = empty_rounds + 1 if not indexed else 0
        if empty_rounds >= MAX_EMPTY_ROUNDS:
            echo("  queue is not emptying; stopped processing it")
            return


def _index_one_by_one(record_ids: set[str]) -> dict[str, str]:
    """Index records individually, returning the error of each that failed."""
    service = current_rdm_records_service
    errors = {}
    for record_id in record_ids:
        try:
            service.indexer.index(service.record_cls.get_record(record_id))
        except Exception as e:
            errors[record_id] = f"{type(e).__name__}: {e}"[:300]
    return errors


def reindex_stale(commit: bool = False, echo=print) -> bool:
    """Find stale and missing latest-version documents and, with commit, re-index them.

    Records still wrong after the bulk re-index are indexed one by one, to report
    why they fail. Returns False if any remain wrong.
    """
    stale, missing = find_stale_and_missing()
    echo(f"Older versions indexed as the latest version: {len(stale)}")
    echo(f"Latest versions not indexed as the latest version: {len(missing)}")
    record_ids = stale | missing
    if not record_ids:
        return True
    if not commit:
        echo("Dry run: nothing re-indexed. Re-run with --commit to re-index them.")
        return True

    echo(f"Re-indexing {len(record_ids)} records")
    current_rdm_records_service.indexer.bulk_index(record_ids)
    _process_queue(echo)
    current_rdm_records_service.indexer.refresh()

    stale, missing = find_stale_and_missing()
    remaining = stale | missing
    if remaining:
        echo(
            f"Still wrong after bulk re-indexing: {len(remaining)}; indexing one by one"
        )
        errors = _index_one_by_one(remaining)
        current_rdm_records_service.indexer.refresh()
        if errors:
            echo(f"  failed: {dict(Counter(e.split(':')[0] for e in errors.values()))}")
            for record_id, error in list(errors.items())[:20]:
                echo(f"  {record_id}: {error}")
        stale, missing = find_stale_and_missing()
        remaining = stale | missing

    echo(
        f"Done. Still wrong: {len(stale)} older versions indexed as latest, "
        f"{len(missing)} latest versions not indexed as latest."
    )
    return not remaining
