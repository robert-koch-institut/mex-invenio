from invenio_rdm_records.services.config import SearchOptions
from invenio_records_resources.services.base.config import SearchOptionsMixin
from invenio_search import RecordsSearchV2
from invenio_records_resources.services.records.queryparser import QueryParser
from invenio_records.dumpers import SearchDumper

from mex_invenio.custom_params import (
    GenericQueryParamsInterpreter,
    TypeLimiterParamsInterpreter,
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
        # Add other interpreters as needed
    ]

class MexDumper(SearchDumper):
    def dump(self, record, data):
        dump_data = super(MexDumper, self).dump(record, data)
        # dump_data["custom_fields"]["index_test"] = "Just testing"
        return dump_data