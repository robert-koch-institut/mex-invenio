from invenio_records_resources.services.custom_fields import TextCF, EDTFDateStringCF, IntegerCF
from marshmallow import validate

from mex_invenio.custom_fields.multilanguagetext import MultiLanguageTextCF

RDM_NAMESPACES = {
    "mex": "https://mex.rki.de/",
}

# Url validator allowing for the file protocol as well
# https://github.com/robert-koch-institut/mex-model/blob/main/mex/model/fields/link.json
url_validator = validate.URL(schemes={"http", "https", "ftp", "ftps", "file"})

mex_identifier_validator = validate.Regexp(r"^[a-zA-Z0-9]{14,22}$")

email_validator = validate.Email()

RDM_CUSTOM_FIELDS = [
    MultiLanguageTextCF(name="mex:titleOfSeries", multiple=True),
    TextCF(name="mex:pages"),
    TextCF(name="mex:meshId", multiple=True), # Can be validated
    TextCF(name="mex:isPartOfActivity", multiple=True, field_args={'validate': mex_identifier_validator}),
    TextCF(name="mex:givenName", multiple=True),
    TextCF(name="mex:email", multiple=True, field_args={'validate': email_validator}),
    TextCF(name="mex:sizeOfDataBasis"),
    TextCF(name="mex:unitInCharge", multiple=True, field_args={'validate': mex_identifier_validator}),
    TextCF(name="mex:endpointURL", field_args={'validate': url_validator}),
    TextCF(name="mex:downloadURL", multiple=True, field_args={'validate': url_validator}),
    TextCF(name="mex:issued"),
    TextCF(name="mex:editor", multiple=True, field_args={'validate': mex_identifier_validator}),
    MultiLanguageTextCF(name="mex:methodDescription", multiple=True),
    TextCF(name="mex:accessRestriction"),
    TextCF(name="mex:bibliographicResourceType", multiple=True),
    TextCF(name="mex:documentation", multiple=True, field_args={'validate': url_validator}),
    MultiLanguageTextCF(name="mex:alternativeTitle", multiple=True),
    TextCF(name="mex:conformsTo", multiple=True),
    TextCF(name="mex:fundingProgram", multiple=True),
    TextCF(name="mex:publisher", multiple=True, field_args={'validate': mex_identifier_validator}),
    MultiLanguageTextCF(name="mex:alternativeName", multiple=True),
    TextCF(name="mex:externalPartner", multiple=True, field_args={'validate': mex_identifier_validator}),
    TextCF(name="mex:license"),
    TextCF(name="mex:mediaType"),
    TextCF(name="mex:doi"), # Can be validated
    TextCF(name="mex:activityType", multiple=True),
    TextCF(name="mex:repositoryURL", field_args={'validate': url_validator}),
    MultiLanguageTextCF(name="mex:title", multiple=True),
    TextCF(name="mex:geprisId", multiple=True), # Can be validated
    EDTFDateStringCF(name="mex:publicationYear"),
    TextCF(name="mex:icd10code", multiple=True), # Can be validated
    TextCF(name="mex:issue"),
    TextCF(name="mex:contact", multiple=True, field_args={'validate': mex_identifier_validator}),
    MultiLanguageTextCF(name="mex:titleOfBook", multiple=True),
    TextCF(name="mex:stateOfDataProcessing", multiple=True),
    TextCF(name="mex:orcidId", multiple=True), # Can be validated
    TextCF(name="mex:involvedUnit", multiple=True, field_args={'validate': mex_identifier_validator}),
    TextCF(name="mex:contributingUnit", multiple=True, field_args={'validate': mex_identifier_validator}),
    TextCF(name="mex:identifier", field_args={'validate': mex_identifier_validator, 'required': True}),
    MultiLanguageTextCF(name="mex:qualityInformation", multiple=True),
    TextCF(name="mex:valueSet", multiple=True),
    TextCF(name="mex:editorOfSeries", multiple=True, field_args={'validate': mex_identifier_validator}),
    TextCF(name="mex:temporal"),
    TextCF(name="mex:wasGeneratedBy", field_args={'validate': mex_identifier_validator}),
    TextCF(name="mex:volumeOfSeries"),
    TextCF(name="mex:codingSystem"),
    TextCF(name="mex:accrualPeriodicity"),
    IntegerCF(name="mex:maxTypicalAge"),
    TextCF(name="mex:memberOf", multiple=True, field_args={'validate': mex_identifier_validator}),
    TextCF(name="mex:containedBy", multiple=True, field_args={'validate': mex_identifier_validator}),
    IntegerCF(name="mex:minTypicalAge"),
    TextCF(name="mex:parentUnit", field_args={'validate': mex_identifier_validator}),
    TextCF(name="mex:alternateIdentifier", multiple=True),
    MultiLanguageTextCF(name="mex:instrumentToolOrApparatus", multiple=True),
    TextCF(name="mex:theme", multiple=True),
    TextCF(name="mex:fullName", multiple=True),
    TextCF(name="mex:endpointDescription", field_args={'validate': url_validator}),
    TextCF(name="mex:resourceTypeGeneral", multiple=True),
    TextCF(name="mex:anonymizationPseudonymization", multiple=True),
    TextCF(name="mex:created"),
    MultiLanguageTextCF(name="mex:journal", multiple=True),
    MultiLanguageTextCF(name="mex:hasLegalBasis", multiple=True),
    TextCF(name="mex:accessService", field_args={'validate': mex_identifier_validator}),
    TextCF(name="mex:belongsTo", multiple=True, field_args={'validate': mex_identifier_validator}),
    TextCF(name="mex:responsibleUnit", multiple=True, field_args={'validate': mex_identifier_validator}),
    MultiLanguageTextCF(name="mex:officialName", multiple=True),
    TextCF(name="mex:language", multiple=True),
    TextCF(name="mex:unitOf", multiple=True, field_args={'validate': mex_identifier_validator}),
    TextCF(name="mex:involvedPerson", multiple=True, field_args={'validate': mex_identifier_validator}),
    TextCF(name="mex:isPartOf", multiple=True, field_args={'validate': mex_identifier_validator}),
    MultiLanguageTextCF(name="mex:subtitle", multiple=True),
    TextCF(name="mex:dataType"),
    TextCF(name="mex:edition"),
    TextCF(name="mex:creator", multiple=True, field_args={'validate': mex_identifier_validator}),
    MultiLanguageTextCF(name="mex:label", multiple=True),
    TextCF(name="mex:hasPersonalData"),
    TextCF(name="mex:familyName", multiple=True),
    TextCF(name="mex:publicationPlace"),
    MultiLanguageTextCF(name="mex:rights", multiple=True),
    TextCF(name="mex:endpointType"),
    TextCF(name="mex:isbnIssn", multiple=True),
    EDTFDateStringCF(name="mex:end", multiple=True),
    TextCF(name="mex:modified"),
    TextCF(name="mex:accessPlatform", multiple=True, field_args={'validate': mex_identifier_validator}),
    MultiLanguageTextCF(name="mex:abstract", multiple=True),
    TextCF(name="mex:technicalAccessibility"),
    MultiLanguageTextCF(name="mex:description", multiple=True),
    TextCF(name="mex:volume"),
    MultiLanguageTextCF(name="mex:keyword", multiple=True),
    MultiLanguageTextCF(name="mex:spatial", multiple=True),
    MultiLanguageTextCF(name="mex:shortName", multiple=True),
    TextCF(name="mex:externalAssociate", multiple=True, field_args={'validate': mex_identifier_validator}),
    MultiLanguageTextCF(name="mex:name", multiple=True),
    TextCF(name="mex:isniId", multiple=True), # Can be validated
    MultiLanguageTextCF(name="mex:resourceTypeSpecific", multiple=True),
    EDTFDateStringCF(name="mex:start", multiple=True),
    TextCF(name="mex:distribution", multiple=True, field_args={'validate': mex_identifier_validator}),
    TextCF(name="mex:section"),
    TextCF(name="mex:wikidataId", multiple=True), # Can be validated
    TextCF(name="mex:publication", multiple=True, field_args={'validate': mex_identifier_validator}),
    TextCF(name="mex:viafId", multiple=True), # Can be validated
    TextCF(name="mex:affiliation", multiple=True, field_args={'validate': mex_identifier_validator}),
    TextCF(name="mex:loincId", multiple=True), # Can be validated
    TextCF(name="mex:gndId", multiple=True), # Can be validated
    TextCF(name="mex:usedIn", multiple=True, field_args={'validate': mex_identifier_validator}),
    TextCF(name="mex:resourceCreationMethod", multiple=True),
    TextCF(name="mex:accessURL", multiple=True, field_args={'validate': url_validator}),
    TextCF(name="mex:succeeds", multiple=True, field_args={'validate': mex_identifier_validator}),
    TextCF(name="mex:landingPage", multiple=True, field_args={'validate': url_validator}),
    TextCF(name="mex:rorId", multiple=True), # Can be validated
    TextCF(name="mex:website", multiple=True, field_args={'validate': url_validator}),
    TextCF(name="mex:funderOrCommissioner", multiple=True, field_args={'validate': mex_identifier_validator}),
    MultiLanguageTextCF(name="mex:method", multiple=True),
    TextCF(name="mex:contributor", multiple=True, field_args={'validate': mex_identifier_validator}),
    MultiLanguageTextCF(name="mex:populationCoverage", multiple=True),
]

RDM_CUSTOM_FIELDS_UI = [{'fields': [{'field': f.name} for f in RDM_CUSTOM_FIELDS]}]
