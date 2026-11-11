import json
from unittest.mock import patch

from mex_invenio.scripts.utils import (
    _duration_seconds,
    _error_details,
    _read_state,
    _update_state,
    _write_state,
    get_installed_model_version,
    get_title,
    normalize_record_data,
)


def test_get_title_with_valid_data(app):
    app.config["RECORD_METADATA_TITLE_PROPERTIES"] = ["someTitle"]
    app.config["RECORD_METADATA_DEFAULT_TITLE"] = "Default Title"

    mex_data = {"someTitle": ["Actual Title"]}
    assert get_title(app.config, mex_data) == "Actual Title"


def test_get_title_falls_back_to_default(app):
    app.config["RECORD_METADATA_TITLE_PROPERTIES"] = ["unavailableKey"]
    app.config["RECORD_METADATA_DEFAULT_TITLE"] = "Default Title"

    mex_data = {}
    assert get_title(app.config, mex_data) == "Default Title"


def test_ignore_two_char_title(app):
    app.config["RECORD_METADATA_TITLE_PROPERTIES"] = ["title", "name"]
    app.config["RECORD_METADATA_DEFAULT_TITLE"] = "Default Title"

    mex_data = {"name": [{"language": "en", "value": "ab"}], "title": "bab"}
    assert get_title(app.config, mex_data) == "bab"


def test_normalize_record_data_string():
    assert normalize_record_data("  hello world  ") == "hello world"
    assert normalize_record_data("hello&nbsp;world") == "hello\xa0world"
    assert normalize_record_data("hello&amp;world") == "hello&world"
    assert normalize_record_data("test\u200bstring") == "teststring"
    assert normalize_record_data("") == ""


def test_normalize_record_data_numbers():
    assert normalize_record_data(123) == "123"
    assert normalize_record_data(123.45) == "123.45"
    assert normalize_record_data(0) == "0"


def test_normalize_record_data_list_order_preservation():
    input_list = ["third", "first", "second"]
    result = normalize_record_data(input_list)
    assert result == ["third", "first", "second"]
    assert result[0] == "third"
    assert result[1] == "first"
    assert result[2] == "second"


def test_normalize_record_data_nested_list_order_preservation():
    input_list = [
        {"name": "charlie", "value": 3},
        {"name": "alice", "value": 1},
        {"name": "bob", "value": 2},
    ]
    result = normalize_record_data(input_list)
    expected = [
        {"name": "charlie", "value": "3"},
        {"name": "alice", "value": "1"},
        {"name": "bob", "value": "2"},
    ]
    assert result == expected
    assert result[0]["name"] == "charlie"
    assert result[1]["name"] == "alice"
    assert result[2]["name"] == "bob"


def test_normalize_record_data_list_with_none_and_empty():
    input_list = ["first", None, "second", [], "third"]
    result = normalize_record_data(input_list)
    assert result == ["first", "second", "third"]


def test_normalize_record_data_dict():
    input_dict = {
        "name": "  John Doe  ",
        "age": 30,
        "items": ["item1", "item2"],
        "empty_list": [],
        "null_value": None,
    }
    expected = {"name": "John Doe", "age": "30", "items": ["item1", "item2"]}
    result = normalize_record_data(input_dict)
    assert result == expected


def test_normalize_record_data_complex_nested_structure():
    input_data = {
        "authors": [
            {"name": "  Author 1  ", "id": 123},
            {"name": "Author 2", "id": 456},
        ],
        "tags": ["python", "testing", "normalization"],
        "metadata": {"title": "&quot;Complex Test&quot;", "year": 2024},
    }
    expected = {
        "authors": [
            {"name": "Author 1", "id": "123"},
            {"name": "Author 2", "id": "456"},
        ],
        "tags": ["python", "testing", "normalization"],
        "metadata": {"title": '"Complex Test"', "year": "2024"},
    }
    result = normalize_record_data(input_data)
    assert result == expected
    assert result["authors"][0]["name"] == "Author 1"
    assert result["authors"][1]["name"] == "Author 2"


def test_normalize_record_data_html_entities():
    assert normalize_record_data("&lt;script&gt;") == "<script>"
    assert normalize_record_data("M&uuml;ller") == "Müller"
    assert normalize_record_data("caf&eacute;") == "café"


def test_get_installed_model_version_truncates_to_major_minor():
    """Returns '<major>.<minor>', dropping any patch component."""
    with patch(
        "mex_invenio.scripts.utils.importlib.metadata.version", return_value="4.10.3"
    ):
        assert get_installed_model_version() == "4.10"


def test_write_state_records_details(tmp_path):
    """The state file holds the format version, status, timestamps and details."""
    state_file = tmp_path / ".import_state"
    counts = {"lines": 3, "created": 2, "failed": 1}

    _write_state(
        str(state_file),
        "success",
        started_at="2026-10-07T10:00:00+00:00",
        finished_at="2026-10-07T10:00:05+00:00",
        kind="diff",
        counts=counts,
    )

    assert json.loads(state_file.read_text()) == {
        "status": "success",
        "started_at": "2026-10-07T10:00:00+00:00",
        "finished_at": "2026-10-07T10:00:05+00:00",
        "kind": "diff",
        "counts": counts,
    }
    assert _read_state(str(state_file))["counts"] == counts
    # Written via a temporary file that's moved into place
    assert [p.name for p in tmp_path.iterdir()] == [".import_state"]


def test_write_state_replaces_previous_state(tmp_path):
    """Details from an earlier state don't linger in the next one."""
    state_file = str(tmp_path / ".import_state")
    _write_state(state_file, "failed", error={"type": "ValueError", "message": "x"})
    _write_state(state_file, "in_progress", started_at="2026-10-07T10:00:00+00:00")

    assert _read_state(state_file) == {
        "status": "in_progress",
        "started_at": "2026-10-07T10:00:00+00:00",
    }


def test_error_details():
    assert _error_details(ValueError("bad line")) == {
        "type": "ValueError",
        "message": "bad line",
    }


def test_duration_seconds():
    assert (
        _duration_seconds("2026-10-07T10:00:00+00:00", "2026-10-07T10:01:02.34+00:00")
        == 62.3
    )


def test_write_state_keeps_downloadable_files_section(tmp_path):
    """Writing the import status keeps the downloadable-files section."""
    state_file = str(tmp_path / ".import_state")
    section = {"status": "success", "counts": {"files": 2, "bytes": 10}}
    _update_state(state_file, "downloadable_files", section)

    _write_state(state_file, "in_progress", started_at="2026-10-07T10:00:00+00:00")

    assert _read_state(state_file) == {
        "status": "in_progress",
        "started_at": "2026-10-07T10:00:00+00:00",
        "downloadable_files": section,
    }


def test_update_state_keeps_import_status(tmp_path):
    """Updating a section leaves the import status and details alone."""
    state_file = str(tmp_path / ".import_state")
    _write_state(state_file, "failed", kind="diff")

    _update_state(state_file, "downloadable_files", {"status": "success"})

    assert _read_state(state_file) == {
        "status": "failed",
        "kind": "diff",
        "downloadable_files": {"status": "success"},
    }
