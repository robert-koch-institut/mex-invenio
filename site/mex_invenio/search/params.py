from invenio_records_resources.services.records.params import ParamInterpreter

ACCESS_RESTRICTION_KW = "custom_fields.mex:accessRestriction.keyword"
JOURNAL_KW = "custom_fields.mex:journal.value.keyword"
KEYWORD_KW = "custom_fields.mex:keyword.value.keyword"
ACTIVITY_TYPE_KW = "custom_fields.mex:activityType.keyword"
THEME_KW = "custom_fields.mex:theme.keyword"
PERSONAL_DATA_KW = "custom_fields.mex:hasPersonalData.keyword"
CREATION_METHOD_KW = "custom_fields.mex:resourceCreationMethod.keyword"
TITLE_KW = "custom_fields.mex:title.value.keyword"
BELONGS_TO_LABEL_KW = "index_data.belongsToLabel.keyword"
MEX_ID_KW = "custom_fields.mex:identifier.keyword"
USED_IN_ID_KW = "custom_fields.mex:usedIn.keyword"
BELONGS_TO_ID_KW = "custom_fields.mex:belongsTo.keyword"

FUNDER_DE_KW = "index_data.deFunderOrCommissioners.keyword"
FUNDER_EN_KW = "index_data.enFunderOrCommissioners.keyword"
LABEL_KW = "custom_fields.mex:label.value.keyword"
USED_IN_EN_KW = "index_data.enUsedInResource.keyword"
USED_IN_DE_KW = "index_data.deUsedInResource.keyword"

# range fields for date histograms
CREATED_RANGE = "custom_fields.mex:created.date_range"
END_RANGE = "custom_fields.mex:end.date_range"
START_RANGE = "custom_fields.mex:start.date_range"
PUBLICATION_YEAR_RANGE = "custom_fields.mex:publicationYear.date_range"

# field containers, for those with language/value sub fields
DESCRIPTION_CONTAINER = "custom_fields.mex:description"
ABSTRACT_CONTAINER = "custom_fields.mex:abstract"
SUBTITLE_CONTAINER = "custom_fields.mex:subtitle"
LABEL_CONTAINER = "custom_fields.mex:label"
TITLE_CONTAINER = "custom_fields.mex:title"
ALT_TITLE_CONTAINER = "custom_fields.mex:alternativeTitle"
KEYWORD_CONTAINER = "custom_fields.mex:keyword"

# data fields for content, where content is available as literal (or as a list of literals)
# for display and free-text searching
VARIABLE_GROUPS_EN = "index_data.enVariableGroups"
VARIABLE_GROUPS_DE = "index_data.deVariableGroups"
DESCRIPTION = "custom_fields.mex:description.value"
CREATED = "custom_fields.mex:created.date"
ABSTRACT = "custom_fields.mex:abstract.value"
START = "custom_fields.mex:start.date"
END = "custom_fields.mex:end.date"
PUBLICATION_YEAR = "custom_fields.mex:publicationYear.date"
USED_IN_EN = "index_data.enUsedInResource"
USED_IN_DE = "index_data.deUsedInResource"
USED_IN_DISPLAY = "display_data.linked_records.mex:usedIn"
BELONGS_TO_LABEL = "index_data.belongsToLabel"
BELONGS_TO_DISPLAY = "display_data.linked_records.mex:belongsTo"
DATA_TYPE = "custom_fields.mex:dataType"
CODING_SYSTEM = "custom_fields.mex:codingSystem"
TITLE = "custom_fields.mex:title.value"
ALT_TITLE = "custom_fields.mex:alternativeTitle.value"
CONTRIBUTORS = "index_data.contributors"
EXTERNAL_PARTNERS = "index_data.externalPartners"
ICD10 = "custom_fields.mex:icd10code.value"
SHORT_NAME = "custom_fields.mex:shortName.value"
EXTERNAL_ASSOCIATE = "index_data.externalAssociates"
INVOLVED_PERSON = "index_data.involvedPersons"
SUBTITLE = "custom_fields.mex:subtitle.value"
CREATOR = "index_data.creators"
KEYWORD = "custom_fields.mex:keyword.value"


DEFAULT_FIELDS = {
    TITLE,
    ALT_TITLE,
    SHORT_NAME,
    ABSTRACT,
    EXTERNAL_ASSOCIATE,
    INVOLVED_PERSON,
    SUBTITLE,
    CREATOR,
    KEYWORD,
    CONTRIBUTORS,
    DESCRIPTION,
    EXTERNAL_PARTNERS,
    ICD10,
}

MUST_FILTERS = {
    ACCESS_RESTRICTION_KW,
    JOURNAL_KW,
    KEYWORD_KW,
    ACTIVITY_TYPE_KW,
    THEME_KW,
    PERSONAL_DATA_KW,
    CREATION_METHOD_KW,
    FUNDER_DE_KW,
    FUNDER_EN_KW,
    CREATED_RANGE,
    START_RANGE,
    END_RANGE,
    PUBLICATION_YEAR_RANGE,
    MEX_ID_KW,
    USED_IN_ID_KW,
    BELONGS_TO_ID_KW,
}

AGGS = {
    ACCESS_RESTRICTION_KW,
    CREATED_RANGE,
    END_RANGE,
    START_RANGE,
    PUBLICATION_YEAR_RANGE,
    JOURNAL_KW,
    KEYWORD_KW,
    ACTIVITY_TYPE_KW,
    FUNDER_DE_KW,
    FUNDER_EN_KW,
    THEME_KW,
    PERSONAL_DATA_KW,
    CREATION_METHOD_KW,
}

SORT = {
    CREATED,
    END,
    START,
    TITLE_KW,
    PUBLICATION_YEAR,
    LABEL_KW,
    USED_IN_EN_KW,
    USED_IN_DE_KW,
    BELONGS_TO_LABEL_KW
}

MAX_AGG_SIZE = 200
MAX_PAGE_SIZE = 100
MAX_FROM = 10000


class GenericQueryParamsInterpreter(ParamInterpreter):
    def _validate(self, raw):
        self._validate_default_fields(raw)
        self._validate_must_filters(raw)
        self._validate_non_must_filters(raw)
        self._validate_aggregations(raw)
        self._validate_paging(raw)
        self._validate_sort(raw)

    def _validate_default_fields(self, raw):
        default_field = (
            raw.get("query", {}).get("query_string", {}).get("default_field")
        )
        if default_field and default_field not in DEFAULT_FIELDS:
            raise ValueError(
                f"Field '{default_field}' is not allowed as default_field."
            )

    def _validate_must_filters(self, raw):
        filters = raw.get("query", {}).get("bool", {}).get("must", [])
        if len(filters) == 0:
            return

        for f in filters:
            if "term" in f:
                field = next(iter(f["term"].keys()))
                if field not in MUST_FILTERS:
                    raise ValueError(f"MUST filter for {field} is not permitted")

            if "terms" in f:
                field = next(iter(f["terms"].keys()))
                if field not in MUST_FILTERS:
                    raise ValueError(f"MUST filter for {field} is not permitted")

            if "range" in f:
                field = next(iter(f["range"].keys()))
                if field not in MUST_FILTERS:
                    raise ValueError(f"MUST filter for {field} is not permitted")

    def _validate_non_must_filters(self, raw):
        bools = raw.get("query", {}).get("bool", {}).keys()
        if len(bools) > 0 and "must" not in bools:
            msg = "Only MUST filters are permitted in the query."
            raise ValueError(msg)

    def _validate_aggregations(self, raw):
        aggs = raw.get("aggs", {})
        for agg in aggs.values():
            if "terms" in agg:
                field = agg["terms"]["field"]
                if field not in AGGS:
                    raise ValueError(f"Aggregation for {field} is not permitted")
                size = agg["terms"].get("size", -1)
                if size > MAX_AGG_SIZE:
                    raise ValueError(
                        f"Aggregation size for {field} exceeds maximum allowed size"
                    )

            elif "date_histogram" in agg:
                field = agg["date_histogram"]["field"]
                if field not in AGGS:
                    raise ValueError(f"Aggregation for {field} is not permitted")

            else:
                raise ValueError(
                    f"Aggregation type {next(iter(agg.keys()))} is not permitted"
                )

    def _validate_paging(self, raw):
        from_ = raw.get("from", 0)
        size = raw.get("size", 10)
        if size > MAX_PAGE_SIZE:
            raise ValueError(
                f"Page size {size} exceeds maximum allowed size of {MAX_PAGE_SIZE}"
            )
        if from_ + size > MAX_FROM:
            raise ValueError(
                f"Result window (from + size = {from_ + size}) exceeds maximum allowed of {MAX_FROM}"
            )

    def _validate_sort(self, raw):
        sort = raw.get("sort", [])
        if isinstance(sort, list):
            if len(sort) == 0:
                return
            if len(sort) > 1:
                msg = "Sorting by multiple fields is not permitted."
                raise ValueError(msg)
            sort = sort[0]
        
        field = list(sort.keys())[0]
        if field not in SORT:
            raise ValueError(f"Sorting by field '{field}' is not permitted.")

    def _constrain(self, q):
        return q.filter("term", versions__is_latest=True)

    def apply(self, identity, search, params):
        """Apply generic query parameters to the search."""
        # print("#########raw###############")
        # print(json.dumps(params["raw"]))
        self._validate(params["raw"])
        q = search.from_dict(params["raw"])
        # print(json.dumps(q.to_dict()))
        return self._constrain(q)
        # print(json.dumps(q.to_dict()))


class TypeLimiterParamsInterpreter(ParamInterpreter):
    def apply(self, identity, search, params):
        """Apply type limiter to the search."""
        resource_type = params.get("resource_type")
        if resource_type:
            if isinstance(resource_type, list):
                search = search.filter(
                    "terms", metadata__resource_type__id=resource_type
                )
            else:
                search = search.filter(
                    "term", metadata__resource_type__id=resource_type
                )
        # Uncomment this to get a view on the query in development
        # print("#####################################")
        # print(json.dumps(search.to_dict()))
        return search


class HighlightParamsInterpreter(ParamInterpreter):
    def apply(self, identity, search, params):
        """Specify the highlighter fields."""
        return search.highlight(
            "custom_fields.mex:description.value",
            "custom_fields.mex:abstract.value",
            "custom_fields.mex:title.value",
        )

        # Uncomment this to get a view on the query in development
        # print("#########highlight###############")
        # print(json.dumps(search.to_dict()))
