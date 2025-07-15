from invenio_rdm_records.services.config import SearchOptions
from invenio_records_resources.services.base.config import SearchOptionsMixin
from invenio_search import RecordsSearchV2
from invenio_records_resources.services.records.queryparser import QueryParser
from invenio_records.dumpers import SearchDumper
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_access.permissions import system_identity

from mex_invenio.custom_params import (
    GenericQueryParamsInterpreter,
    TypeLimiterParamsInterpreter,
    HighlightParamsInterpreter,
)

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

        self._belongs_to(record, dump_data)
        self._contributors(record, dump_data)
        self._creators(record, dump_data)
        self._external_partners(record, dump_data)
        self._external_associates(record, dump_data)
        self._funder_commissioner(record, dump_data)

        self._record_cache = {}
        return dump_data

    def _belongs_to(self, record, dump_data):
        belongs_to_labels = []
        belongs_to_ids = record.get("custom_fields", {}).get("mex:belongsTo", [])

        for belongs_to_id in belongs_to_ids:
            belongs_to = self._record_by_mex_identifier(belongs_to_id)
            if belongs_to:
                labels = belongs_to.get("custom_fields", {}).get("mex:label", [])
                for label in labels:
                    val = label.get("value", "")
                    if val != "" and val not in belongs_to_labels:
                        belongs_to_labels.append(val)

        if len(belongs_to_labels) > 0:
            dump_data["custom_fields"]["index:belongsToLabel"] = belongs_to_labels

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

        print("##############external associates##################")
        print("Record ID:", record.get("id"))
        print("Associate IDs:", associates)

        for partner_id in associates:
            partner = self._record_by_mex_identifier(partner_id)
            if partner:
                print("Partner found:", partner.get("id"))
                official_names = partner.get("custom_fields", {}).get("mex:officialName", [])
                alternative_names = partner.get("custom_fields", {}).get("mex:alternativeName", [])
                short_names = partner.get("custom_fields", {}).get("mex:shortName", [])
                external_partners += official_names + alternative_names + short_names
            else:
                print("No partner found for ID:", partner_id)

        print("Dereferenced:", external_partners)

        external_partners = [ep["value"] for ep in external_partners if isinstance(ep, dict) and "value" in ep]
        print("Final external partners:", external_partners)
        dump_data["custom_fields"]["index:externalAssociates"] = external_partners

    def _funder_commissioner(self, record, dump_data):
        funder_commissioners = []
        funder_ids = record.get("custom_fields", {}).get("mex:funderOrCommissioner", [])
        if not isinstance(funder_ids, list):
            funder_ids = [funder_ids]

        print("##############funder or commissioner##################")
        print("Record ID:", record.get("id"))
        print("Associate IDs:", funder_ids)

        for funder_id in funder_ids:
            funder = self._record_by_mex_identifier(funder_id)
            if funder:
                print("Funder found:", funder.get("id"))
                official_names = funder.get("custom_fields", {}).get("mex:officialName", [])
                funder_commissioners += official_names
            else:
                print("No funder found for ID:", funder_id)

        print("Dereferenced:", funder_commissioners)

        funder_commissioners_en = [fc["value"] for fc in funder_commissioners if isinstance(fc, dict) and "value" in fc and fc.get("language") == "en"]
        funder_commissioners_de = [fc["value"] for fc in funder_commissioners if isinstance(fc, dict) and "value" in fc and fc.get("language") == "de"]
        print("Final funder or commissioner (EN):", funder_commissioners_en)
        print("Final funder or commissioner (DE):", funder_commissioners_de)
        dump_data["custom_fields"]["index:deFunderOrCommissioners"] = funder_commissioners_de
        dump_data["custom_fields"]["index:enFunderOrCommissioners"] = funder_commissioners_en

    def _record_by_mex_identifier(self, mex_id, resource_type=None):
        if mex_id in self._record_cache:
            return self._record_cache[mex_id]

        q = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"custom_fields.mex:identifier.keyword": {"value": mex_id}}}
                    ]
                }
            }
        }

        search_opts = MexSearchOptions()
        search_params = {
            "raw": q,
            "resource_type": resource_type
        }
        search_result = current_rdm_records_service.search(
            identity=system_identity,
            params=search_params,
            search_opts=search_opts)

        record = None
        for hit in search_result.hits:
            record = hit
            break

        self._record_cache[mex_id] = record
        return record

