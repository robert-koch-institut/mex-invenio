from invenio_rdm_records.records import RDMRecord

from mex_invenio.custom_search import MexDumper

class MexRDMRecord(RDMRecord):
    dumper = MexDumper()