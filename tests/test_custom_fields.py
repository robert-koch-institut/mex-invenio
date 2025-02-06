from invenio_access.permissions import system_identity
from invenio_rdm_records.proxies import current_rdm_records

from mex_invenio.config import RECORD_METADATA_DEFAULT_TITLE
from tests.data import org_unit_data


def test_import_org_unit(db, location, resource_type_v, contributors_role_v, import_file):
    """Test that the CLI command imports the org unit data correctly"""
    service = current_rdm_records.records_service

    messages = import_file('org-unit', org_unit_data)

    search_obj = service.search(system_identity)
    record = list(search_obj.hits)[0]

    rec_cf = record['custom_fields']

    assert record['metadata']['title'] == RECORD_METADATA_DEFAULT_TITLE
    assert rec_cf is not {}
    assert rec_cf['mex:identifier'] == org_unit_data['identifier']
    assert rec_cf['mex:shortName'][0]['value'] == org_unit_data['shortName'][0]['value']
    assert org_unit_data['unitOf'] == rec_cf['mex:unitOf']

