from flask import render_template
from flask.views import MethodView
from invenio_pidstore.resolver import Resolver
class MexRecord(MethodView):

    def __init__(self):
        self.template = "invenio_app_rdm/records/detail.html"

    def get(self, mex_id, record=None):
        if record is None:
            resolver = Resolver(pid_type="recid", object_type="Record", getter=lambda x: x)
            try:
                record = resolver.resolve(pid_value=mex_id)
            except (PIDDoesNotExistError, PIDUnregistered):
                abort(404)
            except PIDMissingObjectError as e:
                current_app.logger.exception(
                    "No object assigned to {0}.".format(e.pid), extra={"pid": e.pid}
                )
                abort(500)
        return render_template(self.template, mex_id=mex_id, record=record)

# invenio id: wbdv5-sac84
# mex id: cP1OvUS7rELcPULquIu1dZ