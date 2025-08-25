from invenio_rdm_records.services.schemas import RDMRecordSchema
from marshmallow import Schema, fields
from marshmallow_utils.fields import NestedAttribute, SanitizedUnicode


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


class MexRDMRecordSchema(RDMRecordSchema):
    """MEX RDM record schema with custom index_data field."""

    index_data = NestedAttribute(IndexDataSchema)
