from typing import List

from flask import current_app, g
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.services.results import RDMRecordList


def _get_records_by_field(field_id: str, value) -> List:
    """Fetch records by a specific field and value or values."""
    escaped_field = field_id.replace(":", "\:")

    if isinstance(value, list):
        values_str = " OR ".join([str(v) for v in value])
        search_query = f"custom_fields.{escaped_field}:({values_str})"
    else:
        search_query = f"custom_fields.{escaped_field}:{value}"

    results: RDMRecordList = current_rdm_records_service.search(
        g.identity, q=search_query, size=1000
    )

    all_records = []

    # Add records from first page
    all_records.extend(list(results))

    # Paginate through remaining pages
    while results.pagination.has_next:
        next_page_obj = results.pagination.next_page
        results = current_rdm_records_service.search(
            g.identity, q=search_query, page=next_page_obj.page, size=next_page_obj.size
        )
        all_records.extend(list(results))

    return all_records


def _get_record_by_mex_id(mex_id):
    """Fetch a record by either a single MEx id or a list of MEx ids."""
    results = _get_records_by_field("mex:identifier", mex_id)

    if isinstance(mex_id, str):
        if not results:
            raise PIDDoesNotExistError("rec", mex_id)

        return results[0] if results else None
    else:
        return results


def _get_linked_records(record, field_items):
    records_fields = {}
    cf = record.data["custom_fields"]
    linked_record_ids = []

    for f in field_items:
        linked_ids = cf.get(f[0])
        if linked_ids is not None:
            # Get the linked record ids from the custom fields
            if isinstance(linked_ids, list):
                linked_record_ids.extend(linked_ids)
            else:
                linked_record_ids.append(linked_ids)

    # Remove duplicates and batch fetch all linked records at once
    unique_linked_ids = list(set(linked_record_ids))
    linked_records = (
        _get_record_by_mex_id(unique_linked_ids) if unique_linked_ids else []
    )

    linked_records_map = {
        r["custom_fields"]["mex:identifier"]: r for r in linked_records
    }

    for field, props in field_items:
        raw_value = record["custom_fields"].get(field)

        if not raw_value:
            continue

        linked_record_ids = raw_value if isinstance(raw_value, list) else [raw_value]

        field_values = []

        for linked_record_id in linked_record_ids:
            display_value = False

            linked_record = linked_records_map.get(linked_record_id)

            if linked_record:
                for p in props:
                    for title_field in props[p]:
                        if title_field in linked_record["custom_fields"]:
                            display_value = linked_record["custom_fields"][title_field]
                            break
                    if display_value:
                        break
                if not display_value:
                    display_value = [linked_record_id]
            else:
                display_value = [
                    current_app.config.get("NO_RECORD_STRING", "No record found")
                ]

            field_values.append(
                {
                    "display_value": display_value
                    if isinstance(display_value, list)
                    else [display_value],
                    "link_id": linked_record_id,
                }
            )

        records_fields[field] = field_values

    return records_fields


def _get_records_linked_backwards(mex_id, field_items):
    records_fields = {}
    for field, props in field_items:
        linked_records = _get_records_by_field(field, mex_id)

        if not linked_records:
            continue

        field_values = []

        for r in linked_records:
            display_value = None

            for f in props:
                display_value = r["custom_fields"].get(f, None)

                if display_value:
                    field_values.append(
                        {
                            "link_id": r["custom_fields"]["mex:identifier"],
                            "display_value": display_value
                            if isinstance(display_value, list)
                            else [display_value],
                        }
                    )
                    break

            if display_value is None:
                field_values.append(
                    {
                        "link_id": r["custom_fields"]["mex:identifier"],
                        "display_value": [r["custom_fields"]["mex:identifier"]],
                    }
                )

        records_fields[field] = field_values

    return records_fields


def _get_linked_records_data(record, mex_id):
    """Fetch metadata about linked records for a given record."""
    record_type = record.data["metadata"]["resource_type"]["id"]
    linked_records_fields = current_app.config.get("LINKED_RECORDS_FIELDS", {})
    records_linked_backwards = current_app.config.get("RECORDS_LINKED_BACKWARDS", {})
    linked_records_data = {}

    # TODO:
    # Include lookup for records linked backwards in query for linked records

    if record_type in linked_records_fields:
        field_items = linked_records_fields[record_type].items()
        linked_records = _get_linked_records(record, field_items)
        linked_records_data.update(linked_records)

    if record_type in records_linked_backwards:
        field_items = records_linked_backwards[record_type].items()
        linked_records = _get_records_linked_backwards(mex_id, field_items)
        linked_records_data["backwards_linked"] = linked_records

    return linked_records_data
