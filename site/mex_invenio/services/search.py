from invenio_rdm_records.services.config import SearchOptions
from invenio_records_resources.services.base.config import SearchOptionsMixin
from invenio_search import RecordsSearchV2
from invenio_records_resources.services.records.queryparser import QueryParser
from invenio_records.dumpers import SearchDumper
import json

from mex_invenio.search.params import (
    GenericQueryParamsInterpreter,
    TypeLimiterParamsInterpreter,
    HighlightParamsInterpreter,
)
# from mex_invenio.custom_record import MexRDMRecord


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
        # Add other interpreters as needed
    ]


class MexDumper(SearchDumper):
    def dump(self, record, data):
        dump_data = super(MexDumper, self).dump(record, data)

        # Initialize index_data if it doesn't exist
        if "index_data" not in dump_data:
            dump_data["index_data"] = {}

        self._record_cache = {}

        log = []
        # print(f"###############MEX Dumper##################")
        # print(f"Record ID: {record.get('id')}")
        # print(f"Dump data before processing: {list(dump_data.keys())}")
        log.append("###############MEX Dumper##################")
        log.append("Record ID: " + record.get("id"))
        log.append(json.dumps(record.get("custom_fields", {})))
        log.append(json.dumps(dump_data.get("custom_fields", {})))

        self._belongs_to(record, dump_data, log)
        self._contributors(record, dump_data, log)
        self._creators(record, dump_data, log)
        self._external_partners(record, dump_data, log)
        self._external_associates(record, dump_data, log)
        self._funder_commissioner(record, dump_data, log)
        self._involved_persons(record, dump_data, log)
        self._used_in(record, dump_data, log)
        self._resource_variables_groups(record, dump_data, log)

        # if "mex:start" in dump_data["custom_fields"]:
        #     log.append("Removing mex:start field " + str(dump_data["custom_fields"]["mex:start"]))
        #     #del dump_data["custom_fields"]["mex:start"]
        # if "mex:end" in dump_data["custom_fields"]:
        #     log.append("Removing mex:end field " + str(dump_data["custom_fields"]["mex:end"]))
        #     #del dump_data["custom_fields"]["mex:end"]
        # if "mex:publicationYear" in dump_data["custom_fields"]:
        #     log.append("Removing mex:publicationYear field " + str(dump_data["custom_fields"]["mex:publicationYear"]))
        #     #del dump_data["custom_fields"]["mex:publicationYear"]

        self._record_cache = {}
        log.append("Dumped custom fields:")
        log.append(json.dumps(dump_data.get("custom_fields", {})))
        log.append("###############//MEX Dumper##################")
        print("\n".join(log))
        # print(f"Dump data after processing: {list(dump_data.keys())}")
        # if "index_data" in dump_data:
        #     print(f"index_data contents: {list(dump_data['index_data'].keys())}")
        # print("###############//MEX Dumper##################")
        return dump_data

    def _get_custom_field_list(self, record, field_name):
        """
        Helper function to retrieve a list of custom field values from a record.
        """
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
        return official_names + alternative_names + short_names

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
            labels = group.json.get("custom_fields", {}).get("mex:label", [])
            en = ""
            de = ""
            for label in labels:
                val = label.get("value", "")
                lang = label.get("language", "en")
                if lang == "en":
                    en = val
                elif lang == "de":
                    de = val

            if en != "":
                enGroups.append(en)
            if de != "":
                deGroups.append(de)

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
        funder_commissioners = []
        funder_ids = self._get_custom_field_list(record, "mex:funderOrCommissioner")

        if len(funder_ids) == 0:
            return

        log.append("Funder or Commissioner IDs:" + str(funder_ids))

        results = self._records_by_mex_identifiers(record, funder_ids, log)
        log.append("Funder or Commissioner results:" + str(len(results)))

        for funder in results:
            official_names = self._get_custom_field_list(
                funder.json, "mex:officialName"
            )
            funder_commissioners += official_names

        funder_commissioners_en = [
            fc["value"]
            for fc in funder_commissioners
            if isinstance(fc, dict) and "value" in fc and fc.get("language") == "en"
        ]
        funder_commissioners_de = [
            fc["value"]
            for fc in funder_commissioners
            if isinstance(fc, dict) and "value" in fc and fc.get("language") == "de"
        ]

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
        used_in_en = []
        used_in_de = []
        used_in_ids = self._get_custom_field_list(record, "mex:usedIn")

        if len(used_in_ids) == 0:
            return

        log.append("Used in IDs:" + str(used_in_ids))

        results = self._records_by_mex_identifiers(record, used_in_ids, log)
        log.append("Used in results:" + str(len(results)))

        for result in results:
            titles = result.json.get("custom_fields", {}).get("mex:title", [])
            for title in titles:
                val = title.get("value", "")
                if title.get("language", "en") == "en":
                    used_in_en.append(val)
                elif title.get("language", "de") == "de":
                    used_in_de.append(val)

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
        # from sqlalchemy import select, func, or_
        # db_query = select(source.model_cls).where(
        #     or_(
        #         source.model_cls.json["custom_fields"].op("->>")(name) == value,
        #         func.exists(
        #             select(1).where(
        #                 func.jsonb_array_elements_text(
        #                     source.model_cls.json["custom_fields"][name]
        #                 ) == value
        #             )
        #         )
        #     )
        # )

        # from sqlalchemy import or_, func, select
        # db_query = source.model_cls.query.filter(
        #     or_(
        #         source.model_cls.json["custom_fields"].op("->>")(name) == value,
        #         source.model_cls.json["custom_fields"][name].contains(value)
        #     )
        # )

        from sqlalchemy import or_, func, select
        db_query = source.model_cls.query.filter(
            source.model_cls.json["custom_fields"][name].op("?")(value)
        )

        from sqlalchemy.dialects import postgresql
        log.append(str(db_query.statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})))
        # db_query = source.model_cls.query.filter(
        #     source.model_cls.json["custom_fields"]
        #     .op("->>")(name)
        #     .in_([value]),
        # )
        db_results = db_query.all()
        log.append("DB results found: " + str(len(db_results)))

        return db_results
