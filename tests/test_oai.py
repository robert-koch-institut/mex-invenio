import xml.etree.ElementTree as ET

from tests.conftest import search_messages, created_regex
from tests.data import resource_data


def test_oai_mex_format_exists(app, client):
    """Test that the OAI-PMH Mex crosswalk exists."""

    res = client.get("/oai2d?verb=ListMetadataFormats")

    tree = ET.ElementTree(ET.fromstring(res.data))
    root = tree.getroot()

    oai_url = "{http://www.openarchives.org/OAI/2.0/}"
    oai_dc = root.find(f'.//{oai_url}metadataFormat[{oai_url}metadataPrefix="oai_dc"]')

    assert res.status_code == 200
    assert oai_dc is not None


def test_get_oai_record(
    client, db, location, resource_type_v, contributors_role_v, import_file, app_config
):
    """Test that the OAI-PMH ListRecords verb returns the correct record."""
    oai_prefix = app_config["OAISERVER_ID_PREFIX"]
    messages = import_file("resource", resource_data)

    match = search_messages(messages, created_regex)

    assert match is not None
    rec_id = match.group("record_id")
    # oai_url = f"/oai2d?verb=GetRecord&identifier=oai:{oai_prefix}:{rec_id}&metadataPrefix=oai_mex"

    res = client.get("/oai2d?verb=ListRecords&metadataPrefix=oai_dc")
    assert res.status_code == 200

    tree = ET.ElementTree(ET.fromstring(res.data))
    root = tree.getroot()

    # Define namespaces
    oai_namespace = {"oai": "http://www.openarchives.org/OAI/2.0/"}
    dc_namespace = {"dc": "http://purl.org/dc/elements/1.1/"}

    # Find the ListRecords element
    list_records = root.find("oai:ListRecords", oai_namespace)
    assert len(list_records) == 1

    for rec in list_records:
        metadata = rec.find("oai:metadata", oai_namespace)
        ids = [_id.text for _id in metadata.findall(".//dc:identifier", dc_namespace)]
        assert len(ids) == 2
        assert f"oai:{oai_prefix}:{rec_id}" in ids
        assert resource_data["identifier"] in ids

        description = metadata.find(".//dc:description", dc_namespace)
        assert description.text == resource_data["description"][0]["value"]
        rec_license = metadata.find(".//dc:rights", dc_namespace)
        assert rec_license.text == "info:eu-repo/semantics/openAccess"

        if "mex:unitInCharge" in app_config["OAISERVER_RELATIONS"]:
            unit_in_charge = metadata.find(".//dc:relation", dc_namespace)
            assert unit_in_charge.text in resource_data["unitInCharge"]

        # there will be 2 dates, created by invenio and mex:created
        dates = metadata.findall(".//dc:date", dc_namespace)
        assert resource_data["created"] in [date.text for date in dates]
