import json
import os
from unittest.mock import patch

import pytest

from mex_invenio.scripts.diff_manager import compute_diff, generate_diff

_MODULE = "mex_invenio.scripts.diff_manager"


@pytest.fixture
def app_ctx(base_app):
    """Push the Flask app context without any additional mocking."""
    with base_app.app_context():
        yield base_app


# ---------------------------------------------------------------------------
# compute_diff  (pure filesystem — no Flask needed)
# ---------------------------------------------------------------------------


def test_compute_diff_all_new(tmp_path):
    """All records are written to diff when no processed file exists."""
    downloaded = tmp_path / "new.ndjson"
    diff_out = tmp_path / "diff.ndjson"
    downloaded.write_text(
        '{"identifier": "a", "val": 1}\n{"identifier": "b", "val": 2}\n'
    )

    result = compute_diff(
        str(downloaded), str(tmp_path / "missing.ndjson"), str(diff_out)
    )

    assert result == {"new_or_changed_count": 2, "processed_count": 2}
    lines = [ln for ln in diff_out.read_text().strip().split("\n") if ln]
    assert len(lines) == 2


def test_compute_diff_no_changes(tmp_path):
    """Diff is empty when all records are identical."""
    data = '{"identifier": "x", "val": 1}\n'
    processed = tmp_path / "old.ndjson"
    downloaded = tmp_path / "new.ndjson"
    diff_out = tmp_path / "diff.ndjson"
    processed.write_text(data)
    downloaded.write_text(data)

    result = compute_diff(str(downloaded), str(processed), str(diff_out))

    assert result["new_or_changed_count"] == 0
    assert result["processed_count"] == 1
    assert diff_out.read_text().strip() == ""


def test_compute_diff_changed_record(tmp_path):
    """Changed record appears in the diff output with its new value."""
    processed = tmp_path / "old.ndjson"
    downloaded = tmp_path / "new.ndjson"
    diff_out = tmp_path / "diff.ndjson"
    processed.write_text('{"identifier": "a", "val": 1}\n')
    downloaded.write_text('{"identifier": "a", "val": 2}\n')

    result = compute_diff(str(downloaded), str(processed), str(diff_out))

    assert result["new_or_changed_count"] == 1
    assert json.loads(diff_out.read_text().strip())["val"] == 2


def test_compute_diff_skips_records_without_identifier(tmp_path):
    """Records missing an identifier field are not counted or written."""
    processed = tmp_path / "old.ndjson"
    downloaded = tmp_path / "new.ndjson"
    diff_out = tmp_path / "diff.ndjson"
    processed.write_text("")
    downloaded.write_text('{"no_id": "x"}\n')

    result = compute_diff(str(downloaded), str(processed), str(diff_out))

    assert result["processed_count"] == 0
    assert result["new_or_changed_count"] == 0


def test_compute_diff_skips_invalid_json(tmp_path):
    """Invalid JSON lines in the downloaded file are silently skipped."""
    processed = tmp_path / "old.ndjson"
    downloaded = tmp_path / "new.ndjson"
    diff_out = tmp_path / "diff.ndjson"
    processed.write_text("")
    downloaded.write_text('{"identifier": "a", "val": 1}\nnot-json\n')

    result = compute_diff(str(downloaded), str(processed), str(diff_out))

    assert result["new_or_changed_count"] == 1
    assert result["processed_count"] == 1


def test_compute_diff_returns_none_on_exception(tmp_path):
    """compute_diff returns None when the downloaded file does not exist."""
    result = compute_diff(
        str(tmp_path / "nonexistent.ndjson"),
        str(tmp_path / "old.ndjson"),
        str(tmp_path / "diff.ndjson"),
    )
    assert result is None


# ---------------------------------------------------------------------------
# generate_diff  (needs app context via app_ctx)
# ---------------------------------------------------------------------------


@patch(f"{_MODULE}.get_subdir_by_order", return_value=None)
def test_generate_diff_no_downloaded(mock_subdir, app_ctx):
    """generate_diff returns None when no downloaded dump exists."""
    assert generate_diff("4.10") is None


def test_generate_diff_no_processed(app_ctx):
    """generate_diff returns None when no processed dump exists."""

    def subdir(root, most_recent=True):  # noqa: FBT002
        return None if most_recent else "/some/download/path"

    with patch(f"{_MODULE}.get_subdir_by_order", side_effect=subdir):
        assert generate_diff("4.10") is None


@patch(f"{_MODULE}.get_timestamp", new=lambda: "20240201000001")
@patch(f"{_MODULE}.compute_diff", return_value=None)
@patch(f"{_MODULE}.get_subdir_by_order")
def test_generate_diff_compute_fails(mock_subdir, mock_compute, app_ctx, app_config):
    """generate_diff returns None when compute_diff returns None."""
    base = str(app_config["S3_DOWNLOAD_FOLDER"])
    mock_subdir.side_effect = [
        os.path.join(base, "downloaded", "4.10", "20240201000000"),
        os.path.join(base, "processed", "4.10", "20240101000000"),
    ]
    assert generate_diff("4.10") is None


@patch(f"{_MODULE}.get_timestamp", new=lambda: "20240301000001")
@patch(f"{_MODULE}.shutil.move")
@patch(
    f"{_MODULE}.compute_diff",
    return_value={"new_or_changed_count": 5, "processed_count": 10},
)
@patch(f"{_MODULE}.get_subdir_by_order")
def test_generate_diff_success(
    mock_subdir, mock_compute, mock_move, app_ctx, app_config
):
    """generate_diff returns the diff.ndjson path when compute_diff succeeds."""
    base = str(app_config["S3_DOWNLOAD_FOLDER"])
    dl_sub = os.path.join(base, "downloaded", "4.10", "20240301000000")
    pr_sub = os.path.join(base, "processed", "4.10", "20240201000000")
    os.makedirs(dl_sub, exist_ok=True)
    os.makedirs(pr_sub, exist_ok=True)
    mock_subdir.side_effect = [dl_sub, pr_sub]

    result = generate_diff("4.10")

    assert result is not None
    assert result.endswith("diff.ndjson")
    assert "20240301000001" in result
    mock_compute.assert_called_once()
    mock_move.assert_called_once()
