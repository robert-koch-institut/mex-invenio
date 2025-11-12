from invenio_access.permissions import system_identity
from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.records import RDMRecord

from tests.conftest import created_regex, search_messages
from tests.data import resource_data


def test_initial_import_resource(
    db, location, resource_type_v, contributors_role_v, import_file
):
    """Test that the CLI command imports the contact point data correctly."""
    service = current_rdm_records.records_service

    messages = import_file("resource", resource_data, initial=True)
    match = search_messages(messages, created_regex)

    number_of_records_published = int(match.group("count"))
    published_record_id = match.group("record_id")

    assert match is not None
    assert len(match.groups()) == 3

    # Ensure search index is refreshed before searching
    service.indexer.refresh()

    search_obj = service.search(system_identity)

    assert search_obj.total == 0

    db_result = db.session.query(RDMRecord.model_cls).all()

    assert len(db_result) == 1
    db_record = db_result[0]
    print(db_record.data)
    # assert search_obj.total > 0, "No records found in search results"

    # record = list(search_obj.hits)[0]
    # assert record["id"] == published_record_id
    # assert 'reginagarrett@example.com' in record["custom_fields"]["mex:email"]
    # assert 'zJBx8K7g9mQ8X03VZHnxW' in record["custom_fields"]["mex:identifier"]
