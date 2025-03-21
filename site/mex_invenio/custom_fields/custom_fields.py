from invenio_records_resources.services.custom_fields import TextCF, EDTFDateStringCF, IntegerCF

from mex_invenio.custom_fields.link import LinkCF
from mex_invenio.custom_fields.multilanguagetext import MultiLanguageTextCF

RDM_NAMESPACES = {
    "mex": "https://mex.rki.de/",
}

RDM_CUSTOM_FIELDS = [
    LinkCF(name="mex:documentation", multiple=True),
    TextCF(name="mex:accrualPeriodicity"),
    TextCF(name="mex:publisher", multiple=True),
    TextCF(name="mex:accessService"),
    TextCF(name="mex:conformsTo", multiple=True),
    TextCF(name="mex:wikidataId", multiple=True),
    TextCF(name="mex:contributingUnit", multiple=True),
    TextCF(name="mex:viafId", multiple=True),
    LinkCF(name="mex:repositoryURL"),
    TextCF(name="mex:rorId", multiple=True),
    TextCF(name="mex:volume"),
    LinkCF(name="mex:downloadURL", multiple=True),
    TextCF(name="mex:isPartOf", multiple=True),
    TextCF(name="mex:loincId", multiple=True),
    MultiLanguageTextCF(name="mex:description", multiple=True),
    TextCF(name="mex:bibliographicResourceType", multiple=True),
    MultiLanguageTextCF(name="mex:rights", multiple=True),
    TextCF(name="mex:familyName", multiple=True),
    TextCF(name="mex:geprisId", multiple=True),
    TextCF(name="mex:isniId", multiple=True),
    TextCF(name="mex:isPartOfActivity", multiple=True),
    TextCF(name="mex:contact", multiple=True),
    MultiLanguageTextCF(name="mex:resourceTypeSpecific", multiple=True),
    TextCF(name="mex:involvedPerson", multiple=True),
    TextCF(name="mex:language", multiple=True),
    TextCF(name="mex:unitOf", multiple=True),
    LinkCF(name="mex:endpointDescription"),
    TextCF(name="mex:memberOf", multiple=True),
    TextCF(name="mex:creator", multiple=True),
    MultiLanguageTextCF(name="mex:abstract", multiple=True),
    TextCF(name="mex:publication", multiple=True),
    MultiLanguageTextCF(name="mex:title", multiple=True),
    TextCF(name="mex:issued"),
    TextCF(name="mex:editorOfSeries", multiple=True),
    TextCF(name="mex:resourceTypeGeneral", multiple=True),
    TextCF(name="mex:section"),
    EDTFDateStringCF(name="mex:start", multiple=True),
    TextCF(name="mex:icd10code", multiple=True),
    TextCF(name="mex:isbnIssn", multiple=True),
    TextCF(name="mex:parentUnit"),
    TextCF(name="mex:fullName", multiple=True),
    TextCF(name="mex:unitInCharge", multiple=True),
    TextCF(name="mex:funderOrCommissioner", multiple=True),
    TextCF(name="mex:responsibleUnit", multiple=True),
    TextCF(name="mex:gndId", multiple=True),
    TextCF(name="mex:accessRestriction"),
    MultiLanguageTextCF(name="mex:instrumentToolOrApparatus", multiple=True),
    TextCF(name="mex:hasPersonalData"),
    TextCF(name="mex:identifier", field_args={'required': True}),
    TextCF(name="mex:doi"),
    TextCF(name="mex:givenName", multiple=True),
    TextCF(name="mex:email", multiple=True),
    TextCF(name="mex:wasGeneratedBy"),
    MultiLanguageTextCF(name="mex:shortName", multiple=True),
    TextCF(name="mex:affiliation", multiple=True),
    TextCF(name="mex:sizeOfDataBasis"),
    IntegerCF(name="mex:maxTypicalAge"),
    IntegerCF(name="mex:minTypicalAge"),
    TextCF(name="mex:resourceCreationMethod", multiple=True),
    TextCF(name="mex:involvedUnit", multiple=True),
    MultiLanguageTextCF(name="mex:keyword", multiple=True),
    TextCF(name="mex:externalPartner", multiple=True),
    TextCF(name="mex:orcidId", multiple=True),
    TextCF(name="mex:temporal"),
    MultiLanguageTextCF(name="mex:subtitle", multiple=True),
    MultiLanguageTextCF(name="mex:qualityInformation", multiple=True),
    TextCF(name="mex:anonymizationPseudonymization", multiple=True),
    TextCF(name="mex:endpointType"),
    TextCF(name="mex:volumeOfSeries"),
    TextCF(name="mex:belongsTo", multiple=True),
    MultiLanguageTextCF(name="mex:method", multiple=True),
    TextCF(name="mex:mediaType"),
    MultiLanguageTextCF(name="mex:hasLegalBasis", multiple=True),
    MultiLanguageTextCF(name="mex:officialName", multiple=True),
    LinkCF(name="mex:website", multiple=True),
    MultiLanguageTextCF(name="mex:alternativeTitle", multiple=True),
    TextCF(name="mex:externalAssociate", multiple=True),
    TextCF(name="mex:created"),
    TextCF(name="mex:publicationPlace"),
    TextCF(name="mex:modified"),
    TextCF(name="mex:theme", multiple=True),
    TextCF(name="mex:usedIn", multiple=True),
    TextCF(name="mex:dataType"),
    MultiLanguageTextCF(name="mex:name", multiple=True),
    TextCF(name="mex:alternateIdentifier", multiple=True),
    TextCF(name="mex:codingSystem"),
    TextCF(name="mex:containedBy", multiple=True),
    LinkCF(name="mex:landingPage", multiple=True),
    MultiLanguageTextCF(name="mex:titleOfBook", multiple=True),
    MultiLanguageTextCF(name="mex:titleOfSeries", multiple=True),
    EDTFDateStringCF(name="mex:end", multiple=True),
    LinkCF(name="mex:endpointURL"),
    TextCF(name="mex:contributor", multiple=True),
    TextCF(name="mex:succeeds", multiple=True),
    TextCF(name="mex:license"),
    TextCF(name="mex:editor", multiple=True),
    MultiLanguageTextCF(name="mex:label", multiple=True),
    TextCF(name="mex:edition"),
    MultiLanguageTextCF(name="mex:journal", multiple=True),
    TextCF(name="mex:activityType", multiple=True),
    TextCF(name="mex:distribution", multiple=True),
    TextCF(name="mex:valueSet", multiple=True),
    TextCF(name="mex:technicalAccessibility"),
    TextCF(name="mex:meshId", multiple=True),
    TextCF(name="mex:pages"),
    EDTFDateStringCF(name="mex:publicationYear"),
    MultiLanguageTextCF(name="mex:spatial", multiple=True),
    MultiLanguageTextCF(name="mex:methodDescription", multiple=True),
    MultiLanguageTextCF(name="mex:alternativeName", multiple=True),
    MultiLanguageTextCF(name="mex:populationCoverage", multiple=True),
    LinkCF(name="mex:accessURL", multiple=True),
    TextCF(name="mex:stateOfDataProcessing", multiple=True),
    TextCF(name="mex:fundingProgram", multiple=True),
    TextCF(name="mex:issue"),
    TextCF(name="mex:accessPlatform", multiple=True),
]

RDM_CUSTOM_FIELDS_UI = [{'fields': [{'field': f.name} for f in RDM_CUSTOM_FIELDS]}]
