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
)


import json

def _get_record(mex_id):

    try:
        search_query = f'custom_fields.mex\:identifier:{mex_id}'
        results = list(current_rdm_records_service.search(g.identity, q=search_query))

        if len(results) == 0:
            abort(404)

        elif len(results) == 1:
            return results[0]

        elif len(results) > 1:
            print("too many results")
            abort(500)

    except Exception as e:
        print(e)
        abort(500)


class MexRecord(MethodView):

    def __init__(self):
        self.template = "invenio_app_rdm/records/detail.html"

    def get(self, mex_id):

        record = _get_record(mex_id)
        pid = record["id"]
        service = current_rdm_records_service
        record_item = service.read(system_identity, pid)
        ui_serializer = UIJSONSerializer()
        record_ui = ui_serializer.serialize_object(record_item.data)

        return render_template(self.template, record=json.loads(record_ui), custom_fields_ui = settings.RDM_CUSTOM_FIELDS_UI, is_preview=False)

    # invenio id: wbdv5-sac84
    # mex id: cP1OvUS7rELcPULquIu1dZ