from invenio_rdm_records.services.schemas import RDMRecordSchema
from marshmallow import Schema, fields
from marshmallow_utils.fields import NestedAttribute, SanitizedUnicode


class DisplayDataSchema(Schema):
    """Schema for display data fields."""

    linked_records = fields.Raw(dump_only=True)


class MexRDMRecordSchema(RDMRecordSchema):
    """MEX RDM record schema with custom display_data field."""

    display_data = NestedAttribute(DisplayDataSchema)