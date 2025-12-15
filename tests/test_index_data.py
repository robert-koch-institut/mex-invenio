"""Test index_data population in MEX records."""

from invenio_access.permissions import system_identity
from invenio_rdm_records.proxies import current_rdm_records
from invenio_search import current_search_client
from invenio_search.utils import build_alias_name

from mex_invenio.records.api import MexRDMRecord
from mex_invenio.services.search import MexDumper
from tests.data import resource_data, person_data


def test_index_data_creator_contributor(
    db, location, resource_type_v, contributors_role_v, import_file
):
    """Test that index_data is populated when accessing a record with MexDumper-compatible fields."""
    service = current_rdm_records.records_service

    # 1. Import linked records first (person records for contributors/creators)
    messages_person1 = import_file(
        "person1",
        {
            **person_data,
            "identifier": "gwjehcvTCGBH4CTyDWTiXY",  # matches resource_data contributor
            "fullName": ["John Bazooge"],
        },
    )

    messages_person2 = import_file(
        "person2",
        {
            **person_data,
            "identifier": "ddTKOu0dKtmUsy6SoGjxBC",  # matches resource_data contributor
            "fullName": ["Jane Bumbles"],
        },
    )

    current_search_client.indices.refresh(index=build_alias_name("mexrecords-records"))

    # 2. Import the resource record that has contributor/creator fields (processed by MexDumper)
    messages_resource = import_file("resource", resource_data)

    # 3. Manually trigger index refresh to ensure all records are searchable
    current_search_client.indices.refresh(index=build_alias_name("mexrecords-records"))

    # Debug: Check all created records
    search_obj = service.search(system_identity)
    all_records = list(search_obj.hits)

    # Find and test the resource record specifically
    resource_record = None
    for record in all_records:
        if (
            record.get("custom_fields", {}).get("mex:identifier")
            == resource_data["identifier"]
        ):
            resource_record = record
            break

    assert resource_record is not None, "Resource record not found"

    # The search results already contain index_data populated by the indexing process
    index_data = resource_record.get("index_data", {})
    expected_contributors = resource_data["contributor"]

    # Verify both contributors should be present
    assert "contributors" in index_data
    contributors = index_data["contributors"]

    assert len(contributors) == 2, f"Expected 2 contributors, got {len(contributors)}"
    assert "John Bazooge" in contributors, "Missing John Bazooge in contributors"
    assert "Jane Bumbles" in contributors, "Missing Jane Bumbles in contributors"
