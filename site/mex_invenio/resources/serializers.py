from flask import current_app
from flask_babel import get_locale
from flask_resources import BaseListSchema, MarshmallowSerializer
from flask_resources.serializers import SimpleSerializer

from mex_invenio.services.schema import MExCustomBibTeXSchema


class MExBibTexSerializer(MarshmallowSerializer):
    """Custom MEx BibTex Serializer using the custom MExCustomBibTeXSchema."""

    def __init__(self, **options) -> None:
        """Initialize the serializer."""
        super().__init__(
            format_serializer_cls=SimpleSerializer,
            object_schema_cls=MExCustomBibTeXSchema,
            schema_kwargs={"lang": get_locale()},
            list_schema_cls=BaseListSchema,
            encoder=self.bibtex_tostring,
            **options,
        )

    @classmethod
    def bibtex_tostring(cls, record) -> str:
        """Stringify a BibTex record."""
        return record

    def dump_obj(self, obj) -> dict:
        """Dump the object using object schema class."""
        pref_labels = current_app.config.get("PREF_LABELS")
        return self.object_schema.to_bibtex(obj, pref_labels)
