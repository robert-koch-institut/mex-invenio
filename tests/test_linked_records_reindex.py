"""Test that imports keep linked records' indexed display data up to date.

A record's display_data.linked_records is built when the record is indexed: forward
links carry the linked record's title, and backwards_linked lists the records that
link to it. Each test imports records in an order where the earlier record is only
correct if the later import re-indexes it.
"""

import pytest
from flask import current_app
from invenio_search import current_search_client
from invenio_search.utils import build_alias_name

from mex_invenio.records.api import MexRDMRecord
from tests.data import org_unit_data, resource_data

ORG_UNIT_ID = org_unit_data["identifier"]
PARENT_UNIT_ID = org_unit_data["parentUnit"]
RESOURCE_ID = resource_data["identifier"]
PARENT_RESOURCE_ID = "dO8iP5KEwJGZPXwCXKnFOZ"  # resource_data["isPartOf"]


@pytest.fixture(autouse=True)
def clear_dumper_cache():
    """Start each test with an empty MexDumper record cache.

    The dumper caches linked records for the life of the process, so records from
    an earlier test (whose database rows were rolled back) would otherwise still be
    shown as linked.
    """
    MexRDMRecord.dumper._record_cache.clear()


def _linked_records(mex_id):
    """Indexed display_data.linked_records of the latest version of a record."""
    alias = build_alias_name("mexrecords-records")
    current_search_client.indices.refresh(index=alias)
    hits = current_search_client.search(
        index=alias, body={"size": 100, "query": {"match_all": {}}}
    )["hits"]["hits"]
    latest = [
        h["_source"]
        for h in hits
        if h["_source"].get("custom_fields", {}).get("mex:identifier") == mex_id
        and h["_source"].get("versions", {}).get("is_latest", True)
    ]
    assert len(latest) == 1, f"Expected one latest indexed version of {mex_id}"
    return latest[0].get("display_data", {}).get("linked_records", {})


def _shown_values(linked_records, field, link_id):
    """Display values shown for one link in a forward-linked field."""
    for entry in linked_records.get(field, []):
        if entry.get("link_id") == link_id:
            return [v.get("value") for v in entry.get("display_value", [])]
    return None


def _backlinks(linked_records, field):
    """MEx identifiers listed as linking back to a record through a field."""
    entries = linked_records.get("backwards_linked", {}).get(field, [])
    return {entry.get("link_id") for entry in entries}


def test_backlink_added_to_existing_target(
    db, location, resource_type_v, contributors_role_v, import_file
):
    """A new record linking to an existing one shows up in the existing one's backlinks."""
    import_file(
        "parent-resource",
        {**resource_data, "identifier": PARENT_RESOURCE_ID, "isPartOf": []},
    )
    assert _backlinks(_linked_records(PARENT_RESOURCE_ID), "mex:isPartOf") == set()

    import_file("resource", resource_data)

    assert _backlinks(_linked_records(PARENT_RESOURCE_ID), "mex:isPartOf") == {
        RESOURCE_ID
    }


def test_title_shown_when_target_created_later(
    db, location, resource_type_v, contributors_role_v, import_file
):
    """A record imported before the record it links to shows that record's title once imported."""
    no_record = current_app.config.get("NO_RECORD_STRING", "No record found")

    import_file("resource", resource_data)
    assert _shown_values(
        _linked_records(RESOURCE_ID), "mex:unitInCharge", ORG_UNIT_ID
    ) == [no_record]

    import_file("org-unit", org_unit_data)

    shown = _shown_values(_linked_records(RESOURCE_ID), "mex:unitInCharge", ORG_UNIT_ID)
    assert shown == [name["value"] for name in org_unit_data["name"]]


def test_nullable_reference_title_shown_when_target_created_later(
    db, location, resource_type_v, contributors_role_v, import_file
):
    """The same holds for a nullable single reference (org unit.parentUnit)."""
    no_record = current_app.config.get("NO_RECORD_STRING", "No record found")
    parent_name = [{"value": "Parent unit", "language": "en"}]

    import_file("org-unit", org_unit_data)
    assert _shown_values(
        _linked_records(ORG_UNIT_ID), "mex:parentUnit", PARENT_UNIT_ID
    ) == [no_record]

    import_file(
        "parent-unit",
        {
            **org_unit_data,
            "identifier": PARENT_UNIT_ID,
            "parentUnit": None,
            "name": parent_name,
        },
    )

    shown = _shown_values(
        _linked_records(ORG_UNIT_ID), "mex:parentUnit", PARENT_UNIT_ID
    )
    assert shown == ["Parent unit"]
