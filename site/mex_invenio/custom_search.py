from invenio_rdm_records.services.config import SearchOptions
from invenio_records_resources.services.base.config import SearchOptionsMixin
from invenio_search import RecordsSearchV2
from invenio_records_resources.services.records.queryparser import QueryParser
from invenio_records.dumpers import SearchDumper
import json

from mex_invenio.custom_params import (
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
        HighlightParamsInterpreter
        # Add other interpreters as needed
    ]

class MexDumper(SearchDumper):
    def dump(self, record, data):
        dump_data = super(MexDumper, self).dump(record, data)

        self._record_cache = {}

        log = []
        log.append("###############MEX Dumper##################")
        log.append("Record ID:" + record.get("id"))
        log.append(json.dumps(record.metadata))

        self._belongs_to(record, dump_data, log)
        # self._contributors(record, dump_data)
        # self._creators(record, dump_data)
        # self._external_partners(record, dump_data)
        # self._external_associates(record, dump_data)
        # self._funder_commissioner(record, dump_data)

        self._record_cache = {}
        log.append("###############//MEX Dumper##################")
        print("\n".join(log))
        return dump_data

    def _belongs_to(self, record, dump_data, log):
        belongs_to_labels = []
        belongs_to_ids = record.get("custom_fields", {}).get("mex:belongsTo", [])

        if len(belongs_to_ids) == 0:
            return

        # print("###############belongs to##################")
        # print("Record ID:", record.get("id"))
        log.append("Belongs to IDs:" + str(belongs_to_ids))

        results = self._records_by_mex_identifiers(record, belongs_to_ids)
        log.append("Belongs to results:" + str(len(results)))

        # belongs_to_records = select(record.model_cls).where(record.model_cls.json["custom_fields"]["mex:identifier"] == belongs_to_ids[0])
        # belongs_to_records = record.model_cls.query.filter(
        #     record.model_cls.json["custom_fields"].op("->>")("mex:identifier") == belongs_to_ids[0],
        # )
        # print(belongs_to_records.statement)
        # belongs_to_records = belongs_to_records.all()

        for result in results:
            log.append(json.dumps(result.json))
            cfs = result.json.get("custom_fields", {})
            log.append("Custom fields:" + str(cfs))
            labels = cfs.get("mex:label", [])
            log.append("Labels:" + str(labels))
            for label in labels:
                val = label.get("value", "")
                log.append("Label value:" + str(val))
                if val != "" and val not in belongs_to_labels:
                    belongs_to_labels.append(val)

        if len(belongs_to_labels) > 0:
            dump_data["custom_fields"]["index:belongsToLabel"] = belongs_to_labels
            log.append("Belongs to labels:" + str(belongs_to_labels))

    def _contributors(self, record, dump_data):
        contributors = []
        contributor_ids = record.get("custom_fields", {}).get("mex:contributor", [])
        if not isinstance(contributor_ids, list):
            contributor_ids = [contributor_ids]

        for contributor_id in contributor_ids:
            contributor = self._record_by_mex_identifier(contributor_id)
            if contributor:
                full_names = contributor.get("custom_fields", {}).get("mex:fullName", [])
                family_names = contributor.get("custom_fields", {}).get("mex:familyName", [])
                contributors += full_names + family_names

        dump_data["custom_fields"]["index:contributors"] = contributors

    def _creators(self, record, dump_data):
        creators = []
        creator_ids = record.get("custom_fields", {}).get("mex:creator", [])
        if not isinstance(creator_ids, list):
            creator_ids = [creator_ids]

        for creator_id in creator_ids:
            creator = self._record_by_mex_identifier(creator_id)
            if creator:
                full_names = creator.get("custom_fields", {}).get("mex:fullName", [])
                family_names = creator.get("custom_fields", {}).get("mex:familyName", [])
                creators += full_names + family_names

        dump_data["custom_fields"]["index:creators"] = creators

    def _external_partners(self, record, dump_data):
        external_partners = []
        partner_ids = record.get("custom_fields", {}).get("mex:externalPartner", [])
        if not isinstance(partner_ids, list):
            partner_ids = [partner_ids]

        for partner_id in partner_ids:
            partner = self._record_by_mex_identifier(partner_id)
            if partner:
                official_names = partner.get("custom_fields", {}).get("mex:officialName", [])
                alternative_names = partner.get("custom_fields", {}).get("mex:alternativeName", [])
                short_names = partner.get("custom_fields", {}).get("mex:shortName", [])
                external_partners += official_names + alternative_names + short_names

        external_partners = [ep["value"] for ep in external_partners if isinstance(ep, dict) and "value" in ep]
        dump_data["custom_fields"]["index:externalPartners"] = external_partners

    def _external_associates(self, record, dump_data):
        external_partners = []

        associates = record.get("custom_fields", {}).get("mex:externalAssociate", [])
        if not isinstance(associates, list):
            associates = [associates]

        # print("##############external associates##################")
        # print("Record ID:", record.get("id"))
        # print("Associate IDs:", associates)

        for partner_id in associates:
            partner = self._record_by_mex_identifier(partner_id)
            if partner:
                #print("Partner found:", partner.get("id"))
                official_names = partner.get("custom_fields", {}).get("mex:officialName", [])
                alternative_names = partner.get("custom_fields", {}).get("mex:alternativeName", [])
                short_names = partner.get("custom_fields", {}).get("mex:shortName", [])
                external_partners += official_names + alternative_names + short_names
            else:
                pass
                #print("No partner found for ID:", partner_id)

        #print("Dereferenced:", external_partners)

        external_partners = [ep["value"] for ep in external_partners if isinstance(ep, dict) and "value" in ep]
        #print("Final external partners:", external_partners)
        dump_data["custom_fields"]["index:externalAssociates"] = external_partners

    def _funder_commissioner(self, record, dump_data):
        funder_commissioners = []
        funder_ids = record.get("custom_fields", {}).get("mex:funderOrCommissioner", [])
        if not isinstance(funder_ids, list):
            funder_ids = [funder_ids]

        # print("##############funder or commissioner##################")
        # print("Record ID:", record.get("id"))
        # print("Associate IDs:", funder_ids)

        for funder_id in funder_ids:
            funder = self._record_by_mex_identifier(funder_id)
            if funder:
                #print("Funder found:", funder.get("id"))
                official_names = funder.get("custom_fields", {}).get("mex:officialName", [])
                funder_commissioners += official_names
            else:
                pass
                #print("No funder found for ID:", funder_id)

        #print("Dereferenced:", funder_commissioners)

        funder_commissioners_en = [fc["value"] for fc in funder_commissioners if isinstance(fc, dict) and "value" in fc and fc.get("language") == "en"]
        funder_commissioners_de = [fc["value"] for fc in funder_commissioners if isinstance(fc, dict) and "value" in fc and fc.get("language") == "de"]
        #print("Final funder or commissioner (EN):", funder_commissioners_en)
        #print("Final funder or commissioner (DE):", funder_commissioners_de)
        dump_data["custom_fields"]["index:deFunderOrCommissioners"] = funder_commissioners_de
        dump_data["custom_fields"]["index:enFunderOrCommissioners"] = funder_commissioners_en

    def _records_by_mex_identifiers(self, source, mex_ids):
        results = []

        query_for = []
        for mex_id in mex_ids:
            if self._record_cache.get(mex_id):
                results.append(self._record_cache[mex_id])
            else:
                query_for.append(mex_id)

        if len(query_for) == 0:
            return results

        db_query = source.model_cls.query.filter(
            source.model_cls.json["custom_fields"].op("->>")("mex:identifier").in_(query_for),
        )
        # print(belongs_to_records.statement)
        db_results = db_query.all()

        for res in db_results:
            mex_id = res.json.get("custom_fields", {}).get("mex:identifier")
            self._record_cache[mex_id] = res
            results.append(res)

        return results

