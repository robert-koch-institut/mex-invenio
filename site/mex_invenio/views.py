from flask import Blueprint, redirect, url_for, current_app, abort
from .record.record import MexRecord

from invenio_pidstore.resolver import Resolver
from invenio_pidstore.errors import (
    PIDDoesNotExistError,
    PIDMissingObjectError,
    PIDUnregistered,
)
from invenio_rdm_records.records.api import RDMRecord


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

    return blueprint


def redirect_to_mex(record_id):
    record = None
    resolver = Resolver(pid_type="recid", object_type="rec", getter=RDMRecord.get_record)

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
        current_app.logger.exception(
            "No mex id for the record {0}.".format(e)
        )
        abort(500)

    return redirect(url_for(".mex_view", mex_id=mex_id))
