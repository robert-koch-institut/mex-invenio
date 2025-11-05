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

import copy
import json
import logging
import os.path
from datetime import datetime
from pathlib import Path
import subprocess
import sys
import time

import click
from dictdiffer import diff
from flask import current_app
from invenio_access.permissions import system_identity
from invenio_rdm_records.fixtures.tasks import get_authenticated_identity
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.records.api import RDMRecord
from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier
from sqlalchemy import text

from mex_invenio.scripts.utils import mex_to_invenio_schema, normalize_record_data, get_related_mex_ids

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
    #format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
    #datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)



def get_record_uuids_by_mex_ids(mex_ids: list[str]) -> dict[str, str]:
    """Get record UUIDs for given MEx IDs."""
    if not mex_ids:
        return {}
    
    try:
        # Query for record UUIDs by MEx IDs
        records = db.session.query(
            RDMRecord.model_cls.id,
            RDMRecord.model_cls.json
        ).filter(
            text("rdm_records_metadata.json->'custom_fields'->>'mex:identifier' = ANY(:mex_ids)")
        ).params(mex_ids=mex_ids).all()
        
        # Map MEx ID to UUID
        mex_id_to_uuid = {}
        for record_id, record_json in records:
            mex_id = record_json.get('custom_fields', {}).get('mex:identifier')
            if mex_id in mex_ids:
                mex_id_to_uuid[mex_id] = str(record_id)
        
        return mex_id_to_uuid
        
    except Exception as e:
        logger.error(f"Error getting UUIDs for MEx IDs: {e}")
        return {}


def bulk_search_existing_records(mex_ids: list[str], identity) -> dict[str, dict]:
    """Search for multiple MEx IDs."""
    if not mex_ids:
        return {}

    logger.info(f"Performing bulk search for {len(mex_ids)} MEx IDs")
    logger.info(f"Searching for MEx IDs: {mex_ids}")

    try:
        # Query database with JOIN to get PID in one query using SQLAlchemy ORM
        records_with_pids = db.session.query(
            RDMRecord.model_cls, 
            PersistentIdentifier.pid_value
        ).join(
            PersistentIdentifier,
            (PersistentIdentifier.object_uuid == RDMRecord.model_cls.id) & 
            (PersistentIdentifier.pid_type == 'recid')
        ).filter(
            text("rdm_records_metadata.json->'custom_fields'->>'mex:identifier' = ANY(:mex_ids)")
        ).params(mex_ids=mex_ids).all()

        logger.info(f"Database returned {len(records_with_pids)} records with matching MEx IDs")

        # Convert to the same format as search results
        existing_records = {}
        for record, pid_value in records_with_pids:
            # Extract data immediately to avoid session binding issues
            record_json = copy.deepcopy(record.json)
            mex_id = record_json.get('custom_fields', {}).get('mex:identifier')
            if mex_id:
                if mex_id in existing_records:
                    logger.warning(f"Multiple records found for MEx id: {mex_id}")
                
                # Convert database record to search result format using the joined PID
                record_data = {
                    'id': str(pid_value),
                    'custom_fields': copy.deepcopy(record_json.get('custom_fields', {})),
                    'metadata': copy.deepcopy(record_json.get('metadata', {}))
                }
                existing_records[mex_id] = record_data

        logger.info(f"Found {len(existing_records)} existing records out of {len(mex_ids)} requested")
        return existing_records
        
    except Exception as e:
        logger.error(f"Error in bulk database search: {e}")
        return {}


def process_record_batch(
    records_data: list[dict], existing_records: dict[str, dict], identity
) -> list[dict]:
    """Process a batch of records."""
    results = []

    for json_data in records_data:
        try:
            mex_id = json_data["identifier"]
            mex_data = mex_to_invenio_schema(current_app.config, json_data)

            existing_record = existing_records.get(mex_id)

            logger.info(f"Processing MEx ID: {mex_id} - Existing record: {'found' if existing_record else 'not found'}")

            if not existing_record:
                # Create a new record
                draft = current_rdm_records_service.create(
                    data=mex_data, identity=identity
                )
                published = current_rdm_records_service.publish(
                    id_=draft.id, identity=identity
                )
                results.append({"action": "create", "id": published.id})

                for related_id in get_related_mex_ids(current_app.config, mex_data):
                    results.append({"action": "related", "id": related_id})

            else:
                # Update an existing record
                record_pid = existing_record["id"]

                # Check if the record needs to be updated
                current_data = normalize_record_data(existing_record["custom_fields"])
                new_data = normalize_record_data(mex_data["custom_fields"])
                metadata_diff = list(diff(current_data, new_data))
                logger.info(f"Metadata diff for record {mex_id}: {metadata_diff}")

                if metadata_diff:
                    logger.error(f"Record {mex_id} has differences: {metadata_diff}")
                    logger.error(
                        f"Current custom_fields keys: {list(current_data.keys())}"
                    )
                    logger.error(f"New custom_fields keys: {list(new_data.keys())}")
                    logger.error(
                        f"Missing from current: {set(new_data.keys()) - set(current_data.keys())}"
                    )
                    logger.error("---" * 20)

                    new_version = current_rdm_records_service.new_version(
                        id_=record_pid, identity=identity
                    )
                    current_rdm_records_service.update_draft(
                        identity, new_version.id, mex_data
                    )
                    new_record = current_rdm_records_service.publish(
                        identity=identity, id_=new_version.id
                    )
                    results.append({"action": "update", "id": new_record.id})

                    for related_id in get_related_mex_ids(current_app.config, mex_data):
                        results.append({"action": "related", "id": related_id})
                else:
                    results.append({"action": "skip", "id": record_pid})

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


def process_batch(batch_records: list[dict], identity) -> list[dict]:
    """Process a batch of records with bulk search optimization."""
    # Extract MEx IDs for bulk search
    mex_ids = [record["identifier"] for record in batch_records]

    # Bulk search for existing records
    existing_records = bulk_search_existing_records(mex_ids, identity)

    # Process the batch
    return process_record_batch(batch_records, existing_records, identity)


def update_report(report: dict, batch_results: list[dict]):
    """Update the report with results from a batch."""
    print(batch_results)
    for result in batch_results:
        if result["action"] == "create":
            report["created"].append(result["id"])
        elif result["action"] == "update":
            report["updated"].append(result["id"])
        elif result["action"] == "skip":
            report["skipped"].append(result["id"])
        elif result["action"] == "related":
            report["related"].append(result["id"])


@click.command("import_data")
@click.argument("email")
@click.argument("import_file")
@click.option(
    "--batch-size", default=100, help="Number of records to process in each batch."
)
@click.option(
    "--index", is_flag=True, default=False,
    help="Skip indexing during import for better performance.",
)
def _import_data(email: str, import_file: str, batch_size: int, index: bool) -> bool:
    return import_data(email, import_file, batch_size, index, cli=True)


def import_data(
    email: str,
    import_file: str,
    batch_size: int = 100,
    index: bool = False,
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

    # Find the directory of the file
    directory = "/".join(import_file.split("/")[:-1]) + "/"

    # Sort files by modification time, newest first (ignore directories)
    files = sorted([f for f in Path(directory).iterdir() if f.is_file()], key=lambda x: -x.stat().st_mtime)
    logger.info('=== FILE DEBUGGING ===')
    logger.info(f'Directory: {directory}')
    logger.info(f'Files found: {[f.name for f in files]}')
    logger.info(f'Number of files: {len(files)}')
    logger.info(f'Index parameter passed: {index}')
    logger.info('======================')

    # Skip comparison if this is the first import
    if len(files) > 1:
        diffdirectory = directory + "diffs/"

        if not os.path.exists(diffdirectory):
            os.makedirs(diffdirectory, exist_ok=True)

        last_import = files[1]

        awk_pattern = "NR==FNR{seen[$0]=1; next} !($0 in seen)"
        timestamp = datetime.today().strftime('%d-%m-%Y_%I_%M_%S')
        diff_file = f"{diffdirectory}diff_{timestamp}.ndjson"

        comparison_cmd = f"awk '{awk_pattern}' {last_import} {import_file} > {diff_file}"

        result = subprocess.run([comparison_cmd], shell=True, check=True)

        assert result.returncode == 0, "Error during file comparison"

        logger.info(f'=== DIFF RESULT ===')
        logger.info(f'Diff file: {diff_file}')
        logger.info(f'Diff file size: {os.path.getsize(diff_file)} bytes')
        logger.info(f'Original import_file: {import_file}')
        logger.info('==================')

        if os.path.getsize(diff_file) == 0:
            logger.info("No new/changed records to import since last import.")
            return

        # Use the diff file for import
        logger.info(f'Switching from {import_file} to diff file {diff_file}')
        import_file = diff_file
        # Do manual indexing, because this is an update
        index = True
        logger.info(f'Index parameter now set to: {index}')

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
    report = {"created": [], "updated": [], "skipped": [], "related": [], "error": 0}

    # Process records in batches
    with current_app.app_context():
        identity = get_authenticated_identity(owner.id)

        if not index:
            #RecordCommitOp.on_commit = lambda self, uow: None
            #RecordDeleteOp.on_commit = lambda self, uow: None
            # Temporarily disable indexing for performance
            #original_indexer = current_rdm_records_service.indexer
            # Monkey patch the indexer to a no-op version
            #current_rdm_records_service._indexer = NoOpIndexer()
            logger.info("Disabled indexing during import for better performance")
        
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
                            logger.info(f"Processing batch of {len(batch_records)} records")
                            batch_results = process_batch(batch_records, identity)
                            update_report(report, batch_results)
                            batch_records = []

                    except json.JSONDecodeError:
                        logger.error(f"Error decoding JSON line: {line}")
                        report["error"] += 1

                # Process remaining records
                if batch_records:
                    batch_results = process_batch(batch_records, identity)
                    update_report(report, batch_results)
                    
        finally:
            if not index:
                #current_rdm_records_service._indexer = original_indexer
                logger.info("Restored indexing")

    # End the timer after processing is done
    end_time = time.time()

    # Calculate the total time taken and print the results
    elapsed_time = end_time - start_time
    minutes, seconds = divmod(elapsed_time, 60)

    for action in report:
        if isinstance(report[action], list):
            record_count = len(report[action])
        elif isinstance(report[action], int):
            record_count = report[action]

        if record_count > 0:
            if action == "error":
                logger.error(f"Encountered {record_count} errors during import.")

            else:
                logger.info(f"{action.capitalize()} {record_count} records. Ids: {report[action]}")

    if minutes:
        time_taken = (
            f"Total time taken: {int(minutes)} minutes and {seconds:.2f} seconds."
        )
    else:
        time_taken = f"Total time taken: {seconds:.2f} seconds."

    logger.info(time_taken)

    # Rebuild the search index after all records have been processed (if requested)

    #with app.app_context():
    #    current_rdm_records_service.rebuild_index(identity=system_identity)

    # Get UUIDs for related MEx IDs for indexing
    if report["related"]:
        mex_id_to_uuid = get_record_uuids_by_mex_ids(report["related"])
        for mex_id in report["related"]:
            if mex_id in mex_id_to_uuid:
                uuid = mex_id_to_uuid[mex_id]
                print(f"Indexing record {mex_id} with UUID {uuid}")
                current_rdm_records_service.indexer.index_by_id(uuid)
            else:
                logger.warning(f"Could not find UUID for related MEx ID: {mex_id}")

    return True


if __name__ == "__main__":
    _import_data()
