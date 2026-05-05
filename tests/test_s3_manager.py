import os
from unittest.mock import MagicMock, patch

import pytest

from mex_invenio.scripts.s3_manager import manage_s3_files

_MODULE = "mex_invenio.scripts.s3_manager"


@pytest.fixture
def s3_client(base_app):
    """Push the app context and patch get_s3_client_and_config for each test."""
    mock_client = MagicMock()
    with base_app.app_context():
        with patch(f"{_MODULE}.get_s3_client_and_config") as mock_cfg:
            mock_cfg.return_value = (mock_client, "importer@example.com", "test-bucket")
            yield mock_client


def test_no_s3_contents(cli_runner, app_config, s3_client):
    """Script exits cleanly when S3 bucket returns no contents."""
    s3_client.list_objects_v2.return_value = {}
    result = cli_runner(manage_s3_files)
    assert result.exit_code == 0


def test_no_metadata_file(cli_runner, app_config, s3_client):
    """Script exits cleanly when S3 bucket has no metadata.json."""
    s3_client.list_objects_v2.return_value = {
        "Contents": [{"Key": "items.ndjson", "LastModified": "2024-01-01"}]
    }
    result = cli_runner(manage_s3_files)
    assert result.exit_code == 0


def test_multiple_metadata_files(cli_runner, app_config, s3_client):
    """Script exits cleanly when S3 bucket has multiple metadata.json files."""
    s3_client.list_objects_v2.return_value = {
        "Contents": [
            {"Key": "v1/metadata.json", "LastModified": "2024-01-01"},
            {"Key": "v2/metadata.json", "LastModified": "2024-01-02"},
        ]
    }
    result = cli_runner(manage_s3_files)
    assert result.exit_code == 0


def test_s3_list_failure(cli_runner, app_config, s3_client):
    """Script exits cleanly when list_objects_v2 raises an exception."""
    s3_client.list_objects_v2.side_effect = Exception("Connection refused")
    result = cli_runner(manage_s3_files)
    assert result.exit_code == 0


@patch(f"{_MODULE}.read_json_file")
@patch(f"{_MODULE}.get_subdir_by_order")
def test_identical_checksums_skips_download(
    mock_get_subdir,
    mock_read_json,
    cli_runner,
    app_config,
    s3_client,
):
    """Script skips download when new metadata matches existing checksum and timestamp."""
    download_path = os.path.join(str(app_config["S3_DOWNLOAD_FOLDER"]), "downloaded")
    mock_get_subdir.return_value = os.path.join(download_path, "4.10", "20240101000000")
    mock_read_json.return_value = ("4.10", "abc123checksum", "2024-01-01T00:00:00Z")

    s3_client.list_objects_v2.return_value = {
        "Contents": [{"Key": "4.10/metadata.json", "LastModified": "2024-01-01"}]
    }

    result = cli_runner(manage_s3_files)

    assert result.exit_code == 0
    assert s3_client.download_file.call_count == 1


@patch(f"{_MODULE}.get_timestamp", return_value="20240102000001")
@patch(f"{_MODULE}.import_pending_diffs")
@patch(f"{_MODULE}.get_diff_file")
@patch(f"{_MODULE}.read_json_file")
@patch(f"{_MODULE}.get_subdir_by_order")
def test_new_checksum_triggers_download_and_import(
    mock_get_subdir,
    mock_read_json,
    mock_get_diff,
    mock_import_pending,
    _mock_ts,
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


@patch(f"{_MODULE}.get_timestamp", return_value="20240103000001")
@patch(f"{_MODULE}.import_pending_diffs")
@patch(f"{_MODULE}.get_diff_file")
@patch(f"{_MODULE}.read_json_file")
@patch(f"{_MODULE}.get_subdir_by_order")
def test_diff_failure_skips_import(
    mock_get_subdir,
    mock_read_json,
    mock_get_diff,
    mock_import_pending,
    _mock_ts,
    cli_runner,
    app_config,
    s3_client,
):
    """Script logs error and does not call import_pending_diffs when get_diff_file returns None."""
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
