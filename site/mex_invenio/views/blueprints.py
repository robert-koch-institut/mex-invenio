import json, urllib.parse
from functools import wraps

from flask import (
    Blueprint,
    redirect,
    url_for,
    current_app,
    abort,
    render_template,
    make_response,
    jsonify,
    request,
)
from invenio_access.permissions import system_identity

from invenio_rdm_records.proxies import current_rdm_records_service
from .record import MexRecord

from invenio_pidstore.resolver import Resolver
from invenio_pidstore.errors import (
    PIDDoesNotExistError,
    PIDMissingObjectError,
    PIDUnregistered,
)
from invenio_rdm_records.records.api import RDMRecord
from mex_invenio.services.search import MexSearchOptions


# Decorator which can be used to wrap a function to return JSONP responses.
def jsonp(f):
    """Wraps JSONified output for JSONP"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        callback = request.args.get("callback", False)
        if callback:
            content = (
                str(callback) + "(" + str(f(*args, **kwargs).data.decode("utf-8")) + ")"
            )
            return current_app.response_class(
                content, mimetype="application/javascript"
            )
        else:
            return f(*args, **kwargs)

    return decorated_function


#
# Registration
#
def create_blueprint(app):
    """Register blueprint routes on app."""
    blueprint = Blueprint(
        "mex_invenio",
        __name__,
        template_folder="../templates",
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

    blueprint.add_url_rule("/search/activities", view_func=search_activities)

    blueprint.add_url_rule(
        "/search/bibliographic-resources", view_func=search_bibliographic_resources
    )

    blueprint.add_url_rule(
        "/search/activities-bibliographic-resources",
        view_func=search_activities_bibliographic_resources,
    )

    blueprint.add_url_rule("/search/resources", view_func=search_resources)

    blueprint.add_url_rule("/search/variables", view_func=search_variables)

    blueprint.add_url_rule("/query/api/<resource_type>", view_func=os_query_api)

    return blueprint


def search_activities():
    return render_template("mex_invenio/search/activities.html")


def search_bibliographic_resources():
    return render_template("mex_invenio/search/bibliographic-resources.html")


def search_activities_bibliographic_resources():
    return render_template("mex_invenio/search/activities-bibliographic-resources.html")


def search_resources():
    return render_template("mex_invenio/search/resources.html")


def search_variables():
    return render_template("mex_invenio/search/variables.html")


# mapping from URL query arguments on the /query/api/<resource_type> endpoint
# to the resource_type used in the OpenSearch query.
URL_RESOURCE_TYPE_MAP = {
    "bibliographic-resources": "bibliographicresource",
    "activities": "activity",
    "resources": "resource",
    "variables": "variable",
}


@jsonp
def os_query_api(resource_type):
    q = None
    # if this is a POST, read the contents out of the body
    if request.method == "POST":
        q = request.json
    # if there is a source param, load the json from it
    elif "source" in request.values:
        try:
            q = json.loads(urllib.parse.unquote(request.values["source"]))
        except ValueError:
            abort(400)

    search_opts = MexSearchOptions()

    if q is None:
        # If no query is provided, use a match_all query
        q = {"query": {"match_all": {}}}

    rt = URL_RESOURCE_TYPE_MAP.get(resource_type)
    if rt is None:
        abort(400, description=f"Resource type '{resource_type}' is not supported.")

    # Define search parameters
    search_params = {"raw": q, "resource_type": rt}

    # Perform the search
    search_result = current_rdm_records_service.search(
        identity=system_identity, params=search_params, search_opts=search_opts
    )

    # print("####################################")
    # print(search_result)
    #
    # print("####################################")
    # print(search_result._results.to_dict())
    #
    # from speaklater import _LazyString
    # def custom_serialiser(obj):
    #     if isinstance(obj, _LazyString):
    #         return str(obj)

    # Access the search results
    result = search_result._results.to_dict()
    response = make_response(json.dumps(result), 200)
    response.headers["Content-Type"] = "application/json"
    return response


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
