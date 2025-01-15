# conftest.py
# borrowed from https://github.com/nyudlts/ultraviolet/blob/main/tests/conftest.py
import json
from datetime import datetime

import pytest
from flask_principal import Need
from invenio_access.permissions import system_identity
from invenio_app.factory import create_ui
from invenio_rdm_records.records.api import RDMDraft, RDMRecord
from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_vocabularies.records.api import Vocabulary


@pytest.fixture(scope='module')
def app_config(app_config):
    # sqllite refused to create mock db without those parameters and they are missing
    app_config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": False,
        "pool_recycle": 3600,
    }
    # need this to make sure separate indexes are created for testing
    app_config["SEARCH_INDEX_PREFIX"] = "test"
    app_config["SERVER_NAME"] = "127.0.0.1"
    app_config['MAX_FILE_SIZE'] = 50
    return app_config


@pytest.fixture(scope='module')
def create_app():
    return create_ui


@pytest.fixture(scope="module")
def resource_type_type(app):
    """Resource type vocabulary type."""
    return vocabulary_service.create_type(system_identity, "resourcetypes", "rsrct")


@pytest.fixture(scope="module")
def resource_type_v(app, resource_type_type):
    """Resource type vocabulary record."""
    vocab = vocabulary_service.create(
        system_identity,
        {
            "id": "contactpoint",
            "icon": "code",
            "props": {
                "type": "contactpoint"
            },
            "title": {"en": "Contact point"},
            "tags": ["depositable", "linkable"],
            "type": "resourcetypes",
        },
    )

    '''vocabulary_service.create(
        system_identity,
        {  # create base resource type
            "id": "image",
            "props": {
                "csl": "figure",
                "datacite_general": "Image",
                "datacite_type": "",
                "openaire_resourceType": "25",
                "openaire_type": "dataset",
                "eurepo": "info:eu-repo/semantics/other",
                "schema.org": "https://schema.org/ImageObject",
                "subtype": "",
                "type": "image",
                "marc21_type": "image",
                "marc21_subtype": "",
            },
            "icon": "chart bar outline",
            "title": {"en": "Image"},
            "tags": ["depositable", "linkable"],
            "type": "resourcetypes",
        },
    )

    vocabulary_service.create(
        system_identity,
        {  # create base resource type
            "id": "software",
            "props": {
                "csl": "figure",
                "datacite_general": "Software",
                "datacite_type": "",
                "openaire_resourceType": "0029",
                "openaire_type": "software",
                "eurepo": "info:eu-repo/semantics/other",
                "schema.org": "https://schema.org/SoftwareSourceCode",
                "subtype": "",
                "type": "image",
                "marc21_type": "software",
                "marc21_subtype": "",
            },
            "icon": "code",
            "title": {"en": "Software"},
            "tags": ["depositable", "linkable"],
            "type": "resourcetypes",
        },
    )

    vocab = vocabulary_service.create(
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
    )'''

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

    '''vocabulary_service.create(
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
    )'''

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def cli_runner(base_app):
    """Create a CLI runner for testing a CLI command."""

    def cli_invoke(command, *args, input=None):
        return base_app.test_cli_runner().invoke(command, args, input=input)

    return cli_invoke


@pytest.fixture
def contact_point_file(tmp_path):
    file_path = tmp_path / "contact-point.json"
    file_path.write_text(json.dumps({"email": ["reginagarrett@example.com"], "entityType": "MergedContactPoint",
                                     "identifier": "zJBx8K7g9mQ8X03VZHnxW"}))
    return str(file_path)


@pytest.fixture
def corrupt_json_file(tmp_path):
    file_path = tmp_path / "corrupt.json"
    file_path.write_text("{")
    return str(file_path)
