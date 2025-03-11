## Testing in Invenio v12

### Pytest

For this project, we need to install a version of `pytest` that is less than 8.
This is because dependency resolution issues arise with `pytest` version 8 and above,
which are not compatible with the current setup. Specifically, the issue is
documented in the following GitHub
issue: [pytest-dev/pytest#12144](https://github.com/pytest-dev/pytest/issues/12144).

To run unit tests in Invenio 13 pytest presumably does not have to be pinned to < 8.

### Pytest-Invenio

We need to install `pytest-invenio` version 2.1.1. This specific version is required
because `pytest-invenio` version 3 (the [current version](https://github.com/inveniosoftware/pytest-invenio))
introduces a breaking change where the `flask_sqlalchemy.session` module is not found,
causing the tests to fail.

To run unit tests in Invenio 13 `pytest-invenio` presumably does not have to be pinned
to 2.1.1.

### Overview

In Pytest, fixtures are a powerful feature that allows you to set up and tear down
resources needed for your tests. Fixtures are defined in a special file named
`conftest.py` and can be used across multiple test files without needing to import
them explicitly.

The default method is for a SQLLite database to be created for each test run. This
requires changes to the app config in `conftest.py`.

```python
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

    return app_config
```

#### Using Fixtures in Test Methods

Fixtures are imported into test methods by specifying their names as arguments.
Pytest automatically looks for fixtures with matching names in `conftest.py` and
injects them into the test functions.

```python
# conftest.py
import pytest


@pytest.fixture
def sample_fixture():
    # Setup code
    data = {"key": "value"}
    yield data
    # Teardown code
    data.clear()
```

Here is an example of how to use the `sample_fixture` in a test method:

```python
# test_example.py
def test_using_fixture(sample_fixture):
    assert sample_fixture["key"] == "value"
```

In this example, the sample_fixture is passed as an argument to the `test_using_fixture`
function. Pytest will automatically call the `sample_fixture` fixture, execute its setup
code, and pass the returned value to the test function.

#### Invenio fixtures

Invenio RDM Records provides a set of fixtures that can be used to test the application.
They can be found in [invenio_rdm_recods.tests.conftest](https://github.com/inveniosoftware/invenio-rdm-records/blob/master/tests/conftest.py)

To see tests we've done for Mex, please refer to the [tests](https://github.com/robert-koch-institut/mex-invenio/tree/main/tests) directory.

## Running unit tests
Tests are stored in `./tests`.

To install the testing environment, run the following command:

```bash
pipenv install -d
```

To run the tests, execute the following command:

```bash
pipenv run pytest
```

with the option -W ignore to suppress warnings:

```bash
pipenv run pytest -W ignore
```

with the option -s to show stdout from the app:

```bash
pipenv run pytest -W ignore -s
```
