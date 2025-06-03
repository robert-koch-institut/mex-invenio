from invenio_access.permissions import system_identity
from invenio_rdm_records.proxies import current_rdm_records

from tests.conftest import created_regex, search_messages
from tests.data import person_data


def test_import_person_skipped(
    db, location, resource_type_v, contributors_role_v, import_file
):
    """Test that the CLI command skips a reimport of person data."""
    service = current_rdm_records.records_service

    # Import the person data using the import_file fixture.
    messages = import_file("person", person_data)

    # Log output is captured in the import_file fixture defined in
    # conftest and returned by the fixture as a list of messages.
    match = search_messages(messages, created_regex)

    number_of_records_published = int(match.group("count"))
    published_record_id = match.group("record_id")

    assert match is not None

    search_obj = service.search(system_identity)
    record = list(search_obj.hits)[0]

    # Confirm the record was created with the expected data.
    assert match.group("verb") == "Created"
    assert search_obj.total == number_of_records_published
    assert record["id"] == published_record_id
    # Check the custom fields and metadata.
    assert "dennisray@example.org" in record["custom_fields"]["mex:email"]
    assert record["metadata"]["title"] == "these role early" # original data has two titles, but one only has 2 chars

    # Reimport the same person data to test the "Skipped" case.
    messages = import_file("person", person_data)
    match = search_messages(messages, created_regex)

    assert match.group("verb") == "Skipped"

    search_obj = service.search(system_identity)
    record = list(search_obj.hits)[0]

    # Verify that the record is still the same and has not been modified.
    assert record["versions"]["is_latest"] is True


def test_import_person_2nd_version(
    db, location, resource_type_v, contributors_role_v, import_file
):
    """Test that the CLI command imports the contact point data correctly."""
    service = current_rdm_records.records_service

    # Import the person data using the import_file fixture.
    messages = import_file("person", person_data)

    # Log output is captured in the import_file fixture defined in
    # conftest and returned by the fixture as a list of messages.
    match = search_messages(messages, created_regex)

    number_of_records_published = int(match.group("count"))
    published_record_id = match.group("record_id")

    assert match is not None

    search_obj = service.search(system_identity)
    record = list(search_obj.hits)[0]

    # Confirm the record was created with the expected data.
    assert match.group("verb") == "Created"
    assert search_obj.total == number_of_records_published
    assert record["id"] == published_record_id
    # Check the custom fields and metadata.
    assert "dennisray@example.org" in record["custom_fields"]["mex:email"]
    assert record["metadata"]["title"] == "these role early" # original data has two titles, but one only has 2 chars
    assert record["versions"]["index"] == 1

    # Remove the email to trigger an update.
    person_data["email"].pop()

    # Reimport the same person data to test the "Skipped" case.
    messages = import_file("person_2", person_data)
    match = search_messages(messages, created_regex)

    assert match.group("verb") == "Updated"

    search_obj = service.search(system_identity)
    record = list(search_obj.hits)[0]

    # Verify that the record is still the same and has not been modified.
    assert record["id"] is not published_record_id
    assert record["versions"]["index"] == 2
    assert len(record["custom_fields"]["mex:email"]) == 1
