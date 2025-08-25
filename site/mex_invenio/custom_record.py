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

from mex_invenio.custom_search import MexDumper
from mex_invenio.systemfields import IndexField as MexIndexField


class MexRDMRecord(RDMRecord):
    index = IndexField(
        "mexrecords-records-record-v8.0.0", search_alias="mexrecords-records"
    )

    index_data = MexIndexField()

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
