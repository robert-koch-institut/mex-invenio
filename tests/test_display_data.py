"""Test display_data population in MEX records."""

from invenio_access.permissions import system_identity
from invenio_rdm_records.proxies import current_rdm_records

from tests.data import org_unit_data, person_data, resource_data


def get_record(records, identifier):
    for record in records:
        if record.get("custom_fields", {}).get("mex:identifier") == identifier:
            return record
    return None


def test_display_data_contact_creator(
    db, location, resource_type_v, contributors_role_v, import_file
):
    """Test that display_data is populated and automatically updated when linked records change.

    This test verifies the complete display_data lifecycle:
    1. Creates an organizational unit, two person records, and a resource record
    2. Verifies that the resource record's display_data correctly shows linked person names
       in creator and contributor fields
    3. Updates the organizational unit's name to test cascading display updates
    4. Verifies that person records referencing the updated org unit automatically
       have their memberOf display_data updated with the new organizational unit name

    This ensures that when core entities (like organizational units) are modified,
    all dependent records automatically reflect the updated information in their
    display_data without requiring manual re-indexing of individual records.
    """
    service = current_rdm_records.records_service

    # Import an org unit record (to test org unit linked records)
    messages_orgunit = import_file("orgunit", org_unit_data)

    # Import linked records first (person records for contact/creator)
    messages_person1 = import_file(
        "person1",
        {
            **person_data,
            "identifier": "gwjehcvTCGBH4CTyDWTiXY",  # matches resource_data contributor
            "fullName": ["John Bazooge"],
            "memberOf": ["sLrfLJKbfnSUGkMJsOXA5"],  # Use the org unit being tested
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

    # Import the resource record that has contact/creator fields (processed by MexDumper)
    messages_resource = import_file("resource", resource_data)

    # Debug: Check all created records
    search_obj = service.search(system_identity)
    all_records = list(search_obj.hits)

    # Find and test the resource record specifically
    search_record = get_record(all_records, resource_data["identifier"])
    assert search_record is not None, "Resource record not found"

    # Get the actual record object to trigger display_data generation
    record_id = search_record["id"]
    resource_record = service.read(system_identity, record_id).data

    # The search results already contain display_data populated by the indexing process
    display_data = resource_record.get("display_data", {})
    assert "linked_records" in display_data, "linked_records not found in display_data"

    linked_records = display_data["linked_records"]

    # Verify creator display data
    expected_creators = resource_data["creator"]
    assert "mex:creator" in linked_records, "mex:creator not found in linked_records"

    creators = linked_records["mex:creator"]
    assert len(creators) == 2, f"Expected 2 creators, got {len(creators)}"

    # Check creator display values
    creator_display_values = []
    for creator in creators:
        assert "display_value" in creator, "display_value not found in creator"
        assert "link_id" in creator, "link_id not found in creator"

        # Extract display values
        for display_val in creator["display_value"]:
            assert isinstance(display_val, dict)
            assert "value" in display_val
            creator_display_values.append(display_val["value"])

    assert "John Bazooge" in creator_display_values, (
        "Missing John Bazooge in creator display values"
    )
    assert "Jane Bumbles" in creator_display_values, (
        "Missing Jane Bumbles in creator display values"
    )

    # Verify contributor display data (should be same as creators based on resource_data)
    assert "mex:contributor" in linked_records, (
        "mex:contributor not found in linked_records"
    )

    contributors = linked_records["mex:contributor"]
    assert len(contributors) == 2, f"Expected 2 contributors, got {len(contributors)}"

    # Check contributor display values
    contributor_display_values = []
    for contributor in contributors:
        assert "display_value" in contributor, "display_value not found in contributor"
        assert "link_id" in contributor, "link_id not found in contributor"

        # Extract display values
        for display_val in contributor["display_value"]:
            assert isinstance(display_val, dict)
            assert "value" in display_val
            contributor_display_values.append(display_val["value"])

    assert "John Bazooge" in contributor_display_values, (
        "Missing John Bazooge in contributor display values"
    )
    assert "Jane Bumbles" in contributor_display_values, (
        "Missing Jane Bumbles in contributor display values"
    )

    messages_org_unit_changed = import_file(
        "org_unit_changed",
        {
            **org_unit_data,
            "name": [{"value": "New Org Unit Name"}],
        },
    )

    # Check that the person record's memberOf display value was updated
    person_record_info = get_record(all_records, "gwjehcvTCGBH4CTyDWTiXY")
    assert person_record_info is not None, "Person record not found"
    person_record = service.read(system_identity, person_record_info["id"]).data

    display_data = person_record.get("display_data", {})
    assert "linked_records" in display_data, "linked_records not found in display_data"

    linked_records = display_data["linked_records"]
    member_of = linked_records["mex:memberOf"]

    # Find the org unit that was updated (sLrfLJKbfnSUGkMJsOXA5)
    updated_unit = None
    for unit in member_of:
        if unit["link_id"] == "sLrfLJKbfnSUGkMJsOXA5":
            updated_unit = unit
            break

    assert updated_unit is not None, "Updated org unit not found in memberOf"
    assert updated_unit["display_value"][0]["value"] == "New Org Unit Name"


def test_display_data_normalization(
    db, location, resource_type_v, contributors_role_v, import_file
):
    """Test that display_data properly normalizes mixed display value formats."""
    service = current_rdm_records.records_service

    # Import a person record with a simple string name (will be normalized)
    messages_person = import_file(
        "person_simple",
        {
            **person_data,
            "identifier": "testPersonId123",
            "fullName": ["Simple Name"],  # This will be converted to object format
        },
    )

    # Import a resource that references this person
    test_resource_data = {
        **resource_data,
        "identifier": "testResourceId123",
        "creator": ["testPersonId123"],  # Reference the person above
    }

    messages_resource = import_file("test_resource", test_resource_data)

    # Find the resource record
    search_obj = service.search(system_identity)
    all_records = list(search_obj.hits)

    search_record = None
    for record in all_records:
        if record.get("custom_fields", {}).get("mex:identifier") == "testResourceId123":
            search_record = record
            break

    assert search_record is not None, "Test resource record not found"

    # Get the actual record object to trigger display_data generation
    record_id = search_record["id"]
    resource_record = service.read(system_identity, record_id).data

    # Check display_data normalization
    display_data = resource_record.get("display_data", {})
    assert "linked_records" in display_data, "linked_records not found in display_data"

    linked_records = display_data["linked_records"]
    assert "mex:creator" in linked_records, "mex:creator not found in linked_records"

    creators = linked_records["mex:creator"]
    assert len(creators) == 1, f"Expected 1 creator, got {len(creators)}"

    creator = creators[0]
    assert "display_value" in creator, "display_value not found in creator"

    # Verify normalization: display_value should be list of objects with language/value
    display_values = creator["display_value"]
    assert isinstance(display_values, list), "display_value should be a list"

    for display_val in display_values:
        assert isinstance(display_val, dict), "Each display_value item should be a dict"
        assert "value" in display_val, "display_value should have 'value' key"
        assert display_val["value"] == "Simple Name", (
            "Value should match the person's fullName"
        )
