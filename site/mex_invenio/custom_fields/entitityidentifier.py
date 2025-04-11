from invenio_records_resources.services.custom_fields import BaseListCF
from marshmallow import fields, validate
from marshmallow_utils.fields import SanitizedUnicode

from site.mex_invenio.custom_fields.multilanguagetext import MultiLanguageTextCF


class EntityIdentifierCF(BaseCF):
    """A MEx field representation with id representing another record
    and its displayed value "title" as multilanguage field

    https://github.com/robert-koch-institut/mex-model/blob/main/mex/model/fields/text.json"""

    def __init__(self, id, title, **kwargs):
        """Constructor."""
        super().__init__(
            name=id,
            field_args=fields.Nested(MultiLanguageTextCF(multiple=True, name=title))
            **kwargs
        )

    @property
    def mapping(self):
        """Return the mapping."""
        return {
            "properties": {
                "id": {
                    "type": "text"
                },
                "title": {
                    "language": {
                        "type": "text"
                    },
                    "value": {
                        "type": "text"
                    }
                },
            }
        }
