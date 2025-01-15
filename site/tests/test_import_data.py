from invenio_accounts.models import User
from mex_invenio.scripts.import_data import import_data


def test_nonexistent_user_error_cli(cli_runner, db):
    email = 'non-existent-user@address.com'
    result = cli_runner(import_data, email, 'path/to/file')

    assert result.exit_code == 1
    assert f'User with email {email} not found.' in result.output


def test_nonexistent_file_error_cli(cli_runner, db):
    email = 'alice@address.com'
    filepath = 'path/to/file'
    db.session.add(User(username='alice', email=email))
    db.session.commit()

    result = cli_runner(import_data, email, filepath)

    assert result.exit_code == 1
    assert f'File {filepath} not found.' in result.output
    assert User.query.count() == 1


def test_import_corrupt_data_cli(cli_runner, db, corrupt_json_file):
    email = 'importer@address.com'
    db.session.add(User(username='importer', email=email))
    db.session.commit()

    result = cli_runner(import_data, email, corrupt_json_file)

    assert result.exit_code == 1
    assert 'Error decoding JSON from line: 1' in result.output


def test_import_contact_point(cli_runner, db, contact_point_file, location, resource_type_v,
                              contributors_role_v):
    email = 'importer@address.com'
    db.session.add(User(username='importer', email=email))
    db.session.commit()
    result = cli_runner(import_data, email, contact_point_file)

    assert result.exit_code == 0
    assert "Published record with id " in result.output
