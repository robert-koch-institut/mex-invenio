from flask import current_app

from invenio_records.dumpers import SearchDumper
import json


def normalize_display_value(display_value):
    """Normalize display_value to ensure consistent object structure.

    Args:
        display_value: Can be a string, dict, or list of strings/dicts

    Returns:
        List of dicts with 'language' and 'value' keys
    """
    if display_value is None:
        return []

    if not isinstance(display_value, list):
        display_value = [display_value]

    normalized_values = []
    for item in display_value:
        if isinstance(item, dict) and "value" in item:
            # Already in correct format
            normalized_values.append(item)
        elif isinstance(item, str):
            # Convert string to object format
            normalized_values.append({"value": item})
        else:
            # Fallback for other types
            normalized_values.append({"value": str(item)})

    return normalized_values


class MexDumper(SearchDumper):
    def dump(self, record, data):
        dump_data = super(MexDumper, self).dump(record, data)

        # Initialize display_data if it doesn't exist
        if "display_data" not in dump_data:
            dump_data["display_data"] = {}

        self._record_cache = {}

        log = []
        log.append("###############MEX Dumper##################")
        log.append("Record ID: " + record.get("id"))
        log.append(json.dumps(record.get("custom_fields", {})))
        log.append(json.dumps(dump_data.get("custom_fields", {})))

        # Generate linked records data and add to display_data
        self._linked_records_data(record, dump_data, log)

        log.append("**************************************")
        log.append("Display data:")
        log.append(json.dumps(dump_data.get("display_data", {})))
        log.append("**************************************")

        self._record_cache = {}
        log.append("Dumped custom fields:")
        log.append(json.dumps(dump_data.get("custom_fields", {})))
        log.append("###############//MEX Dumper##################")
        print("\n".join(log))
        return dump_data

    def _records_by_mex_identifiers(self, source, mex_ids, log):
        results = []

        query_for = []
        for mex_id in mex_ids:
            if self._record_cache.get(mex_id):
                log.append("Cache hit for MEx ID: " + mex_id)
                results.append(self._record_cache[mex_id])
            else:
                query_for.append(mex_id)

        if len(query_for) == 0:
            return results

        log.append("Querying for MEx IDs: " + str(query_for))
        db_query = source.model_cls.query.filter(
            source.model_cls.json["custom_fields"]
            .op("->>")("mex:identifier")
            .in_(query_for),
        )
        db_results = db_query.all()
        log.append("DB results found: " + str(len(db_results)))

        for res in db_results:
            mex_id = res.json.get("custom_fields", {}).get("mex:identifier")
            self._record_cache[mex_id] = res
            results.append(res)

        return results

    def _records_by_custom_field(self, source, name, value, log):
        from sqlalchemy import or_, func, select

        db_query = source.model_cls.query.filter(
            source.model_cls.json["custom_fields"][name].op("?")(value)
        )

        from sqlalchemy.dialects import postgresql

        log.append(
            str(
                db_query.statement.compile(
                    dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}
                )
            )
        )
        db_results = db_query.all()
        log.append("DB results found: " + str(len(db_results)))

        return db_results

    def _linked_records_data(self, record, dump_data, log):
        """Generate linked records data and add to display_data."""

        record_type = record.get("metadata", {}).get("resource_type", {}).get("id", "")
        if not record_type:
            log.append("No resource type found, skipping linked records data")
            return

        # Get the record type to determine which fields to process
        records_linked_backwards = current_app.config.get(
            "FIELDS_LINKED_BACKWARDS", {}
        )

        if not records_linked_backwards:
            log.append("No backwards linked records configuration found")

        linked_records_data = {}

        linked_records = self._get_linked_records_for_dump(record, log)
        linked_records_data.update(linked_records)

        # Process backward-linked records
        mex_id = record.get("custom_fields", {}).get("mex:identifier")
        if mex_id and record_type in records_linked_backwards:
            field_items = records_linked_backwards[record_type]
            backwards_linked = self._get_records_linked_backwards_for_dump(
                record, mex_id, field_items, log
            )
            linked_records_data["backwards_linked"] = backwards_linked

        # Add the linked records data to display_data
        if linked_records_data:
            dump_data["display_data"]["linked_records"] = linked_records_data
            log.append("Added linked records data to display_data")
            log.append(str(linked_records_data))
            log.append("-----------------------")
        else:
            log.append("No linked records data generated")

    def _get_linked_records_for_dump(self, record, log):
        """Get forward-linked records for a record during dumping."""
        records_fields = {}
        cf = record.get("custom_fields", {})
        record_type = record.get("metadata", {}).get("resource_type", {}).get("id", "")
        linked_record_ids = []
        record_linked_fields = []


        # Collect all linked record IDs
        for field in cf:
            if current_app.config["FIELD_TYPES"].get(record_type, {}).get(field, "") == "identifier":

                linked_ids = cf.get(field)
                if linked_ids is not None:
                    record_linked_fields.append(field)
                    if isinstance(linked_ids, list):
                        linked_record_ids.extend(linked_ids)
                    else:
                        linked_record_ids.append(linked_ids)

        # Remove duplicates and batch fetch all linked records
        unique_linked_ids = list(set(linked_record_ids))
        if not unique_linked_ids:
            return records_fields

        linked_records = self._records_by_mex_identifiers(
            record, unique_linked_ids, log
        )
        linked_records_map = {}
        for r in linked_records:
            mex_id = r.json.get("custom_fields", {}).get("mex:identifier")
            if mex_id:
                linked_records_map[mex_id] = r.json

        # Process each field
        for field in record_linked_fields:
            raw_value = cf.get(field)
            if not raw_value:
                continue

            linked_record_ids = (
                raw_value if isinstance(raw_value, list) else [raw_value]
            )
            field_values = []

            for linked_record_id in unique_linked_ids:
                display_value = False
                linked_record = linked_records_map.get(linked_record_id, None)

                field_value = {
                    "link_id": linked_record_id,
                }

                if linked_record:
                    record_type = (
                        linked_record.get("metadata", {})
                        .get("resource_type", {})
                        .get("id", None)
                    )

                    if record_type:
                        field_value["core"] = record_type in [
                            "activity",
                            "resource",
                            "bibliographicresource",
                        ]

                    # Try to find display value from props
                    if not "TITLE_FIELDS" in current_app.config:
                        log.append("I don't know which fields are the titles; returning not changed.")
                        return records_fields
                    for title_field in current_app.config.get("TITLE_FIELDS", []):
                        if title_field in linked_record.get("custom_fields", {}):
                            display_value = linked_record["custom_fields"][title_field]
                            break
                    if display_value:
                        break
                    if not display_value:
                        display_value = [{"value": linked_record_id}]
                else:
                    display_value = [
                        {
                            "value": current_app.config.get(
                                "NO_RECORD_STRING", "No record found"
                            ),
                        }
                    ]

                field_value["display_value"] = normalize_display_value(display_value)

                # Handle email for contact fields
                if linked_record and field == "mex:contact":
                        email = linked_record.get("custom_fields", {}).get("mex:email", "")
                        if email:
                            field_value["email"] = email

                field_values.append(field_value)

            if len(field_values):
                records_fields[field] = field_values

        return records_fields

    def _get_records_linked_backwards_for_dump(self, record, mex_id, field_items, log):
        """Get backward-linked records for a record during dumping."""
        records_fields = {}

        for field in field_items:
            # Find records that reference this mex_id in the given field
            linked_records = self._records_by_custom_field(record, field, mex_id, log)

            if not linked_records:
                continue

            field_values = []
            for r in linked_records:
                display_value = None
                record_json = r.json if hasattr(r, "json") else r

                if not "TITLE_FIELDS" in current_app.config:
                        log.append("I don't know which fields are the titles; returning not changed.")
                        return records_fields
                for f in current_app.config.get("TITLE_FIELDS", []):
                    display_value = record_json.get("custom_fields", {}).get(f, None)
                    if display_value:
                        field_values.append(
                            {
                                "link_id": record_json.get("custom_fields", {}).get(
                                    "mex:identifier"
                                ),
                                "display_value": normalize_display_value(display_value),
                            }
                        )
                        break

                if display_value is None:
                    identifier = record_json.get("custom_fields", {}).get(
                        "mex:identifier"
                    )
                    field_values.append(
                        {
                            "link_id": identifier,
                            "display_value": [{"value": identifier}]
                            if identifier
                            else [{"value": "Unknown"}],
                        }
                    )
            if len(field_values):
                records_fields[field] = field_values

        return records_fields
