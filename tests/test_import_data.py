import re

from invenio_access.permissions import system_identity
from invenio_accounts.models import User
from invenio_rdm_records.proxies import current_rdm_records
from mex_invenio.scripts.import_data import import_data


def test_nonexistent_file_error_cli(cli_runner, db):
    email = 'alice@address.com'
    filepath = 'path/to/file'
    db.session.add(User(username='alice', email=email))
    db.session.commit()

    result = cli_runner(import_data, email, filepath)

    assert result.exit_code == 1
    assert f'File {filepath} not found.' in result.output
    assert User.query.count() == 1


def test_nonexistent_user_error_cli(cli_runner, db, empty_json_file):
    email = 'non-existent-user@address.com'
    result = cli_runner(import_data, email, empty_json_file)

    assert result.exit_code == 1
    assert f'User with email {email} not found.' in result.output


def test_import_corrupt_data_cli(cli_runner, db, corrupt_json_file, caplog):
    email = 'importer@address.com'
    db.session.add(User(username='importer', email=email))
    db.session.commit()

    result = cli_runner(import_data, email, corrupt_json_file)

    assert result.exit_code == 0
    assert 'ERROR    mex_invenio.scripts.import_data:import_data.py:134 Error decoding JSON: {' in caplog.text


def test_import_contact_point(db, location, resource_type_v, contributors_role_v, import_file):
    service = current_rdm_records.records_service

    # Log output is captured in the import_file fixture defined in conftest and returned
    # as a list of messages. The second last log statement will be about the published record.
    match = re.search(r'Published (\d) records. Ids: {\'(\w{5}-\w{5})\'}', import_file[-2])

    assert match is not None
    assert len(match.groups()) == 2

    service.indexer.refresh()
    search_obj = service.search(system_identity)

    assert search_obj.total == int(match.group(1))
    assert list(search_obj.hits)[0]['id'] == match.group(2)

