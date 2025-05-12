import json
import os


def get_pref_labels() -> dict:
    """Read and write pref labels from JSON files in the
     vocabularies directory to a template accessible file."""

    pref_labels = {}
    vocab_dir = 'site/mex_invenio/custom_fields/mex-model/mex/model/vocabularies'

    if not os.path.isdir(vocab_dir):
        return pref_labels

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

    return pref_labels
