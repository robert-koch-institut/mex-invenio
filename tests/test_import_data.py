from invenio_access.permissions import system_identity
from invenio_accounts.models import User
from invenio_rdm_records.proxies import current_rdm_records
from mex_invenio.scripts.import_data import _import_data

from tests.conftest import search_messages, created_regex
from tests.data import contact_point_data


def test_nonexistent_file_error_cli(cli_runner, db):
    """Test that the CLI command exits with an error when the file does not exist."""
    email = "alice@address.com"
    filepath = "path/to/file"
    db.session.add(User(username="alice", email=email))
    db.session.commit()

    result = cli_runner(_import_data, email, filepath)

    assert result.exit_code == 1
    assert f"File {filepath} not found." in result.output
    assert User.query.count() == 1


def test_nonexistent_user_error_cli(cli_runner, db, create_file):
    """Test that the CLI command exits with an error when the user does not exist."""
    email = "non-existent-user@address.com"
    result = cli_runner(_import_data, email, create_file("empty.json", "{}"))

    assert result.exit_code == 1
    assert f"User with email {email} not found." in result.output


def test_import_corrupt_data_cli(cli_runner, db, create_file):
    """Test that the CLI command logs an error when the data is corrupt."""
    email = "importer@address.com"
    db.session.add(User(username="importer", email=email))
    db.session.commit()

    result = cli_runner(_import_data, email, create_file("corrupt.json", "{"))

    assert result.exit_code == 0
    # assert isinstance(result.exception, JSONDecodeError)


def test_import_contact_point(
    db, location, resource_type_v, contributors_role_v, import_file
):
    """Test that the CLI command imports the contact point data correctly."""
    service = current_rdm_records.records_service

    messages = import_file("contact-point", contact_point_data)

    # Log output is captured in the import_file fixture defined in
    # conftest and returned by the fixture as a list of messages.
    match = search_messages(messages, created_regex)

    number_of_records_published = int(match.group("count"))
    published_record_id = match.group("record_id")

    assert match is not None
    assert len(match.groups()) == 3

    # Debugging: Check what indexer we're using
    print(f"=== INDEXER DEBUG ===")
    print(f"Service indexer type: {type(service.indexer)}")
    print(f"Service indexer: {service.indexer}")
    print(f"Expected record ID: {published_record_id}")
    print("====================")
    
    # Ensure search index is refreshed before searching
    print("Refreshing service indexer...")
    service.indexer.refresh()
    
    # Let's also try to search the MEX index directly
    from opensearchpy import OpenSearch
    client = OpenSearch([{'host': 'localhost', 'port': 9200}])
    
    print(f"=== DIRECT INDEX CHECK ===")
    try:
        # Check what indexes exist
        indices = client.indices.get_alias()
        mex_indices = {k: v for k, v in indices.items() if 'mexrecords' in k}
        print(f"MEX indices found: {list(mex_indices.keys())}")
        
        # Search the MEX index directly
        if mex_indices:
            index_name = list(mex_indices.keys())[0]
            direct_search = client.search(index=index_name, body={"query": {"match_all": {}}})
            print(f"Direct search in {index_name}: {direct_search['hits']['total']}")
            if direct_search['hits']['hits']:
                print(f"Direct search found records: {[hit['_id'] for hit in direct_search['hits']['hits']]}")
        
    except Exception as e:
        print(f"Direct search error: {e}")
    print("=========================")
    
    search_obj = service.search(system_identity)
    print(f"=== SERVICE SEARCH ===")
    print(f"Search object type: {type(search_obj)}")
    print(f"Search total: {search_obj.total}")
    #print(f"Search results: {search_obj.to_dict()}")
    print("=====================")
    
    # Check if we have any results before trying to access them
    assert search_obj.total == number_of_records_published, f"Expected {number_of_records_published} records, but found {search_obj.total}"
    assert search_obj.total > 0, "No records found in search results"
    
    record = list(search_obj.hits)[0]
    assert record["id"] == published_record_id
