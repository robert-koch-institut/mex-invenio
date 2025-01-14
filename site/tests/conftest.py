# conftest.py
# borrowed from https://github.com/nyudlts/ultraviolet/blob/main/tests/conftest.py
import pytest
from invenio_app.factory import create_ui

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
def cli_runner(base_app):
    """Create a CLI runner for testing a CLI command."""

    def cli_invoke(command, *args, input=None):
        return base_app.test_cli_runner().invoke(command, args, input=input)

    return cli_invoke
