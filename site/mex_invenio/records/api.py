from invenio_rdm_records.records import RDMRecord
from invenio_rdm_records.records.dumpers import (
    EDTFDumperExt,
    EDTFListDumperExt,
    CombinedSubjectsDumperExt,
    StatisticsDumperExt,
)
from invenio_records.dumpers.relations import RelationDumperExt
from invenio_records_resources.records.dumpers import CustomFieldsDumperExt
from invenio_records_resources.records.systemfields import IndexField
from invenio_indexer.api import RecordIndexer

from mex_invenio.services.search import MexDumper
from mex_invenio.fields.systemfields import DisplayField


class MEXBulkIndexer(RecordIndexer):
    """Custom indexer optimized for MEX record processing."""
    
    def __init__(self, *args, **kwargs):
        # Override default batch size from 10,000 to 100 for MEX records
        kwargs.setdefault('bulk_index_max_items', 100)
        super().__init__(*args, **kwargs)


class MexRDMRecord(RDMRecord):
    index = IndexField(
        "mexrecords-records-record-v8.0.0", search_alias="mexrecords-records"
    )

    display_data = DisplayField()

    dumper = MexDumper(
        extensions=[
            EDTFDumperExt("metadata.publication_date"),
            EDTFListDumperExt("metadata.dates", "date"),
            RelationDumperExt("relations"),
            CombinedSubjectsDumperExt(),
            CustomFieldsDumperExt(fields_var="RDM_CUSTOM_FIELDS"),
            StatisticsDumperExt("stats"),
        ]
    )

    # Use custom indexer for MEX records
    @classmethod
    def get_indexer(cls):
        """Get the indexer for MEX records."""
        return MEXBulkIndexer(record_cls=cls)
