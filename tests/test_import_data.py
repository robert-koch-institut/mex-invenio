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
    match = search_messages(messages, created_regex)

    number_of_records_published = int(match.group("count"))
    published_record_id = match.group("record_id")

    assert match is not None
    assert len(match.groups()) == 3

    # Ensure search index is refreshed before searching
    service.indexer.refresh()

    search_obj = service.search(system_identity)

    assert search_obj.total == number_of_records_published, (
        f"Expected {number_of_records_published} records, but found {search_obj.total}"
    )
    assert search_obj.total > 0, "No records found in search results"

    record = list(search_obj.hits)[0]
    assert record["id"] == published_record_id
    assert "reginagarrett@example.com" in record["custom_fields"]["mex:email"]
    assert "zJBx8K7g9mQ8X03VZHnxW" in record["custom_fields"]["mex:identifier"]
