from flask import Blueprint, redirect, url_for, request, current_app
from .record.record import MexRecord

from invenio_pidstore.resolver import Resolver
from invenio_pidstore.errors import (
    PIDDeletedError,
    PIDDoesNotExistError,
    PIDMissingObjectError,
    PIDRedirectedError,
    PIDUnregistered,
)


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

    blueprint.add_url_rule(
        "/records/<record_id>",
        view_func=redirect_to_mex,
    )

    blueprint.add_url_rule(
        "/records/mex/<mex_id>",
        view_func=MexRecord.as_view("mex_view"),
    )

    # print("url_map: ", app.url_map)

    # Add URL rules
    return blueprint

def redirect_to_mex(record_id):
    record = {}
    # resolver = Resolver(pid_type="recid", object_type="rec", record_class="Record")
    # try:
    #     record = resolver.resolve(pid_value=record_id)
    # except (PIDDoesNotExistError, PIDUnregistered):
    #     abort(404)
    # except PIDMissingObjectError as e:
    #     current_app.logger.exception(
    #         "No object assigned to {0}.".format(e.pid), extra={"pid": e.pid}
    #     )
    #     abort(500)
    #
    # mex_id = record["custom_fields"]["mex:identifier"]
    
    mex_id = "mex:"+ record_id

    return redirect(url_for(".mex_view", mex_id=mex_id, record={}))