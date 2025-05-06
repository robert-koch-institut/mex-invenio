import json
import os
import shutil

import click

from mex_invenio.scripts.utils import compare_files


def get_pref_labels():
    """Read and write pref labels from JSON files in the
    vocabularies directory to a template accessible file."""

    pref_labels = {}
    template_dir = "templates/semantic-ui/invenio_app_rdm/records/macros"
    vocab_dir = "site/mex_invenio/custom_fields/mex-model/mex/model/vocabularies"
    existing_pref_labels = f"{template_dir}/pref_labels.jinja"
    new_pref_labels = f"{template_dir}/new_pref_labels.jinja"

    if not os.path.isdir(vocab_dir):
        return

    for vocab in os.listdir(vocab_dir):
        with open(f"{vocab_dir}/{vocab}") as vocab_file:
            prefs = json.load(vocab_file)
            for pref in prefs:
                identifier = pref.get("identifier")
                pref_label = pref.get("prefLabel")
                description = pref.get("description")

                if description:
                    # Concept-schemes.json contains a description of each concept
                    # it is metadata and not a prefLabel
                    pref.pop("identifier")
                    pref_labels[identifier] = pref

                else:
                    pref_labels[identifier] = pref_label

    with open(new_pref_labels, "w", encoding="utf-8") as template_file:
        template_file.write("{% set pref_labels = ")
        template_file.write(json.dumps(pref_labels, indent=4))
        template_file.write(" %}")

    if not compare_files(existing_pref_labels, new_pref_labels):
        shutil.move(new_pref_labels, existing_pref_labels)


@click.command("pref_labels")
def _pref_labels():
    get_pref_labels()


if __name__ == "__main__":
    _pref_labels()
