from invenio_access.permissions import system_identity
from invenio_rdm_records.proxies import current_rdm_records

from tests.data import org_unit_data


def test_custom_fields_configured(app_config):
    """Test that the custom fields are configured in the RDM records service"""

    assert len(app_config["RDM_NAMESPACES"].keys()) == 1
    assert len(app_config["RDM_CUSTOM_FIELDS"]) > 0
    assert (
        len(app_config["RDM_CUSTOM_FIELDS_UI"][0]["fields"])
        == len(app_config["RDM_CUSTOM_FIELDS"]) - 2
    )


def test_import_org_unit(
    db, location, resource_type_v, contributors_role_v, import_file
):
    """Test that the CLI command imports the org unit data correctly"""
    service = current_rdm_records.records_service

    messages = import_file("org-unit", org_unit_data)

    search_obj = service.search(system_identity)
    record = list(search_obj.hits)[0]

    rec_cf = record["custom_fields"]

    assert record["metadata"]["title"] == org_unit_data["name"][0]["value"]
    assert rec_cf != {}
    assert rec_cf["mex:identifier"] == org_unit_data["identifier"]
    assert rec_cf["mex:shortName"][0]["value"] == org_unit_data["shortName"][0]["value"]
    assert org_unit_data["unitOf"] == rec_cf["mex:unitOf"]

    # test for the custom field link
    assert len(rec_cf["mex:website"]) == 1
    assert rec_cf["mex:website"][0]["url"] == org_unit_data["website"][0]["url"]

    # test for the custom field multi-language text
    assert len(rec_cf["mex:alternativeName"]) == 1
    assert (
        rec_cf["mex:alternativeName"][0]["value"]
        == org_unit_data["alternativeName"][0]["value"]
    )
