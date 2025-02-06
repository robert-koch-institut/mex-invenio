from dcxml import simpledc
from flask import g
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.resources.serializers import DublinCoreXMLSerializer

from mex_invenio.config import OAI_SERVER_RELATIONS, OAI_SERVER_SOURCES


def mex_dublincore_etree(pid, record, **serializer_kwargs):
    """Get DublinCore XML etree for OAI-PMH."""
    item = current_rdm_records_service.oai_result_item(g.identity, record["_source"])
    oai_record = item.to_dict()

    # TODO: DublinCoreXMLSerializer should be able to dump an etree directly
    # instead. See https://github.com/inveniosoftware/flask-resources/issues/117
    obj = DublinCoreXMLSerializer(**serializer_kwargs).dump_obj(oai_record)

    # TODO: Rights could be omitted
    # defaults to closedAccess, see
    # https://guidelines.openaire.eu/en/latest/literature/field_accesslevel.html
    obj['rights'] = ['info:eu-repo/semantics/openAccess']

    # not set by default, see
    # https://guidelines.openaire.eu/en/latest/literature/field_publicationtype.html
    obj['types'] = ['info:eu-repo/semantics/other']

    # mex:identifier is a required field
    obj['identifiers'].append('mex:' + oai_record['custom_fields']['mex:identifier'])

    if 'mex:description' in oai_record['custom_fields']:
        obj['descriptions'] = [d['value'] for d in oai_record['custom_fields']['mex:description']]

    # sources, see
    # https://guidelines.openaire.eu/en/latest/literature/field_source.html
    sources = []

    for source in OAI_SERVER_SOURCES:
        if source in oai_record['custom_fields']:
            if isinstance(oai_record['custom_fields'][source], list):
                sources.extend(['mex:' + c for c in oai_record['custom_fields'][source]])
            else:
                sources.append('mex:' + oai_record['custom_fields'][source])

    # relations, see
    # https://guidelines.openaire.eu/en/latest/literature/field_relation.html
    relations = []

    for relation in OAI_SERVER_RELATIONS:
        if relation in oai_record['custom_fields']:
            if isinstance(oai_record['custom_fields'][relation], list):
                relations.extend(['mex:' + c for c in oai_record['custom_fields'][relation]])
            else:
                relations.append('mex:' + oai_record['custom_fields'][relation])

    if sources:
        obj['sources'] = sources

    if relations:
        obj['relations'] = relations

    return simpledc.dump_etree(obj)
