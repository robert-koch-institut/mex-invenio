"""Custom service configurations for MEX Invenio."""

from invenio_rdm_records.services.config import RDMRecordServiceConfig

from .custom_schema import MexRDMRecordSchema
from .custom_record import MexRDMRecord


class MexRDMRecordServiceConfig(RDMRecordServiceConfig):
    """MEX RDM record service config with custom schema and record class."""
    
    schema = MexRDMRecordSchema
    record_cls = MexRDMRecord