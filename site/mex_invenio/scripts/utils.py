"""Utility functions for the MEx-Invenio data import and handling."""

import filecmp
import html
import logging
import os
from datetime import datetime
from typing import Callable

from marshmallow_utils.html import sanitize_unicode


logging.basicConfig(
    level=logging.INFO,
    #format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
    #datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def _get_value_by_lang(config, mex_data: dict, key: str, lang: str, val_filter: Callable):
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
                return _get_value_by_lang(config, mex_data, key, "de", lambda x: len(x) > 2)
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
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, list):
        normalized_items = [
            normalize_record_data(item)
            for item in value
            if item is not None and item != []
        ]

        return normalized_items
    elif isinstance(value, dict):
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


def get_related_mex_ids(config, record: dict) -> list:
    """Get related MEx identifiers from the record's custom fields."""
    field_types = config.get("FIELD_TYPES", [])
    record_type = record.get("metadata", {}).get("resource_type", {}).get("id", "")
    related_ids = set()

    related_fields = [k for k,v in field_types.get(record_type, {}).items() if v == "identifier"]

    print('HERE', related_fields)

    for field in related_fields:
        #mex_field = f"mex:{field}"
        if field in record.get("custom_fields", {}):
            field_value = record["custom_fields"][field]
            if isinstance(field_value, list):
                for item in field_value:
                    related_ids.add(str(item))
            else:
                related_ids.add(str(field_value))

    print('----------------------')
    print(record)
    print(related_ids)
    print('----------------------')

    return list(related_ids)