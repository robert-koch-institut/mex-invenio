from datetime import datetime

from flask import current_app
from invenio_rdm_records.services.config import SearchOptions
from invenio_records.dumpers import SearchDumper
from invenio_records_resources.services.base.config import SearchOptionsMixin
from invenio_records_resources.services.records.queryparser import QueryParser
from invenio_search import RecordsSearchV2

from mex_invenio.search.params import (
    BoostingParamsInterpreter,
    GenericQueryParamsInterpreter,
    HighlightParamsInterpreter,
    TypeLimiterParamsInterpreter,
)

# from mex_invenio.custom_record import MexRDMRecord


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


class MexSearchOptions(SearchOptions, SearchOptionsMixin):
    search_cls = RecordsSearchV2
    query_parser_cls = QueryParser
    suggest_parser_cls = None
    sort_options = {}
    facets = {}
    params_interpreters_cls = [
        GenericQueryParamsInterpreter,
        TypeLimiterParamsInterpreter,
        HighlightParamsInterpreter,
        BoostingParamsInterpreter,
        # Add other interpreters as needed
    ]


# These are the fields that we would lump into a single bucket if we needed
# to optimise the free-text search.  For now these are also reflected in the record
# mapping, and the free-text bucket is not implemented.
FREE_TEXT_SEARCH_FIELDS = [
    "custom_fields.mex:title.value",
    "custom_fields.mex:method.value",
    "custom_fields.mex:keyword.value",
    "custom_fields.mex:description.value",
    "custom_fields.mex:instrumentToolOrApparatus.value",
    "custom_fields.mex:website.url",
    "custom_fields.mex:website.title",
    "custom_fields.mex:abstract.value",
    "custom_fields.mex:shortName.value",
    "custom_fields.mex:documentation.title",
    "custom_fields.mex:alternativeTitle.value",
    "custom_fields.mex:label.value",
    "custom_fields.mex:valueSet",
    "index_data.belongsToLabel",
    "index_data.contributors",
    "index_data.creators",
    "index_data.deFunderOrCommissioners",
    "index_data.enFunderOrCommissioners",
    "index_data.deUsedInResource",
    "index_data.enUsedInResource",
    "index_data.deVariableGroups.value",
    "index_data.enVariableGroups.value",
    "index_data.externalAssociates",
    "index_data.externalPartners",
    "index_data.involvedPersons",
    "index_data.enContributingUnits",
    "index_data.deContributingUnits"
]


class MexDumper(SearchDumper):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._record_cache = {}

    def dump(self, record, data):
        dump_data = super().dump(record, data)

        # Initialize display_data if it doesn't exist
        if "display_data" not in dump_data:
            dump_data["display_data"] = {}

        # Initialize index_data if it doesn't exist
        if "index_data" not in dump_data:
            dump_data["index_data"] = {}
        dump_data["index_data"]["index_generated"] = datetime.utcnow().strftime(
            "%Y-%m-%dT%H:%M:%S"
        )

        # CACHE INVALIDATION: Clear cache entry for the current record being dumped
        # This ensures that when a record is updated, other records that reference it
        # will fetch fresh data instead of stale cached data
        current_mex_id = record.get("custom_fields", {}).get("mex:identifier")
        if current_mex_id and current_mex_id in self._record_cache:
            del self._record_cache[current_mex_id]

        log = []
        # log.append("###############MEX Dumper##################")
        # log.append("Record ID: " + record.get("id"))
        # log.append(json.dumps(record.get("custom_fields", {})))
        # log.append(json.dumps(dump_data.get("custom_fields", {})))

        # Generate linked records data and add to display_data
        self._linked_records_data(record, dump_data, log)
        self._belongs_to(record, dump_data, log)
        self._contributors(record, dump_data, log)
        self._creators(record, dump_data, log)
        self._external_partners(record, dump_data, log)
        self._external_associates(record, dump_data, log)
        self._funder_commissioner(record, dump_data, log)
        self._involved_persons(record, dump_data, log)
        self._used_in(record, dump_data, log)
        self._resource_variables_groups(record, dump_data, log)
        self._contributing_unit(record, dump_data, log)

        # log.append("**************************************")
        # log.append("Display data:")
        # log.append(json.dumps(dump_data.get("display_data", {})))
        # log.append("**************************************")

        # Generate free-text search bucket
        self._generate_sort_fields(record, dump_data, log)

        # PERFORMANCE FIX: Do NOT clear cache after processing
        # Cache should persist across records to avoid redundant database queries
        # self._record_cache = {}
        # log.append("Dumped custom fields:")
        # log.append(json.dumps(dump_data.get("custom_fields", {})))
        # log.append("###############//MEX Dumper##################")
        # print("\n".join(log))
        return dump_data

    def _get_custom_field_list(self, record, field_name):
        """Helper function to retrieve a list of custom field values from a record."""
        custom_fields = record.get("custom_fields", {})
        field_value = custom_fields.get(field_name, [])
        if not isinstance(field_value, list):
            field_value = [field_value]
        return field_value

    def _get_person_names(self, record):
        full_names = self._get_custom_field_list(record.json, "mex:fullName")
        family_names = self._get_custom_field_list(record.json, "mex:familyName")
        return full_names + family_names

    def _get_organisation_names(self, record):
        official_names = self._get_custom_field_list(record.json, "mex:officialName")
        alternative_names = self._get_custom_field_list(
            record.json, "mex:alternativeName"
        )
        short_names = self._get_custom_field_list(record.json, "mex:shortName")
        general_name = self._get_custom_field_list(record.json, "mex:name")
        return official_names + alternative_names + short_names + general_name

    def _get_all_possible_names(self, record):
        person = self._get_person_names(record)
        organisation = self._get_organisation_names(record)

        name_complex = person + organisation

        name_simple = []
        for name in name_complex:
            if isinstance(name, dict) and "value" in name:
                name_simple.append(name["value"])
            elif isinstance(name, str):
                name_simple.append(name)

        return list(set(name_simple))

    def _split_by_language(self, objs):
        required = ["de", "en"]
        split = {}
        default = ""

        # first extract all the language values, grabbing the first one
        # that we see as a default value for use later if needed
        for obj in objs:
            value = obj.get("value", "")
            lang = obj.get("language", "en")
            split[lang] = value
            default = value

        # determine if any of our required languages are missing
        # and record those that are
        has_empty = []
        for lang in required:
            if lang not in split:
                split[lang] = None
                has_empty.append(lang)

        # if there are required languages missing, try to patch them
        if len(has_empty) > 0:
            # find out which languages are actually available to us
            available = set(required) - set(has_empty)
            patched = False
            # first patch from the required languages, in order of preference
            for lang in required:
                if lang in available:
                    patched = True
                    existing = split[lang]
                    for empty in has_empty:
                        split[empty] = existing

            # if we could not patch from required languages, use the default
            if not patched:
                for empty in has_empty:
                    split[empty] = default

        return split

    def _resource_variables_groups(self, record, dump_data, log):
        if record.get("metadata", {}).get("resource_type", {}).get("id") != "resource":
            log.append("Not a resource type, skipping resource variable groups")
            return

        mex_id = record.get("custom_fields", {}).get("mex:identifier", None)
        if not mex_id:
            log.append("No mex:identifier found, skipping resource variable groups")
            return

        groups = self._records_by_custom_field(record, "mex:containedBy", mex_id, log)
        log.append("Resource Variables Groups found: " + str(len(groups)))

        enGroups = []
        deGroups = []
        for group in groups:
            vg_id = group.json.get("custom_fields", {}).get("mex:identifier", None)
            labels = group.json.get("custom_fields", {}).get("mex:label", [])
            split = self._split_by_language(labels)
            enGroups.append({"mex_id": vg_id, "value": split["en"]})
            deGroups.append({"mex_id": vg_id, "value": split["de"]})

        if len(enGroups) > 0:
            dump_data["index_data"]["enVariableGroups"] = enGroups
            log.append("Resource Variables Groups EN:" + str(enGroups))

        if len(deGroups) > 0:
            dump_data["index_data"]["deVariableGroups"] = deGroups
            log.append("Resource Variables Groups DE:" + str(deGroups))

    def _belongs_to(self, record, dump_data, log):
        belongs_to_labels = []
        belongs_to_ids = self._get_custom_field_list(record, "mex:belongsTo")

        if len(belongs_to_ids) == 0:
            return

        log.append("Belongs to IDs:" + str(belongs_to_ids))

        results = self._records_by_mex_identifiers(record, belongs_to_ids, log)
        log.append("Belongs to results:" + str(len(results)))

        for result in results:
            labels = result.json.get("custom_fields", {}).get("mex:label", [])
            for label in labels:
                val = label.get("value", "")
                if val != "" and val not in belongs_to_labels:
                    belongs_to_labels.append(val)

        if len(belongs_to_labels) > 0:
            dump_data["index_data"]["belongsToLabel"] = belongs_to_labels
            log.append("Belongs to labels:" + str(belongs_to_labels))

    def _contributors(self, record, dump_data, log):
        contributors = []
        contributor_ids = self._get_custom_field_list(record, "mex:contributor")

        if len(contributor_ids) == 0:
            return

        log.append("Contributor IDs:" + str(contributor_ids))

        results = self._records_by_mex_identifiers(record, contributor_ids, log)
        log.append("Contributor results:" + str(len(results)))

        for contributor in results:
            contributors.extend(self._get_all_possible_names(contributor))

        log.append("Contributors:" + str(contributors))
        dump_data["index_data"]["contributors"] = contributors

    def _creators(self, record, dump_data, log):
        creators = []
        creator_ids = self._get_custom_field_list(record, "mex:creator")

        if len(creator_ids) == 0:
            return

        log.append("Creator IDs:" + str(creator_ids))

        results = self._records_by_mex_identifiers(record, creator_ids, log)
        log.append("Creator results:" + str(len(results)))

        for creator in results:
            creators.extend(self._get_all_possible_names(creator))

        log.append("Creators:" + str(creators))
        dump_data["index_data"]["creators"] = creators

    def _external_partners(self, record, dump_data, log):
        external_partners = []
        partner_ids = self._get_custom_field_list(record, "mex:externalPartner")

        if len(partner_ids) == 0:
            return

        log.append("External Partner IDs:" + str(partner_ids))

        results = self._records_by_mex_identifiers(record, partner_ids, log)
        log.append("External Partner results:" + str(len(results)))

        for partner in results:
            external_partners.extend(self._get_all_possible_names(partner))

        # external_partners = [ep["value"] for ep in external_partners if isinstance(ep, dict) and "value" in ep]
        log.append("External Partners:" + str(external_partners))
        dump_data["index_data"]["externalPartners"] = external_partners

    def _external_associates(self, record, dump_data, log):
        external_associates = []
        associates = self._get_custom_field_list(record, "mex:externalAssociate")
        if len(associates) == 0:
            return

        log.append("External Associate IDs:" + str(associates))

        results = self._records_by_mex_identifiers(record, associates, log)
        log.append("External Associate results:" + str(len(results)))

        for associate in results:
            external_associates.extend(self._get_all_possible_names(associate))

        # external_associates = [ep["value"] for ep in external_associates if isinstance(ep, dict) and "value" in ep]
        log.append("External Associates:" + str(external_associates))
        dump_data["index_data"]["externalAssociates"] = external_associates

    def _funder_commissioner(self, record, dump_data, log):
        funder_ids = self._get_custom_field_list(record, "mex:funderOrCommissioner")

        if len(funder_ids) == 0:
            return

        log.append("Funder or Commissioner IDs:" + str(funder_ids))

        results = self._records_by_mex_identifiers(record, funder_ids, log)
        log.append("Funder or Commissioner results:" + str(len(results)))

        funder_commissioners = []
        for funder in results:
            official_names = self._get_custom_field_list(
                funder.json, "mex:officialName"
            )
            lang_names = self._split_by_language(official_names)
            funder_commissioners.append(lang_names)

        funder_commissioners_en = [fc["en"] for fc in funder_commissioners]
        funder_commissioners_de = [fc["de"] for fc in funder_commissioners]

        # funder_commissioners_en = [
        #     fc["value"]
        #     for fc in funder_commissioners
        #     if isinstance(fc, dict) and "value" in fc and fc.get("language") == "en"
        # ]
        # funder_commissioners_de = [
        #     fc["value"]
        #     for fc in funder_commissioners
        #     if isinstance(fc, dict) and "value" in fc and fc.get("language") == "de"
        # ]

        log.append("Funder or Commissioner EN:" + str(funder_commissioners_en))
        log.append("Funder or Commissioner DE:" + str(funder_commissioners_de))

        if len(funder_commissioners_en) == 0:
            funder_commissioners_en = funder_commissioners_de
        if len(funder_commissioners_de) == 0:
            funder_commissioners_de = funder_commissioners_en

        if len(funder_commissioners_de) > 0:
            dump_data["index_data"]["deFunderOrCommissioners"] = funder_commissioners_de

        if len(funder_commissioners_en) > 0:
            dump_data["index_data"]["enFunderOrCommissioners"] = funder_commissioners_en

    def _involved_persons(self, record, dump_data, log):
        involved_persons = []
        person_ids = self._get_custom_field_list(record, "mex:involvedPerson")

        if len(person_ids) == 0:
            return

        log.append("Involved Person IDs:" + str(person_ids))

        results = self._records_by_mex_identifiers(record, person_ids, log)
        log.append("Involved Person results:" + str(len(results)))

        for person in results:
            involved_persons.extend(self._get_all_possible_names(person))

        log.append("Involved Persons:" + str(involved_persons))
        dump_data["index_data"]["involvedPersons"] = involved_persons

    def _used_in(self, record, dump_data, log):
        used_in_ids = self._get_custom_field_list(record, "mex:usedIn")

        if len(used_in_ids) == 0:
            return

        log.append("Used in IDs:" + str(used_in_ids))

        results = self._records_by_mex_identifiers(record, used_in_ids, log)
        log.append("Used in results:" + str(len(results)))

        used_in_en = []
        used_in_de = []
        for result in results:
            titles = result.json.get("custom_fields", {}).get("mex:title", [])
            lang_titles = self._split_by_language(titles)
            used_in_en.append(lang_titles["en"])
            used_in_de.append(lang_titles["de"])
            # for title in titles:
            #     lang = title.get("language", "en")
            #     val = title.get("value", "")
            #
            #     if title.get("language", "en") == "en":
            #         used_in_en.append(val)
            #     elif title.get("language", "de") == "de":
            #         used_in_de.append(val)

        log.append("Used in EN:" + str(used_in_en))
        log.append("Used in DE:" + str(used_in_de))

        if len(used_in_en) == 0:
            used_in_en = used_in_de
        if len(used_in_de) == 0:
            used_in_de = used_in_en

        if len(used_in_en) > 0:
            dump_data["index_data"]["enUsedInResource"] = used_in_en

        if len(used_in_de) > 0:
            dump_data["index_data"]["deUsedInResource"] = used_in_de

    def _contributing_unit(self, record, dump_data, log):
        unit_ids = self._get_custom_field_list(record, "mex:contributingUnit")

        if len(unit_ids) == 0:
            return

        log.append("Contributing Unit IDs:" + str(unit_ids))

        results = self._records_by_mex_identifiers(record, unit_ids, log)
        log.append("Contributing Unit results:" + str(len(results)))

        units = []
        for unit in results:
            official_names = self._get_custom_field_list(
                unit.json, "mex:name"
            )
            lang_names = self._split_by_language(official_names)
            units.append(lang_names)

        units_en = [fc["en"] for fc in units]
        units_de = [fc["de"] for fc in units]

        log.append("Contributing Units EN:" + str(units_en))
        log.append("Contributing Units DE:" + str(units_de))

        if len(units_en) == 0:
            units_en = units_de
        if len(units_de) == 0:
            units_de = units_en

        if len(units_de) > 0:
            dump_data["index_data"]["deContributingUnits"] = units_de

        if len(units_en) > 0:
            dump_data["index_data"]["enContributingUnits"] = units_en

    def _records_by_mex_identifiers(self, source, mex_ids, log):
        results = []

        query_for = []
        for mex_id in mex_ids:
            if self._record_cache.get(mex_id):
                # log.append("Cache hit for MEx ID: " + mex_id)
                results.append(self._record_cache[mex_id])
            else:
                query_for.append(mex_id)

        if len(query_for) == 0:
            return results

        # log.append("Querying for MEx IDs: " + str(query_for))
        db_query = source.model_cls.query.filter(
            source.model_cls.json["custom_fields"]
            .op("->>")("mex:identifier")
            .in_(query_for),
        )
        db_results = db_query.all()
        # log.append("DB results found: " + str(len(db_results)))

        for res in db_results:
            mex_id = res.json.get("custom_fields", {}).get("mex:identifier")
            self._record_cache[mex_id] = res
            results.append(res)

        return results

    def _records_by_custom_field(self, source, name, value, log):
        # PERFORMANCE FIX: Use @> (contains) operator instead of ? (key exists) operator
        # The @> operator uses the GIN index on custom_fields, providing ~4000x speedup

        # Check if the field is configured as multiple=True (array field)
        from sqlalchemy import cast
        from sqlalchemy.dialects.postgresql import JSONB

        from mex_invenio.custom_fields.custom_fields import RDM_CUSTOM_FIELDS

        field_config = None
        for field in RDM_CUSTOM_FIELDS:
            if field.name == name:
                field_config = field
                break

        # Determine if field stores arrays or single values
        is_multiple = (
            getattr(field_config, "_multiple", False) if field_config else True
        )

        # For array fields (multiple=True), match array structure: {"field": ["value"]}
        # For single-value fields, match plain value: {"field": "value"}
        # Use .op('@>') to explicitly use the JSONB containment operator
        if is_multiple:
            # Array field: wrap value in array
            db_query = source.model_cls.query.filter(
                source.model_cls.json["custom_fields"].op("@>")(
                    cast({name: [value]}, JSONB)
                )
            )
        else:
            # Single-value field: use plain value
            db_query = source.model_cls.query.filter(
                source.model_cls.json["custom_fields"].op("@>")(
                    cast({name: value}, JSONB)
                )
            )

        return db_query.all()

    def _generate_sort_fields(self, record, dump_data, log):
        # titles
        titles = record.get("custom_fields", {}).get("mex:title", [])
        values = [
            title.get("value")
            for title in titles
            if isinstance(title, dict) and "value" in title
        ]
        dump_data["index_data"]["title_sort"] = values

        # labels
        labels = record.get("custom_fields", {}).get("mex:label", [])
        values = [
            label.get("value")
            for label in labels
            if isinstance(label, dict) and "value" in label
        ]
        dump_data["index_data"]["label_sort"] = values

    def _linked_records_data(self, record, dump_data, log):
        """Generate linked records data and add to display_data."""
        record_type = record.get("metadata", {}).get("resource_type", {}).get("id", "")
        if not record_type:
            # log.append("No resource type found, skipping linked records data")
            return

        # Get the record type to determine which fields to process
        FIELDS_LINKED_BACKWARDS = current_app.config.get("FIELDS_LINKED_BACKWARDS", {})

        # if not FIELDS_LINKED_BACKWARDS:
        #    log.append("No backwards linked records configuration found")

        linked_records_data = {}

        linked_records = self._get_linked_records_for_dump(record, log)
        linked_records_data.update(linked_records)

        # Process backward-linked records
        mex_id = record.get("custom_fields", {}).get("mex:identifier")
        if mex_id and record_type in FIELDS_LINKED_BACKWARDS:
            field_items = FIELDS_LINKED_BACKWARDS[record_type]
            backwards_linked = self._get_records_linked_backwards_for_dump(
                record, mex_id, field_items, log
            )
            linked_records_data["backwards_linked"] = backwards_linked

        # Add the linked records data to display_data
        if linked_records_data:
            dump_data["display_data"]["linked_records"] = linked_records_data
            # log.append("Added linked records data to display_data")
            # log.append(str(linked_records_data))
            # log.append("-----------------------")
        # else:
        #    log.append("No linked records data generated")

    def _get_linked_records_for_dump(self, record, log):
        """Get forward-linked records for a record during dumping."""
        records_fields = {}
        cf = record.get("custom_fields", {})
        record_type = record.get("metadata", {}).get("resource_type", {}).get("id", "")
        linked_record_ids = []
        record_linked_fields = []

        # Collect all linked record IDs
        for field in cf:
            if (
                current_app.config["FIELD_TYPES"].get(record_type, {}).get(field, "")
                == "identifier"
            ):
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
        # print("linked_records: ", linked_records)
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

            # TODO
            # This check was reinserted after if became clear that single values
            # were being passed. Should this not happen after normalisation?
            linked_record_ids = (
                raw_value if isinstance(raw_value, list) else [raw_value]
            )
            field_values = []

            for linked_record_id in linked_record_ids:
                display_value = False
                linked_record = linked_records_map.get(linked_record_id)

                field_value = {
                    "link_id": linked_record_id,
                }

                if linked_record:
                    record_type = (
                        linked_record.get("metadata", {})
                        .get("resource_type", {})
                        .get("id", None)
                    )

                    core_records = ["activity", "resource", "bibliographicresource"]
                    if record_type and record_type in core_records:
                        # print(f"Found core record: {record_type}")
                        field_value["core"] = record_type

                    # Try to find display value from props
                    if "TITLE_FIELDS" not in current_app.config:
                        # log.append(
                        #    "I don't know which fields are the titles; returning not changed."
                        # )
                        return records_fields
                    for title_field in current_app.config.get("TITLE_FIELDS", []):
                        if title_field in linked_record.get("custom_fields", {}):
                            display_value = linked_record["custom_fields"][title_field]
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

            if field_values:
                records_fields[field] = field_values

        return records_fields

    def _get_records_linked_backwards_for_dump(self, record, mex_id, field_items, log):
        """Get backward-linked records for a record during dumping."""
        records_fields = {}

        for field in field_items:
            # Find records that reference this mex_id in the given field
            # print("field: ", field)
            linked_records = self._records_by_custom_field(record, field, mex_id, log)
            # print("linked_records: ", linked_records)

            if not linked_records:
                continue

            field_values = []
            for r in linked_records:
                display_value = None
                record_json = r.json if hasattr(r, "json") else r
                # print("record_json: ", record_json)

                record_type = (
                    record_json.get("metadata", {})
                    .get("resource_type", {})
                    .get("id", None)
                )

                core_records = ["activity", "resource", "bibliographicresource"]
                record_core = None
                if record_type and record_type in core_records:
                    # print(f"Found core record: {record_type}")
                    record_core = record_type

                if "TITLE_FIELDS" not in current_app.config:
                    # log.append(
                    #    "I don't know which fields are the titles; returning not changed."
                    # )
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
                                "core": record_core or "",
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
                            "core": record_core or "",
                        }
                    )

            if field_values:
                records_fields[field] = field_values

        return records_fields
