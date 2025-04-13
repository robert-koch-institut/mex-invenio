from flask import render_template
from flask.views import MethodView

class MexRecord(MethodView):

    def __init__(self):
        self.template = "invenio_app_rdm/records/detail.html"

    def get(self, record_id):
        return render_template(self.template, record_id=record_id)
