"""Utility functions for the MEx-Invenio data import and handling."""

import filecmp
import os
from datetime import datetime
from typing import Union, Any, Callable

from flask import current_app


def _get_value_by_lang(
    mex_data: dict, key: str, lang: str, val_filter: Callable
) -> str:
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

    return mex_data[key][0]["value"]


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


def compare_dicts(dict1: dict, dict2: dict) -> dict:
    """Compare two dictionaries and return a dictionary with the differences."""
    diff = {}

    # Check for keys in dict1 that are not in dict2
    for key in dict1:
        if key not in dict2:
            diff[key] = {"dict1": dict1[key], "dict2": None}
        elif dict1[key] != dict2[key]:
            diff[key] = {"dict1": dict1[key], "dict2": dict2[key]}

    # Check for keys in dict2 that are not in dict1
    for key in dict2:
        if key not in dict1:
            diff[key] = {"dict1": None, "dict2": dict2[key]}

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
