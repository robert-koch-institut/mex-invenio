"""Utility functions for the MEx-Invenio data import and handling."""

import filecmp
import hashlib
import html
import importlib.metadata
import json
import logging
import os
from collections.abc import Callable
from datetime import datetime

from invenio_db import db
from invenio_rdm_records.records.api import RDMRecord
from marshmallow_utils.html import sanitize_unicode
from mex.model import ENTITY_JSON_BY_NAME
from sqlalchemy import or_, text

logging.basicConfig(
    level=logging.INFO,
    # format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
    # datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def _get_value_by_lang(
    config, mex_data: dict, key: str, lang: str, val_filter: Callable
):
    """Get the value of a key in the MEx metadata by language."""
    if isinstance(mex_data[key], str) and (
        val_filter is None or val_filter(mex_data[key])
    ):
        return mex_data[key]

    if isinstance(mex_data[key], list):
        for item in mex_data[key]:
            if (
                isinstance(item, str)
                and item
                and (val_filter is None or val_filter(item))
            ):
                return item

    values_by_lang = [
        t for t in mex_data[key] if "language" in t and t["language"] == lang
    ]

    if values_by_lang:
        for item in values_by_lang:
            if (
                isinstance(item["value"], str)
                and item["value"]
                and (val_filter is None or val_filter(item["value"]))
            ):
                return item["value"]

    if val_filter is None or val_filter(mex_data[key][0]["value"]):
        return mex_data[key][0]["value"]

    return config.get("RECORD_METADATA_DEFAULT_TITLE", "")


def get_title(config, mex_data: dict) -> str:
    """Get the title of the record from the MEx metadata."""
    for key in config.get("RECORD_METADATA_TITLE_PROPERTIES", ""):
        if key in mex_data and len(mex_data[key]) > 0:
            try:
                return _get_value_by_lang(
                    config, mex_data, key, "de", lambda x: len(x) > 2
                )
            except TypeError:
                continue

    return config.get("RECORD_METADATA_DEFAULT_TITLE", "")


def mex_to_invenio_schema(config, mex_data: dict) -> dict:
    """Convert MEx schema metadata to internal Invenio RDM Record schema."""
    # Remove the 'Merged' prefix from the entityType in order to be able to process test data
    resource_type = mex_data.pop("entityType").removeprefix("Merged").lower()

    data = {
        "access": {
            "record": "public",
            "files": "public",
        },
        "files": {
            "enabled": False,
        },
        "pids": {},
        "metadata": {
            "resource_type": {"id": resource_type},
            "creators": [config.get("RECORD_METADATA_CREATOR", "")],
            "publication_date": datetime.today().strftime("%Y-%m-%d"),
            "title": get_title(config, mex_data),
        },
        "custom_fields": {},
    }

    for k in mex_data:
        data["custom_fields"][f"mex:{k}"] = mex_data[k]

    return data


def normalize_record_data(value):
    """Normalize a record data for comparison by handling type coercion and whitespace."""
    if isinstance(value, str):
        # convert HTML entities to unicode characters
        unescaped = html.unescape(value)

        # This is the same sanitation function used in Invenio RDM Records
        # to ensure consistent handling of unicode and whitespace.
        # It removes leading/trailing whitespace, normalizes unicode characters and
        # removes zero-width space "\u200b".
        return sanitize_unicode(unescaped)
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        return [
            normalize_record_data(item)
            for item in value
            if item is not None and item != []
        ]

    if isinstance(value, dict):
        return {
            k: normalize_record_data(v)
            for k, v in value.items()
            if v is not None and v != []
        }
    return value


def compare_files(existing_file: str, new_file: str) -> bool:
    """Compares files and deletes the new file if it's the same."""
    if os.path.exists(existing_file) and filecmp.cmp(
        existing_file, new_file, shallow=False
    ):
        os.remove(new_file)  # Remove duplicate file
        return True
    return False


def cleanup_files(directory: str, keep: int = 20):
    """Remove old files, keeping only the most recent ones."""
    try:
        files = sorted(
            [
                os.path.join(directory, f)
                for f in os.listdir(directory)
                if os.path.isfile(os.path.join(directory, f))
            ],
            key=os.path.getmtime,
            reverse=True,
        )
        for f in files[keep:]:
            try:
                os.remove(f)
                logger.info(f"Removed old file: {f}")
            except OSError as e:
                logger.warning(f"Could not remove old file {f}: {e}")
    except FileNotFoundError:
        pass


def diff_files(directory: str, existing_file: str, new_file: str):
    """Create a diff file containing only new or changed records based on identifier comparison.

    Optimized for large files by using streaming and hash-based comparison.
    """
    diffdirectory = os.path.join(directory, "diffs")
    os.makedirs(diffdirectory, exist_ok=True)

    timestamp = datetime.today().strftime("%d-%m-%Y_%I_%M_%S")
    mex_model_version = importlib.metadata.version("mex-model")
    existing_basename = os.path.basename(existing_file).removesuffix(".ndjson")
    new_basename = os.path.basename(new_file).removesuffix(".ndjson")
    diff_file = os.path.join(
        diffdirectory,
        f"{existing_basename}-{new_basename}-{mex_model_version}_{timestamp}.ndjson",
    )

    try:
        # Read existing records and create hash index (memory efficient)
        existing_hashes = {}  # identifier -> content_hash
        existing_count = 0

        logger.info(f"Reading existing file: {existing_file}")
        if os.path.exists(existing_file):
            with open(existing_file, encoding="utf-8") as f:
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
                            f"Invalid JSON at line {line_num} in {existing_file}: {e}"
                        )

                    # Log progress for large files
                    if line_num % 10000 == 0:
                        logger.info(f"Processed {line_num} lines from existing file")

        logger.info(f"Indexed {existing_count} existing records")

        # Stream process new file and write diff directly
        new_or_changed_count = 0
        processed_count = 0

        logger.info(f"Processing new file: {new_file}")
        with (
            open(new_file, encoding="utf-8") as infile,
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
                            f"Record without identifier at line {line_num} in {new_file}"
                        )

                except json.JSONDecodeError as e:
                    logger.warning(
                        f"Invalid JSON at line {line_num} in {new_file}: {e}"
                    )

                # Log progress for large files
                if line_num % 10000 == 0:
                    logger.info(
                        f"Processed {line_num} lines, found {new_or_changed_count} changes"
                    )

        logger.info(
            f"Comparison complete: {new_or_changed_count} new/changed records out of {processed_count} total"
        )
        logger.info(f"Created diff file: {diff_file}")
        cleanup_files(diffdirectory)
        return diff_file

    except Exception as e:
        logger.error(f"Error during JSON-based file comparison: {e}")

        return None


def get_related_mex_ids(record: dict) -> list:
    """Get UUIDs of MEX records that reference this record's identifier in their custom fields."""
    record_id = record.get("custom_fields", {}).get("mex:identifier")

    if not record_id:
        return []

    mapping = {
        "organizationalunit": "organizational-unit",
        "contactpoint": "contact-point",
        "accessplatform": "access-platform",
        "bibliographicresource": "bibliographic-resource",
        "variablegroup": "variable-group",
        "primarysource": "primary-source",
    }

    record_type = record.get("metadata", {}).get("resource_type", {}).get("id", "")

    if record_type in mapping:
        record_type = mapping[record_type]

    target_id = f"/schema/entities/{record_type}#/identifier"

    # Find fields that reference this record type
    target_fields = []
    for entity in ENTITY_JSON_BY_NAME.values():
        for prop_name, prop in entity.get("properties", {}).items():
            if prop.get("$ref") == target_id:
                target_fields.append(prop_name)
            elif prop.get("type") == "array" and "items" in prop:
                if prop["items"].get("$ref") == target_id:
                    target_fields.append(prop_name)
                elif "anyOf" in prop["items"]:
                    for sub_prop in prop["items"]["anyOf"]:
                        if sub_prop.get("$ref") == target_id:
                            target_fields.append(prop_name)
                            break

    if not target_fields:
        return []

    try:
        # Build OR conditions for each target field
        conditions = []
        for field in target_fields:
            # Check if record_id is in the field (handles both string and array values)
            conditions.append(
                text(
                    f"rdm_records_metadata.json->'custom_fields'->'mex:{field}' ? :record_id_{field}"
                )
            )
            # Also check if it's a direct string match
            conditions.append(
                text(
                    f"rdm_records_metadata.json->'custom_fields'->>'mex:{field}' = :record_id_str_{field}"
                )
            )

        # Build parameters dict
        params = {}
        for field in target_fields:
            params[f"record_id_{field}"] = record_id
            params[f"record_id_str_{field}"] = record_id

        # Query database for records that reference this record_id
        record_uuids = (
            db.session.query(RDMRecord.model_cls.id)
            .filter(or_(*conditions))
            .params(**params)
            .all()
        )

        return [str(uuid) for (uuid,) in record_uuids]

    except Exception as e:
        logger.info(f"Error searching for related MEX IDs for {record_id}: {e}")
        return []
