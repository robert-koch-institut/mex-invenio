"""Script to do the initial import of a large number of data for the MEx Invenio repository.

This script is intended to run only once, to import the data to a vanilla database.
It does not do any lookups or comparisons. Synchronous indexing is disabled in order to
speed up the processing. Note that since no check is made on the mex:identifier value,
running this script twice with an object with the same mex:identifier will result in
two records being created with the same identifier.

Make sure the Invenio services have been set up and are running.

Does the following:
- Finds the file provided as CLI argument.
- Finds a user to own the record.
- Reads in the metadata in MEx json format.
- Disables synchronous indexing by monkey patching
- Creates a new draft and publishes as a record

To run the script, go to the repository root directory and use the following command:

        $ pipenv run invenio shell site/mex_invenio/scripts/initial_import.py <email> <filepath>
"""

import json
import logging
import os.path
import sys
import time

import click
from flask import current_app
from invenio_rdm_records.fixtures.tasks import get_authenticated_identity
from invenio_rdm_records.proxies import current_rdm_records_service

from mex_invenio.scripts.utils import (
    mex_to_invenio_schema,
    normalize_record_data,
    get_related_mex_ids,
)

from invenio_records_resources.services.uow import RecordCommitOp, RecordDeleteOp


# No-op indexer class to disable indexing during import
class NoOpIndexer:
    """A no-operation indexer that does nothing."""

    def index(self, *args, **kwargs):
        pass

    def delete(self, *args, **kwargs):
        pass

    def delete_by_id(self, *args, **kwargs):
        pass

    def exists(self, *args, **kwargs):
        return False

    def bulk_index(self, *args, **kwargs):
        pass

    def bulk_delete(self, *args, **kwargs):
        pass

    def refresh(self, *args, **kwargs):
        pass


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    # format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
    # datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def process_record_batch(records_data: list[dict], identity) -> list[dict]:
    """Process a batch of records."""
    results = []

    for json_data in records_data:
        try:
            mex_data = mex_to_invenio_schema(current_app.config, json_data)

            # Create a new record
            draft = current_rdm_records_service.create(data=mex_data, identity=identity)
            published = current_rdm_records_service.publish(
                id_=draft.id, identity=identity
            )
            results.append(published.id)

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON: {json_data}")
        except KeyError as ke:
            logger.error(f"KeyError: {ke}\nError processing record: {json_data}")
        except Exception as e:
            import traceback

            logger.error(
                f"Error processing record {json_data.get('identifier', 'unknown')}: {e}\n"
                f"Full traceback:\n{traceback.format_exc()}"
            )

    return results


@click.command("initial_import")
@click.argument("email")
@click.argument("import_file")
@click.option(
    "--batch-size", default=100, help="Number of records to process in each batch."
)
def _initial_import(email: str, import_file: str, batch_size: int) -> bool:
    return initial_import(email, import_file, batch_size, cli=True)


def initial_import(
    email: str,
    import_file: str,
    batch_size: int = 100,
    cli: bool = False,
) -> bool:
    """Main function to import data.
    Batch size is set to 100 records by default.
    Expected data source is a JSON file with one MEx record per line."""

    if not os.path.isfile(import_file):
        message = f"File {import_file} not found."

        if cli:
            click.secho(message, fg="red")
            sys.exit(1)
        else:
            logger.error(message)
            return False

    # Store original on_commit methods
    original_record_commit_op = RecordCommitOp.on_commit
    original_record_delete_op = RecordDeleteOp.on_commit

    # Disable on_commit methods for performance
    RecordCommitOp.on_commit = lambda self, uow: None
    RecordDeleteOp.on_commit = lambda self, uow: None

    # Temporarily disable indexing for performance
    original_indexer = current_rdm_records_service.indexer
    # Monkey patch the indexer to a no-op version
    current_rdm_records_service._indexer = NoOpIndexer()
    logger.info(
        "Disabled indexing and commit operations during import for better performance"
    )

    with current_app.app_context():
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
    report = []
    errors = []

    # Process records in batches
    with current_app.app_context():
        identity = get_authenticated_identity(owner.id)

        try:
            with open(import_file) as f:
                batch_records = []

                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        json_data = json.loads(line)
                        batch_records.append(json_data)
                        num_lines += 1

                        logger.info(f"Processing line: {num_lines}")

                        # Process batch when it reaches batch_size
                        if len(batch_records) >= batch_size:
                            logger.info(
                                f"Processing batch of {len(batch_records)} records"
                            )
                            batch_results = process_record_batch(
                                batch_records, identity
                            )
                            report.extend(batch_results)
                            batch_records = []

                    except json.JSONDecodeError:
                        logger.error(f"Error decoding JSON line: {line}")
                        errors.append(line)

                # Process remaining records
                if batch_records:
                    batch_results = process_record_batch(batch_records, identity)
                    report.extend(batch_results)
        finally:
            # Restore original indexer
            current_rdm_records_service._indexer = original_indexer

            # Restore original on_commit methods
            RecordCommitOp.on_commit = original_record_commit_op
            RecordDeleteOp.on_commit = original_record_delete_op

            logger.info("Restored indexing and commit operations")

    # End the timer after processing is done
    end_time = time.time()

    # Calculate the total time taken and print the results
    elapsed_time = end_time - start_time
    minutes, seconds = divmod(elapsed_time, 60)
    record_count = len(report)
    errors = len(errors)

    if record_count > 0:
        logger.info(f"Created {record_count} records. Ids: {report}")

    if errors:
        logger.error(f"Errors: {errors}")

    if minutes:
        time_taken = (
            f"Total time taken: {int(minutes)} minutes and {seconds:.2f} seconds."
        )
    else:
        time_taken = f"Total time taken: {seconds:.2f} seconds."

    logger.info(time_taken)

    return True


if __name__ == "__main__":
    _initial_import()
