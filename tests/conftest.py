# conftest.py
# see https://github.com/nyudlts/ultraviolet/blob/main/tests/conftest.py

import json
import logging
import os
import re
from unittest.mock import patch, MagicMock

import pytest
from dotenv import find_dotenv, load_dotenv
from invenio_access.permissions import system_identity
from invenio_accounts.models import User
from invenio_app.factory import create_ui
from invenio_rdm_records.cli import (
    create_records_custom_field,
    custom_field_exists_in_records,
)
from invenio_rdm_records.proxies import current_rdm_records
from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_vocabularies.records.api import Vocabulary

from mex_invenio.scripts.import_data import _import_data
from mex_invenio.config import (
    OAISERVER_ID_PREFIX,
    OAISERVER_RELATIONS,
    RECORD_METADATA_CREATOR,
    RECORD_METADATA_DEFAULT_TITLE,
    RECORD_METADATA_TITLE_PROPERTIES,
)
from mex_invenio.fields.custom_fields import (
    RDM_CUSTOM_FIELDS,
    RDM_CUSTOM_FIELDS_UI,
    RDM_NAMESPACES,
)


created_regex = (
    r"(?P<verb>\w+) (?P<count>\d) records. Ids: \[\'(?P<record_id>\w{5}-\w{5})\'\]"
)


def search_messages(messages, pattern):
    """Search for a pattern in the log messages. Returns the first/most recent match."""
    for message in reversed(messages):
        if re.search(pattern, message):
            return re.search(pattern, message)

    return None


@pytest.fixture(scope="session", autouse=True)
def load_env():
    env_file = find_dotenv(".env.tests")
    load_dotenv(env_file)


@pytest.fixture(scope="module")
def module_tmp_path(tmp_path_factory):
    return tmp_path_factory.mktemp("module_temp")


@pytest.fixture(scope="module")
def app_config(app_config, module_tmp_path):
    # sqllite refused to create mock db without those parameters and they are missing
    # app_config["SQLALCHEMY_ENGINE_OPTIONS"] = {}

    # need this to make sure separate indexes are created for testing
    app_config["SEARCH_INDEX_PREFIX"] = "test"
    app_config["SERVER_NAME"] = "127.0.0.1"

    # add custom fields
    app_config["RDM_NAMESPACES"] = RDM_NAMESPACES
    app_config["RDM_CUSTOM_FIELDS"] = RDM_CUSTOM_FIELDS
    app_config["RDM_CUSTOM_FIELDS_UI"] = RDM_CUSTOM_FIELDS_UI

    # add import settings
    app_config["RECORD_METADATA_DEFAULT_TITLE"] = RECORD_METADATA_DEFAULT_TITLE
    app_config["RECORD_METADATA_TITLE_PROPERTIES"] = RECORD_METADATA_TITLE_PROPERTIES
    app_config["RECORD_METADATA_CREATOR"] = RECORD_METADATA_CREATOR

    # add oai
    app_config["OAISERVER_ID_PREFIX"] = OAISERVER_ID_PREFIX
    app_config["OAISERVER_RELATIONS"] = OAISERVER_RELATIONS

    # add S3
    app_config["S3_DOWNLOAD_FOLDER"] = module_tmp_path
    return app_config


@pytest.fixture(scope="module")
def create_app():
    return create_ui


@pytest.fixture(scope="module")
def resource_type_type(app):
    """Resource type vocabulary type."""
    return vocabulary_service.create_type(system_identity, "resourcetypes", "rsrct")


@pytest.fixture(scope="module")
def resource_type_v(app, resource_type_type):
    """Resource type vocabulary record."""
    Vocabulary.index.create(ignore=400)
    vocab = vocabulary_service.create(
        system_identity,
        {
            "id": "contactpoint",
            "icon": "code",
            "props": {"type": "contactpoint"},
            "title": {"en": "Contact point"},
            "tags": ["depositable", "linkable"],
            "type": "resourcetypes",
        },
    )

    vocabulary_service.create(
        system_identity,
        {
            "id": "organizationalunit",
            "icon": "code",
            "props": {"type": "organizationalunit"},
            "title": {"en": "Organizational unit"},
            "tags": ["depositable", "linkable"],
            "type": "resourcetypes",
        },
    )

    vocabulary_service.create(
        system_identity,
        {
            "id": "resource",
            "icon": "code",
            "props": {"type": "resource"},
            "title": {"en": "Resource"},
            "tags": ["depositable", "linkable"],
            "type": "resourcetypes",
        },
    )

    vocabulary_service.create(
        system_identity,
        {
            "id": "person",
            "icon": "code",
            "props": {"type": "person"},
            "title": {"en": "Person"},
            "tags": ["depositable", "linkable"],
            "type": "resourcetypes",
        },
    )

    """vocab = vocabulary_service.create(
        system_identity,
        {
            "id": "image-photo",
            "props": {
                "csl": "graphic",
                "datacite_general": "Image",
                "datacite_type": "Photo",
                "openaire_resourceType": "25",
                "openaire_type": "dataset",
                "eurepo": "info:eu-repo/semantics/other",
                "schema.org": "https://schema.org/Photograph",
                "subtype": "image-photo",
                "type": "image",
                "marc21_type": "image",
                "marc21_subtype": "photo",
            },
            "icon": "chart bar outline",
            "title": {"en": "Photo"},
            "tags": ["depositable", "linkable"],
            "type": "resourcetypes",
        },
    )"""

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def contributors_role_type(app):
    """Contributor role vocabulary type."""
    return vocabulary_service.create_type(system_identity, "contributorsroles", "cor")


@pytest.fixture(scope="module")
def contributors_role_v(app, contributors_role_type):
    """Contributor role vocabulary record."""
    vocab = vocabulary_service.create(
        system_identity,
        {
            "id": "datamanager",
            "props": {"datacite": "DataManager"},
            "title": {"en": "Data manager"},
            "type": "contributorsroles",
        },
    )

    """vocabulary_service.create(
        system_identity,
        {
            "id": "projectmanager",
            "props": {"datacite": "ProjectManager"},
            "title": {"en": "Project manager"},
            "type": "contributorsroles",
        },
    )

    vocab = vocabulary_service.create(
        system_identity,
        {
            "id": "other",
            "props": {"datacite": "Other", "marc": "oth"},
            "title": {"en": "Other"},
            "type": "contributorsroles",
        },
    )"""

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def cli_runner(base_app):
    """Create a CLI runner for testing a CLI command."""

    def cli_invoke(command, *args, input=None):
        return base_app.test_cli_runner().invoke(command, args, input=input)

    return cli_invoke


@pytest.fixture(scope="module")
def custom_field_exists(cli_runner):
    """Factory fixture, tests whether a given custom field exists."""

    def _custom_field_exists(cf_name):
        return cli_runner(custom_field_exists_in_records, "-f", cf_name)

    return _custom_field_exists


@pytest.fixture(scope="function")
def initialise_custom_fields(app, location, db, search_clear, cli_runner):
    """Fixture initialises custom fields."""
    return cli_runner(create_records_custom_field)


@pytest.fixture
def create_file(tmp_path):
    """Create a file, either absolute or relative to the tmp_path."""

    def _create_file(filename, data, absolute=False):
        if isinstance(data, dict):
            data = json.dumps(data)

        if absolute:
            with open(filename, "w") as f:
                f.write(data)
            file_path = filename
        else:
            file_path = tmp_path / filename
            file_path.write_text(data)

        return str(file_path)

    return _create_file


@pytest.fixture
def create_user(db):
    def _create_user(username, email):
        user = User(username=username, email=email)
        db.session.add(user)
        db.session.commit()
        return user

    return _create_user


@pytest.fixture
def import_file(
    initialise_custom_fields,
    custom_field_exists,
    db,
    caplog,
    cli_runner,
    create_user,
    create_file,
):
    email = "importer@address.com"
    create_user("importer", email)

    def _import_file(filename, data):
        contact_point_file = create_file(f"{filename}.json", data)

        with caplog.at_level(logging.INFO):
            cli_runner(_import_data, email, contact_point_file)

        current_rdm_records.records_service.indexer.refresh()

        return caplog.messages

    return _import_file


@pytest.fixture
def mock_s3_client():
    with patch("boto3.client") as mock:
        s3_client = MagicMock()
        mock.return_value = s3_client
        yield s3_client
