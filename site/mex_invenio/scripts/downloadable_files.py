"""Helpers for listing the CSVs mirrored from the bucket's
'downloadable files-<version>' prefix (synced by s3_manager.py), for
the /downloads page.
"""

import os

from flask import current_app

from mex_invenio.scripts.utils import read_json_file


def list_downloadable_files() -> list[dict]:
    """List the currently-mirrored downloadable CSVs.

    Returns [] if DOWNLOADABLE_FILES_DIR isn't configured or doesn't exist
    yet (e.g. local dev, or before the first nightly sync has run).
    """
    downloadable_files_dir = current_app.config.get("DOWNLOADABLE_FILES_DIR")
    if not downloadable_files_dir or not os.path.isdir(downloadable_files_dir):
        return []

    entries = []
    for filename in sorted(os.listdir(downloadable_files_dir)):
        if not filename.endswith(".csv"):
            continue

        path = os.path.join(downloadable_files_dir, filename)
        entry = {
            "filename": filename,
            "size": os.path.getsize(path),
            "url": f"/downloadable-files/{filename}",
            "generated_at": None,
        }

        # e.g. "Publikationen_Abt.1.csv" -> suffix "Abt.1" -> "metadata_Abt.1.json"
        suffix = filename.rpartition("_")[2].removesuffix(".csv")
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
