import json
import os
from unittest.mock import MagicMock, patch

import pytest

from mex_invenio.scripts.s3_manager import (
    compute_diff,
    get_diff_file,
    get_s3_client_and_config,
    import_pending_diffs,
    manage_s3_files,
)

_MODULE = "mex_invenio.scripts.s3_manager"


@pytest.fixture
def s3_client(base_app):
    """Push the app context and patch get_s3_client_and_config for each test."""
    mock_client = MagicMock()
    with (
        base_app.app_context(),
        patch(f"{_MODULE}.get_s3_client_and_config") as mock_cfg,
    ):
        mock_cfg.return_value = (mock_client, "importer@example.com", "test-bucket")
        yield mock_client


@pytest.fixture
def app_ctx(base_app):
    """Push the Flask app context without any additional mocking."""
    with base_app.app_context():
        yield base_app


# ---------------------------------------------------------------------------
# get_s3_client_and_config
# ---------------------------------------------------------------------------


def test_get_s3_client_config_raises_on_missing_credentials():
    """get_s3_client_and_config raises ValueError when bucket/email are absent."""
    empty = {
        "MEX_IMPORT_BUCKET": "",
        "MEX_IMPORT_AWS_KEY_ID": "",
        "MEX_IMPORT_AWS_SECRET": "",
        "MEX_IMPORT_EMAIL": "",
    }
    with (
        patch.dict(os.environ, empty),
        pytest.raises(ValueError, match="Missing required"),
    ):
        get_s3_client_and_config()


def test_get_s3_client_config_success():
    """get_s3_client_and_config returns (client, email, bucket) when credentials present."""
    valid = {
        "MEX_IMPORT_BUCKET": "my-bucket",
        "MEX_IMPORT_AWS_KEY_ID": "key-id",
        "MEX_IMPORT_AWS_SECRET": "secret",
        "MEX_IMPORT_EMAIL": "admin@example.com",
    }
    mock_s3 = MagicMock()
    with patch.dict(os.environ, valid), patch("boto3.client", return_value=mock_s3):
        client, email, bucket = get_s3_client_and_config()
    assert client is mock_s3
    assert email == "admin@example.com"
    assert bucket == "my-bucket"


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
# get_diff_file  (needs app context via app_ctx)
# ---------------------------------------------------------------------------


@patch(f"{_MODULE}.get_subdir_by_order", return_value=None)
def test_get_diff_file_no_downloaded(mock_subdir, app_ctx):
    """get_diff_file returns None when no downloaded dump exists."""
    assert get_diff_file("4.10") is None


def test_get_diff_file_no_processed(app_ctx):
    """get_diff_file returns None when no processed dump exists."""

    def subdir(root, most_recent=True):  # noqa: FBT002
        return None if most_recent else "/some/download/path"

    with patch(f"{_MODULE}.get_subdir_by_order", side_effect=subdir):
        assert get_diff_file("4.10") is None


@patch(f"{_MODULE}.get_timestamp", new=lambda: "20240201000001")
@patch(f"{_MODULE}.compute_diff", return_value=None)
@patch(f"{_MODULE}.get_subdir_by_order")
def test_get_diff_file_compute_fails(mock_subdir, mock_compute, app_ctx, app_config):
    """get_diff_file returns None when compute_diff returns None."""
    base = str(app_config["S3_DOWNLOAD_FOLDER"])
    mock_subdir.side_effect = [
        os.path.join(base, "downloaded", "4.10", "20240201000000"),
        os.path.join(base, "processed", "4.10", "20240101000000"),
    ]
    assert get_diff_file("4.10") is None


@patch(f"{_MODULE}.get_timestamp", new=lambda: "20240301000001")
@patch(f"{_MODULE}.shutil.move")
@patch(
    f"{_MODULE}.compute_diff",
    return_value={"new_or_changed_count": 5, "processed_count": 10},
)
@patch(f"{_MODULE}.get_subdir_by_order")
def test_get_diff_file_success(
    mock_subdir, mock_compute, mock_move, app_ctx, app_config
):
    """get_diff_file returns the diff.ndjson path when compute_diff succeeds."""
    base = str(app_config["S3_DOWNLOAD_FOLDER"])
    dl_sub = os.path.join(base, "downloaded", "4.10", "20240301000000")
    pr_sub = os.path.join(base, "processed", "4.10", "20240201000000")
    os.makedirs(dl_sub, exist_ok=True)
    os.makedirs(pr_sub, exist_ok=True)
    mock_subdir.side_effect = [dl_sub, pr_sub]

    result = get_diff_file("4.10")

    assert result is not None
    assert result.endswith("diff.ndjson")
    assert "20240301000001" in result
    mock_compute.assert_called_once()
    mock_move.assert_called_once()


# ---------------------------------------------------------------------------
# import_pending_diffs  (pure filesystem — no Flask needed)
# ---------------------------------------------------------------------------


@patch(f"{_MODULE}.import_data")
def test_import_pending_diffs_empty(mock_import, tmp_path):
    """import_pending_diffs returns True and does nothing when diffs dir is empty."""
    (tmp_path / "diffs").mkdir()
    assert import_pending_diffs(str(tmp_path), "user@example.com") is True
    mock_import.assert_not_called()


@patch(f"{_MODULE}.import_data", return_value=True)
def test_import_pending_diffs_success(mock_import, tmp_path):
    """import_pending_diffs imports the diff and moves the directory to history."""
    diff_dir = tmp_path / "diffs" / "20240101000001"
    diff_dir.mkdir(parents=True)
    (diff_dir / "diff.ndjson").write_text('{"identifier": "a"}\n')
    (diff_dir / "metadata.json").write_text('{"model_version": "4.10"}')

    result = import_pending_diffs(str(tmp_path), "user@example.com")

    assert result is True
    mock_import.assert_called_once_with(
        "4.10", "user@example.com", str(diff_dir / "diff.ndjson")
    )
    assert (tmp_path / "history" / "20240101000001").exists()


@patch(f"{_MODULE}.import_data", return_value=False)
def test_import_pending_diffs_import_failure(mock_import, tmp_path):
    """import_pending_diffs returns False and stops when import_data fails."""
    diff_dir = tmp_path / "diffs" / "20240101000002"
    diff_dir.mkdir(parents=True)
    (diff_dir / "diff.ndjson").write_text('{"identifier": "a"}\n')
    (diff_dir / "metadata.json").write_text('{"model_version": "4.10"}')

    assert import_pending_diffs(str(tmp_path), "user@example.com") is False


@patch(f"{_MODULE}.import_data", return_value=True)
def test_import_pending_diffs_ordered(mock_import, tmp_path):
    """import_pending_diffs imports diffs oldest-first regardless of walk order."""
    for ts in ["20240102000001", "20240101000001", "20240103000001"]:
        d = tmp_path / "diffs" / ts
        d.mkdir(parents=True)
        (d / "diff.ndjson").write_text("{}")
        (d / "metadata.json").write_text('{"model_version": "4.10"}')

    import_pending_diffs(str(tmp_path), "user@example.com")

    timestamps = [
        os.path.basename(os.path.dirname(c.args[2])) for c in mock_import.call_args_list
    ]
    assert timestamps == sorted(timestamps)


@patch(f"{_MODULE}.import_data")
def test_import_pending_diffs_skips_corrupt_metadata(mock_import, tmp_path):
    """import_pending_diffs skips diff directories whose metadata.json is unreadable."""
    diff_dir = tmp_path / "diffs" / "20240101000003"
    diff_dir.mkdir(parents=True)
    (diff_dir / "diff.ndjson").write_text("{}")
    (diff_dir / "metadata.json").write_text("not-valid-json")

    assert import_pending_diffs(str(tmp_path), "user@example.com") is True
    mock_import.assert_not_called()


# ---------------------------------------------------------------------------
# manage_s3_files  (existing tests)
# ---------------------------------------------------------------------------


def test_no_s3_contents(cli_runner, app_config, s3_client):
    """Script exits cleanly when S3 bucket returns no contents."""
    s3_client.list_objects_v2.return_value = {}
    assert cli_runner(manage_s3_files).exit_code == 0


def test_no_metadata_file(cli_runner, app_config, s3_client):
    """Script exits cleanly when S3 bucket has no metadata.json."""
    s3_client.list_objects_v2.return_value = {
        "Contents": [{"Key": "items.ndjson", "LastModified": "2024-01-01"}]
    }
    assert cli_runner(manage_s3_files).exit_code == 0


def test_multiple_metadata_files(cli_runner, app_config, s3_client):
    """Script exits cleanly when S3 bucket has multiple metadata.json files."""
    s3_client.list_objects_v2.return_value = {
        "Contents": [
            {"Key": "v1/metadata.json", "LastModified": "2024-01-01"},
            {"Key": "v2/metadata.json", "LastModified": "2024-01-02"},
        ]
    }
    assert cli_runner(manage_s3_files).exit_code == 0


def test_s3_list_failure(cli_runner, app_config, s3_client):
    """Script exits with code 1 (retry) when list_objects_v2 raises a network error."""
    s3_client.list_objects_v2.side_effect = Exception("Connection refused")
    assert cli_runner(manage_s3_files).exit_code == 1


def test_s3_client_config_failure(cli_runner, app_config, base_app):
    """Script exits cleanly (no retry) when credentials are misconfigured."""
    with (
        base_app.app_context(),
        patch(f"{_MODULE}.get_s3_client_and_config", side_effect=ValueError),
    ):
        assert cli_runner(manage_s3_files).exit_code == 0


def test_metadata_download_failure(cli_runner, app_config, s3_client):
    """Script exits with code 1 (retry) when the S3 metadata download fails."""
    s3_client.list_objects_v2.return_value = {
        "Contents": [{"Key": "4.10/metadata.json", "LastModified": "2024-01-01"}]
    }
    s3_client.download_file.side_effect = Exception("network error")
    assert cli_runner(manage_s3_files).exit_code == 1


@patch(f"{_MODULE}.read_json_file", side_effect=Exception("parse error"))
def test_read_new_metadata_failure(mock_read, cli_runner, app_config, s3_client):
    """Script exits cleanly when reading the downloaded metadata.json fails."""
    s3_client.list_objects_v2.return_value = {
        "Contents": [{"Key": "4.10/metadata.json", "LastModified": "2024-01-01"}]
    }
    assert cli_runner(manage_s3_files).exit_code == 0


@patch(f"{_MODULE}.get_subdir_by_order", return_value=None)
@patch(
    f"{_MODULE}.read_json_file", return_value=("4.10", "abc", "2024-01-01T00:00:00Z")
)
def test_no_processed_dump(mock_read, mock_subdir, cli_runner, app_config, s3_client):
    """Script exits cleanly when no processed dump exists to compare the checksum against."""
    s3_client.list_objects_v2.return_value = {
        "Contents": [{"Key": "4.10/metadata.json", "LastModified": "2024-01-01"}]
    }
    assert cli_runner(manage_s3_files).exit_code == 0


@patch(f"{_MODULE}.read_json_file")
@patch(f"{_MODULE}.get_subdir_by_order")
def test_read_last_metadata_failure(
    mock_subdir, mock_read, cli_runner, app_config, s3_client
):
    """Script exits cleanly when reading the existing local metadata.json fails."""
    dl = os.path.join(str(app_config["S3_DOWNLOAD_FOLDER"]), "downloaded")
    mock_subdir.return_value = os.path.join(dl, "4.10", "20240101000000")
    mock_read.side_effect = [
        ("4.10", "new_ck", "2024-01-05T00:00:00Z"),
        Exception("read error"),
    ]
    s3_client.list_objects_v2.return_value = {
        "Contents": [{"Key": "4.10/metadata.json", "LastModified": "2024-01-05"}]
    }
    assert cli_runner(manage_s3_files).exit_code == 0


@patch(f"{_MODULE}.read_json_file")
@patch(f"{_MODULE}.get_subdir_by_order")
def test_identical_checksums_skips_download(
    mock_get_subdir, mock_read_json, cli_runner, app_config, s3_client
):
    """Script skips download when new metadata matches existing checksum and timestamp."""
    dl = os.path.join(str(app_config["S3_DOWNLOAD_FOLDER"]), "downloaded")
    mock_get_subdir.return_value = os.path.join(dl, "4.10", "20240101000000")
    mock_read_json.return_value = ("4.10", "abc123checksum", "2024-01-01T00:00:00Z")
    s3_client.list_objects_v2.return_value = {
        "Contents": [{"Key": "4.10/metadata.json", "LastModified": "2024-01-01"}]
    }

    result = cli_runner(manage_s3_files)

    assert result.exit_code == 0
    assert s3_client.download_file.call_count == 1


@patch(f"{_MODULE}.get_timestamp", new=lambda: "20240105000001")
@patch(f"{_MODULE}.read_json_file")
@patch(f"{_MODULE}.get_subdir_by_order")
def test_items_download_failure(
    mock_subdir, mock_read, cli_runner, app_config, s3_client
):
    """Script exits with code 1 (retry) when the S3 items file download fails."""
    dl = os.path.join(str(app_config["S3_DOWNLOAD_FOLDER"]), "downloaded")
    mock_subdir.return_value = os.path.join(dl, "4.10", "20240101000000")
    mock_read.side_effect = [
        ("4.10", "ck_new", "2024-01-05T00:00:00Z"),
        ("4.10", "ck_old", "2024-01-01T00:00:00Z"),
    ]
    s3_client.list_objects_v2.return_value = {
        "Contents": [{"Key": "4.10/metadata.json", "LastModified": "2024-01-05"}]
    }
    call_count = [0]

    def fake_download(bucket, key, dest):
        call_count[0] += 1
        if call_count[0] == 1:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            open(dest, "w").close()
        else:
            msg = "S3 items error"
            raise RuntimeError(msg)

    s3_client.download_file.side_effect = fake_download
    assert cli_runner(manage_s3_files).exit_code == 1


@patch(f"{_MODULE}.get_timestamp", new=lambda: "20240102000001")
@patch(f"{_MODULE}.import_pending_diffs")
@patch(f"{_MODULE}.get_diff_file")
@patch(f"{_MODULE}.read_json_file")
@patch(f"{_MODULE}.get_subdir_by_order")
def test_new_checksum_triggers_download_and_import(
    mock_get_subdir,
    mock_read_json,
    mock_get_diff,
    mock_import_pending,
    cli_runner,
    app_config,
    s3_client,
):
    """Script downloads new dump and imports diffs when checksum differs from existing."""
    download_folder = str(app_config["S3_DOWNLOAD_FOLDER"])
    download_path = os.path.join(download_folder, "downloaded")
    mock_get_subdir.return_value = os.path.join(download_path, "4.10", "20240101000000")
    mock_read_json.side_effect = [
        ("4.10", "new_checksum_xyz", "2024-01-02T00:00:00Z"),
        ("4.10", "old_checksum_abc", "2024-01-01T00:00:00Z"),
    ]
    mock_get_diff.return_value = os.path.join(
        download_folder, "diffs", "20240102000000", "diff.ndjson"
    )
    mock_import_pending.return_value = True

    def fake_download(bucket, key, dest):
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w") as f:
            f.write("{}")

    s3_client.download_file.side_effect = fake_download
    s3_client.list_objects_v2.return_value = {
        "Contents": [{"Key": "4.10/metadata.json", "LastModified": "2024-01-02"}]
    }

    result = cli_runner(manage_s3_files)

    assert result.exit_code == 0
    mock_get_diff.assert_called_once_with("4.10")
    mock_import_pending.assert_called_once()


@patch(f"{_MODULE}.get_timestamp", new=lambda: "20240103000001")
@patch(f"{_MODULE}.import_pending_diffs")
@patch(f"{_MODULE}.get_diff_file")
@patch(f"{_MODULE}.read_json_file")
@patch(f"{_MODULE}.get_subdir_by_order")
def test_diff_failure_skips_import(
    mock_get_subdir,
    mock_read_json,
    mock_get_diff,
    mock_import_pending,
    cli_runner,
    app_config,
    s3_client,
):
    """Script does not call import_pending_diffs when get_diff_file returns None."""
    download_folder = str(app_config["S3_DOWNLOAD_FOLDER"])
    download_path = os.path.join(download_folder, "downloaded")
    mock_get_subdir.return_value = os.path.join(download_path, "4.10", "20240101000000")
    mock_read_json.side_effect = [
        ("4.10", "new_checksum_xyz", "2024-01-02T00:00:00Z"),
        ("4.10", "old_checksum_abc", "2024-01-01T00:00:00Z"),
    ]
    mock_get_diff.return_value = None

    def fake_download(bucket, key, dest):
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w") as f:
            f.write("{}")

    s3_client.download_file.side_effect = fake_download
    s3_client.list_objects_v2.return_value = {
        "Contents": [{"Key": "4.10/metadata.json", "LastModified": "2024-01-02"}]
    }

    result = cli_runner(manage_s3_files)

    assert result.exit_code == 0
    mock_import_pending.assert_not_called()
