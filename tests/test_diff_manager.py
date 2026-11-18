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


# ---------------------------------------------------------------------------
# generate_diff — model-version scoping and upgrade-transition fallback
# ---------------------------------------------------------------------------


def test_generate_diff_oldest_download_scoped_to_model_version(app_ctx, app_config):
    """The pending-download lookup is scoped to this model version only."""
    seen_roots = []

    def subdir(root, most_recent=True):  # noqa: FBT002
        seen_roots.append((root, most_recent))

    with patch(f"{_MODULE}.get_subdir_by_order", side_effect=subdir):
        assert generate_diff("5.0") is None

    base = str(app_config["S3_DOWNLOAD_FOLDER"])
    # The pending-download lookup (always the first call) must be scoped to
    # this model version; unrelated to whether a fallback happens afterwards
    # for the processed-dump lookup.
    assert seen_roots[0] == (os.path.join(base, "downloaded", "5.0"), False)


@patch(f"{_MODULE}.get_timestamp", new=lambda: "20260201000001")
@patch(f"{_MODULE}.shutil.move")
@patch(
    f"{_MODULE}.compute_diff",
    return_value={"new_or_changed_count": 3, "processed_count": 3},
)
def test_generate_diff_falls_back_to_other_version_when_first_run(
    mock_compute, mock_move, app_ctx, app_config
):
    """A brand-new model version diffs against the most recent processed dump of any version when it has no processed history of its own (upgrade transition, e.g. 4.10 -> 5.0)."""
    base = str(app_config["S3_DOWNLOAD_FOLDER"])
    dl_sub = os.path.join(base, "downloaded", "5.0", "20260201000000")
    pr_sub_410 = os.path.join(base, "processed", "4.10", "20260101000000")
    os.makedirs(dl_sub, exist_ok=True)
    os.makedirs(pr_sub_410, exist_ok=True)

    def subdir(root, most_recent=True):  # noqa: FBT002
        if root == os.path.join(base, "downloaded", "5.0"):
            return dl_sub
        if root == os.path.join(base, "processed", "5.0"):
            return None  # no processed history yet for the new version
        if root == os.path.join(base, "processed"):
            return pr_sub_410  # global fallback finds the old version's dump
        return None

    with patch(f"{_MODULE}.get_subdir_by_order", side_effect=subdir):
        result = generate_diff("5.0")

    assert result is not None
    downloaded_file, processed_file, _diff_file = mock_compute.call_args[0]
    assert downloaded_file == os.path.join(dl_sub, "items.ndjson")
    assert processed_file == os.path.join(pr_sub_410, "items.ndjson")


@patch(f"{_MODULE}.get_timestamp", new=lambda: "20260301000001")
@patch(f"{_MODULE}.shutil.move")
@patch(
    f"{_MODULE}.compute_diff",
    return_value={"new_or_changed_count": 1, "processed_count": 1},
)
def test_generate_diff_prefers_own_version_processed_over_other_versions(
    mock_compute, mock_move, app_ctx, app_config
):
    """A model version's own processed history is used as the diff baseline, never another version's, even if that other version's dump sorts as more recent."""
    base = str(app_config["S3_DOWNLOAD_FOLDER"])
    dl_sub = os.path.join(base, "downloaded", "5.0", "20260301000000")
    pr_sub_50 = os.path.join(base, "processed", "5.0", "20260201000000")
    pr_sub_410 = os.path.join(base, "processed", "4.10", "20260225000000")
    os.makedirs(dl_sub, exist_ok=True)
    os.makedirs(pr_sub_50, exist_ok=True)
    os.makedirs(pr_sub_410, exist_ok=True)

    def subdir(root, most_recent=True):  # noqa: FBT002
        if root == os.path.join(base, "downloaded", "5.0"):
            return dl_sub
        if root == os.path.join(base, "processed", "5.0"):
            return pr_sub_50
        if root == os.path.join(base, "processed"):
            # Would be picked up if scoping were broken -- must not be used.
            return pr_sub_410
        return None

    with patch(f"{_MODULE}.get_subdir_by_order", side_effect=subdir):
        result = generate_diff("5.0")

    assert result is not None
    _downloaded_file, processed_file, _diff_file = mock_compute.call_args[0]
    assert processed_file == os.path.join(pr_sub_50, "items.ndjson")
