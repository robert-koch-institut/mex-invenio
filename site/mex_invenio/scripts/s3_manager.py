"""
This script fetches the latest file from an S3 store and uploads it to the server.

### How to Run
To execute the script, run:
pipenv run invenio shell site/mex_invenio/scripts/s3_manager.py

### Parameters
The script takes the following parameters:
2. **checkLastDownload** This flag compares the latest downloaded file with the
   previous one to determine whether an upload is necessary.

### Requirements
Before running the script, ensure you have the following:
- **S3 Credentials**, which should include:
  - `bucket`
  - `aws_access_key`
  - `aws_secret_key`
  - `region`
- Make sure you also have added email (used for uploading data on mex) in your file

You can store these credentials in a custom file, a `.env` file,
"""

import sys

import click
import boto3
import logging
import os
from dotenv import load_dotenv
from flask import current_app
from mex_invenio.scripts.import_data import import_data
from mex_invenio.scripts.utils import compare_files
from datetime import datetime, timezone

from mex_invenio.config import S3_LOG_FILE, S3_LOG_FORMAT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(S3_LOG_FILE)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter(S3_LOG_FORMAT)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def load_config():
    s3_config = {}
    file_found = load_dotenv()

    if file_found:
        s3_config = {
            "bucket": os.getenv("bucket"),
            "aws_access_key_id": os.getenv("aws_access_key"),
            "aws_secret_access_key": os.getenv("aws_secret_key"),
            "region_name": os.getenv("region", "eu-central-1"),
            "email": os.getenv("email"),
        }

    if not s3_config:
        logger.error("Unable to fetch configration, env file is missing")
        sys.exit(1)

    if not all(
        [
            s3_config["bucket"],
            s3_config["aws_access_key_id"],
            s3_config["aws_secret_access_key"],
        ]
    ):
        logger.error(
            "Missing required configurations (bucket, aws_access_key, aws_secret_key)."
        )
        sys.exit(1)

    if not s3_config["email"]:
        logger.error("email environment variable is not set.")
        sys.exit(1)

    s3_endpoint_url = current_app.config.get("S3_ENDPOINT_URL", None)

    if s3_endpoint_url:
        s3_config["endpoint_url"] = s3_endpoint_url

    s3_object_key = current_app.config.get("S3_OBJECT_KEY", None)

    if s3_object_key:
        s3_config["object_key"] = s3_object_key

    return s3_config


def get_latest_file(s3_client, bucket_name):
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        if "Contents" not in response:
            logger.info("No files found in the bucket.")
            return
        latest_file = max(response["Contents"], key=lambda obj: obj["LastModified"])
        return latest_file["Key"]
    except Exception as e:
        logger.error(f"Error fetching latest file: {e}")


def download_file(s3_client, bucket_name, file_key, payload_folder):
    try:
        local_filename = os.path.join(payload_folder, os.path.basename(file_key))
        s3_client.download_file(bucket_name, file_key, local_filename)

        return local_filename
    except Exception as e:
        logger.error(f"Error downloading file: {e}")


def get_latest_existing_file(payload_folder):
    """Fetches the most recent file in the payload folder."""
    files = sorted(
        [
            os.path.join(payload_folder, f)
            for f in os.listdir(payload_folder)
            if os.path.isfile(os.path.join(payload_folder, f))
        ],
        key=os.path.getmtime,  # Sort by last modified time
    )

    return files[-1] if files else None


def rename_and_keep_latest_file(
    existing_file, new_file, payload_folder, check_comparison: bool
):
    """Handles file retention based on check flag."""
    if check_comparison and compare_files(existing_file, new_file):
        logger.info("No new content found. File is exactly the same as before.")
        return  # New file is identical, so discard it

    # Generate a timestamped filename to avoid overwriting
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    new_filename = f"{timestamp}_{os.path.basename(new_file)}"
    final_new_file_path = os.path.join(payload_folder, new_filename)

    os.rename(new_file, final_new_file_path)  # Rename new file

    # Always replace old file if check == False
    os.remove(existing_file)
    logger.info(
        f"Replaced old file: {existing_file} with new file: {final_new_file_path}"
    )

    return final_new_file_path


@click.command("manage_s3_files")
@click.option("--check", is_flag=True, default=False)
def manage_s3_files(check: bool):
    """Main function to download the latest file from S3, compare, and manage local storage."""

    s3_config = load_config()
    user_email = s3_config.pop("email")
    s3_bucket = s3_config.pop("bucket")
    s3_object_key = s3_config.pop("object_key", None)
    s3_client = boto3.client("s3", **s3_config)

    latest_file_key = s3_object_key or get_latest_file(s3_client, s3_bucket)
    if not latest_file_key:
        return

    s3_download_folder = current_app.config.get("S3_DOWNLOAD_FOLDER")
    os.makedirs(s3_download_folder, exist_ok=True)

    # This will be the most recently modified file in the download folder
    existing_file_path = get_latest_existing_file(s3_download_folder)

    # This is the most recently modified file in the S3 bucket
    new_file_path = download_file(
        s3_client, s3_bucket, latest_file_key, s3_download_folder
    )

    if new_file_path:
        final_file_path = rename_and_keep_latest_file(
            existing_file_path, new_file_path, s3_download_folder, check
        )
        if final_file_path:
            logger.info(f"importing data using file {final_file_path}")

            result = import_data(user_email, final_file_path)

            if not result:
                logger.error(
                    f"Error in import_data, check the import log files for more details."
                )
                sys.exit(1)
            else:
                logger.info(f"Import successful. Data imported from {final_file_path}.")


if __name__ == "__main__":
    manage_s3_files()
