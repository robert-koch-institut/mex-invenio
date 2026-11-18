"""Helpers for listing the CSVs mirrored from the bucket's
'downloadable files-<version>' prefix (synced by s3_manager.py), for
the /downloads page.
"""

import json
import os

from flask import current_app

from mex_invenio.scripts.utils import read_json_file

DATAPACKAGE_FILENAME = "datapackage.json"


def list_downloadable_files() -> list[dict]:
    """List the currently-mirrored downloadable CSVs.

    The files, their order and their titles come from the Data Package
    descriptor (datapackage.json).
    """
    downloadable_files_dir = current_app.config.get("DOWNLOADABLE_FILES_DIR")
    if not downloadable_files_dir or not os.path.isdir(downloadable_files_dir):
        return []

    datapackage_path = os.path.join(downloadable_files_dir, DATAPACKAGE_FILENAME)
    try:
        with open(datapackage_path) as f:
            resources = json.load(f)["resources"]
    except Exception:
        current_app.logger.exception(
            f"Failed to read downloadable-files descriptor {datapackage_path}."
        )
        return []

    entries = []
    for resource in resources:
        filename = resource.get("path")

        if not isinstance(filename, str) or os.path.basename(filename) != filename:
            current_app.logger.warning(
                f"Skipping downloadable-files resource with invalid path {filename!r}."
            )
            continue

        path = os.path.join(downloadable_files_dir, filename)
        if not os.path.isfile(path):
            current_app.logger.warning(
                f"Skipping downloadable-files resource {filename}: file not found."
            )
            continue

        entry = {
            "filename": filename,
            "title": resource.get("title") or filename,
            "size": os.path.getsize(path),
            "url": f"/downloadable-files/{filename}",
            "generated_at": None,
        }

        # e.g. "Publikationen_Abt.1.csv" -> suffix "Abt.1" -> "metadata_Abt.1.json"
        suffix = os.path.splitext(filename)[0].rpartition("_")[2]
        metadata_path = os.path.join(downloadable_files_dir, f"metadata_{suffix}.json")

        if os.path.isfile(metadata_path):
            try:
                _, _, entry["generated_at"] = read_json_file(metadata_path)
            except Exception:
                current_app.logger.exception(
                    f"Failed to read downloadable-file metadata {metadata_path}."
                )

        entries.append(entry)

    return entries
