from flask import render_template, abort
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

class MexRecord(MethodView):

    def __init__(self):
        self.template = "invenio_app_rdm/records/detail.html"

    def get(self, mex_id):

        resolver = Resolver(pid_type="recid", object_type="rec", getter=RDMRecord.get_record)
        try:
            pid, record = resolver.resolve(mex_id)
        except (PIDDoesNotExistError, PIDUnregistered):
            abort(404)
        except PIDMissingObjectError as e:
            current_app.logger.exception(
                "No object assigned to {0}.".format(e.pid), extra={"pid": e.pid}
            )
            abort(500)

        service = current_rdm_records_service
        record_item = service.read(system_identity, pid.pid_value)
        ui_serializer = UIJSONSerializer()
        record_ui = ui_serializer.serialize_object(record_item.data)

        return render_template(self.template, record=json.loads(record_ui), custom_fields_ui = settings.RDM_CUSTOM_FIELDS_UI, is_preview=False)

# invenio id: wbdv5-sac84
# mex id: cP1OvUS7rELcPULquIu1dZ