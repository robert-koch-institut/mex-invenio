"""Script to generate a diff file from the latest downloaded and most recently processed dumps.

### How to Run
To execute the script, run:
pipenv run invenio shell site/mex_invenio/scripts/diff_manager.py <model_version>

### Parameters
**model_version** The model version to generate the diff for.
"""

import hashlib
import json
import logging
import os
import shutil
import sys
from datetime import datetime, timezone

import click
from flask import current_app

from mex_invenio.scripts.utils import (
    get_subdir_by_order,
    get_timestamp,
    normalize_record_data,
    write_json_file,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def compute_diff(downloaded_file: str, processed_file: str, diff_file: str):
    """Create a diff file containing only new or changed records based on identifier comparison.

    Optimized for large files by using streaming and hash-based comparison.
    """

    try:
        existing_hashes = {}
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

                    if line_num % 10000 == 0:
                        logger.info(f"Processed {line_num} lines from existing file")

        logger.info(f"Indexed {existing_count} existing records")

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
                        normalized = normalize_record_data(record)
                        content_hash = hashlib.md5(
                            json.dumps(normalized, sort_keys=True).encode("utf-8")
                        ).hexdigest()

                        existing_hash = existing_hashes.get(record_id)
                        if existing_hash is None or existing_hash != content_hash:
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

                if line_num % 10000 == 0:
                    logger.info(
                        f"Processed {line_num} lines, found {new_or_changed_count} changes"
                    )

        logger.info(
            f"Comparison complete: {new_or_changed_count} new/changed records out of {processed_count} total"
        )

        return {
            "new_or_changed_count": new_or_changed_count,
            "processed_count": processed_count,
        }

    except Exception as e:
        logger.error(f"Error during JSON-based file comparison: {e}")
        return None


def generate_diff(model_version: str) -> str | None:
    """Generate a diff file from the oldest pending download against the most recent processed dump.

    Returns the path to the diff file, or None if no diff was generated.
    """
    s3_download_folder = current_app.config.get("S3_DOWNLOAD_FOLDER", "s3_downloads")
    downloaded_path = os.path.join(s3_download_folder, "downloaded")
    processed_path = os.path.join(s3_download_folder, "processed")
    diff_path = os.path.join(s3_download_folder, "diffs")

    oldest_download_path = get_subdir_by_order(downloaded_path, False)
    most_recent_processed_path = get_subdir_by_order(processed_path)

    if not oldest_download_path:
        logger.warning(f"No pending download found in {downloaded_path}.")
        return None

    if not most_recent_processed_path:
        logger.warning(f"No processed dump found in {processed_path}.")
        return None

    timestamp = get_timestamp()
    diff_folder = os.path.join(diff_path, f"draft-{timestamp}")
    os.makedirs(diff_folder, exist_ok=True)
    processed_file = os.path.join(most_recent_processed_path, "items.ndjson")
    downloaded_file = os.path.join(oldest_download_path, "items.ndjson")
    diff_file = os.path.join(diff_folder, "diff.ndjson")

    diff_result = compute_diff(downloaded_file, processed_file, diff_file)

    if diff_result:
        diff_metadata = {
            "model_version": model_version,
            "processed_file": processed_file,
            "downloaded_file": downloaded_file,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **diff_result,
        }
        write_json_file(os.path.join(diff_folder, "metadata.json"), diff_metadata)

        os.rename(diff_folder, os.path.join(diff_path, timestamp))
        diff_file = os.path.join(diff_path, timestamp, "diff.ndjson")

        rel = os.path.relpath(
            oldest_download_path, downloaded_path
        )  # e.g. "4.10/20260504230150"
        destination = os.path.join(processed_path, rel)
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        shutil.move(oldest_download_path, destination)

        logger.info(f"Diff file created: {diff_file}")

        return diff_file

    return None


@click.command("generate_diff")
@click.argument("model_version")
def _generate_diff(model_version: str):
    """Generate a diff file from the latest downloaded dump."""
    diff_file = generate_diff(model_version)
    if not diff_file:
        click.secho("No diff file created.", fg="red")
        sys.exit(1)
    click.echo(f"Diff file: {diff_file}")


if __name__ == "__main__":
    _generate_diff()
