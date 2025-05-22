from invenio_records_resources.services.records.facets import NestedTermsFacet
from invenio_search.engine import dsl


class RestrictedTermsFacet(NestedTermsFacet):
    """Facet that only displays specific values."""

    def __init__(self, field, label, excluded_values=None, **kwargs):
        """Initialize facet with allowed values."""
        super().__init__(field=field, label=label, **kwargs)
        self.excluded_values = excluded_values

    def get_aggregation(self):
        """Get the aggregation and subaggregation."""
        kwargs = {
            "field": self._field,
            "aggs": {"inner": dsl.A("terms", field=self._subfield), }
        }

        if self.excluded_values:
            kwargs["exclude"] = self.excluded_values

        return dsl.A(
            "terms",
            **kwargs,
        )
