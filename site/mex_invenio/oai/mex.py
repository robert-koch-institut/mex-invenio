from dcxml import simpledc
from flask import g, current_app
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.resources.serializers import DublinCoreXMLSerializer


def mex_dublincore_etree(pid, record, **serializer_kwargs):
    """Get DublinCore XML etree for OAI-PMH.
    Based off invenio_rdm_records.oai.dublincore_etree
    """
    item = current_rdm_records_service.oai_result_item(g.identity, record["_source"])
    oai_record = item.to_dict()

    # TODO: DublinCoreXMLSerializer should be able to dump an etree directly
    # instead. See https://github.com/inveniosoftware/flask-resources/issues/117
    obj = DublinCoreXMLSerializer(**serializer_kwargs).dump_obj(oai_record)

    cf = oai_record['custom_fields']

    # TODO: Rights could be omitted
    # defaults to closedAccess, see
    # https://guidelines.openaire.eu/en/latest/literature/field_accesslevel.html
    # only set license to open if there is a license
    if 'mex:license' in cf:
        obj['rights'] = ['info:eu-repo/semantics/openAccess']

    # not set by default, see
    # https://guidelines.openaire.eu/en/latest/literature/field_publicationtype.html
    obj['types'] = ['info:eu-repo/semantics/other']

    # mex:identifier is a required field
    obj['identifiers'].append(cf['mex:identifier'])

    # description and abstract get mapped to descriptions
    for p in ['mex:description', 'mex:abstract']:
        if p in cf:
            if 'descriptions' not in obj:
                obj['descriptions'] = []

            obj['descriptions'].extend([d['value'] for d in cf[p]])

    if 'mex:creator' in cf:
        # all records will have a creator because it's a mandatory field
        # that will be the config value of RECORD_METADATA_CREATOR
        obj['creators'].extend(cf['mex:creator'])

    if 'mex:keyword' in cf:
        obj['subjects'] = [k['value'] for k in cf['mex:keyword']]

    if 'mex:publisher' in cf:
        obj['publishers'] = cf['mex:publisher']

    if 'mex:contact' in cf:
        obj['contributors'] = cf['mex:contact']

    if 'mex:mediaType' in cf:
        obj['formats'] = [cf['mex:mediaType']]

    if 'mex:language' in cf:
        obj['languages'] = cf['mex:language']

    #print(type(oai_record['custom_fields']['mex:mediaType']))

    dates = []

    # there seems to be a bug in how EDTFDateStringCF fields are serialized
    # they are serialized as lists, but should be strings
    for date in ['mex:issued', 'mex:publicationYear', 'mex:created', 'mex:start', 'mex:end']:
        if date in cf:
            if isinstance(cf[date], list):
                dates.append(''.join(cf[date]))
            else:
                dates.append(cf[date])

    if dates:
        obj['dates'].extend(dates)

    # sources, see
    # https://guidelines.openaire.eu/en/latest/literature/field_source.html
    sources = []

    for source in current_app.config.get('OAISERVER_SOURCES', []):
        if source in cf:
            if isinstance(cf[source], list):
                sources.extend(cf[source])
            else:
                sources.append(cf[source])

    # relations, see
    # https://guidelines.openaire.eu/en/latest/literature/field_relation.html
    relations = []

    for relation in current_app.config.get('OAISERVER_RELATIONS', []):
        if relation in cf:
            if isinstance(cf[relation], list):
                relations.extend(cf[relation])
            else:
                relations.append(cf[relation])

    if sources:
        obj['sources'] = sources

    if relations:
        obj['relations'] = relations

    return simpledc.dump_etree(obj)
