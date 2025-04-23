# custom_facets.py
from invenio_records_resources.services.records.facets import NestedTermsFacet

class RestrictedTermsFacet(NestedTermsFacet):
    """Facet that only displays specific values."""

    def __init__(self, field, label, allowed_values=None, **kwargs):
        """Initialize facet with allowed values."""
        super().__init__(field=field, label=label, **kwargs)
        self.allowed_values = set(allowed_values) if allowed_values else None

    def get_labelled_values(self, data, filter_values, bucket_label=True, key_prefix=None):
        """Get an unlabelled version of the bucket, filtered by allowed values."""
        out = []
        label_map = self.get_label_mapping(data.buckets)
        for bucket in data.buckets:
            key = full_key = self.get_value(bucket)
            if key_prefix:
                full_key = key_prefix + self._splitchar + full_key

            if self.allowed_values is None or key in self.allowed_values:
                bucket_out = {
                    "key": key,
                    "doc_count": self.get_metric(bucket),
                    "label": label_map[key],
                    "is_selected": self.is_filtered(full_key, filter_values),
                }
                if "inner" in bucket:
                    bucket_out["inner"] = self.get_labelled_values(
                        bucket.inner, filter_values, bucket_label=False, key_prefix=full_key
                    )
                out.append(bucket_out)

        ret_val = {"buckets": out}
        if bucket_label:
            ret_val["label"] = str(self._label)
        return ret_val
