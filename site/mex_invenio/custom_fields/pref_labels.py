from mex.model import VOCABULARY_JSON_BY_NAME


def get_pref_labels() -> dict:
    """Get pref labels from Mex model package."""
    pref_labels = {}

    # Use the pre-loaded vocabulary data from mex-model package
    for vocabulary_name, vocabularies in VOCABULARY_JSON_BY_NAME.items():
        try:
            for vocabulary in vocabularies:
                identifier = vocabulary.get("identifier")
                pref_label = vocabulary.get("prefLabel")
                if identifier and pref_label:
                    pref_labels[identifier] = pref_label
        except Exception as e:
            print(f"Error processing vocabulary {vocabulary_name}: {e}")

    return pref_labels
