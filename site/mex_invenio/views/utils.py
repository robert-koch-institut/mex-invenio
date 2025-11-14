from typing import List

from flask import g
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
