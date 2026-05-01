from invenio_rdm_records.services.schemas import RDMRecordSchema
from marshmallow import Schema, fields
from marshmallow_utils.fields import NestedAttribute, SanitizedUnicode


class DisplayDataSchema(Schema):
    """Schema for display data fields."""

    linked_records = fields.Raw(dump_only=True)


class IndexDataSchema(Schema):
    """Schema for index data fields."""

    belongsToLabel = fields.List(SanitizedUnicode(), dump_only=True)
    contributors = fields.List(SanitizedUnicode(), dump_only=True)
    creators = fields.List(SanitizedUnicode(), dump_only=True)
    externalPartners = fields.List(SanitizedUnicode(), dump_only=True)
    externalAssociates = fields.List(SanitizedUnicode(), dump_only=True)
    deFunderOrCommissioners = fields.List(SanitizedUnicode(), dump_only=True)
    enFunderOrCommissioners = fields.List(SanitizedUnicode(), dump_only=True)
    involvedPersons = fields.List(SanitizedUnicode(), dump_only=True)
    enUsedInResource = fields.List(SanitizedUnicode(), dump_only=True)
    deUsedInResource = fields.List(SanitizedUnicode(), dump_only=True)
    enContributingUnits = fields.List(SanitizedUnicode(), dump_only=True)
    deContributingUnits = fields.List(SanitizedUnicode(), dump_only=True)


class MexRDMRecordSchema(RDMRecordSchema):
    """MEX RDM record schema with custom index_data and display_data field."""

    index_data = NestedAttribute(IndexDataSchema, dump_only=True)
    display_data = NestedAttribute(DisplayDataSchema, dump_only=True)
