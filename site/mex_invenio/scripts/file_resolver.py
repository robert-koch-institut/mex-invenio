"""This script fetches the latest file from an S3 store and imports it to the server.

If more than 20 files are present in the local download folder, the oldest ones are deleted.

### How to Run
To execute the script, run:
pipenv run invenio shell site/mex_invenio/scripts/s3_manager.py

### Parameters
The script takes the following parameters:
**initial** Whether to do an initial import of the data after downloading it from S3 or
            a standard one.

### Requirements
Before running the script, there is a number of environment variables you can set:
- **S3 Credentials**:
  - `MEX_IMPORT_BUCKET`: the name of the S3 bucket
  - `MEX_IMPORT_AWS_KEY_ID`: your AWS access key ID
  - `MEX_IMPORT_AWS_SECRET`: your AWS secret access key
  - `MEX_IMPORT_REGION_NAME`: the AWS region where your bucket is located, optional and defaults to
   `eu-central-1`
  - `MEX_IMPORT_ENDPOINT_URL`: optional, if you are using a custom S3 endpoint
- Make sure you also have added email (used for uploading data on mex) in your file via MEX_IMPORT_EMAIL

You can store these credentials in a `.env` file,
"""

from datetime import datetime, timezone
import hashlib
import json
import logging
import os
import re
import shutil

import boto3
import click
from dotenv import load_dotenv
from flask import current_app

from mex_invenio.scripts.import_data import import_data
from mex_invenio.scripts.initial_import import initial_import
from mex_invenio.scripts.utils import (
    cleanup_files,
    get_timestamp,
    get_subdir_by_order,
    normalize_record_data,
    read_json_file,
    setup_file_logging,
    write_json_file,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

envvar_prefix = "MEX_IMPORT_"


def get_s3_client_and_config():
    load_dotenv()

    s3_config = {
        "aws_access_key_id": os.getenv(envvar_prefix + "AWS_KEY_ID"),
        "aws_secret_access_key": os.getenv(envvar_prefix + "AWS_SECRET"),
        "region_name": os.getenv(envvar_prefix + "REGION_NAME", "eu-central-1"),
        "endpoint_url": os.getenv(envvar_prefix + "ENDPOINT_URL"),
    }
    bucket = os.getenv(envvar_prefix + "BUCKET")
    email = os.getenv(envvar_prefix + "EMAIL")

    # Get rid of the None values that weren't provided
    s3_config = {k: v for k, v in s3_config.items() if v is not None}

    if not all(
        [
            bucket,
            email,
            "aws_access_key_id" in s3_config,
            "aws_secret_access_key" in s3_config,
        ]
    ):
        logger.error(
            "Missing required configurations (bucket, aws_access_key, aws_secret_key, email)."
        )
        raise ValueError

    s3_client = boto3.client("s3", **s3_config)

    return s3_client, email, bucket


def download_file(s3_client, bucket_name, file_key, payload_folder):
    try:
        local_filename = os.path.join(payload_folder, os.path.basename(file_key))
        s3_client.download_file(bucket_name, file_key, local_filename)

        return local_filename
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        raise


def compute_diff(downloaded_file: str, processed_file: str, diff_file: str):
    """Create a diff file containing only new or changed records based on identifier comparison.

    Optimized for large files by using streaming and hash-based comparison.
    """

    try:
        # Read existing records and create hash index (memory efficient)
        existing_hashes = {}  # identifier -> content_hash
        existing_count = 0

        logger.info(f"Reading existing file: {processed_file}")
        if os.path.exists(processed_file):
            with open(processed_file, encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                        record_id = record.get("identifier")
                        if record_id:
                            # Create hash of normalized content for efficient comparison
                            normalized = normalize_record_data(record)
                            content_hash = hashlib.md5(
                                json.dumps(normalized, sort_keys=True).encode("utf-8")
                            ).hexdigest()
                            existing_hashes[record_id] = content_hash
                            existing_count += 1
                    except json.JSONDecodeError as e:
                        logger.warning(
                            f"Invalid JSON at line {line_num} in {processed_file}: {e}"
                        )

                    # Log progress for large files
                    if line_num % 10000 == 0:
                        logger.info(f"Processed {line_num} lines from existing file")

        logger.info(f"Indexed {existing_count} existing records")

        # Stream process new file and write diff directly
        new_or_changed_count = 0
        processed_count = 0

        logger.info(f"Processing new file: {downloaded_file}")
        with (
            open(downloaded_file, encoding="utf-8") as infile,
            open(diff_file, "w", encoding="utf-8") as outfile,
        ):
            for line_num, line in enumerate(infile, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    record = json.loads(line)
                    record_id = record.get("identifier")
                    if record_id:
                        # Create hash of new record
                        normalized = normalize_record_data(record)
                        content_hash = hashlib.md5(
                            json.dumps(normalized, sort_keys=True).encode("utf-8")
                        ).hexdigest()

                        existing_hash = existing_hashes.get(record_id)
                        if existing_hash is None or existing_hash != content_hash:
                            # New or changed record - write to diff file immediately
                            json.dump(record, outfile, ensure_ascii=False)
                            outfile.write("\n")
                            new_or_changed_count += 1

                        processed_count += 1
                    else:
                        logger.warning(
                            f"Record without identifier at line {line_num} in {downloaded_file}"
                        )

                except json.JSONDecodeError as e:
                    logger.warning(
                        f"Invalid JSON at line {line_num} in {downloaded_file}: {e}"
                    )

                # Log progress for large files
                if line_num % 10000 == 0:
                    logger.info(
                        f"Processed {line_num} lines, found {new_or_changed_count} changes"
                    )

        logger.info(
            f"Comparison complete: {new_or_changed_count} new/changed records out of {processed_count} total"
        )

        return { "new_or_changed_count": new_or_changed_count, "processed_count": processed_count }

    except Exception as e:
        logger.error(f"Error during JSON-based file comparison: {e}")
        return None


def get_diff_file():
    # Define folder locations
    s3_download_folder = current_app.config.get("S3_DOWNLOAD_FOLDER", "s3_downloads")
    downloaded_path = os.path.join(s3_download_folder, "downloaded")
    processed_path = os.path.join(s3_download_folder, "processed")
    diff_path = os.path.join(s3_download_folder, "diffs")

    # Get the oldest downloaded dump and the most recently processed one
    oldest_download_path = get_subdir_by_order(downloaded_path, False)
    most_recent_processed_path = get_subdir_by_order(processed_path)

    timestamp = get_timestamp()
    diff_folder = os.path.join(diff_path, f"draft-{timestamp}")
    os.makedirs(diff_folder, exist_ok=True)
    processed_file = os.path.join(most_recent_processed_path, "items.ndjson")
    downloaded_file = os.path.join(oldest_download_path, "items.ndjson")
    diff_file = os.path.join(diff_folder, "diff.ndjson")

    diff_result = compute_diff(downloaded_file, processed_file, diff_file)

    if diff_result:
        # Write process output to metadata.json
        diff_metadata = {
            'processed_file': processed_file,
            'downloaded_file': downloaded_file,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            **diff_result,
        }
        write_json_file(os.path.join(diff_folder, "metadata.json"), diff_metadata)

        # Rename diff folder as non-draft
        os.rename(diff_folder, os.path.join(diff_path, timestamp))
        diff_file = os.path.join(diff_path, timestamp, "diff.ndjson")

        logger.info(diff_file)

        # Move dump from downloaded to processed
        rel = os.path.relpath(oldest_download_path, downloaded_path)  # e.g. "4.10/20260504230150"
        destination = os.path.join(processed_path, rel)
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        shutil.move(oldest_download_path, destination)

        logger.info(f"Found {diff_file}.")

        return diff_file

    return None


@click.command("manage_s3_files")
@click.option("--initial", is_flag=True, default=False)
def manage_s3_files(initial: bool = False):
    """Main function to download the latest file from S3, compare, and manage local storage."""
    # Get the download folder from config
    s3_download_folder = current_app.config.get("S3_DOWNLOAD_FOLDER", "s3_downloads")

    # Create directories and set up logging at start
    for sub_dir in ['logs', 'downloaded', 'processed', 'diffs', 'history']:
        sub_dir = os.path.join(s3_download_folder, sub_dir)
        os.makedirs(sub_dir, exist_ok=True)

    log_dir = os.path.join(s3_download_folder, "logs")

    file_handler = setup_file_logging(log_dir, name="s3_manager")
    logger.addHandler(file_handler)

    # Load s3_client and config
    try:
        s3_client, user_email, s3_bucket = get_s3_client_and_config()
    except ValueError:
        return None

    response = s3_client.list_objects_v2(Bucket=s3_bucket)

    if "Contents" not in response:
        logger.info("No files found in the bucket.")
        return None

    download_path = os.path.join(s3_download_folder, "downloaded")

    # Get the metadata file
    metadata_files = [m for m in response['Contents'] if m['Key'].endswith("metadata.json")]

    if len(metadata_files) == 0:
        logger.info("No metadata files found in the bucket.")
        return None
    elif len(metadata_files) > 1:
        logger.info("Multiple metadata files found in the bucket.")
        return None

    metadata_file = metadata_files[0]

    # Create tmp draft downloaded location for dump
    dump_folder = f"draft-{get_timestamp()}"
    # e.g. s3_downloads/downloaded/tmp/draft-20260430104905
    tmp_dump_path = os.path.join(download_path, 'tmp', dump_folder)
    logger.info(f"Downloading file {metadata_file['Key']} to {tmp_dump_path}")
    os.makedirs(tmp_dump_path, exist_ok=True)

    # Download metadata file
    new_metadata_file = os.path.join(tmp_dump_path, "metadata.json")
    s3_client.download_file(s3_bucket, metadata_file['Key'], new_metadata_file)
    new_model_version, new_checksum, new_timestamp = read_json_file(new_metadata_file)

    # All check for previous download
    last_download_path = get_subdir_by_order(download_path)

    if not last_download_path:
        logger.info(f"No files found in the downloaded folder: {new_metadata_file}")
        return None

    most_recent_metadata_file = os.path.join(last_download_path, "metadata.json")
    last_model_version, last_checksum, last_timestamp = read_json_file(most_recent_metadata_file)

    # Only download if there is a new dump
    if new_checksum == last_checksum and new_timestamp == last_timestamp:
        logger.info('Checksums and timestamps match.')
        logger.info(f'{most_recent_metadata_file}\n{new_metadata_file}')
        logger.info(f'Removing {tmp_dump_path}')
        shutil.rmtree(tmp_dump_path)
        return None

    # Move from tmp path to download folder, download items file and remove draft- prefix
    destination_path = os.path.join(download_path, new_model_version, dump_folder)
    shutil.move(tmp_dump_path, destination_path)
    downloaded_items_file = os.path.join(destination_path, "items.ndjson")
    bucket_key = metadata_file['Key'].replace('metadata.json', 'items.ndjson')
    s3_client.download_file(s3_bucket, bucket_key, downloaded_items_file)
    os.rename(destination_path, os.path.join(download_path, new_model_version, dump_folder.removeprefix('draft-')))

    # Compute diff file
    diff_file = get_diff_file()

    if not diff_file:
        logger.error(f"Error creating diff files for model version: {new_model_version}.")
        return None

    logger.info(f"Downloaded {diff_file}.")

    try:
        result = import_data(new_model_version, user_email, diff_file)

        # Import was successful
        if result:
            diff_path = os.path.dirname(diff_file)
            diffs_root = os.path.join(s3_download_folder, "diffs")
            rel = os.path.relpath(os.path.dirname(diff_file), diffs_root)  # e.g. "1.2/20260430104905"
            diff_history_path = os.path.join(s3_download_folder, "history", rel)
            logger.info(f"{diff_path}\n{diffs_root}\n{diff_history_path}")
            os.makedirs(os.path.dirname(diff_history_path), exist_ok=True)
            logger.info(f"Moving {diff_path} to {diff_history_path}")
            shutil.move(diff_path, diff_history_path)
    except Exception as e:
        logger.error(f"Error importing {diff_file}.")


    return
    for dirpath, dirnames, _ in os.walk(os.path.join(s3_download_folder, "diffs")):
        for name in dirnames:
            # Skip the parent model
            if re.search(r'^\d*\.\d*$', name):
                continue

            new_model_version = os.path.basename(dirpath)
            diff_dir = os.path.join(dirpath, name)
            diff_file = os.path.join(diff_dir, "diff.ndjson")
            diff_metadata_file = os.path.join(diff_dir, "metadata.json")

            if os.path.isfile(diff_file) and os.path.isfile(diff_metadata_file):
                result =  import_data(new_model_version, user_email, diff_file)

                if not result:
                    break


if __name__ == "__main__":
    manage_s3_files()
