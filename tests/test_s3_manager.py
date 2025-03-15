import datetime
import os

from mex_invenio.scripts.s3_manager import manage_s3_files, get_latest_file

from freezegun import freeze_time

def test_identical_files(app_config, db, create_file, load_env, mock_s3_client, cli_runner):
    # download_path is a module scope temp path, so we need to be careful about
    # file names
    download_path = app_config['S3_DOWNLOAD_FOLDER']

    # Create the existing file in the S3_DOWNLOAD_FOLDER
    existing_file = 'test_identical_files_1.json'
    existing_file_path = create_file(f'{download_path}/{existing_file}', '{}', absolute=True)

    # Establish the file path of the file to be downloaded from S3
    downloaded_file = 'test_identical_files_2.json'
    downloaded_file_path = f'{download_path}/{downloaded_file}'

    # Mock the download_file function to create the file locally
    def download_file(Bucket, Key, Filename):
        create_file(downloaded_file_path, '{}', absolute=True)

    mock_s3_client.download_file = download_file

    # Pretend S3 is returning them, the returned dict has more information than
    # the single key 'Contents' and each file has more information than just the
    # 'Key' and 'LastModified' keys but this is all we need for unit testing.
    mock_s3_client.list_objects_v2.return_value = {
        'Contents': [{'Key': downloaded_file_path, 'LastModified': datetime.datetime.now()}]}
    # {'Key': file_path2, 'LastModified': datetime.datetime.now()}]}

    # Import should not import anything and the younger file should be removed
    result = cli_runner(manage_s3_files, "--check")

    assert result.exit_code == 0 # No files imported
    assert os.path.exists(existing_file_path)
    assert not os.path.exists(downloaded_file_path)

@freeze_time("2023-01-01")
def test_replace_file_but_fail_import(app_config, db, create_file, load_env, mock_s3_client, cli_runner):
    # download_path is a module scope temp path, so we need to be careful about
    # file names
    download_path = app_config['S3_DOWNLOAD_FOLDER']

    # Create the existing file in the S3_DOWNLOAD_FOLDER
    existing_file = 'test_replace_file_but_fail_import1.json'
    existing_file_path = create_file(f'{download_path}/{existing_file}', '{"s":"a"}', absolute=True)

    # Establish the file path of the file to be downloaded from S3
    downloaded_file = 'test_replace_file_but_fail_import2.json'
    downloaded_file_path = f'{download_path}/{downloaded_file}'

    # Mock the download_file function to create the file locally
    def download_file(Bucket, Key, Filename):
        create_file(downloaded_file_path, '{"s":"b"}', absolute=True)
    mock_s3_client.download_file = download_file

    # Pretend S3 is returning them, the returned dict has more information than
    # the single key 'Contents' and each file has more information than just the
    # 'Key' and 'LastModified' keys but this is all we need for unit testing.
    mock_s3_client.list_objects_v2.return_value = {
        'Contents': [{'Key': downloaded_file_path, 'LastModified': datetime.datetime.now()}]}
    #{'Key': file_path2, 'LastModified': datetime.datetime.now()}]}

    # Import should not import anything and the younger file should be removed
    result = cli_runner(manage_s3_files, "--check")

    renamed_downloaded_file = f'{download_path}/20230101000000_{downloaded_file}'

    assert not os.path.exists(existing_file_path)
    assert result.exit_code == 1 # The import job will error because the user is not found
    assert os.path.exists(renamed_downloaded_file)
