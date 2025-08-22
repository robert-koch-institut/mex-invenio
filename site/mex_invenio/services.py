"""Custom service configurations for MEX Invenio."""

from invenio_rdm_records.services.config import RDMRecordServiceConfig

from .custom_schema import MexRDMRecordSchema


class MexRDMRecordServiceConfig(RDMRecordServiceConfig):
    """MEX RDM record service config with custom schema."""
    
    schema = MexRDMRecordSchema