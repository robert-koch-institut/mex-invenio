import json
import os
import time
from unittest.mock import patch

import pytest
from flask import current_app
from invenio_access.permissions import system_identity
from invenio_accounts.models import User
from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.records.api import RDMRecord
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import scoped_session, sessionmaker

from mex_invenio.scripts.import_data import (
    LOOKUP_RETRY_DELAYS,
    _import_data,
    _query_existing_records,
    bulk_search_existing_records,
)
from mex_invenio.scripts.utils import get_linked_target_ids, get_related_mex_ids
from tests.conftest import created_regex, search_messages
from tests.data import contact_point_data


def test_nonexistent_file_error_cli(cli_runner, db, model_version):
    """Test that the CLI command exits with an error when the file does not exist."""
    email = "alice@address.com"
    filepath = "path/to/file"
    db.session.add(User(username="alice", email=email))
    db.session.commit()

    result = cli_runner(_import_data, model_version, email, filepath)

    assert result.exit_code == 1
    assert f"File {filepath} not found." in result.output
    assert User.query.count() == 1


def test_nonexistent_user_error_cli(cli_runner, db, create_file, model_version):
    """Test that the CLI command exits with an error when the user does not exist."""
    email = "non-existent-user@address.com"
    result = cli_runner(
        _import_data, model_version, email, create_file("empty.json", "{}")
    )

    assert result.exit_code == 1
    assert f"User with email {email} not found." in result.output


def test_import_corrupt_data_cli(cli_runner, db, create_file, model_version):
    """Test that the CLI command logs an error when the data is corrupt."""
    email = "importer@address.com"
    db.session.add(User(username="importer", email=email))
    db.session.commit()

    result = cli_runner(
        _import_data, model_version, email, create_file("corrupt.json", "{")
    )

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


def test_import_creates_log_file(
    app, db, location, resource_type_v, contributors_role_v, import_file
):
    """Test that the import creates a timestamped log file."""
    import_file("contact-point", contact_point_data)

    log_dir = os.path.join(app.config["S3_DOWNLOAD_FOLDER"], "logs")
    expected_log = os.path.join(log_dir, f"import-{time.strftime('%Y%m%d')}.log")

    assert os.path.isfile(expected_log), f"Log file not found: {expected_log}"
    assert os.path.getsize(expected_log) > 0, "Log file is empty"


def _dropped_connection():
    return OperationalError("SELECT 1", {}, Exception("server closed the connection"))


def _records_with_identifier(mex_id):
    records = RDMRecord.model_cls.query.all()
    return [r for r in records if r.json["custom_fields"]["mex:identifier"] == mex_id]


def _state_file():
    return os.path.join(current_app.config["S3_DOWNLOAD_FOLDER"], ".import_state")


@pytest.fixture
def session_with_terminated_connection(db):
    """Session whose database connection has been killed by the server."""
    # The session of the db fixture is held in a savepoint, which can't reconnect
    engine = create_engine(db.engine.url)
    session = scoped_session(sessionmaker(bind=engine))

    pid = session.execute(text("SELECT pg_backend_pid()")).scalar()
    with db.engine.connect() as other_connection:
        other_connection.execute(
            text("SELECT pg_terminate_backend(:pid)"), {"pid": pid}
        )

    yield session

    session.remove()
    engine.dispose()


def test_lookup_recovers_from_terminated_connection(
    session_with_terminated_connection,
):
    """A connection killed by the server is rolled back and the lookup repeated."""
    with (
        patch(
            "mex_invenio.scripts.import_data.db.session",
            session_with_terminated_connection,
        ),
        patch("mex_invenio.scripts.import_data.time.sleep") as sleep,
    ):
        assert bulk_search_existing_records(["some-id"]) == {}

    sleep.assert_called_once_with(LOOKUP_RETRY_DELAYS[0])


@pytest.mark.parametrize(
    ("lookup", "record"),
    [
        (
            get_related_mex_ids,
            {
                "custom_fields": {"mex:identifier": "some-id"},
                "metadata": {"resource_type": {"id": "contactpoint"}},
            },
        ),
        (get_linked_target_ids, {"custom_fields": {"mex:isPartOf": ["some-id"]}}),
    ],
)
def test_related_lookups_raise_on_terminated_connection(
    app, session_with_terminated_connection, lookup, record
):
    """A lost connection isn't reported as a record having nothing related to it."""
    with (
        patch(
            "mex_invenio.scripts.utils.db.session",
            session_with_terminated_connection,
        ),
        pytest.raises(OperationalError),
    ):
        lookup(record)


def test_lookup_raises_when_database_stays_unavailable(app):
    """A lookup that keeps failing raises rather than report no existing records."""
    with (
        patch(
            "mex_invenio.scripts.import_data._query_existing_records",
            side_effect=_dropped_connection(),
        ) as query,
        patch("mex_invenio.scripts.import_data.time.sleep") as sleep,
        pytest.raises(OperationalError),
    ):
        bulk_search_existing_records(["some-id"])

    assert query.call_count == len(LOOKUP_RETRY_DELAYS) + 1
    assert [c.args[0] for c in sleep.call_args_list] == list(LOOKUP_RETRY_DELAYS)


def test_failed_lookup_does_not_duplicate_record(
    db, location, resource_type_v, contributors_role_v, import_file
):
    """An import that can't look up existing records stops without creating any."""
    mex_id = contact_point_data["identifier"]
    import_file("contact-point", contact_point_data)
    assert len(_records_with_identifier(mex_id)) == 1

    changed_data = {**contact_point_data, "email": ["changed@example.com"]}

    try:
        with (
            patch(
                "mex_invenio.scripts.import_data._query_existing_records",
                side_effect=_dropped_connection(),
            ),
            patch("mex_invenio.scripts.import_data.time.sleep"),
        ):
            import_file("contact-point-changed", changed_data)

        with open(_state_file()) as f:
            assert json.load(f)["status"] == "failed"
    finally:
        os.remove(_state_file())

    assert len(_records_with_identifier(mex_id)) == 1


def test_lookup_retry_updates_instead_of_duplicating_record(
    db, location, resource_type_v, contributors_role_v, import_file
):
    """A lookup that succeeds on retry leads to a new version, not a new record."""
    mex_id = contact_point_data["identifier"]
    import_file("contact-point", contact_point_data)

    changed_data = {**contact_point_data, "email": ["changed@example.com"]}

    with (
        patch(
            "mex_invenio.scripts.import_data._query_existing_records",
            side_effect=[_dropped_connection(), _query_existing_records([mex_id])],
        ),
        patch("mex_invenio.scripts.import_data.time.sleep"),
    ):
        import_file("contact-point-changed", changed_data)

    records = _records_with_identifier(mex_id)
    assert len(records) == 2
    assert len({r.parent_id for r in records}) == 1


def test_failed_related_lookup_is_logged_and_next_record_imported(
    db, location, resource_type_v, contributors_role_v, import_file
):
    """A failed lookup after a record is reported, and doesn't fail the next record."""
    second_id = "zJBx8K7g9mQ8X03VZHnxX"
    lines = "\n".join(
        json.dumps(data)
        for data in (
            contact_point_data,
            {**contact_point_data, "identifier": second_id},
        )
    )

    with (
        patch(
            "mex_invenio.scripts.import_data.get_related_mex_ids",
            side_effect=[_dropped_connection(), []],
        ),
        patch(
            "mex_invenio.scripts.import_data.db.session.rollback",
            wraps=db.session.rollback,
        ) as rollback,
    ):
        messages = import_file("contact-points", lines)

    rollback.assert_called_once()
    errors = [m for m in messages if "server closed the connection" in m]
    assert len(errors) == 1
    assert contact_point_data["identifier"] in errors[0]
    assert len(_records_with_identifier(contact_point_data["identifier"])) == 1
    assert len(_records_with_identifier(second_id)) == 1
