"""Script to upload realistic test datasets for the MEx Invenio repository.

Make sure you've started the Invenio services have been set up and are running.

Does the following:

- Finds the file provided as CLI argument.
- Reads in the metadata in MEx json format.
- Finds a user to own the record.
- Creates a draft record by converting the MEx metadata to the repository schema.
- Publishes the record.
"""

import json
import os.path
import sys
from datetime import datetime

import click
from flask import current_app
from flask.cli import with_appcontext
from invenio_rdm_records.fixtures.tasks import get_authenticated_identity
from invenio_rdm_records.proxies import current_rdm_records_service

from mex_invenio.config import RECORD_METADATA_CREATOR


def mex_to_invenio_schema(mex_data: dict) -> dict:
    """Convert MEx schema metadata to internal Invenio RDM Record schema."""
    resource_type = mex_data.pop("entityType").removeprefix('Merged').lower()
    identifier = mex_data['identifier']

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
            "creators": [RECORD_METADATA_CREATOR],
            "publication_date": datetime.today().strftime('%Y-%m-%d'),
            "title": f'{resource_type}_{identifier}'
        },
        "custom_fields": {}
    }

    for k in mex_data:
        data['custom_fields'][f'mex:{k}'] = mex_data[k]

    return data


@click.command("import_data")
@click.argument("email")
@click.argument("filepath")
@with_appcontext
def import_data(email: str, filepath: str):
    """Main function to import data."""
    user_datastore = current_app.extensions["security"].datastore
    owner = user_datastore.find_user(email=email)

    if not owner:
        click.secho(f"User with email {email} not found.")
        sys.exit(1)
    elif not os.path.isfile(filepath):
        click.secho(f"File {filepath} not found.")
        sys.exit(1)

    with open(filepath) as f:
        num_lines = 0

        for line in f:
            mex_data = json.loads(line)
            identity = get_authenticated_identity(owner.id)
            data = mex_to_invenio_schema(mex_data)
            draft = current_rdm_records_service.create(data=data, identity=identity)
            published = current_rdm_records_service.publish(id_=draft.id, identity=identity)
            num_lines += 1

        if num_lines == 1:
            click.secho(f"Published record with id {published.id}.")  # noqa: T001
        else:
            click.secho(f"Published {num_lines} records.")


if __name__ == "__main__":
    import_data()

