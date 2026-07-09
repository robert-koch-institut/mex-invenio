import os
from unittest.mock import MagicMock, patch

import pytest

from mex_invenio.scripts.s3_manager import (
    get_model_metadata_files,
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
# get_model_metadata_files
# ---------------------------------------------------------------------------


def test_get_model_metadata_files_matches_publisher_prefix():
    """Only 'publisher-<version>/metadata.json' keys are matched."""
    contents = [
        {"Key": "publisher-4.10/metadata.json"},
        {"Key": "publisher-5.0/metadata.json"},
        {"Key": "publisher-4.10/items.ndjson"},
        {"Key": "publisher.ndjson"},
        {"Key": "DatenkompassActivity.xlsx"},
        {"Key": "some/other/metadata.json"},
    ]
    matched = [f["Key"] for f in get_model_metadata_files(contents)]
    assert matched == ["publisher-4.10/metadata.json", "publisher-5.0/metadata.json"]


def test_get_model_metadata_files_empty_when_no_match():
    """Returns an empty list when nothing in the bucket matches."""
    contents = [{"Key": "publisher.ndjson"}, {"Key": "DatenkompassActivity.xlsx"}]
    assert get_model_metadata_files(contents) == []


# ---------------------------------------------------------------------------
# manage_s3_files
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
    """Script exits cleanly when S3 bucket has multiple matching metadata.json files."""
    s3_client.list_objects_v2.return_value = {
        "Contents": [
            {"Key": "publisher-4.10/metadata.json", "LastModified": "2024-01-01"},
            {"Key": "publisher-5.0/metadata.json", "LastModified": "2024-01-02"},
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
        "Contents": [
            {"Key": "publisher-4.10/metadata.json", "LastModified": "2024-01-01"}
        ]
    }
    s3_client.download_file.side_effect = Exception("network error")
    assert cli_runner(manage_s3_files).exit_code == 1


@patch(f"{_MODULE}.read_json_file", side_effect=Exception("parse error"))
def test_read_new_metadata_failure(mock_read, cli_runner, app_config, s3_client):
    """Script exits cleanly when reading the downloaded metadata.json fails."""
    s3_client.list_objects_v2.return_value = {
        "Contents": [
            {"Key": "publisher-4.10/metadata.json", "LastModified": "2024-01-01"}
        ]
    }
    assert cli_runner(manage_s3_files).exit_code == 0


@patch(f"{_MODULE}.get_installed_model_version", return_value="4.10")
@patch(f"{_MODULE}.get_subdir_by_order", return_value=None)
@patch(
    f"{_MODULE}.read_json_file", return_value=("4.10", "abc", "2024-01-01T00:00:00Z")
)
def test_no_processed_dump(
    mock_read, mock_subdir, mock_installed_version, cli_runner, app_config, s3_client
):
    """Script exits cleanly when no processed dump exists to compare the checksum against."""
    s3_client.list_objects_v2.return_value = {
        "Contents": [
            {"Key": "publisher-4.10/metadata.json", "LastModified": "2024-01-01"}
        ]
    }
    assert cli_runner(manage_s3_files).exit_code == 0


@patch(f"{_MODULE}.get_installed_model_version", return_value="4.10")
@patch(f"{_MODULE}.read_json_file")
@patch(f"{_MODULE}.get_subdir_by_order")
def test_read_last_metadata_failure(
    mock_subdir, mock_read, mock_installed_version, cli_runner, app_config, s3_client
):
    """Script exits cleanly when reading the existing local metadata.json fails."""
    dl = os.path.join(str(app_config["S3_DOWNLOAD_FOLDER"]), "downloaded")
    mock_subdir.return_value = os.path.join(dl, "4.10", "20240101000000")
    mock_read.side_effect = [
        ("4.10", "new_ck", "2024-01-05T00:00:00Z"),
        Exception("read error"),
    ]
    s3_client.list_objects_v2.return_value = {
        "Contents": [
            {"Key": "publisher-4.10/metadata.json", "LastModified": "2024-01-05"}
        ]
    }
    assert cli_runner(manage_s3_files).exit_code == 0


@patch(f"{_MODULE}.get_installed_model_version", return_value="4.10")
@patch(f"{_MODULE}.read_json_file")
@patch(f"{_MODULE}.get_subdir_by_order")
def test_identical_checksums_skips_download(
    mock_get_subdir,
    mock_read_json,
    mock_installed_version,
    cli_runner,
    app_config,
    s3_client,
):
    """Script skips download when new metadata matches existing checksum and timestamp."""
    dl = os.path.join(str(app_config["S3_DOWNLOAD_FOLDER"]), "downloaded")
    mock_get_subdir.return_value = os.path.join(dl, "4.10", "20240101000000")
    mock_read_json.return_value = ("4.10", "abc123checksum", "2024-01-01T00:00:00Z")
    s3_client.list_objects_v2.return_value = {
        "Contents": [
            {"Key": "publisher-4.10/metadata.json", "LastModified": "2024-01-01"}
        ]
    }

    result = cli_runner(manage_s3_files)

    assert result.exit_code == 0
    assert s3_client.download_file.call_count == 1


@patch(f"{_MODULE}.get_timestamp", new=lambda: "20240105000001")
@patch(f"{_MODULE}.get_installed_model_version", return_value="4.10")
@patch(f"{_MODULE}.read_json_file")
@patch(f"{_MODULE}.get_subdir_by_order")
def test_items_download_failure(
    mock_subdir, mock_read, mock_installed_version, cli_runner, app_config, s3_client
):
    """Script exits with code 1 (retry) when the S3 items file download fails."""
    dl = os.path.join(str(app_config["S3_DOWNLOAD_FOLDER"]), "downloaded")
    mock_subdir.return_value = os.path.join(dl, "4.10", "20240101000000")
    mock_read.side_effect = [
        ("4.10", "ck_new", "2024-01-05T00:00:00Z"),
        ("4.10", "ck_old", "2024-01-01T00:00:00Z"),
    ]
    s3_client.list_objects_v2.return_value = {
        "Contents": [
            {"Key": "publisher-4.10/metadata.json", "LastModified": "2024-01-05"}
        ]
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
@patch(f"{_MODULE}.get_installed_model_version", return_value="4.10")
@patch(f"{_MODULE}.import_pending_diffs")
@patch(f"{_MODULE}.generate_diff")
@patch(f"{_MODULE}.read_json_file")
@patch(f"{_MODULE}.get_subdir_by_order")
def test_new_checksum_triggers_download_and_import(
    mock_get_subdir,
    mock_read_json,
    mock_generate_diff,
    mock_import_pending,
    mock_installed_version,
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
    mock_generate_diff.return_value = os.path.join(
        download_folder, "diffs", "20240102000000", "diff.ndjson"
    )
    mock_import_pending.return_value = True

    def fake_download(bucket, key, dest):
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w") as f:
            f.write("{}")

    s3_client.download_file.side_effect = fake_download
    s3_client.list_objects_v2.return_value = {
        "Contents": [
            {"Key": "publisher-4.10/metadata.json", "LastModified": "2024-01-02"}
        ]
    }

    result = cli_runner(manage_s3_files)

    assert result.exit_code == 0
    mock_generate_diff.assert_called_once_with("4.10")
    mock_import_pending.assert_called_once()


@patch(f"{_MODULE}.get_timestamp", new=lambda: "20240103000001")
@patch(f"{_MODULE}.get_installed_model_version", return_value="4.10")
@patch(f"{_MODULE}.import_pending_diffs")
@patch(f"{_MODULE}.generate_diff")
@patch(f"{_MODULE}.read_json_file")
@patch(f"{_MODULE}.get_subdir_by_order")
def test_diff_failure_skips_import(
    mock_get_subdir,
    mock_read_json,
    mock_generate_diff,
    mock_import_pending,
    mock_installed_version,
    cli_runner,
    app_config,
    s3_client,
):
    """Script does not call import_pending_diffs when generate_diff returns None."""
    download_folder = str(app_config["S3_DOWNLOAD_FOLDER"])
    download_path = os.path.join(download_folder, "downloaded")
    mock_get_subdir.return_value = os.path.join(download_path, "4.10", "20240101000000")
    mock_read_json.side_effect = [
        ("4.10", "new_checksum_xyz", "2024-01-02T00:00:00Z"),
        ("4.10", "old_checksum_abc", "2024-01-01T00:00:00Z"),
    ]
    mock_generate_diff.return_value = None

    def fake_download(bucket, key, dest):
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w") as f:
            f.write("{}")

    s3_client.download_file.side_effect = fake_download
    s3_client.list_objects_v2.return_value = {
        "Contents": [
            {"Key": "publisher-4.10/metadata.json", "LastModified": "2024-01-02"}
        ]
    }

    result = cli_runner(manage_s3_files)

    assert result.exit_code == 0
    mock_import_pending.assert_not_called()


# ---------------------------------------------------------------------------
# manage_s3_files — multiple model versions in the same bucket/run
# ---------------------------------------------------------------------------


@patch(f"{_MODULE}.get_timestamp", new=lambda: "20260401000001")
@patch(f"{_MODULE}.get_installed_model_version", return_value="5.0")
@patch(f"{_MODULE}.import_pending_diffs")
@patch(f"{_MODULE}.generate_diff")
@patch(f"{_MODULE}.read_json_file")
@patch(f"{_MODULE}.get_subdir_by_order")
def test_unchanged_version_does_not_block_other_versions_in_same_run(
    mock_get_subdir,
    mock_read_json,
    mock_generate_diff,
    mock_import_pending,
    mock_installed_version,
    cli_runner,
    app_config,
    s3_client,
):
    """A non-installed-version dump (download-only) must not stop the installed version's dump from being reached and diffed in the same run."""
    download_folder = str(app_config["S3_DOWNLOAD_FOLDER"])
    processed_path = os.path.join(download_folder, "processed")
    last_processed_410 = os.path.join(processed_path, "4.10", "20260101000000")

    def fake_subdir(root, most_recent=True):  # noqa: FBT002
        if root == os.path.join(processed_path, "5.0"):
            return None  # 5.0 (installed) has no processed history yet
        if root == processed_path:
            return last_processed_410  # global fallback for 5.0's first run
        return None

    mock_get_subdir.side_effect = fake_subdir
    mock_read_json.side_effect = [
        (
            "4.10",
            "unused_checksum",
            "2026-01-01T00:00:00Z",
        ),  # 4.10 new metadata (not installed)
        (
            "5.0",
            "new_checksum",
            "2026-04-01T00:00:00Z",
        ),  # 5.0 new metadata (installed version)
        (
            "4.10",
            "old_checksum",
            "2026-01-01T00:00:00Z",
        ),  # fallback baseline (4.10's last processed)
    ]
    mock_generate_diff.return_value = os.path.join(
        download_folder, "diffs", "20260401000001", "diff.ndjson"
    )
    mock_import_pending.return_value = True

    def fake_download(bucket, key, dest):
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w") as f:
            f.write("{}")

    s3_client.download_file.side_effect = fake_download
    s3_client.list_objects_v2.return_value = {
        "Contents": [
            {"Key": "publisher-4.10/metadata.json", "LastModified": "2026-01-01"},
            {"Key": "publisher-5.0/metadata.json", "LastModified": "2026-04-01"},
        ]
    }

    result = cli_runner(manage_s3_files)

    assert result.exit_code == 0
    mock_generate_diff.assert_called_once_with("5.0")
    mock_import_pending.assert_called_once()


@patch(f"{_MODULE}.get_timestamp", new=lambda: "20260501000001")
@patch(f"{_MODULE}.get_installed_model_version", return_value="5.0")
@patch(f"{_MODULE}.import_pending_diffs")
@patch(f"{_MODULE}.generate_diff")
@patch(f"{_MODULE}.read_json_file")
@patch(f"{_MODULE}.get_subdir_by_order")
def test_new_model_version_falls_back_to_other_version_baseline(
    mock_get_subdir,
    mock_read_json,
    mock_generate_diff,
    mock_import_pending,
    mock_installed_version,
    cli_runner,
    app_config,
    s3_client,
):
    """The first dump of a new model version compares against the last processed dump of whatever version came before it, instead of being skipped as 'no processed dump found'."""
    download_folder = str(app_config["S3_DOWNLOAD_FOLDER"])
    processed_path = os.path.join(download_folder, "processed")
    fallback_path = os.path.join(processed_path, "4.10", "20260101000000")

    def fake_subdir(root, most_recent=True):  # noqa: FBT002
        if root == os.path.join(processed_path, "5.0"):
            return None  # no 5.0 history yet
        if root == processed_path:
            return fallback_path
        return None

    mock_get_subdir.side_effect = fake_subdir
    mock_read_json.side_effect = [
        ("5.0", "new_checksum", "2026-04-01T00:00:00Z"),
        ("4.10", "old_checksum", "2026-01-01T00:00:00Z"),
    ]
    mock_generate_diff.return_value = os.path.join(
        download_folder, "diffs", "20260501000001", "diff.ndjson"
    )
    mock_import_pending.return_value = True

    def fake_download(bucket, key, dest):
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w") as f:
            f.write("{}")

    s3_client.download_file.side_effect = fake_download
    s3_client.list_objects_v2.return_value = {
        "Contents": [
            {"Key": "publisher-5.0/metadata.json", "LastModified": "2026-04-01"}
        ]
    }

    result = cli_runner(manage_s3_files)

    assert result.exit_code == 0
    mock_generate_diff.assert_called_once_with("5.0")
    mock_import_pending.assert_called_once()


@patch(f"{_MODULE}.get_timestamp", new=lambda: "20260601000001")
@patch(f"{_MODULE}.get_installed_model_version", return_value="4.10")
@patch(f"{_MODULE}.read_json_file", return_value=("5.0", "ck", "2026-06-01T00:00:00Z"))
@patch(f"{_MODULE}.import_pending_diffs")
@patch(f"{_MODULE}.generate_diff")
def test_non_installed_version_downloads_but_never_diffs(
    mock_generate_diff,
    mock_import_pending,
    mock_read_json,
    mock_installed_version,
    cli_runner,
    app_config,
    s3_client,
):
    """A dump whose model version doesn't match the installed one is downloaded (metadata + items) but never diffed or imported."""
    download_folder = str(app_config["S3_DOWNLOAD_FOLDER"])
    download_path = os.path.join(download_folder, "downloaded")

    def fake_download(bucket, key, dest):
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w") as f:
            f.write("{}")

    s3_client.download_file.side_effect = fake_download
    s3_client.list_objects_v2.return_value = {
        "Contents": [
            {"Key": "publisher-5.0/metadata.json", "LastModified": "2026-06-01"}
        ]
    }

    result = cli_runner(manage_s3_files)

    assert result.exit_code == 0
    # Both metadata.json and items.ndjson were fetched...
    assert s3_client.download_file.call_count == 2
    # ...but the dump was never diffed or imported, since 5.0 != installed 4.10.
    mock_generate_diff.assert_not_called()
    mock_import_pending.assert_not_called()
    # And it's cached on disk under its own version, ready for a future upgrade.
    cached_dir = os.path.join(download_path, "5.0", "20260601000001")
    assert os.path.exists(os.path.join(cached_dir, "metadata.json"))
    assert os.path.exists(os.path.join(cached_dir, "items.ndjson"))
