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
    assert User.query.count()
