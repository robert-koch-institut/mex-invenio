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
  - `MEX_IMPORT_OBJECT_KEY`: optional, if you want to download a specific file from S3 if it
   is not set the script will download the latest file in the bucket
- Make sure you also have added email (used for uploading data on mex) in your file via MEX_IMPORT_EMAIL

You can store these credentials in a `.env` file,
"""
import importlib.metadata
import logging
import os
import sys
from datetime import datetime, timezone

import boto3
import packaging.version
import click
from dotenv import load_dotenv
from flask import current_app

from mex_invenio.scripts.import_data import import_data
from mex_invenio.scripts.initial_import import initial_import
from mex_invenio.scripts.utils import compare_files, diff_files, setup_file_logging, cleanup_files, _read_lock, _write_lock

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

envvar_prefix = "MEX_IMPORT_"


def load_config():
    load_dotenv()

    v = packaging.version.Version(importlib.metadata.version("mex-model"))
    mex_model_version = f"{v.major}.{v.minor}"
    env_object_key = os.getenv(envvar_prefix + "OBJECT_KEY")
    object_key = f"publisher-{mex_model_version}/{env_object_key}" if env_object_key else None

    s3_config = {
        "bucket": os.getenv(envvar_prefix + "BUCKET"),
        "aws_access_key_id": os.getenv(envvar_prefix + "AWS_KEY_ID"),
        "aws_secret_access_key": os.getenv(envvar_prefix + "AWS_SECRET"),
        "region_name": os.getenv(envvar_prefix + "REGION_NAME", "eu-central-1"),
        "email": os.getenv(envvar_prefix + "EMAIL"),
        "endpoint_url": os.getenv(envvar_prefix + "ENDPOINT_URL", None),
        "object_key": object_key,
    }

    # Get rid of the None values that weren't provided
    s3_config = {k: v for k, v in s3_config.items() if v is not None}

    if not all(
        [
            s3_config["bucket"],
            s3_config["aws_access_key_id"],
            s3_config["aws_secret_access_key"],
            s3_config["email"],
        ]
    ):
        logger.error(
            "Missing required configurations (bucket, aws_access_key, aws_secret_key, email)."
        )
        sys.exit(1)

    return s3_config


def get_latest_file(s3_client, bucket_name):
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        if "Contents" not in response:
            logger.info("No files found in the bucket.")
            return None
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
        raise


def get_latest_existing_file(payload_folder):
    """Fetches the most recent file in the payload folder and removes files older than the 20 most recent ones."""
    files = sorted(
        [
            os.path.join(payload_folder, f)
            for f in os.listdir(payload_folder)
            if os.path.isfile(os.path.join(payload_folder, f)) and not f.startswith(".")
        ],
        key=os.path.getmtime,  # Sort by last modified time
        reverse=True,  # Most recent first
    )

    if len(files) > 20:
        for f in files[20:]:
            try:
                os.remove(f)
                logger.info(f"Removed old file: {f}")
            except OSError as e:
                logger.warning(f"Could not remove old file {f}: {e}")

    return files[0] if files else None


def get_final_import_file(existing_file, new_file, payload_folder):
    """Handles file retention based on check flag."""
    if existing_file and compare_files(existing_file, new_file):
        logger.info("No new content found. File is exactly the same as before.")
        logger.info(f"{new_file} deleted")
        return None  # New file is identical, so discard it

    # Generate a timestamped filename to avoid overwriting
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    new_filename = f"{timestamp}_{os.path.basename(new_file)}"
    final_new_file_path = os.path.join(payload_folder, new_filename)

    os.rename(new_file, final_new_file_path)  # Rename new file

    # Create diff file if both files exist
    diff_file_path = final_new_file_path
    if existing_file and os.path.exists(existing_file):
        try:
            diff_file_path = diff_files(
                payload_folder, existing_file, final_new_file_path
            )
            # os.remove(existing_file)
            logger.info(
                f"Replaced old file: {existing_file} with new file: {final_new_file_path}"
            )
        except OSError as e:
            logger.warning(f"Could not remove existing file {existing_file}: {e}")

    return diff_file_path


@click.command("manage_s3_files")
@click.option("--initial", is_flag=True, default=False)
def manage_s3_files(initial: bool = False):
    """Main function to download the latest file from S3, compare, and manage local storage."""
    # Get the download folder from config
    s3_download_folder = current_app.config.get("S3_DOWNLOAD_FOLDER", "s3_downloads")
    # Set up logging at start
    log_dir = os.path.join(s3_download_folder, "logs")
    os.makedirs(log_dir, exist_ok=True)
    file_handler = setup_file_logging(log_dir, name="s3_manager")
    logger.addHandler(file_handler)

    s3_config = load_config()
    user_email = s3_config.pop("email")
    s3_bucket = s3_config.pop("bucket")
    s3_object_key = s3_config.pop("object_key", None)
    s3_client = boto3.client("s3", **s3_config)

    latest_file_key = s3_object_key or get_latest_file(s3_client, s3_bucket)
    if not latest_file_key:
        return

    lock_file = os.path.join(s3_download_folder, ".import_lock")
    lock = _read_lock(lock_file)
    if lock:
        lock_status = lock.get("status")
        if lock_status == "in_progress":
            # This should not happen because of "concurrencyPolicy: Forbid" in the
            # Helm chart, but acts as a safety valve in case a pod crashed mid-import.
            logger.warning("Import already in progress (lock file found). Skipping.")
            sys.exit(1)
        elif lock_status == "failed":
            logger.error(
                f"Previous import failed (lock file: {lock_file}). "
                "Resolve the issue and delete the lock file to re-enable imports."
            )
            sys.exit(1)

    started_at = datetime.now(timezone.utc).isoformat()
    _write_lock(lock_file, "in_progress", started_at=started_at)

    try:
        logger.info(f"Downloading file {latest_file_key} from bucket {s3_bucket}")
        logger.info(f"To download folder: {s3_download_folder}")

        # This will be the most recently modified file in the download folder
        existing_file_path = get_latest_existing_file(s3_download_folder)

        # This is the most recently modified file in the S3 bucket
        new_file_path = download_file(
            s3_client, s3_bucket, latest_file_key, s3_download_folder
        )

        logger.info(f"Download file {new_file_path} from bucket {s3_bucket}")

        final_file_path = get_final_import_file(
            existing_file_path, new_file_path, s3_download_folder
        )

        if not final_file_path:
            logger.info("No new content to import.")
            _write_lock(lock_file, "success", started_at=started_at,
                        finished_at=datetime.now(timezone.utc).isoformat())
            sys.exit(0)

        logger.info(f"Importing data using file {final_file_path}")

        if initial:
            result = initial_import(user_email, final_file_path)
        else:
            result = import_data(user_email, final_file_path)

        finished_at = datetime.now(timezone.utc).isoformat()

        if not result:
            logger.error(
                "Error in import_data, check the import log files for more details."
            )
            _write_lock(lock_file, "failed", started_at=started_at, finished_at=finished_at)
            sys.exit(1)
        else:
            logger.info(f"Import successful. Data imported from {final_file_path}.")
            _write_lock(lock_file, "success", started_at=started_at, finished_at=finished_at)
    except Exception:
        _write_lock(lock_file, "failed", started_at=started_at, finished_at=datetime.now(timezone.utc).isoformat())
        raise

    finally:
        logger.removeHandler(file_handler)
        file_handler.close()
        cleanup_files(log_dir, "s3_manager")


if __name__ == "__main__":
    manage_s3_files()
