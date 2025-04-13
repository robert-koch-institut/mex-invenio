"""Additional views."""

from flask import Blueprint, redirect, url_for, request
from .record.record import MexRecord

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
        "/records/mex/<record_id>",
        view_func=MexRecord.as_view("mex_view"),
    )

    # Add URL rules
    return blueprint

def redirect_to_mex(record_id):
    # Lookup logic here — replace with your actual way of finding the mex_id
    mex_id = "mex:" + record_id  # This needs to be a real function

    if not mex_id:
        abort(404)

    return redirect(url_for(".mex_view", record_id=mex_id))