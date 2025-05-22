"""Script to import data for the MEx Invenio repository.

Make sure the Invenio services have been set up and are running.

Does the following:
- Finds the file provided as CLI argument.
- Finds a user to own the record.
- Reads in the metadata in MEx json format.
- Looks up the record in the repository by the MEx identifier.
- If the record does not exist, creates a new record.
- Else compares the custom fields of the existing record with the new data and creates a new version of the record.

To run the script, go to the repository root directory and use the following command:

        $ pipenv run invenio shell site/mex_invenio/scripts/import_data.py <email> <filepath>
"""

import json
import logging
import os.path
import sys
import time
from typing import Union, Any

import click
from flask import current_app
from invenio_app.factory import create_app
from invenio_rdm_records.fixtures.tasks import get_authenticated_identity
from invenio_rdm_records.proxies import current_rdm_records_service
from multiprocessing import Pool, cpu_count

from mex_invenio.config import IMPORT_LOG_FILE, IMPORT_LOG_FORMAT
from mex_invenio.scripts.utils import compare_dicts, clean_dict, mex_to_invenio_schema

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(IMPORT_LOG_FILE)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter(IMPORT_LOG_FORMAT)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def process_record(
    mex_id: str, mex_data: dict, owner_id: int
) -> Union[None, dict[str, Any]]:
    """Create and publish a single record."""
    app = current_app._get_current_object()  # Get the actual Flask app object
    with app.app_context():  # Manually push application context in each process
        identity = get_authenticated_identity(owner_id)

        try:  # Create draft record and publish
            search_query = f"custom_fields.mex\:identifier:{mex_id}"
            results = list(current_rdm_records_service.search(identity, q=search_query))

            if len(results) == 0:
                # Create a new record
                draft = current_rdm_records_service.create(
                    data=mex_data, identity=identity
                )
                published = current_rdm_records_service.publish(
                    id_=draft.id, identity=identity
                )

                return {"action": "create", "id": published.id}
            elif len(results) == 1:
                # Update an existing record
                record_pid = results[0]["id"]

                # Check if the record needs to be updated, it's sufficient to compare
                # the custom_fields as the Datacite metadata is not expected to change
                metadata_diff = compare_dicts(
                    results[0]["custom_fields"], mex_data["custom_fields"]
                )

                if metadata_diff != {}:
                    new_version = current_rdm_records_service.new_version(
                        id_=record_pid, identity=identity
                    )
                    current_rdm_records_service.update_draft(
                        identity, new_version.id, mex_data
                    )
                    new_record = current_rdm_records_service.publish(
                        identity=identity, id_=new_version.id
                    )

                    return {"action": "update", "id": new_record.id}
                else:
                    return {"action": "skip", "id": record_pid}
            elif len(results) > 1:
                # Log and skip the record if multiple records are found
                logger.error(f"Multiple records found for MEx id: {mex_id}")
                return None

            return None
        except Exception as e:
            logger.error(f"Error processing record: {str(e)}")
            return None


@click.command("import_data")
@click.argument("email")
@click.argument("filepath")
@click.option("--batch-size", default=10 * 1024 * 1024, help="Chunk size to read.")
def _import_data(email: str, filepath: str, batch_size: int):
    return import_data(email, filepath, batch_size, cli=True)


def import_data(
    email: str, filepath: str, batch_size: int = 10 * 1024 * 1024, cli: bool = False
) -> bool:
    """Main function to import data.
    Batch size is set to 10mb by default.
    Expected data source is a JSON file with one MEx record per line.
    About 50k records, or ~100mb."""

    if not os.path.isfile(filepath):
        message = f"File {filepath} not found."

        if cli:
            click.secho(message, fg="red")
            sys.exit(1)
        else:
            logger.error(message)
            return False

    # Here we need to manually create an application context, it is not
    # possible to use the current_app proxy directly in a separate process.
    app = create_app()
    with app.app_context():
        user_datastore = current_app.extensions["security"].datastore
        owner = user_datastore.find_user(email=email)

        if not owner:
            message = f"User with email {email} not found."

            if cli:
                click.secho(message, fg="red")
                sys.exit(1)
            else:
                logger.error(message)
                return False

    # Start the timer to measure processing time
    start_time = time.time()
    num_lines = 0
    report = {"created": [], "updated": [], "skipped": []}

    # Batch read the file to avoid memory issues
    with open(filepath) as f:
        while True:
            futures = []
            lines = f.readlines(batch_size)
            num_lines += len(lines)

            if not lines or lines[0] == "":
                break

            # Use multiprocessing Pool to parallelize the process
            with Pool(processes=cpu_count()) as pool:  # Use all available CPU cores
                for line in lines:
                    json_data = json.loads(line)
                    clean_data = clean_dict(json_data)
                    mex_id = json_data["identifier"]

                    try:
                        mex_data = mex_to_invenio_schema(clean_data)
                    except json.JSONDecodeError:
                        # Log and skip the line if it is not valid JSON
                        logger.error(f"Error decoding JSON: {line}")
                        continue
                    except KeyError as ke:
                        # Log and skip the line if it is missing a key
                        logger.error(f"KeyError: {ke}\nError processing record: {line}")
                        continue

                    futures.append(
                        pool.apply_async(process_record, (mex_id, mex_data, owner.id))
                    )

                # Collect the results as they complete
                for future in futures:
                    try:
                        result = future.get()  # get the result from the process

                        if result is not None:
                            if result["action"] == "create":
                                report["created"].append(result["id"])
                            elif result["action"] == "update":
                                report["updated"].append(result["id"])
                            elif result["action"] == "skip":
                                report["skipped"].append(result["id"])
                    except Exception as e:
                        logger.error(f"Error processing record: {str(e)}")

        # End the timer after processing is done
        end_time = time.time()

    # Calculate the total time taken and print the results
    elapsed_time = end_time - start_time
    minutes, seconds = divmod(elapsed_time, 60)

    for action in report:
        record_count = len(report[action])

        if record_count > 0:
            logger.info(
                f"{action.capitalize()} {record_count} records. Ids: {report[action]}"
            )

    if minutes:
        time_taken = (
            f"Total time taken: {int(minutes)} minutes and {seconds:.2f} seconds."
        )
    else:
        time_taken = f"Total time taken: {seconds:.2f} seconds."

    logger.info(time_taken)

    return True


if __name__ == "__main__":
    _import_data()
