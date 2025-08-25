from flask import render_template, abort
from flask.views import MethodView
from invenio_rdm_records.resources.serializers import UIJSONSerializer
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_access.permissions import system_identity
from invenio_pidstore.errors import PIDDoesNotExistError

import json

from .utils import _get_linked_records_data, _get_record_by_mex_id


class MexRecord(MethodView):
    def __init__(self):
        self.template = "invenio_app_rdm/records/detail.html"

    def get(self, mex_id):
        try:
            record = _get_record_by_mex_id(mex_id)
        except PIDDoesNotExistError:
            abort(404)
        except Exception:
            abort(500)

        pid = record["id"]
        service = current_rdm_records_service
        record_item = service.read(system_identity, pid)
        ui_serializer = UIJSONSerializer()
        record_ui = ui_serializer.serialize_object(record_item.data)

        linked_records_data = _get_linked_records_data(record, mex_id)

        return render_template(
            self.template,
            record=json.loads(record_ui),
            linked_records_data=linked_records_data,
            is_preview=False,
        )
