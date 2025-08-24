from invenio_records_resources.services.custom_fields import (
    TextCF,
    EDTFDateStringCF,
    IntegerCF,
)

from mex_invenio.fields.link import LinkCF
from mex_invenio.fields.multilanguagetext import MultiLanguageTextCF
from mex_invenio.fields.fixededtfdatestringcf import FixedEDTFDateStringCF

RDM_NAMESPACES = {
    "mex": "https://mex.rki.de/",
    "index": "https://mex.rki.de/index#",
}

RDM_CUSTOM_FIELDS = [
    MultiLanguageTextCF(name="mex:abstract", multiple=True),
    TextCF(name="mex:accessPlatform", multiple=True),
    TextCF(name="mex:accessRestriction", use_as_filter=True),
    TextCF(name="mex:accessService"),
    LinkCF(name="mex:accessURL", multiple=True),
    TextCF(name="mex:accrualPeriodicity"),
    TextCF(name="mex:activityType", multiple=True, use_as_filter=True),
    TextCF(name="mex:affiliation", multiple=True),
    TextCF(name="mex:alternateIdentifier", multiple=True),
    MultiLanguageTextCF(name="mex:alternativeName", multiple=True),
    MultiLanguageTextCF(name="mex:alternativeTitle", multiple=True),
    TextCF(name="mex:anonymizationPseudonymization", multiple=True),
    TextCF(
        name="mex:belongsTo", multiple=True, use_as_filter=True
    ),  # FIXME: index external document
    TextCF(name="mex:bibliographicResourceType", multiple=True),
    TextCF(name="mex:codingSystem"),
    TextCF(name="mex:conformsTo", multiple=True),
    TextCF(name="mex:contact", multiple=True),
    TextCF(name="mex:containedBy", multiple=True),
    TextCF(name="mex:contributingUnit", multiple=True),
    TextCF(name="mex:contributor", multiple=True),  # FIXME: index external document
    TextCF(name="mex:created"),
    TextCF(name="mex:creator", multiple=True),
    TextCF(name="mex:dataType"),
    MultiLanguageTextCF(name="mex:description", multiple=True),
    TextCF(name="mex:distribution", multiple=True),
    LinkCF(name="mex:documentation", multiple=True),
    TextCF(name="mex:doi"),
    LinkCF(name="mex:downloadURL", multiple=True),
    TextCF(name="mex:edition"),
    TextCF(name="mex:editor", multiple=True),
    TextCF(name="mex:editorOfSeries", multiple=True),
    TextCF(name="mex:email", multiple=True),
    FixedEDTFDateStringCF(name="mex:end", multiple=True),
    LinkCF(name="mex:endpointDescription"),
    TextCF(name="mex:endpointType"),
    LinkCF(name="mex:endpointURL"),
    TextCF(
        name="mex:externalAssociate", multiple=True
    ),  # FIXME: index external document
    TextCF(name="mex:externalPartner", multiple=True),
    TextCF(name="mex:familyName", multiple=True),
    TextCF(name="mex:fullName", multiple=True),
    TextCF(
        name="mex:funderOrCommissioner", multiple=True, use_as_filter=True
    ),  # FIXME: index external document
    TextCF(name="mex:fundingProgram", multiple=True),
    TextCF(name="mex:geprisId", multiple=True),
    TextCF(name="mex:givenName", multiple=True),
    TextCF(name="mex:gndId", multiple=True),
    MultiLanguageTextCF(name="mex:hasLegalBasis", multiple=True),
    TextCF(name="mex:hasPersonalData", use_as_filter=True),
    TextCF(name="mex:icd10code", multiple=True),
    TextCF(
        name="mex:identifier", field_args={"required": True}, use_as_filter=True
    ),  # technically we just want the keyword mapping
    MultiLanguageTextCF(name="mex:instrumentToolOrApparatus", multiple=True),
    TextCF(name="mex:involvedPerson", multiple=True),  # FIXME: index external document
    TextCF(name="mex:involvedUnit", multiple=True),
    TextCF(name="mex:isPartOf", multiple=True),
    TextCF(name="mex:isPartOfActivity", multiple=True),
    TextCF(name="mex:isbnIssn", multiple=True),
    TextCF(name="mex:isniId", multiple=True),
    TextCF(name="mex:issue"),
    TextCF(name="mex:issued"),
    MultiLanguageTextCF(name="mex:journal", multiple=True, value_as_filter=True),
    MultiLanguageTextCF(name="mex:keyword", multiple=True, value_as_filter=True),
    MultiLanguageTextCF(name="mex:label", multiple=True, value_as_filter=True),
    LinkCF(name="mex:landingPage", multiple=True),
    TextCF(name="mex:language", multiple=True),
    TextCF(name="mex:license"),
    TextCF(name="mex:loincId", multiple=True),
    IntegerCF(name="mex:maxTypicalAge"),
    TextCF(name="mex:mediaType"),
    TextCF(name="mex:memberOf", multiple=True),
    TextCF(name="mex:meshId", multiple=True),
    MultiLanguageTextCF(name="mex:method", multiple=True),
    MultiLanguageTextCF(name="mex:methodDescription", multiple=True),
    IntegerCF(name="mex:minTypicalAge"),
    TextCF(name="mex:modified"),
    MultiLanguageTextCF(name="mex:name", multiple=True),
    MultiLanguageTextCF(name="mex:officialName", multiple=True),
    TextCF(name="mex:orcidId", multiple=True),
    TextCF(name="mex:pages"),
    TextCF(name="mex:parentUnit"),
    MultiLanguageTextCF(name="mex:populationCoverage", multiple=True),
    TextCF(name="mex:publication", multiple=True),
    TextCF(name="mex:publicationPlace"),
    FixedEDTFDateStringCF(name="mex:publicationYear"),
    TextCF(name="mex:publisher", multiple=True),
    MultiLanguageTextCF(name="mex:qualityInformation", multiple=True),
    LinkCF(name="mex:repositoryURL"),
    TextCF(name="mex:resourceCreationMethod", multiple=True, use_as_filter=True),
    TextCF(name="mex:resourceTypeGeneral", multiple=True),
    MultiLanguageTextCF(name="mex:resourceTypeSpecific", multiple=True),
    TextCF(name="mex:responsibleUnit", multiple=True),
    MultiLanguageTextCF(name="mex:rights", multiple=True),
    TextCF(name="mex:rorId", multiple=True),
    TextCF(name="mex:section"),
    MultiLanguageTextCF(name="mex:shortName", multiple=True),
    TextCF(name="mex:sizeOfDataBasis"),
    MultiLanguageTextCF(name="mex:spatial", multiple=True),
    FixedEDTFDateStringCF(name="mex:start", multiple=True),
    TextCF(name="mex:stateOfDataProcessing", multiple=True),
    MultiLanguageTextCF(name="mex:subtitle", multiple=True),
    TextCF(name="mex:succeeds", multiple=True),
    TextCF(name="mex:technicalAccessibility"),
    TextCF(name="mex:temporal"),
    TextCF(name="mex:theme", multiple=True, use_as_filter=True),
    MultiLanguageTextCF(name="mex:title", multiple=True),
    MultiLanguageTextCF(name="mex:titleOfBook", multiple=True),
    MultiLanguageTextCF(name="mex:titleOfSeries", multiple=True),
    TextCF(name="mex:unitInCharge", multiple=True),
    TextCF(name="mex:unitOf", multiple=True),
    TextCF(
        name="mex:usedIn", multiple=True, use_as_filter=True
    ),  # FIXME: index external document
    TextCF(name="mex:valueSet", multiple=True),
    TextCF(name="mex:viafId", multiple=True),
    TextCF(name="mex:volume"),
    TextCF(name="mex:volumeOfSeries"),
    TextCF(name="mex:wasGeneratedBy"),
    LinkCF(name="mex:website", multiple=True),
    TextCF(name="mex:wikidataId", multiple=True),
    ##########################################
    ## Index fields for search support - now handled by IndexField system field
    # TextCF(name="index:belongsToLabel", multiple=True, use_as_filter=True),
    # TextCF(name="index:contributors", multiple=True),
    # TextCF(name="index:creators", multiple=True),
    # TextCF(name="index:externalPartners", multiple=True),
    # TextCF(name="index:externalAssociates", multiple=True),
    # TextCF(name="index:deFunderOrCommissioners", multiple=True, use_as_filter=True),
    # TextCF(name="index:enFunderOrCommissioners", multiple=True, use_as_filter=True),
    # TextCF(name="index:involvedPersons", multiple=True),
    # TextCF(name="index:enUsedInResource", multiple=True, use_as_filter=True),
    # TextCF(name="index:deUsedInResource", multiple=True, use_as_filter=True),
]

RDM_CUSTOM_FIELDS_UI = [
    {
        "fields": [
            {
                "field": "mex:abstract",
                "props": {
                    "type": "/schema/fields/text",
                    "description": "An account of the publication.",
                },
            },
            {
                "field": "mex:accessPlatform",
                "props": {
                    "type": "/schema/entities/access-platform#/identifier",
                    "description": "A platform from which the resource can be accessed.",
                },
            },
            {
                "field": "mex:accessRestriction",
                "props": {
                    "type": "/schema/entities/concept#/identifier",
                    "description": "Indicates how access to the publication is restricted.",
                },
            },
            {
                "field": "mex:accessService",
                "props": {
                    "type": "/schema/entities/access-platform#/identifier",
                    "description": "A data service that gives access to the distribution of the dataset (DCAT, 2020-02-04).",
                },
            },
            {
                "field": "mex:accessURL",
                "props": {
                    "type": "/schema/fields/link",
                    "description": "A URL of the resource that gives access to a distribution of the dataset. E.g. landing page, feed, SPARQL endpoint (DCAT, 2020-02-04).",
                },
            },
            {
                "field": "mex:accrualPeriodicity",
                "props": {
                    "type": "/schema/entities/concept#/identifier",
                    "description": "The frequency with which items are added to a collection.",
                },
            },
            {
                "field": "mex:activityType",
                "props": {
                    "type": "/schema/entities/concept#/identifier",
                    "description": "The type of the activity.",
                },
            },
            {
                "field": "mex:affiliation",
                "props": {
                    "type": "/schema/entities/organization#/identifier",
                    "description": "An organization that the described person is affiliated with.",
                },
            },
            {
                "field": "mex:alternateIdentifier",
                "props": {
                    "type": "string",
                    "description": "Another identifier used for the reference.",
                },
            },
            {
                "field": "mex:alternativeName",
                "props": {
                    "type": "/schema/fields/text",
                    "description": "An alternative name for the organization",
                },
            },
            {
                "field": "mex:alternativeTitle",
                "props": {
                    "type": "/schema/fields/text",
                    "description": "Another title for the publication.",
                },
            },
            {
                "field": "mex:anonymizationPseudonymization",
                "props": {
                    "type": "/schema/entities/concept#/identifier",
                    "description": "Indicates whether the data has been anonymized and/or pseudonymized.",
                },
            },
            {
                "field": "mex:belongsTo",
                "props": {
                    "type": "/schema/entities/variable-group#/identifier",
                    "description": "The variable group, the described variable is part of. Used to group variables together, depending on how they are structured in the primary source.",
                },
            },
            {
                "field": "mex:bibliographicResourceType",
                "props": {
                    "type": "/schema/entities/concept#/identifier",
                    "description": "The type of bibliographic resource.",
                },
            },
            {
                "field": "mex:codingSystem",
                "props": {
                    "type": "string",
                    "description": "An established standard to which the described resource conforms (DCT, 2020-01-20).",
                },
            },
            {
                "field": "mex:conformsTo",
                "props": {
                    "type": "string",
                    "description": "Standards used in the creation, analysis or transmission of the resource.",
                },
            },
            {
                "field": "mex:contact",
                "props": {
                    "type": "/schema/entities/organizational-unit#/identifier",
                    "description": "An agent that serves as a contact for the resource.",
                },
            },
            {
                "field": "mex:containedBy",
                "props": {
                    "type": "/schema/entities/resource#/identifier",
                    "description": "The resource, the variable group is contained by. Used to connect a variable group to its resource.",
                },
            },
            {
                "field": "mex:contributingUnit",
                "props": {
                    "type": "/schema/entities/organizational-unit#/identifier",
                    "description": "An organizational unit of RKI, that is contributing to the publication.",
                },
            },
            {
                "field": "mex:contributor",
                "props": {
                    "type": "/schema/entities/person#/identifier",
                    "description": " A person involved in the creation of the resource.",
                },
            },
            {
                "field": "mex:created",
                "props": {
                    "type": "string",
                    "description": "Date of creation of the resource",
                },
            },
            {
                "field": "mex:creator",
                "props": {
                    "type": "/schema/entities/person#/identifier",
                    "description": "The author of the publication.",
                },
            },
            {
                "field": "mex:dataType",
                "props": {
                    "type": "string",
                    "description": "The defined data type of the variable.",
                },
            },
            {
                "field": "mex:description",
                "props": {
                    "type": "/schema/fields/text",
                    "description": "A description of the variable. How the variable is defined in the primary source.",
                },
            },
            {
                "field": "mex:distribution",
                "props": {
                    "type": "/schema/entities/distribution#/identifier",
                    "description": "An available distribution of the publication (DCAT, 2020-02-04)",
                },
            },
            {
                "field": "mex:documentation",
                "props": {
                    "type": "/schema/fields/link",
                    "description": "A link to a document documenting the resource.",
                },
            },
            {
                "field": "mex:doi",
                "props": {
                    "type": "string",
                    "description": "The Digital Object Identifier (DOI) of the publication.",
                },
            },
            {
                "field": "mex:downloadURL",
                "props": {
                    "type": "/schema/fields/link",
                    "description": "The URL of the downloadable file in a given format. E.g. CSV file or RDF file. The format is indicated by the distribution's `dcat:mediaType` (DCAT, 2020-02-04).",
                },
            },
            {
                "field": "mex:edition",
                "props": {
                    "type": "string",
                    "description": "The edition of the publication.",
                },
            },
            {
                "field": "mex:editor",
                "props": {
                    "type": "/schema/entities/person#/identifier",
                    "description": "The editor of the publication.",
                },
            },
            {
                "field": "mex:editorOfSeries",
                "props": {
                    "type": "/schema/entities/person#/identifier",
                    "description": "The editor of the series.",
                },
            },
            {
                "field": "mex:email",
                "props": {
                    "type": "string",
                    "description": "The email address through which the person can be contacted.",
                },
            },
            {
                "field": "mex:end",
                "props": {
                    "type": "string",
                    "description": "(Planned) end of the activity.",
                },
            },
            {
                "field": "mex:endpointDescription",
                "props": {
                    "type": "/schema/fields/link",
                    "description": "A description of the services available via the end-points, including their operations, parameters etc.",
                },
            },
            {
                "field": "mex:endpointType",
                "props": {
                    "type": "/schema/entities/concept#/identifier",
                    "description": "The type of endpoint, e.g. REST.",
                },
            },
            {
                "field": "mex:endpointURL",
                "props": {
                    "type": "/schema/fields/link",
                    "description": "The root location or primary endpoint of the service (a Web-resolvable IRI)",
                },
            },
            {
                "field": "mex:externalAssociate",
                "props": {
                    "type": "/schema/entities/organization#/identifier",
                    "description": "An external institution or person, that is associated with the activity.",
                },
            },
            {
                "field": "mex:externalPartner",
                "props": {
                    "type": "/schema/entities/organization#/identifier",
                    "description": "An external organization that is somehow involved in the creation of the resource.",
                },
            },
            {
                "field": "mex:familyName",
                "props": {
                    "type": "string",
                    "description": "The name inherited from the family.",
                },
            },
            {
                "field": "mex:fullName",
                "props": {
                    "type": "string",
                    "description": "The full name of a person. Also used if the naming schema (given name and family name) does not apply to the name.",
                },
            },
            {
                "field": "mex:funderOrCommissioner",
                "props": {
                    "type": "/schema/entities/organization#/identifier",
                    "description": "An agent, that has either funded or commissioned the activity.",
                },
            },
            {
                "field": "mex:fundingProgram",
                "props": {
                    "type": "string",
                    "description": "The program in which the activity is funded, e.g. Horizon2020.",
                },
            },
            {
                "field": "mex:geprisId",
                "props": {
                    "type": "string",
                    "description": "Identifier from GEPRIS authority file.",
                },
            },
            {
                "field": "mex:givenName",
                "props": {
                    "type": "string",
                    "description": "The name given to the person e.g. by their parents.",
                },
            },
            {
                "field": "mex:gndId",
                "props": {
                    "type": "string",
                    "description": "An identifier from the German authority file named Gemeinsame Normdatei (GND), curated by the German National Library (DNB).",
                },
            },
            {
                "field": "mex:hasLegalBasis",
                "props": {
                    "type": "/schema/fields/text",
                    "description": "The legal basis used to justify processing of personal data. Legal basis (plural: legal bases) are defined by legislations and regulations, whose applicability is usually restricted to specific jurisdictions which can be represented using dpv:hasJurisdiction or dpv:hasLaw. Legal basis can be used without such declarations, e.g. 'Consent', however their interpretation will require association with a law, e.g. 'EU GDPR'.",
                },
            },
            {
                "field": "mex:hasPersonalData",
                "props": {
                    "type": "/schema/entities/concept#/identifier",
                    "description": "Indicates, if a resource contains data directly or indirectly associated or related to an individual.",
                },
            },
            {
                "field": "mex:icd10code",
                "props": {"type": "string", "description": "A concept from ICD-10."},
            },
            {
                "field": "mex:identifier",
                "props": {
                    "type": "/schema/fields/identifier",
                    "description": "An unambiguous reference to the resource within a given context. Persistent identifiers should be provided as HTTP URIs (DCT, 2020-01-20).",
                },
            },
            {
                "field": "mex:instrumentToolOrApparatus",
                "props": {
                    "type": "/schema/fields/text",
                    "description": "Instrument, tool, or apparatus used in the research, analysis, observation, or processing of the object that is the subject of this resource.",
                },
            },
            {
                "field": "mex:involvedPerson",
                "props": {
                    "type": "/schema/entities/person#/identifier",
                    "description": "A person involved in the activity.",
                },
            },
            {
                "field": "mex:involvedUnit",
                "props": {
                    "type": "/schema/entities/organizational-unit#/identifier",
                    "description": "An organizational unit that is involved in the activity.",
                },
            },
            {
                "field": "mex:isPartOf",
                "props": {
                    "type": "/schema/entities/resource#/identifier",
                    "description": "A related resource, in which the described resource is physically or logically included.",
                },
            },
            {
                "field": "mex:isPartOfActivity",
                "props": {
                    "type": "/schema/entities/activity#/identifier",
                    "description": "Another activity, this activity is part of.",
                },
            },
            {
                "field": "mex:isbnIssn",
                "props": {
                    "type": "string",
                    "description": "Either the ISBN (for books) or ISSN (for periodicals) of the publication.",
                },
            },
            {
                "field": "mex:isniId",
                "props": {
                    "type": "string",
                    "description": "The ISNI (International Standard Name Identifier) of the organization.",
                },
            },
            {
                "field": "mex:issue",
                "props": {
                    "type": "string",
                    "description": "The issue of the periodical.",
                },
            },
            {
                "field": "mex:issued",
                "props": {
                    "type": "string",
                    "description": "Date of formal issuance of the publication (DCT, 2020-01-20).",
                },
            },
            {
                "field": "mex:journal",
                "props": {
                    "type": "/schema/fields/text",
                    "description": "The periodical in which the article was published.",
                },
            },
            {
                "field": "mex:keyword",
                "props": {
                    "type": "/schema/fields/text",
                    "description": "A keyword or tag describing the resource (DCAT, 2020-02-04).",
                },
            },
            {"field": "mex:label", "props": {"type": "/schema/fields/text"}},
            {
                "field": "mex:landingPage",
                "props": {
                    "type": "/schema/fields/link",
                    "description": "A Web page that can be navigated to in a Web browser to gain access to the catalog, a dataset, its distributions and/or additional information.",
                },
            },
            {
                "field": "mex:language",
                "props": {
                    "type": "/schema/entities/concept#/identifier",
                    "description": "The language in which the publication was written.",
                },
            },
            {
                "field": "mex:license",
                "props": {
                    "type": "/schema/entities/concept#/identifier",
                    "description": "A legal document giving official permission to do something with the publication (DCT, 2020-01-20).",
                },
            },
            {
                "field": "mex:loincId",
                "props": {"type": "string", "description": "A concept from LOINC."},
            },
            {
                "field": "mex:maxTypicalAge",
                "props": {
                    "type": "string",
                    "description": "Specifies the maximum age of the population within the data collection, expressed in years.",
                },
            },
            {
                "field": "mex:mediaType",
                "props": {
                    "type": "/schema/entities/concept#/identifier",
                    "description": "The media type of the distribution as defined by IANA media types (DCAT, 2020-02-04).",
                },
            },
            {
                "field": "mex:memberOf",
                "props": {
                    "type": "/schema/entities/organizational-unit#/identifier",
                    "description": "Organizational unit at RKI the person is associated with.",
                },
            },
            {
                "field": "mex:meshId",
                "props": {"type": "string", "description": "A concept from MeSH."},
            },
            {
                "field": "mex:method",
                "props": {
                    "type": "/schema/fields/text",
                    "description": "Method used in the research, analysis, observation or processing of the object that is subject to the resource.",
                },
            },
            {
                "field": "mex:methodDescription",
                "props": {
                    "type": "/schema/fields/text",
                    "description": "The description of the method, that was used to research, analysis, observation or processing of the object that was subject to the resource.",
                },
            },
            {
                "field": "mex:minTypicalAge",
                "props": {
                    "type": "string",
                    "description": "Specifies the minimum age of the population within the data collection, expressed in years.",
                },
            },
            {
                "field": "mex:modified",
                "props": {
                    "type": "string",
                    "description": "Date on which the resource was changed.",
                },
            },
            {
                "field": "mex:name",
                "props": {
                    "type": "/schema/fields/text",
                    "description": "The official name of the organizational unit.",
                },
            },
            {
                "field": "mex:officialName",
                "props": {
                    "type": "/schema/fields/text",
                    "description": "The official name of the organization.",
                },
            },
            {
                "field": "mex:orcidId",
                "props": {
                    "type": "string",
                    "description": "Identifier of a person from the ORCID authority file.",
                },
            },
            {
                "field": "mex:pages",
                "props": {
                    "type": "string",
                    "description": "The range of pages or a single page.",
                },
            },
            {
                "field": "mex:parentUnit",
                "props": {
                    "type": "/schema/entities/organizational-unit#/identifier",
                    "description": "The described unit is a subunit of another organizational unit.",
                },
            },
            {
                "field": "mex:populationCoverage",
                "props": {
                    "type": "/schema/fields/text",
                    "description": "The type of population common to all subjects of the data collection.",
                },
            },
            {
                "field": "mex:publication",
                "props": {
                    "type": "/schema/entities/bibliographic-resource#/identifier",
                    "description": "A publication that deals with the research, analysis, observation or processing of the object that was subject to the resource, e.g. a research paper.",
                },
            },
            {
                "field": "mex:publicationPlace",
                "props": {
                    "type": "string",
                    "description": "The place where the document was issued.",
                },
            },
            {
                "field": "mex:publicationYear",
                "props": {
                    "type": "string",
                    "description": "The year in which the publication was issued.",
                },
            },
            {
                "field": "mex:publisher",
                "props": {
                    "type": "/schema/entities/organization#/identifier",
                    "description": "An entity responsible for making the publication available (DCT, 2020-01-20).",
                },
            },
            {
                "field": "mex:qualityInformation",
                "props": {
                    "type": "/schema/fields/text",
                    "description": "Some information about the quality of the resource.",
                },
            },
            {
                "field": "mex:repositoryURL",
                "props": {
                    "type": "/schema/fields/link",
                    "description": "The handle of the publication in the repository, where the publication is stored.",
                },
            },
            {
                "field": "mex:resourceCreationMethod",
                "props": {
                    "type": "/schema/entities/concept#/identifier",
                    "description": "Method how the resource was created.",
                },
            },
            {
                "field": "mex:resourceTypeGeneral",
                "props": {
                    "type": "/schema/entities/concept#/identifier",
                    "description": "General type of the resource.",
                },
            },
            {
                "field": "mex:resourceTypeSpecific",
                "props": {
                    "type": "/schema/fields/text",
                    "description": "A term describing the specific nature of the resource. A more precise term than given by the property 'resourceTypeGeneral'.",
                },
            },
            {
                "field": "mex:responsibleUnit",
                "props": {
                    "type": "/schema/entities/organizational-unit#/identifier",
                    "description": "A unit, that is responsible for the activity.",
                },
            },
            {
                "field": "mex:rights",
                "props": {
                    "type": "/schema/fields/text",
                    "description": "Information about rights held in and over the resource as well as rights about the possibilities of the usage of the resource.",
                },
            },
            {
                "field": "mex:rorId",
                "props": {
                    "type": "string",
                    "description": "An identifier of the Research Organization Registry (ROR).",
                },
            },
            {
                "field": "mex:section",
                "props": {
                    "type": "string",
                    "description": "The name of the chapter of the publication, the book section belongs to.",
                },
            },
            {
                "field": "mex:shortName",
                "props": {
                    "type": "/schema/fields/text",
                    "description": "A short name or abbreviation of the organization.",
                },
            },
            {
                "field": "mex:sizeOfDataBasis",
                "props": {
                    "type": "string",
                    "description": "The size of the underlying data basis, e.g. for studies: the size of the sample.",
                },
            },
            {
                "field": "mex:spatial",
                "props": {
                    "type": "/schema/fields/text",
                    "description": "Spatial coverage of the resource.",
                },
            },
            {
                "field": "mex:start",
                "props": {
                    "type": "string",
                    "description": "The start of the activity.",
                },
            },
            {
                "field": "mex:stateOfDataProcessing",
                "props": {
                    "type": "/schema/entities/concept#/identifier",
                    "description": "The processing state of the data, e.g. raw or aggregated.",
                },
            },
            {
                "field": "mex:subtitle",
                "props": {
                    "type": "/schema/fields/text",
                    "description": "The subtitle of the publication.",
                },
            },
            {
                "field": "mex:succeeds",
                "props": {
                    "type": "/schema/entities/activity#/identifier",
                    "description": "Another activity, that ended with the start of the described activity. A follow-up activity.",
                },
            },
            {
                "field": "mex:technicalAccessibility",
                "props": {
                    "type": "/schema/entities/concept#/identifier",
                    "description": "Indicates form if the platform can be accessed only within RKI network (internally) or if the platform is accessible publicly (externally).",
                },
            },
            {
                "field": "mex:temporal",
                "props": {
                    "type": "string",
                    "description": "Temporal coverage of the resource.",
                },
            },
            {
                "field": "mex:theme",
                "props": {
                    "type": "/schema/entities/concept#/identifier",
                    "description": "A main category of the resource. A resource can have multiple themes.",
                },
            },
            {
                "field": "mex:title",
                "props": {
                    "type": "/schema/fields/text",
                    "description": "The full title of the publication.",
                },
            },
            {
                "field": "mex:titleOfBook",
                "props": {
                    "type": "/schema/fields/text",
                    "description": "The title of the book in which the book section is published.",
                },
            },
            {
                "field": "mex:titleOfSeries",
                "props": {
                    "type": "/schema/fields/text",
                    "description": "The title of the book series, the book belongs to.",
                },
            },
            {
                "field": "mex:unitInCharge",
                "props": {
                    "type": "/schema/entities/organizational-unit#/identifier",
                    "description": "This property refers to agents who assume responsibility and accountability for the resource and its appropriate maintenance.",
                },
            },
            {
                "field": "mex:unitOf",
                "props": {
                    "type": "/schema/entities/organization#/identifier",
                    "description": "Indicates an organization of which this unit is a part, e.g. a department within a larger organization.",
                },
            },
            {
                "field": "mex:usedIn",
                "props": {
                    "type": "/schema/entities/resource#/identifier",
                    "description": "The resource, the variable is used in.",
                },
            },
            {
                "field": "mex:valueSet",
                "props": {
                    "type": "string",
                    "description": "A set of predefined values as given in the primary source.",
                },
            },
            {
                "field": "mex:viafId",
                "props": {
                    "type": "string",
                    "description": "Identifier from VIAF (Virtual Authority File).",
                },
            },
            {
                "field": "mex:volume",
                "props": {
                    "type": "string",
                    "description": "The volume of the periodical.",
                },
            },
            {
                "field": "mex:volumeOfSeries",
                "props": {
                    "type": "string",
                    "description": "The volume of the periodical series.",
                },
            },
            {
                "field": "mex:wasGeneratedBy",
                "props": {
                    "type": "/schema/entities/activity#/identifier",
                    "description": "Generation is the completion of production of a new entity by an activity. This entity did not exist before generation and becomes available for usage after this generation.",
                },
            },
            {
                "field": "mex:website",
                "props": {
                    "type": "/schema/fields/link",
                    "description": "A web presentation of the activity, e.g. on the RKI homepage.",
                },
            },
            {
                "field": "mex:wikidataId",
                "props": {"type": "string", "description": "Identifier from Wikidata."},
            },
        ]
    }
]
