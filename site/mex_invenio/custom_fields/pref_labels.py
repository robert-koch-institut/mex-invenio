import json
import shutil

import click

from mex.model import VOCABULARY_JSON_BY_NAME
from mex_invenio.scripts.utils import compare_files


def get_pref_labels():
    """Read and write pref labels from JSON files in the
     vocabularies directory to a template accessible file."""

    pref_labels = {}
    template_dir = 'templates/semantic-ui/invenio_app_rdm/records/macros'
    existing_pref_labels = f'{template_dir}/pref_labels.jinja'
    new_pref_labels = f'{template_dir}/new_pref_labels.jinja'

    for vocabulary in VOCABULARY_JSON_BY_NAME:
        for pref in vocabulary:
            identifier = pref.get('identifier')
            pref_label = pref.get('prefLabel')
            pref_labels[identifier] = pref_label

    with open(new_pref_labels, 'w', encoding='utf-8') as template_file:
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
