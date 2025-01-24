"""Script to upload realistic test datasets for the MEx Invenio repository.

Make sure the Invenio services have been set up and are running.

Does the following:

- Finds the file provided as CLI argument.
- Reads in the metadata in MEx json format.
- Finds a user to own the record.
- Creates a draft record by converting the MEx metadata to the repository schema.
- Publishes the record.

To run the script, go to the repository root directory and use the following command:

        $ pipenv run invenio shell site/mex_invenio/scripts/import_data.py <email> <filepath>
"""

import json
import logging
import os.path
import sys
import time
from datetime import datetime
import click
from flask import current_app
from invenio_app.factory import create_app
from invenio_rdm_records.fixtures.tasks import get_authenticated_identity
from invenio_rdm_records.proxies import current_rdm_records_service
from mex_invenio.config import RECORD_METADATA_CREATOR
from multiprocessing import Pool, cpu_count

# Configure logging
log_file_path = 'import_data.log'
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - (line: %(lineno)d) - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def mex_to_invenio_schema(mex_data: dict) -> dict:
    """Convert MEx schema metadata to internal Invenio RDM Record schema."""
    # Remove the 'Merged' prefix from the entityType in order to be able to process test data
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


def process_record(mex_data: dict, owner_id: int) -> str:
    """Function to create and publish a single record."""
    app = current_app._get_current_object()  # Get the actual Flask app object
    with app.app_context():  # Manually push application context in each process
        identity = get_authenticated_identity(owner_id)

        try: # Create draft record and publish
            draft = current_rdm_records_service.create(data=mex_data, identity=identity)
            published = current_rdm_records_service.publish(id_=draft.id, identity=identity)

            return published.id
        except Exception as e:
            logger.error(f"Error processing record: {str(e)}")


@click.command("import_data")
@click.argument("email")
@click.argument("filepath")
@click.option("--batch-size", default=10 * 1024 * 1024, help="Number of records to process in parallel.")
def import_data(email: str, filepath: str, batch_size: int):
    """Main function to import data.
       Batch size is set to 10mb by default.
       Expected data source is a JSON file with one MEx record per line.
       About 50k records, or ~100mb."""
    if not os.path.isfile(filepath):
        click.secho(f"File {filepath} not found.", fg="red")
        sys.exit(1)

    # Here we need to manually create an application context, it is not
    # possible to use the current_app proxy directly in a separate process.
    app = create_app()
    with app.app_context():
        user_datastore = current_app.extensions["security"].datastore
        owner = user_datastore.find_user(email=email)

        if not owner:
            click.secho(f"User with email {email} not found.", fg="red")
            sys.exit(1)

    # Start the timer to measure processing time
    start_time = time.time()
    num_lines = 0
    record_ids = set()

    # Batch read the file to avoid memory issues
    with open(filepath) as f:
        while True:
            futures = []
            lines = f.readlines(batch_size)
            num_lines += len(lines)

            if not lines or lines[0] == '':
                break

            # Use multiprocessing Pool to parallelize the process
            with Pool(processes=cpu_count()) as pool:  # Use all available CPU cores
                # Process in batches to avoid creating too many futures at once
                for line in lines:
                    try:
                        mex_data = mex_to_invenio_schema(json.loads(line))
                    except json.JSONDecodeError:
                        # Log and skip the line if it is not valid JSON
                        logger.error(f"Error decoding JSON: {line}")
                        continue
                    except KeyError:
                        # Log and skip the line if it is missing a key
                        logger.error(f"Error processing record: {line}")
                        continue

                    futures.append(pool.apply_async(process_record, (mex_data, owner.id)))

                # Collect the results as they complete
                for future in futures:
                    try:
                        published_id = future.get()  # get the result from the process

                        if published_id is not None:
                            record_ids.add(published_id)
                    except Exception as e:
                        logger.error(f"Error processing record: {str(e)}")

        # End the timer after processing is done
        end_time = time.time()

    # Calculate the total time taken and print the results
    elapsed_time = end_time - start_time
    minutes, seconds = divmod(elapsed_time, 60)
    num_records = len(record_ids)

    logger.info(f"Published {num_records} records. Ids: {record_ids}")

    if minutes:
        time_taken = f"Total time taken: {int(minutes)} minutes and {seconds:.2f} seconds."
    else:
        time_taken = f"Total time taken: {seconds:.2f} seconds."

    logger.info(time_taken)


if __name__ == "__main__":
    import_data()
