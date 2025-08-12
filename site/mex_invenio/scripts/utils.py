"""Utility functions for the MEx-Invenio data import and handling."""

import filecmp
import html
import os
from datetime import datetime
from typing import Union, Any, Callable

from flask import current_app
from marshmallow_utils.html import sanitize_unicode


def _get_value_by_lang(mex_data: dict, key: str, lang: str, val_filter: Callable):
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

    return current_app.config.get("RECORD_METADATA_DEFAULT_TITLE", "")


def get_title(mex_data: dict) -> str:
    """Get the title of the record from the MEx metadata."""
    for key in current_app.config.get("RECORD_METADATA_TITLE_PROPERTIES", ""):
        if key in mex_data and len(mex_data[key]) > 0:
            try:
                return _get_value_by_lang(mex_data, key, "de", lambda x: len(x) > 2)
            except TypeError:
                continue

    return current_app.config.get("RECORD_METADATA_DEFAULT_TITLE", "")


def mex_to_invenio_schema(mex_data: dict) -> dict:
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
            "creators": [current_app.config.get("RECORD_METADATA_CREATOR", "")],
            "publication_date": datetime.today().strftime("%Y-%m-%d"),
            "title": get_title(mex_data),
        },
        "custom_fields": {},
    }

    for k in mex_data:
        data["custom_fields"][f"mex:{k}"] = mex_data[k]

    return data


def _normalize_value(value):
    """Normalize a value for comparison by handling type coercion and whitespace."""
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
        normalized_items = [_normalize_value(item) for item in value]
        # Sort list items for consistent comparison, handling mixed types
        try:
            return sorted(normalized_items, key=lambda x: (type(x).__name__, str(x)))
        except TypeError:
            # If items can't be sorted (e.g., complex nested structures), keep original order
            return normalized_items
    elif isinstance(value, dict):
        return {k: _normalize_value(v) for k, v in sorted(value.items())}
    return value


def compare_dicts(current_data: dict, new_data: dict) -> dict:
    """Compare two dictionaries and return a dictionary with the differences.

    Handles nested structures, type normalization, and whitespace differences
    to provide accurate comparison for record metadata.
    """
    diff = {}

    # Normalize both dictionaries for comparison
    normalized_current = _normalize_value(current_data)
    normalized_new = _normalize_value(new_data)

    # Check for keys in current_data that are not in new_data
    for key in normalized_current:
        if key not in normalized_new:
            diff[key] = {"current_data": current_data[key], "new_data": None}
        elif normalized_current[key] != normalized_new[key]:
            diff[key] = {"current_data": current_data[key], "new_data": new_data[key]}

    # Check for keys in new_data that are not in current_data
    for key in normalized_new:
        if key not in normalized_current:
            diff[key] = {"current_data": None, "new_data": new_data[key]}

    return diff


def clean_dict(d: dict) -> Union[dict[Any, dict], list[dict], dict]:
    """Recursively remove keys with None or empty list values from a dictionary or list."""
    if isinstance(d, dict):
        return {k: clean_dict(v) for k, v in d.items() if v is not None and v != []}
    elif isinstance(d, list):
        return [clean_dict(item) for item in d if item is not None and item != []]
    else:
        return d


def compare_files(existing_file: str, new_file: str) -> bool:
    """Compares files and deletes the new file if it's the same."""
    if os.path.exists(existing_file) and filecmp.cmp(
        existing_file, new_file, shallow=False
    ):
        os.remove(new_file)  # Remove duplicate file
        return True
    return False
