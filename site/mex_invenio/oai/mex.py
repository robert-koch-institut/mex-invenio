from dcxml.simpledc import container_element, rules, ns, container_attribs

from flask import g, current_app
from invenio_rdm_records.proxies import current_rdm_records_service
from lxml import etree


def dump_etree_helper(container_name, data, rules, nsmap, attrib):
    """Convert DataCite JSON format to DataCite XML.

    JSON should be validated before it is given to to_xml.
    This function is a modified version of dcxml.xmlutils.dump_etree in order
    to support the xml:lang attrib.
    """
    nsmap["xml"] = "http://www.w3.org/XML/1998/namespace"
    output = etree.Element(container_name, nsmap=nsmap, attrib=attrib)

    for rule in rules:
        if rule not in data:
            continue

        element_data = []

        for d in data[rule]:
            if isinstance(d, dict):
                element_data.append(d["value"])
            else:
                element_data.append(d)

        element = rules[rule](rule, element_data)

        for e in element:
            lang = [
                a["language"]
                for a in data[rule]
                if isinstance(a, dict) and a["value"] == e.text
            ]

            if lang:
                e.set("{http://www.w3.org/XML/1998/namespace}lang", lang[0])
            output.append(e)

    return output


def mex_dublincore_etree(pid, record, **serializer_kwargs):
    """Get DublinCore XML etree for OAI-PMH.
    This function is a modified version of invenio_rdm_records.oai.dublincore_etree
    in order to crosswalk the MEx custom fields.
    """
    item = current_rdm_records_service.oai_result_item(g.identity, record["_source"])
    oai_record = item.to_dict()

    obj = {
        "titles": [],
        "identifiers": [oai_record["pids"]["oai"]["identifier"]],
        "creators": [],
        "dates": [],
        "descriptions": [],
    }

    cf = oai_record["custom_fields"]

    for t in current_app.config.get("RECORD_METADATA_TITLE_PROPERTIES", ""):
        if f"mex:{t}" in cf:
            obj["titles"].extend(cf[f"mex:{t}"])

    # defaults to closedAccess, see
    # https://guidelines.openaire.eu/en/latest/literature/field_accesslevel.html
    # only set license to open if there is a license
    if "mex:license" in cf:
        obj["rights"] = ["info:eu-repo/semantics/openAccess"]

    # not set by default, see
    # https://guidelines.openaire.eu/en/latest/literature/field_publicationtype.html
    obj["types"] = ["info:eu-repo/semantics/other"]

    # mex:identifier is a required field
    obj["identifiers"].append(cf["mex:identifier"])

    # description and abstract get mapped to descriptions
    for p in ["mex:description", "mex:abstract"]:
        if p in cf:
            obj["descriptions"].extend(cf[p])

    if "mex:creator" in cf:
        # all records will have a creator because it's a mandatory field
        # that will be the config value of RECORD_METADATA_CREATOR
        obj["creators"].extend(cf["mex:creator"])

    if "mex:keyword" in cf:
        obj["subjects"] = cf["mex:keyword"]

    if "mex:publisher" in cf:
        obj["publishers"] = cf["mex:publisher"]

    if "mex:contact" in cf:
        obj["contributors"] = cf["mex:contact"]

    if "mex:mediaType" in cf:
        obj["formats"] = [cf["mex:mediaType"]]

    if "mex:language" in cf:
        obj["languages"] = cf["mex:language"]

    dates = []

    # there seems to be a bug in how EDTFDateStringCF fields are serialized
    # they are serialized as lists, but should be strings
    for date in [
        "mex:issued",
        "mex:publicationYear",
        "mex:created",
        "mex:start",
        "mex:end",
    ]:
        if date in cf:
            if isinstance(cf[date], list):
                dates.append("".join(cf[date]))
            else:
                dates.append(cf[date])

    if dates:
        obj["dates"].extend(dates)

    # sources, see
    # https://guidelines.openaire.eu/en/latest/literature/field_source.html
    sources = []

    for source in current_app.config.get("OAISERVER_SOURCES", []):
        if source in cf:
            if isinstance(cf[source], list):
                sources.extend(cf[source])
            else:
                sources.append(cf[source])

    # relations, see
    # https://guidelines.openaire.eu/en/latest/literature/field_relation.html
    relations = []

    for relation in current_app.config.get("OAISERVER_RELATIONS", []):
        if relation in cf:
            if isinstance(cf[relation], list):
                relations.extend(cf[relation])
            else:
                relations.append(cf[relation])

    if sources:
        obj["sources"] = sources

    if relations:
        obj["relations"] = relations

    return dump_etree_helper(container_element, obj, rules, ns, container_attribs)
