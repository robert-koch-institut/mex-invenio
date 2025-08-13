from mex_invenio.scripts.utils import get_title


def test_get_title_with_valid_data(app):
    app.config["RECORD_METADATA_TITLE_PROPERTIES"] = ["someTitle"]
    app.config["RECORD_METADATA_DEFAULT_TITLE"] = "Default Title"

    mex_data = {"someTitle": ["Actual Title"]}
    assert get_title(mex_data) == "Actual Title"


def test_get_title_falls_back_to_default(app):
    app.config["RECORD_METADATA_TITLE_PROPERTIES"] = ["unavailableKey"]
    app.config["RECORD_METADATA_DEFAULT_TITLE"] = "Default Title"

    mex_data = {}
    assert get_title(mex_data) == "Default Title"


def test_ignore_two_char_title(app):
    app.config["RECORD_METADATA_TITLE_PROPERTIES"] = ["title", "name"]
    app.config["RECORD_METADATA_DEFAULT_TITLE"] = "Default Title"

    mex_data = {"name": [{"language": "en", "value": "ab"}], "title": "bab"}
    assert get_title(mex_data) == "bab"