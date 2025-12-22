import datetime
import importlib
import os
from unittest.mock import patch

from freezegun import freeze_time

from mex_invenio.scripts.s3_manager import manage_s3_files


@patch("mex_invenio.scripts.s3_manager.import_data")
@patch("mex_invenio.scripts.s3_manager.initial_import")
def test_identical_files(
    mock_initial_import,
    mock_import_data,
    app_config,
    db,
    create_file,
    load_env,
    mock_s3_client,
    cli_runner,
):
    """Test that the script does not import files that are identical."""
    # Mock the import functions to return True
    mock_import_data.return_value = True
    mock_initial_import.return_value = True
    # download_path is a module scope temp path, so we need to be careful about
    # file names
    download_path = app_config["S3_DOWNLOAD_FOLDER"]

    # Create the existing file in the S3_DOWNLOAD_FOLDER
    existing_file = "test_identical_files_1.json"
    existing_file_path = create_file(
        f"{download_path}/{existing_file}", "{}", absolute=True
    )

    # Establish the file path of the file to be downloaded from S3
    downloaded_file = "test_identical_files_2.json"
    downloaded_file_path = f"{download_path}/{downloaded_file}"

    # Mock the download_file function to create the file locally
    def download_file(Bucket, Key, Filename):
        create_file(downloaded_file_path, "{}", absolute=True)

    mock_s3_client.download_file = download_file

    # Pretend S3 is returning them, the returned dict has more information than
    # the single key 'Contents' and each file has more information than just the
    # 'Key' and 'LastModified' keys but this is all we need for unit testing.
    mock_s3_client.list_objects_v2.return_value = {
        "Contents": [
            {"Key": downloaded_file_path, "LastModified": datetime.datetime.now()}
        ]
    }
    # {'Key': file_path2, 'LastModified': datetime.datetime.now()}]}

    # Import should not import anything and the younger file should be removed
    result = cli_runner(manage_s3_files)

    assert result.exit_code == 0
    assert os.path.exists(existing_file_path)
    assert not os.path.exists(downloaded_file_path)
    assert len(os.listdir(download_path)) == 1


@freeze_time("2023-01-01")
@patch("mex_invenio.scripts.s3_manager.import_data")
@patch("mex_invenio.scripts.s3_manager.initial_import")
def test_replace_file_but_fail_import(
    mock_initial_import,
    mock_import_data,
    app_config,
    db,
    create_file,
    load_env,
    mock_s3_client,
    cli_runner,
):
    """Test that the script replaces a file but fails to import it."""
    # Mock the import functions to return True
    mock_import_data.return_value = True
    mock_initial_import.return_value = True
    # download_path is a module scope temp path, so we need to be careful about
    # file names
    download_path = app_config["S3_DOWNLOAD_FOLDER"]

    # Create the existing file in the S3_DOWNLOAD_FOLDER
    existing_file = "test_replace_file_but_fail_import1.json"
    existing_file_path = create_file(
        f"{download_path}/{existing_file}",
        '{"identifier": "unique", "b":"a"}',
    )

    # Establish the file path of the file to be downloaded from S3
    downloaded_file = "test_replace_file_but_fail_import2.json"
    downloaded_file_path = f"{download_path}/{downloaded_file}"

    # Mock the download_file function to create the file locally
    def download_file(Bucket, Key, Filename):
        create_file(downloaded_file_path, '{"identifier": "unique", "s":"b"}')

    mock_s3_client.download_file = download_file

    # Pretend S3 is returning them, the returned dict has more information than
    # the single key 'Contents' and each file has more information than just the
    # 'Key' and 'LastModified' keys but this is all we need for unit testing.
    mock_s3_client.list_objects_v2.return_value = {
        "Contents": [
            {"Key": downloaded_file_path, "LastModified": datetime.datetime.now()}
        ]
    }
    # {'Key': file_path2, 'LastModified': datetime.datetime.now()}]}

    # Import should not import anything
    result = cli_runner(manage_s3_files)

    renamed_downloaded_file = f"{download_path}/20230101000000_{downloaded_file}"
    directory_contents = os.listdir(download_path)
    diff_directory_contents = os.listdir(os.path.join(download_path, "diffs"))
    mex_model_version = importlib.metadata.version("mex-model")
    renamed_downloaded_filename = f"20230101000000_{downloaded_file}"
    diff_filename = f"{existing_file}-{renamed_downloaded_filename}-{mex_model_version}_01-01-2023_12_00_00.ndjson"

    assert result.exit_code == 0
    assert os.path.exists(renamed_downloaded_file)
    assert "diffs" in directory_contents
    assert diff_filename in diff_directory_contents

    with open(os.path.join(download_path, "diffs", diff_filename), "r") as diff_file:
        diff_content = diff_file.read()
        assert diff_content.strip() == '{"identifier": "unique", "s": "b"}'
