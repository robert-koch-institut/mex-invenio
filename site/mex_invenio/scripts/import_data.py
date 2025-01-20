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
import time
from datetime import datetime
import click
from flask import current_app
from flask.cli import with_appcontext
from invenio_rdm_records.fixtures.tasks import get_authenticated_identity
from invenio_rdm_records.proxies import current_rdm_records_service
from mex_invenio.config import RECORD_METADATA_CREATOR
from multiprocessing import Pool

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

def process_record(mex_data: dict, owner_email: str):
    """Function to create and publish a single record."""
    app = current_app._get_current_object()  # Get the actual Flask app object
    with app.app_context():  # Manually push application context in each process
        user_datastore = current_app.extensions["security"].datastore
        owner = user_datastore.find_user(email=owner_email)

        if not owner:
            raise ValueError(f"User with email {owner_email} not found.")

        identity = get_authenticated_identity(owner.id)
        data = mex_to_invenio_schema(mex_data)
        
        # Create draft record and publish
        draft = current_rdm_records_service.create(data=data, identity=identity)
        published = current_rdm_records_service.publish(id_=draft.id, identity=identity)
        
    return published.id

@click.command("import_data")
@click.argument("email")
@click.argument("filepath")
@click.option("--batch-size", default=1000, help="Number of records to process in parallel.")
@with_appcontext
def import_data(email: str, filepath: str, batch_size: int):
    """Main function to import data."""
    if not os.path.isfile(filepath):
        click.secho(f"File {filepath} not found.")
        sys.exit(1)

    with open(filepath) as f:
        lines = f.readlines()
        total_lines = len(lines)

    # Start the timer to measure processing time
    start_time = time.time()

    # Use multiprocessing Pool to parallelize the process
    with Pool(processes=10) as pool:  # Use 10 processes for parallelism
        futures = []
        num_lines = 0
        # Process in batches to avoid creating too many futures at once
        for i in range(0, total_lines, batch_size):
            batch = lines[i:i + batch_size]
            for line in batch:
                try:
                    mex_data = json.loads(line)
                except json.JSONDecodeError:
                    click.secho(f"Error decoding JSON from line: {i + 1}")
                    sys.exit(1)
                
                futures.append(pool.apply_async(process_record, (mex_data, email)))
            
            # Collect the results as they complete
            for future in futures:
                try:
                    published_id = future.get()  # get the result from the process
                    click.secho(f"Published record with id {published_id}.")
                    num_lines += 1
                except Exception as e:
                    click.secho(f"Error processing record: {str(e)}", fg="red")
        
        # End the timer after processing is done
        end_time = time.time()

    # Calculate the total time taken and print the results
    elapsed_time = end_time - start_time
    click.secho(f"Published {num_lines} records.", fg="green")
    click.secho(f"Total time taken: {elapsed_time:.2f} seconds.", fg="green")


if __name__ == "__main__":
    import_data()
