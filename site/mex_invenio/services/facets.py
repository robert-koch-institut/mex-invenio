
from invenio_records_resources.services.records.facets import NestedTermsFacet

class FilteredNestedTermsFacet(NestedTermsFacet):
    def __init__(self, field, label=None, allowed_values=None, **kwargs):
        super().__init__(field=field, label=label, **kwargs)
        self.allowed_values = set(allowed_values or [])

    def post_process(self, result, params):
        result["buckets"] = [
            b for b in result.get("buckets", [])
            if b.get("key") in self.allowed_values
        ]
        return result