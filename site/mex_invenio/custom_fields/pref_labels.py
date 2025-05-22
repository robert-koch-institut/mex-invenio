from importlib import resources
import os
import json


def get_pref_labels() -> dict:
    """Get pref labels from Mex model package."""

    vocabularies_directory = resources.files("mex").joinpath("model/vocabularies")

    if not os.path.isdir(vocabularies_directory):
        return {}

    pref_labels = {}

    for vocabulary_filename in os.listdir(vocabularies_directory):
        try:
            with open(f"{vocabularies_directory}/{vocabulary_filename}", "r") as f:
                vocabularies = json.load(f)

                for vocabulary in vocabularies:
                    identifier = vocabulary.get("identifier")
                    pref_label = vocabulary.get("prefLabel")
                    pref_labels[identifier] = pref_label
        except Exception as e:
            print(e)

    return pref_labels
