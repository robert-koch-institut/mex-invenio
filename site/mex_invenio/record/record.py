from flask import current_app, render_template, abort, g
from flask.views import MethodView
from invenio_rdm_records.resources.serializers import UIJSONSerializer
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_access.permissions import system_identity
from invenio_pidstore.errors import PIDDoesNotExistError, PIDValueError

import json


def _get_records_by_field(field_id: str, value) -> list:
    """Fetch records by a specific field and value."""
    escaped_field = field_id.replace(":", "\:")
    search_query = f"custom_fields.{escaped_field}:{value}"
    results = list(current_rdm_records_service.search(g.identity, q=search_query))

    return results


def _get_record_by_mex_id(mex_id: str) -> dict:
    """Fetch a record by its MEx ID."""
    results = _get_records_by_field("mex:identifier", mex_id)

    if not results:
        raise PIDDoesNotExistError()

    if len(results) == 1:
        return results[0]
    else:
        raise PIDValueError("Too many records")


def _get_linked_records(record, mex_id):
    """Fetch metadata about linked records for a given record."""
    record_type = record["metadata"]["resource_type"]["id"]
    linked_records_fields = current_app.config.get("LINKED_RECORDS_FIELDS", {})
    records_linked_backwards = current_app.config.get("RECORDS_LINKED_BACKWARDS", {})
    linked_records_data = {}

    if record_type in linked_records_fields:
        for field, props in linked_records_fields[record_type].items():
            raw_value = record["custom_fields"].get(field)

            if not raw_value:
                continue

            linked_record_ids = (
                raw_value if isinstance(raw_value, list) else [raw_value]
            )

            field_values = []

            for linked_record_id in linked_record_ids:
                display_value = False

                try:
                    linked_record = _get_record_by_mex_id(linked_record_id)
                except Exception:
                    linked_record = None

                if linked_record:
                    for p in props:
                        for title_field in props[p]:
                            if title_field in linked_record["custom_fields"]:
                                display_value = linked_record["custom_fields"][
                                    title_field
                                ]
                                break
                        if display_value:
                            break
                else:
                    display_value = current_app.config.get(
                        "NO_RECORD_STRING", "No record found"
                    )

                if not display_value:
                    display_value = [linked_record_id]

                field_values.append(
                    {"display_value": display_value, "link_id": linked_record_id}
                )

            linked_records_data[field] = field_values

    if record_type in records_linked_backwards:
        for field, props in records_linked_backwards[record_type].items():
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
                                "display_value": display_value,
                            }
                        )
                        break

                if display_value is None:
                    field_values.append(
                        {
                            "link_id": r["custom_fields"]["mex:identifier"],
                            "display_value": r["custom_fields"]["mex:identifier"],
                        }
                    )

            linked_records_data[field] = field_values
    return linked_records_data


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
        r = json.loads(record_ui)
        r["ui"]["custom_fields"]["mex:documentation"] = []
        record_ui = json.dumps(r)

        linked_records_data = _get_linked_records(record, mex_id)
        current_app.logger.info(f"Linked records data: {linked_records_data}")
        current_app.logger.info(f"{record}")
        current_app.logger.info(f"{mex_id}")

        return render_template(
            self.template,
            record=json.loads(record_ui),
            linked_records_data=linked_records_data,
            is_preview=False,
        )
