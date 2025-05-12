from mex.model import VOCABULARY_JSON_BY_NAME
from mex_invenio.scripts.utils import compare_files

def get_pref_labels() -> dict:
    """Read and write pref labels from JSON files in the
    vocabularies directory to a template accessible file."""

    pref_labels = {}

    for vocabulary in VOCABULARY_JSON_BY_NAME:
        for pref in vocabulary:
            identifier = pref.get('identifier')
            pref_label = pref.get('prefLabel')
            pref_labels[identifier] = pref_label

    return pref_labels
