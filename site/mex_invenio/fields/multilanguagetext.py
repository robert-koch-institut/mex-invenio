from invenio_records_resources.services.custom_fields import BaseListCF
from invenio_records_resources.services.custom_fields.mappings import TextMapping
from marshmallow import fields, validate
from marshmallow_utils.fields import SanitizedUnicode


class MultiLanguageTextCF(BaseListCF):
    """A MEx text field representation with a limited choice set
     of language and a required value property.

    https://github.com/robert-koch-institut/mex-model/blob/main/mex/model/fields/text.json"""

    def __init__(self, name, value_as_filter=False, **kwargs):
        """Constructor."""
        super().__init__(
            name,
            field_cls=fields.Nested,
            field_args=dict(
                nested=dict(
                    language=SanitizedUnicode(
                        validate=validate.OneOf(choices=["en", "de"])
                    ),
                    value=SanitizedUnicode(
                        required=True, validate=validate.Length(min=1)
                    ),
                )
            ),
            **kwargs,
        )
        self._value_as_filter = value_as_filter

    @property
    def mapping(self):
        """Return the mapping."""
        return {
            "properties": {
                "language": {"type": "text"},
                "value": TextMapping(use_as_filter=self._value_as_filter).to_dict(),
            }
        }
