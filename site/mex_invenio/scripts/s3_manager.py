"""
This script fetches the latest file from an S3 store and uploads it to the server.

### How to Run  
To execute the script, run:  
pipenv run invenio shell site/mex_invenio/scripts/s3_manager.py  

### Parameters  
The script requires two parameters:  
1. **File Path**  This specifies the file containing your S3 credentials.  
2. **checkLastDownload** This flag compares the latest downloaded file with the previous one to determine whether an upload is necessary.  

### Requirements  
Before running the script, ensure you have the following:  
- **S3 Credentials**, which should include:  
  - `bucket`  
  - `aws_access_key`  
  - `aws_secret_key`  
  - `region`  

You can store these credentials in a custom file, a `.env` file, or preferably inside `.aws/config` under the `[DEFAULT]` profile for 
better security.  

**Note:** We strongly recommend storing your credentials in `.aws/config` with the `[DEFAULT]` header to keep them secure and organized.  
"""



import boto3
import logging
import argparse
import os
import filecmp
import configparser
from dotenv import load_dotenv
import import_data
from datetime import datetime
from click.testing import CliRunner

# Configure logging
log_file_path = 's3_manager.log'
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - (line: %(lineno)d) - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def load_config(config_path=None):
    config = {}
    
    if config_path and os.path.exists(config_path):
        parser = configparser.ConfigParser()
        parser.read(config_path)
    
        config = {
            "bucket": parser.get("DEFAULT", "bucket", fallback=None),
            "aws_access_key": parser.get("DEFAULT", "aws_access_key", fallback=None),
            "aws_secret_key": parser.get("DEFAULT", "aws_secret_key", fallback=None),
            "region": parser.get("DEFAULT", "region", fallback="eu-central-1")
        }
    else:
        load_dotenv()
        config = {
            "bucket": os.getenv("bucket"),
            "aws_access_key": os.getenv("aws_access_key"),
            "aws_secret_key": os.getenv("aws_secret_key"),
            "region": os.getenv("region", "eu-central-1")
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
    if not os.path.exists(payload_folder):
        os.makedirs(payload_folder)
        return None
    
    files = sorted(
        [os.path.join(payload_folder, f) for f in os.listdir(payload_folder) if os.path.isfile(os.path.join(payload_folder, f))],
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
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    new_filename = f"{timestamp}_{os.path.basename(new_file)}"
    final_new_file_path = os.path.join(payload_folder, new_filename)
    
    os.rename(new_file, final_new_file_path)  # Rename new file

    # Always replace old file if checkLastDownload == "no"
    if existing_file:
        os.remove(existing_file)
        logger.info(f"Replaced old file: {existing_file} with new file: {final_new_file_path}")

    return final_new_file_path

def manage_s3_files():
    """Main function to download the latest file from S3, compare, and manage local storage."""
    parser = argparse.ArgumentParser(
        description="Download the latest file from an S3 bucket and process it.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("config", help="Path to config file", nargs="?", default=None)
    parser.add_argument("checkLastDownload", choices=["yes", "no"], nargs="?", default="yes",
                        help="Check if the latest file is different before replacing (default: yes)")

    args = parser.parse_args()
    
    config = load_config(args.config) if args.config else load_config()
    
    if not all([config["bucket"], config["aws_access_key"], config["aws_secret_key"]]):
        logger.error("Missing required configurations (bucket, aws_access_key, aws_secret_key).")
        return
    
    email = os.getenv("email")
    if not email:
        logger.error("email environment variable is not set.")
        return
    
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
        final_file_path = rename_and_keep_latest_file(existing_file_path, new_file_path, payload_folder, args.checkLastDownload)
        if final_file_path:
            logger.info(f"importing data using file ${final_file_path}")
            
            runner = CliRunner()
            result = runner.invoke(import_data.import_data, [email, final_file_path])

            if result.exit_code != 0:
                logger.error(f"Error in import_data: {result.output}")

if __name__ == "__main__":
    manage_s3_files()
