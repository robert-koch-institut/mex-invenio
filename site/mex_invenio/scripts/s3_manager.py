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

import click
import boto3
import logging
import os
import filecmp
from dotenv import load_dotenv
from mex_invenio.scripts.import_data import import_data
from datetime import datetime, timezone
import subprocess

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
    config = {}
    file_found = load_dotenv()

    if file_found:
        config = {
            "bucket": os.getenv("bucket"),
            "aws_access_key": os.getenv("aws_access_key"),
            "aws_secret_key": os.getenv("aws_secret_key"),
            "region": os.getenv("region", "eu-central-1"),
            "email": os.getenv("email"),
        }

    return config


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
        return None


def download_file(s3_client, bucket_name, file_key, payload_folder):
    try:
        os.makedirs(payload_folder, exist_ok=True)
        local_filename = os.path.join(payload_folder, os.path.basename(file_key))
        s3_client.download_file(bucket_name, file_key, local_filename)
        return local_filename
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        return None


def get_latest_existing_file(payload_folder):
    """Fetches the most recent file in the payload folder."""
    files = sorted(
        [os.path.join(payload_folder, f) for f in os.listdir(payload_folder) if
         os.path.isfile(os.path.join(payload_folder, f))],
        key=os.path.getmtime,  # Sort by last modified time
    )

    return files[-1] if files else None


def check_last_download(existing_file, new_file):
    """Compares files and deletes the new file if it's the same."""
    if existing_file and os.path.exists(existing_file) and filecmp.cmp(existing_file, new_file, shallow=False):
        logger.info("No new content found. File is exactly the same as before.")
        os.remove(new_file)  # Remove duplicate file
        return True
    return False


def rename_and_keep_latest_file(existing_file, new_file, payload_folder, check_comparison):
    """Handles file retention based on checkLastDownload flag."""
    if check_comparison == "yes" and check_last_download(existing_file, new_file):
        return None  # New file is identical, so discard it

    # Generate a timestamped filename to avoid overwriting
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    new_filename = f"{timestamp}_{os.path.basename(new_file)}"
    final_new_file_path = os.path.join(payload_folder, new_filename)

    os.rename(new_file, final_new_file_path)  # Rename new file

    # Always replace old file if checkLastDownload == "no"
    if existing_file:
        os.remove(existing_file)
        logger.info(f"Replaced old file: {existing_file} with new file: {final_new_file_path}")

    return final_new_file_path


@click.command("manage_s3_files")
@click.option("--checkLastDownload", "checkLastDownload", type=click.Choice(["yes", "no"]), default="no")
def manage_s3_files(checkLastDownload: str):
    """Main function to download the latest file from S3, compare, and manage local storage."""

    config = load_config()

    if not config:
        logger.error("Unable to fetch configration, env file is missing")
        exit(1)

    if not all([config["bucket"], config["aws_access_key"], config["aws_secret_key"]]):
        logger.error("Missing required configurations (bucket, aws_access_key, aws_secret_key).")
        exit(1)

    if not config["email"]:
        logger.error("email environment variable is not set.")
        exit(1)

    s3_client = boto3.client(
        "s3",
        region_name=config["region"],
        aws_access_key_id=config["aws_access_key"],
        aws_secret_access_key=config["aws_secret_key"],
    )

    latest_file_key = get_latest_file(s3_client, config["bucket"])
    if not latest_file_key:
        return

    payload_folder = "payload"
    os.makedirs(payload_folder, exist_ok=True)

    existing_file_path = get_latest_existing_file(payload_folder)
    new_file_path = download_file(s3_client, config["bucket"], latest_file_key, payload_folder)

    if new_file_path:
        final_file_path = rename_and_keep_latest_file(existing_file_path, new_file_path, payload_folder,
                                                      checkLastDownload)
        if final_file_path:
            logger.info(f"importing data using file ${final_file_path}")

            # Absolute path to import_data.py
            script_path = os.path.join(os.path.dirname(__file__), "import_data.py")

            # Command to execute
            command = ["pipenv", "run", "invenio", "shell", script_path, config["email"], final_file_path]
            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode != 0:  # Use returncode instead of exit_code
                logger.error(f"Error in import_data: {result.stderr}")  # Use stderr for errors
            else:
                logger.info(f"Import successful: {result.stdout}")  # stdout for success messages


if __name__ == "__main__":
    manage_s3_files()
