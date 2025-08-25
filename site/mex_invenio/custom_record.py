from invenio_rdm_records.records import RDMRecord
from invenio_rdm_records.records.dumpers import EDTFDumperExt, EDTFListDumperExt, CombinedSubjectsDumperExt, \
    StatisticsDumperExt
from invenio_records.dumpers.relations import RelationDumperExt
from invenio_records_resources.records.dumpers import CustomFieldsDumperExt

from mex_invenio.custom_search import MexDumper

class MexRDMRecord(RDMRecord):
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