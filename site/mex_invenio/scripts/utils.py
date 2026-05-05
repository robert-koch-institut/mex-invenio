"""Utility functions for the MEx-Invenio data import and handling."""

import html
import json
import logging
import os
import re
import time
from collections.abc import Callable
from datetime import datetime, timezone

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


def get_timestamp():
    return datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")

def read_json_file(file_path):
    with open(file_path, "r") as f:
        metadata = json.load(f)
        model_version = metadata['versions']['mex-model']

        # omit patch version if present
        if len(model_version.split('.')) > 2:
            model_version = '.'.join(model_version.split('.')[:2])

        checksum = metadata['sha256_checksum']
        timestamp = metadata['write_completed_at']

        return model_version, checksum, timestamp

def write_json_file(file_path, json_data):
    with open(file_path, "w") as f:
        json.dump(json_data, f)


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


def cleanup_files(directory: str, prefix: str | None = None, keep: int = 20):
    """Remove old files, keeping only the most recent ones."""
    try:
        if prefix:
            files = [
                os.path.join(directory, f)
                for f in os.listdir(directory)
                if os.path.isfile(os.path.join(directory, f)) and f.startswith(prefix)
            ]
        else:
            files = [
                os.path.join(directory, f)
                for f in os.listdir(directory)
                if os.path.isfile(os.path.join(directory, f))
            ]

        files = sorted(
            files,
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

    target_id = f"/mex/model/entities/merged-{record_type}#/identifier"

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


def setup_file_logging(log_dir, name="import"):
    """Add a timestamped file handler to the given logger."""
    os.makedirs(log_dir, exist_ok=True)
    date_str = time.strftime("%Y%m%d")
    handler = logging.FileHandler(os.path.join(log_dir, f"{name}-{date_str}.log"))
    handler.setLevel(logging.INFO)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    return handler


def _read_state(state_file: str) -> dict | None:
    """Read the import state file, returning its contents or None if absent/corrupt."""
    try:
        with open(state_file) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def get_subdir_by_order(root: str, most_recent: bool = True) -> str | None:
    latest = None

    if most_recent:
        condition = lambda name: name > latest[1]
    else:
        condition = lambda name: name < latest[1]

    for dirpath, dirnames, _ in os.walk(root):
        for name in dirnames:
            if re.match(r'^\d+$', name) and (latest is None or condition(name)):
                latest = (os.path.join(dirpath, name), name)

    return latest[0] if latest else None

def _write_state(
    state_file: str,
    status: str,
    started_at: str | None = None,
    finished_at: str | None = None,
):
    """Write the import state file with the given status and timestamps."""
    data = {"status": status}
    if started_at:
        data["started_at"] = started_at
    if finished_at:
        data["finished_at"] = finished_at
    with open(state_file, "w") as f:
        json.dump(data, f)
