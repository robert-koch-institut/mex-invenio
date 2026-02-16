"""Script to import data for the MEx Invenio repository on a regular basis.

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
import sys
import time

import click
from dictdiffer import diff
from flask import current_app
from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier
from invenio_rdm_records.fixtures.tasks import get_authenticated_identity
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.records.api import RDMRecord
from sqlalchemy import text

from mex_invenio.scripts.utils import (
    get_related_mex_ids,
    mex_to_invenio_schema,
    normalize_record_data,
    cleanup_files,
    setup_file_logging,
)

from mex_invenio.scripts.no_op_indexer import disable_indexing, re_enable_indexing

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def bulk_search_existing_records(mex_ids: list[str]) -> dict[str, dict]:
    """Search for multiple MEx IDs."""
    if not mex_ids:
        return {}

    try:
        # Query database with JOIN to get PID in one query using SQLAlchemy ORM.
        # Use DISTINCT ON to return only the latest version (highest index)
        # per mex:identifier, avoiding unnecessary updates from old versions.
        mex_id_expr = text(
            "rdm_records_metadata.json->'custom_fields'->>'mex:identifier'"
        )
        records_with_pids = (
            db.session.query(RDMRecord.model_cls, PersistentIdentifier.pid_value)
            .join(
                PersistentIdentifier,
                (PersistentIdentifier.object_uuid == RDMRecord.model_cls.id)
                & (PersistentIdentifier.pid_type == "recid"),
            )
            .filter(
                text(
                    "rdm_records_metadata.json->'custom_fields'->>'mex:identifier' = ANY(:mex_ids)"
                )
            )
            .distinct(mex_id_expr)
            .order_by(mex_id_expr, RDMRecord.model_cls.index.desc())
            .params(mex_ids=mex_ids)
            .all()
        )

        # Convert to the same format as search results
        existing_records = {}
        for record, pid_value in records_with_pids:
            # Extract data immediately to avoid session binding issues
            record_json = copy.deepcopy(record.json)
            mex_id = record_json.get("custom_fields", {}).get("mex:identifier")
            if mex_id:
                # Convert database record to search result format using the joined PID
                record_data = {
                    "id": str(pid_value),
                    "custom_fields": copy.deepcopy(
                        record_json.get("custom_fields", {})
                    ),
                    "metadata": copy.deepcopy(record_json.get("metadata", {})),
                }
                existing_records[mex_id] = record_data

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

            if not existing_record:
                # Create a new record
                draft = current_rdm_records_service.create(
                    data=mex_data, identity=identity
                )
                published = current_rdm_records_service.publish(
                    id_=draft.id, identity=identity
                )
                results.append(
                    {
                        "action": "create",
                        "id": published.id,
                        "uuid": published._record.id,
                    }
                )

            else:
                # Update an existing record
                record_pid = existing_record["id"]

                # Check if the record needs to be updated
                current_data = normalize_record_data(existing_record["custom_fields"])
                new_data = normalize_record_data(mex_data["custom_fields"])
                metadata_diff = list(diff(current_data, new_data))

                if metadata_diff:
                    new_version = current_rdm_records_service.new_version(
                        id_=record_pid, identity=identity
                    )
                    current_rdm_records_service.update_draft(
                        identity, new_version.id, mex_data
                    )
                    new_record = current_rdm_records_service.publish(
                        identity=identity, id_=new_version.id
                    )
                    results.append(
                        {
                            "action": "update",
                            "id": new_record.id,
                            "uuid": new_record._record.id,
                            "parent": new_record._record.parent.id,
                        }
                    )

                else:
                    # This shouldn't happen as the import files have been diffed
                    results.append({"action": "skip", "id": record_pid})
                    continue

                # Collect all related record UUIDs of created/updated records
                for related_id in get_related_mex_ids(mex_data):
                    results.append({"action": "related", "id": related_id})

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
    existing_records = bulk_search_existing_records(mex_ids)

    # Process the batch
    return process_record_batch(batch_records, existing_records, identity)


def update_report(report: dict, batch_results: list[dict]):
    """Update the report with results from a batch."""
    for result in batch_results:
        if result["action"] == "create":
            report["created"].append({"id": result["id"], "uuid": result["uuid"]})
        elif result["action"] == "update":
            report["updated"].append({"id": result["id"], "uuid": result["uuid"]})
        elif result["action"] == "skip":
            report["skipped"].append(result["id"])
        elif result["action"] == "related":
            report["related"].add(result["id"])


@click.command("import_data")
@click.argument("email")
@click.argument("import_file")
@click.option(
    "--batch-size", default=100, help="Number of records to process in each batch."
)
def _import_data(email: str, import_file: str, batch_size: int) -> bool:
    return import_data(email, import_file, batch_size, cli=True)


def import_data(
    email: str,
    import_file: str,
    batch_size: int = 100,
    cli: bool = False,
) -> bool:
    """Main function to import data.

    Batch size is set to 100 records by default.
    Expected data source is a JSON file with one MEx record per line.
    """

    if not os.path.isfile(import_file):
        message = f"File {import_file} not found."

        if cli:
            click.secho(message, fg="red")
            sys.exit(1)
        else:
            logger.error(message)
            return False

    with current_app.app_context():
        log_dir = os.path.join(current_app.config.get("S3_DOWNLOAD_FOLDER", "s3_downloads"), 'logs')
        file_handler = setup_file_logging(log_dir)
        logger.addHandler(file_handler)
        user_datastore = current_app.extensions["security"].datastore
        owner = user_datastore.find_user(email=email)
        logger.info(f"Importing {import_file}")

        if not owner:
            message = f"User with email {email} not found."
            logger.error(message)
            logger.removeHandler(file_handler)
            file_handler.close()

            if cli:
                click.secho(message, fg="red")
                sys.exit(1)
            else:
                return False

    # Start the timer to measure processing time
    start_time = time.time()
    num_lines = 0
    report = {"created": [], "updated": [], "skipped": [], "related": set(), "error": 0}

    # Process records in batches
    with current_app.app_context():
        identity = get_authenticated_identity(owner.id)

        try:
            disable_indexing(logger)

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
            re_enable_indexing(logger)

        # Re-index related records while still in app context to keep
        # SQLAlchemy instances bound to the active session
        if report["related"]:
            logger.info(f"Indexing {len(report['related'])} related records.")
            current_rdm_records_service.indexer.bulk_index(r for r in report["related"])

        # Re-indexing created and updated records in case there are any
        # bi-directional relationships

        if report["updated"]:
            parent_uuids = [r["parent"] for r in report["updated"]]
            updated_all_versions = db.session.query(RDMRecord.model_cls.id).filter(RDMRecord.model_cls.parent_id.in_(parent_uuids)).all()
            current_rdm_records_service.indexer.bulk_index(
                u for u in updated_all_versions
            )

        if report["created"]:
            current_rdm_records_service.indexer.bulk_index(
                r["uuid"] for r in report["created"]
            )

        # Process the bulk queue synchronously to ensure all records
        # are indexed before the function returns
        current_rdm_records_service.indexer.process_bulk_queue()

    # End the timer after processing is done
    end_time = time.time()

    # Calculate the total time taken and print the results
    elapsed_time = end_time - start_time
    minutes, seconds = divmod(elapsed_time, 60)

    for action in report:
        if isinstance(report[action], (list, set)):
            record_count = len(report[action])
        elif isinstance(report[action], int):
            record_count = report[action]

        if record_count > 0:
            if action == "error":
                logger.error(f"Encountered {record_count} errors during import.")
            elif action in ("created", "updated"):
                ids = [r["id"] for r in report[action]]
                logger.info(
                    f"{action.capitalize()} {record_count} records. Ids: {ids}"
                )
            else:
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

    logger.removeHandler(file_handler)
    file_handler.close()
    cleanup_files(log_dir, "import")

    return True


if __name__ == "__main__":
    _import_data()
