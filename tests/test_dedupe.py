"""Test removal of duplicate records: a second parent for an existing MEx identifier."""

import copy
import json
import os

import pytest
import sqlalchemy as sa
from invenio_accounts.models import User
from invenio_db import db
from invenio_rdm_records.fixtures.tasks import get_authenticated_identity
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.records.api import RDMRecord
from invenio_search import current_search_client
from invenio_search.utils import build_alias_name

from mex_invenio.cli import dedupe_records
from mex_invenio.scripts.import_data import process_record_batch
from tests.data import contact_point_data

MEX_ID = contact_point_data["identifier"]


def _records(mex_id):
    """(record id, parent id) of every version of the given MEx identifier, oldest first."""
    rows = db.session.execute(
        sa.text(
            "SELECT id::text, parent_id::text FROM rdm_records_metadata "
            "WHERE json->'custom_fields'->>'mex:identifier' = :mex_id "
            "ORDER BY created"
        ),
        {"mex_id": mex_id},
    ).fetchall()
    return [tuple(r) for r in rows]


def _parents(mex_id):
    return list(dict.fromkeys(parent for _, parent in _records(mex_id)))


def _indexed(mex_id):
    """IDs of the search documents of the given MEx identifier."""
    alias = build_alias_name("mexrecords-records")
    current_search_client.indices.refresh(index=alias)
    hits = current_search_client.search(
        index=alias, body={"size": 100, "query": {"match_all": {}}}
    )["hits"]["hits"]
    return {
        h["_id"]
        for h in hits
        if h["_source"].get("custom_fields", {}).get("mex:identifier") == mex_id
    }


def _import(records_data, existing_records=None):
    """Run the import's batch step, as when its existing-record lookup came back empty.

    The data is copied, as mex_to_invenio_schema modifies the record it is given.
    """
    owner = User.query.filter_by(email="importer@address.com").one()
    identity = get_authenticated_identity(owner.id)
    results = process_record_batch(
        copy.deepcopy(records_data), existing_records or {}, identity
    )
    current_rdm_records_service.indexer.refresh()
    return results


def _as_existing(record_id):
    """A record in the form bulk_search_existing_records returns it."""
    record = RDMRecord.get_record(record_id)
    return {
        "id": record.pid.pid_value,
        "uuid": str(record.id),
        "custom_fields": record["custom_fields"],
        "metadata": record["metadata"],
    }


@pytest.fixture
def duplicated(db, location, resource_type_v, contributors_role_v, import_file):
    """A contact point imported twice, the second time without finding the first.

    Returns the (record id, parent id) of the original and of the duplicate.
    """
    import_file("contact-point", contact_point_data)
    _import([contact_point_data])

    records = _records(MEX_ID)
    assert len(_parents(MEX_ID)) == 2
    assert _indexed(MEX_ID) == {record_id for record_id, _ in records}
    return records


def test_dry_run_deletes_nothing(duplicated, cli_runner):
    """Without --commit the duplicate is reported and nothing is changed."""
    result = cli_runner(dedupe_records)

    assert result.exit_code == 0, result.output
    assert "Duplicates to delete: 1" in result.output
    assert "Dry run: nothing deleted" in result.output
    assert _records(MEX_ID) == duplicated
    assert len(_indexed(MEX_ID)) == 2


def test_commit_deletes_newer_parent(duplicated, cli_runner):
    """The later-created parent is deleted with its PIDs and search document."""
    (original_id, original_parent), (duplicate_id, duplicate_parent) = duplicated

    result = cli_runner(dedupe_records, "--commit")

    assert result.exit_code == 0, result.output
    assert "Deleted 1 duplicates." in result.output
    assert _records(MEX_ID) == [(original_id, original_parent)]
    assert _indexed(MEX_ID) == {original_id}

    leftovers = db.session.execute(
        sa.text("""
            SELECT (SELECT count(*) FROM pidstore_pid
                    WHERE object_uuid = ANY(CAST(:ids AS uuid[])))
                 + (SELECT count(*) FROM rdm_versions_state WHERE parent_id = :parent)
                 + (SELECT count(*) FROM rdm_parents_metadata WHERE id = :parent)
                 + (SELECT count(*) FROM rdm_records_metadata_version WHERE id = :record)
        """),
        {
            "ids": [duplicate_id, duplicate_parent],
            "parent": duplicate_parent,
            "record": duplicate_id,
        },
    ).scalar()
    assert leftovers == 0

    # The original is untouched and can still be read through the service.
    assert (
        RDMRecord.get_record(original_id)["custom_fields"]["mex:identifier"] == MEX_ID
    )


def test_duplicate_outside_window_left_alone(duplicated, cli_runner):
    """Only duplicates created within --created-after/--created-before are deleted."""
    result = cli_runner(dedupe_records, "--created-after", "2999-01-01", "--commit")

    assert result.exit_code == 0, result.output
    assert "outside the creation window, left alone: 1" in result.output
    assert "Duplicates to delete: 0" in result.output
    assert _records(MEX_ID) == duplicated


def test_updated_duplicate_refused(duplicated, cli_runner):
    """A duplicate an import has since updated is reported, not deleted."""
    duplicate_id = duplicated[1][0]
    _import(
        [{**contact_point_data, "email": ["updated@example.com"]}],
        {MEX_ID: _as_existing(duplicate_id)},
    )
    records = _records(MEX_ID)
    assert len(records) == 3

    result = cli_runner(dedupe_records, "--commit")

    assert result.exit_code == 0, result.output
    assert "updated since it was created (2 versions)" in result.output
    assert "Duplicates to delete: 0" in result.output
    assert _records(MEX_ID) == records


def test_import_in_progress_stops(app, duplicated, cli_runner):
    """Nothing is done while an import is in progress."""
    state_file = os.path.join(app.config["S3_DOWNLOAD_FOLDER"], ".import_state")
    with open(state_file, "w") as f:
        json.dump({"status": "in_progress"}, f)
    try:
        result = cli_runner(dedupe_records, "--commit")
    finally:
        os.remove(state_file)

    assert result.exit_code == 1
    assert "An import is in progress" in result.output
    assert _records(MEX_ID) == duplicated
