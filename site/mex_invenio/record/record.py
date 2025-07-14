from flask import render_template, abort, request, g
from flask.views import MethodView
from flask_babel import ngettext, _

from invenio_rdm_records.records.api import RDMRecord
from invenio_rdm_records.resources.serializers import UIJSONSerializer
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_pidstore.errors import PIDDoesNotExistError

import json

from mex_invenio.record.utils import _get_linked_records_data, _get_record_by_mex_id


class MexRecord(MethodView):
    def __init__(self):
        self.template = "invenio_app_rdm/records/detail.html"

    def get(self, mex_id):
        version_id = request.args.get("version_id", None)

        # Establish the version_id as an integer if it is provided
        if version_id:
            try:
                version_id = int(version_id)
            except ValueError:
                version_id = None

        if version_id:
            # Try to fetch the record by mex_id and version_id
            # Note: RDMRecord.model_cls is used to access the underlying SQLAlchemy model,
            # this is because RDMRecord api methods expect a PID and not a mex_id.
            record = RDMRecord.model_cls.query.filter(
                RDMRecord.model_cls.json["custom_fields"]["mex:identifier"].as_string()
                == mex_id,
                RDMRecord.model_cls.index == version_id,
            ).one_or_none()

            if not record:
                abort(404)
            pid = record.json["id"]
        else:
            # Version_id is not provided, fetch the latest record by mex_id
            try:
                record = _get_record_by_mex_id(mex_id)
            except PIDDoesNotExistError:
                abort(404)
            except Exception:
                abort(500)

            pid = record["id"]

        record_item = current_rdm_records_service.read(g.identity, pid)
        ui_serializer = UIJSONSerializer()
        record_ui = ui_serializer.serialize_object(record_item.data)

        linked_records_data = _get_linked_records_data(record_item, mex_id)

        return render_template(
            self.template,
            record=json.loads(record_ui),
            linked_records_data=linked_records_data,
            is_preview=False,
        )
