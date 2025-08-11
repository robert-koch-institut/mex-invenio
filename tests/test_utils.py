from mex_invenio.scripts.utils import compare_dicts, get_title


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


def test_identical_after_whitespace_normalization():
    """Test that dictionaries are identical after whitespace normalization."""
    current_data = {"a": "  hello  ", "b": 123, "nested": {"x": "world", "y": [1, 2]}}
    new_data = {"a": "hello", "b": "123", "nested": {"y": [1, 2], "x": "world"}}

    result = compare_dicts(current_data, new_data)
    assert result == {}


def test_identical_after_type_normalization():
    """Test that dictionaries are identical after type normalization."""
    current_data = {"field": "  value  ", "number": 42}
    new_data = {"field": "value", "number": "42"}

    result = compare_dicts(current_data, new_data)
    assert result == {}


def test_actual_differences_detected():
    """Test that actual differences are properly detected."""
    current_data = {"a": "hello", "b": "world"}
    new_data = {"a": "hello", "b": "different"}

    result = compare_dicts(current_data, new_data)
    assert result == {"b": {"current_data": "world", "new_data": "different"}}


def test_complex_nested_structure_identical():
    """Test complex nested structure that should be identical after normalization."""
    current_data = {
        "mex:identifier": "  ID123  ",
        "mex:title": [{"language": "de", "value": "Test Title"}],
        "mex:authors": [{"name": "John", "id": 1}, {"name": "Jane", "id": 2}],
    }
    new_data = {
        "mex:identifier": "ID123",
        "mex:title": [{"language": "de", "value": "Test Title"}],
        "mex:authors": [{"name": "John", "id": "1"}, {"name": "Jane", "id": "2"}],
    }

    result = compare_dicts(current_data, new_data)
    assert result == {}


def test_missing_keys_in_new_data():
    """Test detection of keys missing in new data."""
    current_data = {"a": "value", "b": "another"}
    new_data = {"a": "value"}

    result = compare_dicts(current_data, new_data)
    assert result == {"b": {"current_data": "another", "new_data": None}}


def test_missing_keys_in_current_data():
    """Test detection of keys missing in current data."""
    current_data = {"a": "value"}
    new_data = {"a": "value", "b": "new"}

    result = compare_dicts(current_data, new_data)
    assert result == {"b": {"current_data": None, "new_data": "new"}}
