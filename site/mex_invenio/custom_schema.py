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
    
    # Let's try a simple raw field first to test if our schema is being used
    '''test_field = fields.Raw(dump_only=True, default="MEX_SCHEMA_WORKING")
    
    index_data = fields.Method("get_index_data", dump_only=True)
    
    def get_index_data(self, obj):
        """Get the index data for the record."""
        # Check if obj already has index_data (from search dumper)
        print(obj)
        print('--- get_index_data called ---')
        print(obj['index_data'])
        if isinstance(obj, dict) and 'index_data' in obj and obj['index_data']:
            return obj['index_data']
        
        # For record objects that don't have index_data yet
        return {'notnoworking': True}'''