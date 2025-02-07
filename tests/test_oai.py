import xml.etree.ElementTree as ET

from flask import current_app

from tests.conftest import search_messages
from tests.data import resource_data


def test_oai_mex_format_exists(app, client):
    """Test that the OAI-PMH Mex crosswalk exists."""

    res = client.get('/oai2d?verb=ListMetadataFormats')

    tree = ET.ElementTree(ET.fromstring(res.data))
    root = tree.getroot()

    oai_url = '{http://www.openarchives.org/OAI/2.0/}'
    oai_mex = root.find(f'.//{oai_url}metadataFormat[{oai_url}metadataPrefix="oai_mex"]')

    assert res.status_code == 200
    assert oai_mex is not None


def test_get_oai_record(client, db, location, resource_type_v, contributors_role_v, import_file, app_config):
    """Test that the OAI-PMH ListRecords verb returns the correct record."""
    oai_prefix = app_config['OAISERVER_ID_PREFIX']
    messages = import_file('resource', resource_data)

    match = search_messages(messages, 'Published (\d) records. Ids: {\'(\w{5}-\w{5})\'}')

    assert match is not None
    rec_id = match.group(2)
    # oai_url = f"/oai2d?verb=GetRecord&identifier=oai:{oai_prefix}:{rec_id}&metadataPrefix=oai_mex"

    res = client.get('/oai2d?verb=ListRecords&metadataPrefix=oai_mex')
    assert res.status_code == 200

    tree = ET.ElementTree(ET.fromstring(res.data))
    root = tree.getroot()

    # Define namespaces
    oai_namespace = {'oai': 'http://www.openarchives.org/OAI/2.0/'}
    dc_namespace = {'dc': 'http://purl.org/dc/elements/1.1/'}

    # Find the ListRecords element
    list_records = root.find('oai:ListRecords', oai_namespace)
    assert len(list_records) == 1

    for rec in list_records:
        metadata = rec.find('oai:metadata', oai_namespace)
        ids = [_id.text for _id in metadata.findall('.//dc:identifier', dc_namespace)]
        assert len(ids) == 2
        assert f'oai:{oai_prefix}:{rec_id}' in ids
        assert 'mex:' + resource_data['identifier'] in ids

        description = metadata.find('.//dc:description', dc_namespace)
        assert description.text == resource_data['description'][0]['value']

        if 'mex:unitInCharge' in current_app.config.get('OAI_SERVER_RELATIONS', []):
            unit_in_charge = metadata.find('.//dc:relation', dc_namespace)
            assert unit_in_charge.text.removeprefix('mex:') in resource_data['unitInCharge']
