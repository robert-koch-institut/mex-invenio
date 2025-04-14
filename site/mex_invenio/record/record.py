from flask import render_template, abort, g
from flask.views import MethodView
from invenio_pidstore.resolver import Resolver
from invenio_rdm_records.records.api import RDMRecord
from invenio_rdm_records.resources.serializers import UIJSONSerializer
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_access.permissions import system_identity
from mex_invenio.config import settings
from invenio_pidstore.errors import (
    PIDDeletedError,
    PIDDoesNotExistError,
    PIDMissingObjectError,
    PIDRedirectedError,
    PIDUnregistered,
    PIDValueError
)


import json

def _get_record_by_field(field_id, value):
    escaped_field = field_id.replace(':', '\:')
    search_query = f'custom_fields.{escaped_field}:{value}'
    print(search_query)
    results = list(current_rdm_records_service.search(g.identity, q=search_query))

    return results or None

def _get_record_by_id(mex_id):

    print(mex_id)
    results = _get_record_by_field("mex:identifier", mex_id)

    if not results:
        raise PIDDoesNotExistError()

    if len(results) == 1:
        return results[0]
    else:
        raise PIDValueError("Too many records")


class MexRecord(MethodView):

    def __init__(self):
        self.template = "invenio_app_rdm/records/detail.html"

    def get(self, mex_id):

        try:
            record = _get_record_by_id(mex_id)
        except PIDDoesNotExistError:
            abort(404)
        except Exception:
            abort(500)

        pid = record["id"]
        service = current_rdm_records_service
        record_item = service.read(system_identity, pid)
        ui_serializer = UIJSONSerializer()
        record_ui = ui_serializer.serialize_object(record_item.data)

        record_type = record["metadata"]["resource_type"]["id"]

        linked_records_data = {}

        if record_type in settings.LINKED_RECORDS_FIELDS:

            for field, props in settings.LINKED_RECORDS_FIELDS[record_type].items():
                raw_value = record["custom_fields"].get(field)

                if not raw_value:
                    continue

                linked_record_ids = raw_value if isinstance(raw_value, list) else [raw_value]

                field_values = []

                for linked_record_id in linked_record_ids:

                    display_value = linked_record_id

                    try:
                        linked_record = _get_record_by_id(linked_record_id)
                    except Exception:
                        linked_record = None

                    if linked_record:
                        for f in props["fields"]:
                            display_value = linked_record["custom_fields"].get(f, None)
                            if display_value:
                                break
                    else:
                        display_value = f'Record with id { linked_record_id } not found'

                    field_values.append({
                        "display_value": display_value,
                        "link_id": linked_record_id
                    })

                linked_records_data[field] = field_values

        return render_template(self.template,
                               record=json.loads(record_ui),
                               linked_records_data = linked_records_data,
                               is_preview=False)

    # invenio id: wbdv5-sac84
    # mex id: cP1OvUS7rELcPULquIu1dZ