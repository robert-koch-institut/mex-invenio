import json, urllib.parse

from flask import Blueprint, redirect, url_for, current_app, abort, render_template, make_response, jsonify, request
from invenio_access.permissions import system_identity
from invenio_rdm_records.services.config import SearchOptions
from invenio_rdm_records import InvenioRDMRecords
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.services import RDMRecordService
from invenio_records.dumpers import SearchDumperExt
from invenio_records_resources.services.base.config import SearchOptionsMixin
from invenio_records_resources.services.records.params import ParamInterpreter
from invenio_records_resources.services.records.queryparser import QueryParser
from invenio_search import current_search, RecordsSearch, RecordsSearchV2
from speaklater import _LazyString

from .record.record import MexRecord

from invenio_pidstore.resolver import Resolver
from invenio_pidstore.errors import (
    PIDDoesNotExistError,
    PIDMissingObjectError,
    PIDUnregistered,
)
from invenio_rdm_records.records.api import RDMRecord

import opensearch_dsl as dsl

#
# Registration
#
def create_blueprint(app):
    """Register blueprint routes on app."""
    blueprint = Blueprint(
        "mex_invenio",
        __name__,
        template_folder="./templates",
    )

    # Ideally we would overwrite /records/<record_id>, however blueprints are loaded
    # in a non-deterministic way. Therefore, there is a redirect in the nginx config
    # that redirects /records/<record_id> to /records/pid/<record_id>.
    # see (/docker/nginx/conf.d/default.conf)
    blueprint.add_url_rule(
        "/records/pid/<record_id>",
        view_func=redirect_to_mex,
    )

    blueprint.add_url_rule(
        "/records/mex/<mex_id>",
        view_func=MexRecord.as_view("mex_view"),
    )

    blueprint.add_url_rule(
        "/search/variables",
        view_func=search_variables
    )

    blueprint.add_url_rule(
        "/search/bibliographic-resources",
        view_func=search_bibliographic_resources
    )

    blueprint.add_url_rule(
        "/search/api/bibliographic-resources",
        view_func=search_api
    )

    return blueprint

def search_variables():
    return render_template("mex_invenio/search/variables.html")

def search_bibliographic_resources():
    return render_template("mex_invenio/search/bibliographic-resources.html")

class GenericQueryParamsInterpreter(ParamInterpreter):
    def apply(self, identity, search, params):
        """Apply generic query parameters to the search."""
        # This is a placeholder for any generic query parameter handling
        # that might be needed in the future.
        return search.from_dict(params["raw"])

class TypeLimiterParamsInterpreter(ParamInterpreter):
    def apply(self, identity, search, params):
        """Apply type limiter to the search."""
        resource_type = params.get("resource_type")
        if resource_type:
            search = search.filter("term", metadata__resource_type__id=resource_type)
        print("#####################################")
        print(search.to_dict())
        return search

class CustomSearchOptions(SearchOptions, SearchOptionsMixin):
    search_cls = RecordsSearchV2
    query_parser_cls = QueryParser
    suggest_parser_cls = None
    # sort_default = "bestmatch"
    # sort_default_no_query = "newest"
    # sort_options = {
    #     "bestmatch": dict(
    #         title=_("Best match"),
    #         fields=["_score"],  # ES defaults to desc on `_score` field
    #     ),
    #     "newest": dict(
    #         title=_("Newest"),
    #         fields=["-created"],
    #     ),
    #     "oldest": dict(
    #         title=_("Oldest"),
    #         fields=["created"],
    #     ),
    # }
    facets = {}
    pagination_options = {"default_results_per_page": 25, "default_max_results": 10000}
    #params_interpreters_cls = [QueryStrParam, PaginationParam, SortParam, FacetsParam]
    params_interpreters_cls = [
        GenericQueryParamsInterpreter,
        TypeLimiterParamsInterpreter,
        # Add other interpreters as needed
    ]

from functools import wraps
def jsonp(f):
    """Wraps JSONified output for JSONP"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            content = str(callback) + '(' + str(f(*args, **kwargs).data.decode("utf-8")) + ')'
            return current_app.response_class(content, mimetype='application/javascript')
        else:
            return f(*args, **kwargs)
    return decorated_function

@jsonp
def search_api():
    q = None
    # if this is a POST, read the contents out of the body
    if request.method == "POST":
        q = request.json
    # if there is a source param, load the json from it
    elif 'source' in request.values:
        try:
            q = json.loads(urllib.parse.unquote(request.values['source']))
        except ValueError:
            abort(400)

    # q = {
    #     "query": {
    #         "bool": {
    #             "must": [
    #                 {
    #                     "term": {
    #                         "metadata.resource_type.id": "activity"
    #                     }
    #                 }
    #             ]
    #         }
    #     },
    #     "aggs": {
    #         "user": {
    #             "terms": {
    #                 "field": "parent.access.owned_by.user",
    #                 "size": 10
    #             }
    #         }
    #     },
    #     "size": 1
    # }

    #search_instance = dsl.Search.from_dict(q)

    search_opts = CustomSearchOptions()
    #search_opts.customize({})

    if q is None:
        # If no query is provided, use a match_all query
        q = {"query": {"match_all": {}}}
    # Define search parameters
    search_params = {
        "raw": q,
        "resource_type": "bibliographicresource"
        # "sort": None,
        # "size": 1,
        # "page": 1
    }

    # Perform the search
    # print("####################################")
    # print(current_rdm_records_service.config.record_cls.dumper)
    # print(current_rdm_records_service)
    # search_result = current_rdm_records_service.search(
    #     identity=system_identity,
    #     params=search_params
    # )

    search_result = current_rdm_records_service.search(identity=system_identity, params=search_params, search_opts=search_opts)

    print("####################################")
    print(search_result)

    print("####################################")
    print(search_result._results.to_dict())

    def custom_serialiser(obj):
        if isinstance(obj, _LazyString):
            return str(obj)

    # Access the search results
    result = search_result._results.to_dict()
    response = make_response(json.dumps(result, default=custom_serialiser), 200)
    response.headers["Content-Type"] = "application/json"
    return response

    #return hits

    #recordservice = current_rdm_records_service
    # from opensearch_dsl import Q
    # q = Q({"bool": {"must": [{"term": {"metadata.resource_type.id": "activity"}}]}})
    # todo = current_search.faceted_search(q)
    # res = todo.execute()
    # raw = res.response
    # response = make_response(json.dumps(raw), 200)
    # response.headers["Content-Type"] = "application/json"
    # return response

    #assert isinstance(recordservice, RDMRecordService)
    #recordservice.search(system_identity, q={"query": {"match_all": {}}})

def redirect_to_mex(record_id):
    record = None
    resolver = Resolver(
        pid_type="recid", object_type="rec", getter=RDMRecord.get_record
    )

    try:
        pid, record = resolver.resolve(record_id)
    except (PIDDoesNotExistError, PIDUnregistered):
        abort(404)
    except PIDMissingObjectError as e:
        current_app.logger.exception(
            "No object assigned to {0}.".format(e.pid), extra={"pid": e.pid}
        )
        abort(500)
    except Exception as e:
        current_app.logger.exception("Unknown error occurred.", extra={"error": e})
        abort(500)
    try:
        mex_id = record["custom_fields"]["mex:identifier"]
    except Exception as e:
        current_app.logger.exception("No mex id for the record {0}.".format(e))
        abort(500)

    return redirect(url_for(".mex_view", mex_id=mex_id))
