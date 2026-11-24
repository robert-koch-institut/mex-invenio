"""Test re-indexing of records whose search documents disagree with the database."""

import copy

import pytest
import sqlalchemy as sa
from invenio_accounts.models import User
from invenio_db import db
from invenio_rdm_records.fixtures.tasks import get_authenticated_identity
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.records.api import RDMRecord
from invenio_search import current_search_client
from invenio_search.utils import build_alias_name

from mex_invenio.cli import reindex_stale
from mex_invenio.scripts.import_data import process_record_batch
from tests.data import contact_point_data

MEX_ID = contact_point_data["identifier"]
ALIAS = "mexrecords-records"


def _import(records_data, existing_records=None):
    owner = User.query.filter_by(email="importer@address.com").one()
    identity = get_authenticated_identity(owner.id)
    process_record_batch(copy.deepcopy(records_data), existing_records or {}, identity)
    current_rdm_records_service.indexer.refresh()


def _versions():
    """Record ids of the identifier's versions, oldest first."""
    rows = db.session.execute(
        sa.text(
            "SELECT id::text FROM rdm_records_metadata "
            "WHERE json->'custom_fields'->>'mex:identifier' = :mex_id ORDER BY created"
        ),
        {"mex_id": MEX_ID},
    ).fetchall()
    return [r[0] for r in rows]


def _document(record_id):
    alias = build_alias_name(ALIAS)
    current_search_client.indices.refresh(index=alias)
    hits = current_search_client.search(
        index=alias,
        body={"query": {"ids": {"values": [record_id]}}, "version": True},
    )["hits"]["hits"]
    return hits[0] if hits else None


def _is_latest(record_id):
    return _document(record_id)["_source"]["versions"]["is_latest"]


@pytest.fixture
def two_versions(db, location, resource_type_v, contributors_role_v, import_file):
    """A contact point imported, then updated by a second import: two versions."""
    import_file("contact-point", contact_point_data)
    record = RDMRecord.get_record(_versions()[0])
    existing = {
        MEX_ID: {
            "id": record.pid.pid_value,
            "uuid": str(record.id),
            "custom_fields": record["custom_fields"],
            "metadata": record["metadata"],
        }
    }
    _import([{**contact_point_data, "email": ["updated@example.com"]}], existing)

    older, latest = _versions()
    assert not _is_latest(older)
    assert _is_latest(latest)
    return older, latest


@pytest.fixture
def stale_index(two_versions):
    """Index the older version as the latest, and remove the latest version.

    That is what an import leaves behind when its indexing is cut short.
    """
    older, latest = two_versions

    document = _document(older)
    source = document["_source"]
    source["versions"]["is_latest"] = True
    # Same external version, so the indexer can still overwrite it afterwards.
    current_search_client.index(
        index=document["_index"],
        id=older,
        body=source,
        version=document["_version"],
        version_type="external_gte",
        refresh=True,
    )
    # A plain delete would raise the document's version past the record's revision,
    # making the indexer's later write a version conflict; keep the version as it is.
    latest_document = _document(latest)
    current_search_client.delete(
        index=latest_document["_index"],
        id=latest,
        version=latest_document["_version"],
        version_type="external_gte",
        refresh=True,
    )
    return older, latest


def test_nothing_to_do(two_versions, cli_runner):
    result = cli_runner(reindex_stale)

    assert result.exit_code == 0, result.output
    assert "Older versions indexed as the latest version: 0" in result.output
    assert "Latest versions not indexed as the latest version: 0" in result.output


def test_dry_run_reindexes_nothing(stale_index, cli_runner):
    older, latest = stale_index

    result = cli_runner(reindex_stale)

    assert result.exit_code == 0, result.output
    assert "Older versions indexed as the latest version: 1" in result.output
    assert "Latest versions not indexed as the latest version: 1" in result.output
    assert "Dry run: nothing re-indexed" in result.output
    assert _is_latest(older)
    assert _document(latest) is None


def test_commit_reindexes_stale_and_missing(stale_index, cli_runner):
    older, latest = stale_index

    result = cli_runner(reindex_stale, "--commit")

    assert result.exit_code == 0, result.output
    assert "Re-indexing 2 records" in result.output
    assert "Still wrong: 0 older versions indexed as latest, 0 latest" in result.output
    assert not _is_latest(older)
    assert _is_latest(latest)
