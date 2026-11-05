import os
from unittest.mock import patch

from flask import current_app
from invenio_access.permissions import system_identity
from invenio_rdm_records.proxies import current_rdm_records
from invenio_search import current_search_client
from invenio_search.utils import build_alias_name

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
    assert (
        record["metadata"]["title"] == "these role early"
    )  # original data has two titles, but one only has 2 chars

    # Reimport the same person data to test the "Skipped" case.
    messages = import_file("person", person_data)
    match = search_messages(messages, created_regex)

    assert match.group("verb") == "Skipped"

    search_obj = service.search(system_identity)
    record = list(search_obj.hits)[0]

    # Verify that the record is still the same and has not been modified.
    assert record["versions"]["is_latest"] is True


def test_import_person_2nd_version(
    db, location, resource_type_v, contributors_role_v, import_file, client
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
    assert (
        record["metadata"]["title"] == "these role early"
    )  # original data has two titles, but one only has 2 chars
    assert record["versions"]["index"] == 1

    # Remove the email to trigger an update.
    person_data["email"].pop()

    # Reimport modified person data to test the "Updated" case.
    messages = import_file("person_2", person_data)
    match = search_messages(messages, created_regex)

    assert match.group("verb") == "Updated"

    search_obj = service.search(system_identity)
    record = list(search_obj.hits)[0]

    # Verify that the record is not the same and has been modified.
    assert record["id"] is not published_record_id
    assert record["versions"]["index"] == 2
    assert len(record["custom_fields"]["mex:email"]) == 1

    # Verify versioned redirects
    mex_id = record["custom_fields"]["mex:identifier"]

    new_version_resp = client.get(f"/records/pid/{record['id']}")
    assert new_version_resp.status_code == 302
    assert f"/records/mex/{mex_id}" in new_version_resp.data.decode("utf-8")

    older_version_resp = client.get(f"/records/pid/{published_record_id}")
    assert older_version_resp.status_code == 302
    assert f"/records/mex/{mex_id}?version_id=1" in older_version_resp.data.decode(
        "utf-8"
    )


def test_rerun_of_failed_import_corrects_indexed_latest_version(
    db, location, resource_type_v, contributors_role_v, import_file
):
    """A rerun leaves one version indexed as latest if a failed import made a new one."""
    service = current_rdm_records.records_service
    mex_id = person_data["identifier"]
    changed_data = {**person_data, "email": ["changed@example.org"]}
    state_file = os.path.join(current_app.config["S3_DOWNLOAD_FOLDER"], ".import_state")

    def indexed_latest_flags():
        alias = build_alias_name("mexrecords-records")
        current_search_client.indices.refresh(index=alias)
        hits = current_search_client.search(
            index=alias, body={"size": 100, "query": {"match_all": {}}}
        )["hits"]["hits"]
        return sorted(
            h["_source"]["versions"]["is_latest"]
            for h in hits
            if h["_source"]["custom_fields"]["mex:identifier"] == mex_id
        )

    import_file("person", person_data)
    assert indexed_latest_flags() == [True]

    # The import stops after creating the new version, before indexing anything
    with patch.object(
        type(service.indexer), "bulk_index", side_effect=RuntimeError("stopped")
    ):
        import_file("person-changed", changed_data)
    os.remove(state_file)
    assert indexed_latest_flags() == [True]

    messages = import_file("person-changed", changed_data)

    assert search_messages(messages, created_regex).group("verb") == "Skipped"
    assert indexed_latest_flags() == [False, True]
