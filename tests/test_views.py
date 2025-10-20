"""Tests of view functions."""

from invenio_access.permissions import system_identity
from invenio_rdm_records.proxies import current_rdm_records

from mex_invenio.record.record import MexRecord
from tests.conftest import created_regex, search_messages
from tests.data import person_data


def test_index_view(client):
    """Simple check that index view does not give an error when rendered."""
    res = client.get("/")
    assert res.status_code == 200


def test_mex_record_view_as_json(
    db, location, resource_type_v, contributors_role_v, import_file, client
):
    """Test that MexRecord JSON endpoint returns proper JSON."""
    service = current_rdm_records.records_service

    # Import the person data using the import_file fixture
    messages = import_file("person", person_data)

    # Get the created record ID from log messages
    match = search_messages(messages, created_regex)
    assert match is not None
    assert match.group("verb") == "Created"

    # Get the record from search to find the mex_id
    search_obj = service.search(system_identity)
    record = list(search_obj.hits)[0]
    mex_id = record["custom_fields"]["mex:identifier"]

    # Test the JSON endpoint using client
    json_url = f"/records/mex/{mex_id}/json"
    response = client.get(json_url)

    # Verify response is successful
    assert response.status_code == 200, (
        f"JSON endpoint should return 200, got {response.status_code}"
    )

    # Verify content type is JSON
    assert response.content_type == "application/json", (
        f"Expected JSON content type, got {response.content_type}"
    )

    # Parse the JSON response
    json_result = response.get_json()
    assert json_result is not None, "Response should contain valid JSON"

    # Verify that essential record fields are present
    assert "id" in json_result, "JSON result should contain 'id' field"
    assert "metadata" in json_result, "JSON result should contain 'metadata' field"
    assert "custom_fields" in json_result, (
        "JSON result should contain 'custom_fields' field"
    )

    # Verify that the mex_id matches
    assert json_result["custom_fields"]["mex:identifier"] == mex_id, (
        "JSON result should contain the correct mex:identifier"
    )

    # Verify that the JSON contains the expected person data
    assert "dennisray@example.org" in json_result["custom_fields"]["mex:email"], (
        "JSON result should contain the expected email"
    )
    assert json_result["metadata"]["title"] == "these role early", (
        "JSON result should contain the expected title"
    )
