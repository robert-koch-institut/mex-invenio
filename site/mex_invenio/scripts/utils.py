""" Utility functions for the MEx-Invenio data import and handling. """
import filecmp
import json
import os
import shutil
from datetime import datetime
from typing import Union, Any

from flask import current_app

def _get_value_by_lang(mex_data: dict, key: str, lang: str) -> str:
    """Get the value of a key in the MEx metadata by language."""
    if isinstance(mex_data[key], str):
        return mex_data[key]

    if isinstance(mex_data[key][0], str):
        return mex_data[key][0]

    if [t for t in mex_data[key] if 'language' in t and t['language'] == lang]:
        return [t for t in mex_data[key] if 'language' in t and t['language'] == lang][0]['value']

    return mex_data[key][0]['value']


def get_title(mex_data: dict) -> str:
    """Get the title of the record from the MEx metadata."""
    for key in current_app.config.get('RECORD_METADATA_TITLE_PROPERTIES', ''):
        if key in mex_data and len(mex_data[key]) > 0:
            return _get_value_by_lang(mex_data, key, 'de')

    return current_app.config.get('RECORD_METADATA_DEFAULT_TITLE', '')


def mex_to_invenio_schema(mex_data: dict) -> dict:
    """Convert MEx schema metadata to internal Invenio RDM Record schema."""
    # Remove the 'Merged' prefix from the entityType in order to be able to process test data
    resource_type = mex_data.pop("entityType").removeprefix('Merged').lower()

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
            "creators": [current_app.config.get('RECORD_METADATA_CREATOR', '')],
            "publication_date": datetime.today().strftime('%Y-%m-%d'),
            "title": get_title(mex_data),
        },
        "custom_fields": {}
    }

    for k in mex_data:
        data['custom_fields'][f'mex:{k}'] = mex_data[k]

    return data

def compare_dicts(dict1: dict, dict2: dict) -> dict:
    """Compare two dictionaries and return a dictionary with the differences."""
    diff = {}

    # Check for keys in dict1 that are not in dict2
    for key in dict1:
        if key not in dict2:
            diff[key] = {'dict1': dict1[key], 'dict2': None}
        elif dict1[key] != dict2[key]:
            diff[key] = {'dict1': dict1[key], 'dict2': dict2[key]}

    # Check for keys in dict2 that are not in dict1
    for key in dict2:
        if key not in dict1:
            diff[key] = {'dict1': None, 'dict2': dict2[key]}

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
    if os.path.exists(existing_file) and filecmp.cmp(existing_file, new_file, shallow=False):
        os.remove(new_file)  # Remove duplicate file
        return True
    return False


def get_pref_labels():
    """Read and write pref labels from JSON files in the vocabularies directory to a template accessible file."""
    pref_labels = {}
    template_dir = 'templates/semantic-ui/invenio_app_rdm/records/macros'
    vocab_dir = 'site/mex_invenio/custom_fields/mex-model/mex/model/vocabularies'
    existing_pref_labels = f'{template_dir}/pref_labels.jinja'
    new_pref_labels = f'{template_dir}/new_pref_labels.jinja'

    if not os.path.isdir(vocab_dir):
        return

    for vocab in os.listdir(vocab_dir):
        with open(f'{vocab_dir}/{vocab}') as vocab_file:
            prefs = json.load(vocab_file)
            for pref in prefs:
                identifier = pref.get('identifier')
                pref_label = pref.get('prefLabel')
                description = pref.get('description')

                if description:
                    # Concept-schemes.json contains a description of each concept
                    # it is metadata and not a prefLabel
                    pref.pop('identifier')
                    pref_labels[identifier] = pref

                else:
                    pref_labels[identifier] = pref_label

    with open(new_pref_labels, 'w', encoding='utf-8') as template_file:
        template_file.write("{% set pref_labels = ")
        template_file.write(json.dumps(pref_labels, indent=4))
        template_file.write(" %}")

    if not compare_files(existing_pref_labels, new_pref_labels):
        shutil.move(new_pref_labels, existing_pref_labels)
