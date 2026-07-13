import logging
import re
import unicodedata

from invenio_records_resources.services.records.params import ParamInterpreter

ABSTRACT_CONTAINER = "custom_fields.mex:abstract"
ABSTRACT = "custom_fields.mex:abstract.value"

ACCESS_RESTRICTION_KW = "custom_fields.mex:accessRestriction.keyword"

ACTIVITY_TYPE_KW = "custom_fields.mex:activityType.keyword"

ALT_TITLE_CONTAINER = "custom_fields.mex:alternativeTitle"
ALT_TITLE = "custom_fields.mex:alternativeTitle.value"

BELONGS_TO_ID_KW = "custom_fields.mex:belongsTo.keyword"
BELONGS_TO_DISPLAY = "display_data.linked_records.mex:belongsTo"

BELONGS_TO_LABEL = "index_data.belongsToLabel"
BELONGS_TO_LABEL_KW = "index_data.belongsToLabel.keyword"

CODING_SYSTEM = "custom_fields.mex:codingSystem"

CONTRIBUTORS = "index_data.contributors"

CREATED = "custom_fields.mex:created.date"
CREATED_RANGE = "custom_fields.mex:created.date_range"

CREATION_METHOD_KW = "custom_fields.mex:resourceCreationMethod.keyword"

CREATOR = "index_data.creators"

DATA_TYPE = "custom_fields.mex:dataType"

DESCRIPTION_CONTAINER = "custom_fields.mex:description"
DESCRIPTION = "custom_fields.mex:description.value"

END = "custom_fields.mex:end.date"
END_RANGE = "custom_fields.mex:end.date_range"

EXTERNAL_ASSOCIATE = "index_data.externalAssociates"

EXTERNAL_PARTNERS = "index_data.externalPartners"

FUNDER_DE_KW = "index_data.deFunderOrCommissioners.keyword"
FUNDER_EN_KW = "index_data.enFunderOrCommissioners.keyword"

ICD10 = "custom_fields.mex:icd10code.value"

INVOLVED_PERSON = "index_data.involvedPersons"

JOURNAL_KW = "custom_fields.mex:journal.value.keyword"

KEYWORD_CONTAINER = "custom_fields.mex:keyword"
KEYWORD_KW = "custom_fields.mex:keyword.value.keyword"
KEYWORD = "custom_fields.mex:keyword.value"

LABEL_CONTAINER = "custom_fields.mex:label"
LABEL_KW = "custom_fields.mex:label.value.keyword"
LABEL = "custom_fields.mex:label.value"

MEX_ID_KW = "custom_fields.mex:identifier.keyword"

PERSONAL_DATA_KW = "custom_fields.mex:hasPersonalData.keyword"

PUBLICATION_YEAR = "custom_fields.mex:publicationYear.date"
PUBLICATION_YEAR_RANGE = "custom_fields.mex:publicationYear.date_range"

SHORT_NAME = "custom_fields.mex:shortName.value"

START = "custom_fields.mex:start.date"
START_RANGE = "custom_fields.mex:start.date_range"

SUBTITLE_CONTAINER = "custom_fields.mex:subtitle"
SUBTITLE = "custom_fields.mex:subtitle.value"

THEME_KW = "custom_fields.mex:theme.keyword"

TITLE_CONTAINER = "custom_fields.mex:title"
TITLE = "custom_fields.mex:title.value"
TITLE_KW = "custom_fields.mex:title.value.keyword"

USED_IN_ID_KW = "custom_fields.mex:usedIn.keyword"
USED_IN_DISPLAY = "display_data.linked_records.mex:usedIn"

USED_IN_EN = "index_data.enUsedInResource"
USED_IN_DE = "index_data.deUsedInResource"
USED_IN_EN_KW = "index_data.enUsedInResource.keyword"
USED_IN_DE_KW = "index_data.deUsedInResource.keyword"

VARIABLE_GROUPS_EN = "index_data.enVariableGroups"
VARIABLE_GROUPS_DE = "index_data.deVariableGroups"

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
    BELONGS_TO_LABEL_KW,
}

MAX_AGG_SIZE = 200
MAX_PAGE_SIZE = 100
MAX_FROM = 100000

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GenericQueryParamsInterpreter(ParamInterpreter):
    def _validate(self, raw):
        try:
            self._validate_default_fields(raw)
            self._validate_must_filters(raw)
            self._validate_non_must_filters(raw)
            self._validate_aggregations(raw)
            self._validate_paging(raw)
            self._validate_sort(raw)
        except ValueError as e:
            logger.warning(f"QUERY VALIDATION FAILURE: {e}")

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

        try:
            size = int(size)
        except (TypeError, ValueError):
            raise ValueError(f"Page size {size} is not a valid integer") from None
        try:
            from_ = int(from_)
        except (TypeError, ValueError):
            raise ValueError(f"From {from_} is not a valid integer") from None

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

        keys = list(sort.keys())
        if len(keys) > 0:
            field = keys[0]
            if field not in SORT:
                raise ValueError(f"Sorting by field '{field}' is not permitted.")

    def _constrain(self, q):
        return q.filter("term", versions__is_latest=True)

    def apply(self, identity, search, params):
        """Apply generic query parameters to the search."""
        # print("#########raw###############")
        # import json
        # print(json.dumps(params["raw"]))
        self._validate(params["raw"])
        q = search.from_dict(params["raw"])
        # import json
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
        print("##############TypeLimiter###################")
        import json

        print(json.dumps(search.to_dict()))
        return search


class HighlightParamsInterpreter(ParamInterpreter):
    def apply(self, identity, search, params):
        """Specify the highlighter fields."""
        if params.get("resource_type") == "variable":
            search = search.highlight(
                LABEL,
                USED_IN_DE,
                USED_IN_EN,
                BELONGS_TO_LABEL,
                DATA_TYPE,
                pre_tags=["<xh>"],
                post_tags=["</xh>"],
            )
        elif isinstance(params.get("resource_type"), list):
            search = search.highlight(
                DESCRIPTION,
                ABSTRACT,
                TITLE,
                LABEL,
                pre_tags=["<xh>"],
                post_tags=["</xh>"],
            )
        else:
            search = search.highlight(
                DESCRIPTION,
                ABSTRACT,
                TITLE,
                pre_tags=["<xh>"],
                post_tags=["</xh>"],
            )

        # Uncomment this to get a view on the query in development
        # print("#########highlight###############")
        # import json
        # print(json.dumps(search.to_dict()))

        return search


class BoostingParamsInterpreter(ParamInterpreter):
    TITLE_AGG = [TITLE, LABEL]
    DESC_AGG = [ALT_TITLE, DESCRIPTION, ABSTRACT]
    DISPLAYED_AGG = [
        KEYWORD,
        USED_IN_DE,
        USED_IN_EN,
        BELONGS_TO_LABEL,
        DATA_TYPE,
        CODING_SYSTEM,
        SUBTITLE,
        CREATOR,
    ]

    # These are the fields that we would lump into a single bucket if we needed
    # to optimise the free-text search.  For now these are also reflected in the record
    # mapping, and the free-text bucket is not implemented.
    FREE_TEXT_SEARCH_FIELDS = [
        "custom_fields.mex:title.value",
        "custom_fields.mex:method.value",
        "custom_fields.mex:keyword.value",
        "custom_fields.mex:description.value",
        "custom_fields.mex:instrumentToolOrApparatus.value",
        "custom_fields.mex:website.url",
        "custom_fields.mex:website.title",
        "custom_fields.mex:abstract.value",
        "custom_fields.mex:shortName.value",
        "custom_fields.mex:documentation.title",
        "custom_fields.mex:alternativeTitle.value",
        "custom_fields.mex:label.value",
        "custom_fields.mex:valueSet",
        "index_data.belongsToLabel",
        "index_data.contributors",
        "index_data.creators",
        "index_data.deFunderOrCommissioners",
        "index_data.enFunderOrCommissioners",
        "index_data.deUsedInResource",
        "index_data.enUsedInResource",
        "index_data.deVariableGroups.value",
        "index_data.enVariableGroups.value",
        "index_data.externalAssociates",
        "index_data.externalPartners",
        "index_data.involvedPersons",
        "index_data.enContributingUnits",
        "index_data.deContributingUnits",
    ]

    STOP_WORDS = {
        "a",
        "an",
        "and",
        "the",
        "of",
        "in",
        "on",
        "for",
        "to",
        "is",
        "are",
        "with",  # english
        "und",
        "der",
        "die",
        "das",
        "ein",
        "eine",
        "auf",
        "zu",
        "von",
        "ist",  # german
    }

    MIN_TOKEN = 4

    # BOOSTS = {
    #     "global": {
    #         TITLE: 20,
    #         LABEL: 20,
    #         ALT_TITLE: 10,
    #         DESCRIPTION: 10,
    #         ABSTRACT: 10,
    #     },
    #     "resource": {
    #         TITLE: 20,
    #         ALT_TITLE: 10,
    #         DESCRIPTION: 10,
    #         KEYWORD: 10,
    #     },
    #     "variable": {
    #         LABEL: 20,
    #         USED_IN_EN: 10,
    #         USED_IN_DE: 10,
    #         BELONGS_TO_LABEL: 10,
    #         DATA_TYPE: 10,
    #         CODING_SYSTEM: 5,
    #     },
    #     "activity": {
    #         TITLE: 20,
    #         ALT_TITLE: 10,
    #         ABSTRACT: 10,
    #         # START: 10,
    #         # END: 10
    #     },
    #     "bibliographicresource": {
    #         TITLE: 20,
    #         ALT_TITLE: 10,
    #         SUBTITLE: 10,
    #         ABSTRACT: 10,
    #         CREATOR: 10,
    #         # RESPONSIBLE_UNIT: 10
    #     },
    # }

    # def _make_functions_old(self, typ, qs):
    #     functions = []
    #     if typ not in self.BOOSTS:
    #         return functions
    #     for field, weight in self.BOOSTS[typ].items():
    #         functions.append(
    #             {
    #                 "filter": {
    #                     "query_string": {
    #                         "default_field": field,
    #                         "query": qs,
    #                     }
    #                 },
    #                 "weight": weight,
    #             }
    #         )
    #     return functions

    def _make_functions(self, norm, base, words) -> list:
        functions = []

        # 1. Exact unpunctuated, ascii-folded string appears in the field "title"
        if norm:
            functions.append(
                {
                    "filter": _match_phrase_any_field(self.TITLE_AGG, norm),
                    # "filter": {"match_phrase": {TITLE: {"query": norm}}},
                    "weight": 50,
                }
            )

        # 2. Any variation of all words in the query string appears in "title"
        if words:
            functions.append(
                {
                    "filter": {
                        "bool": {
                            "should": [
                                _wildcard_must(f, words) for f in self.TITLE_AGG
                            ],
                            "minimum_should_match": 1,
                        }
                    },
                    "weight": 45,
                }
            )

        # 2a. Any variation of any words in the query string in "title"
        if words:
            functions.append(
                {
                    "filter": {
                        "bool": {
                            "should": [
                                _wildcard_should(f, words) for f in self.TITLE_AGG
                            ],
                            "minimum_should_match": 1,
                        }
                    },
                    "weight": 40,
                }
            )

        # 3. Exact query string appears in "description" or "abstract" -> boost 8
        if norm:
            functions.append(
                {
                    "filter": _match_phrase_any_field(self.DESC_AGG, norm),
                    "weight": 8,
                }
            )

        # 4. Exact query string appears in "keyword" or "coding_system" -> boost 7
        if norm:
            functions.append(
                {
                    "filter": _match_phrase_any_field(self.DISPLAYED_AGG, norm),
                    "weight": 7,
                }
            )

        # 5. Any variation of any word in "description" or "abstract" -> boost 6
        if words:
            functions.append(
                {
                    "filter": {
                        "bool": {
                            "should": [
                                _wildcard_should(f, words) for f in self.DESC_AGG
                            ],
                            "minimum_should_match": 1,
                        }
                    },
                    "weight": 6,
                }
            )

        # 6. Any variation of any word in "keyword" or "coding_system" -> boost 5
        if words:
            functions.append(
                {
                    "filter": {
                        "bool": {
                            "should": [
                                _wildcard_should(f, words) for f in self.DISPLAYED_AGG
                            ],
                            "minimum_should_match": 1,
                        }
                    },
                    "weight": 5,
                }
            )

        # 7. Any combination of the exact words in "title" -> boost 4
        if norm:
            functions.append(
                {
                    "filter": _match_and_any_field(self.TITLE_AGG, norm),
                    # "filter": {"match": {TITLE: {"query": norm, "operator": "and"}}},
                    "weight": 4,
                }
            )

        # 8. Any combination of the exact words in "description" or "abstract" -> boost 3
        if norm:
            functions.append(
                {
                    "filter": _match_and_any_field(self.DESC_AGG, norm),
                    "weight": 3,
                }
            )

        # 9. Any combination of the exact words in "keyword" or "coding_system" -> boost 2
        if norm:
            functions.append(
                {
                    "filter": _match_and_any_field(self.DISPLAYED_AGG, norm),
                    "weight": 2,
                }
            )

        # 10. Any combination of the exact words in any other field -> boost 1.5
        # Use a multi_match across all fields (best-effort) with operator 'and'.
        if norm:
            functions.append(
                {
                    "filter": {
                        "multi_match": {
                            "query": norm,
                            "operator": "and",
                            "fields": self.FREE_TEXT_SEARCH_FIELDS,
                        }
                    },
                    "weight": 1.5,
                }
            )

        return functions

    def _normalize_text(self, text: str) -> str:
        """Remove punctuation, ascii-fold (remove diacritics), normalize spacing.

        Keeps word spacing (collapses runs of whitespace to single spaces) and
        returns lower-cased text.
        """
        if not text:
            return ""

        # Replace any punctuation characters with a space. We use Unicode
        # character categories to detect punctuation (categories starting with 'P').
        out_chars = []
        for ch in text:
            if unicodedata.category(ch).startswith("P"):
                out_chars.append(" ")
            else:
                out_chars.append(ch)
        without_punct = "".join(out_chars)

        # Decompose and strip diacritics, then keep only ASCII characters
        folded = unicodedata.normalize("NFKD", without_punct)
        ascii_only = folded.encode("ascii", "ignore").decode("ascii")

        # Normalize whitespace and lowercase
        normalized = re.sub(r"\s+", " ", ascii_only).strip().lower()
        return normalized

    def _generalise_query_string(self, qs):
        norm = self._normalize_text(qs)
        words = [w for w in norm.split(" ") if w and w not in self.STOP_WORDS]

        # Broad query_string that searches for any variation of any word: *w1* OR *w2*
        if words:
            broad_query = " OR ".join(
                [f"*{w}*" if len(w) >= self.MIN_TOKEN else w for w in words]
            )
        else:
            # If no words after normalization, fall back to match_all
            broad_query = "*"

        return norm, broad_query, words

    def apply(self, identity, search, params):
        raw = search.to_dict()

        # import json
        # print("#########boosting2###############")
        # print(json.dumps(raw, indent=2))
        # print("-----------")

        base_query = raw.get("query", {})
        musts = base_query.get("bool", {}).get("must", [])
        qs = None
        idx = None
        for i, m in enumerate(musts):
            if "query_string" in m:
                qs = m["query_string"].get("query")
                idx = i
                break

        if idx is not None:
            del musts[idx]

        if qs is not None:
            norm, broad_qs, words = self._generalise_query_string(qs)

            # typ = params.get("resource_type")
            # if isinstance(typ, list):
            #     typ = "global"

            functions = self._make_functions(norm, broad_qs, words)

            # functions = self._make_functions(typ, qs)
            if len(functions) == 0:
                return search

            if broad_qs != "*":
                musts.append(
                    {
                        "query_string": {
                            "query": broad_qs,
                            "default_operator": "OR",
                            "fields": self.FREE_TEXT_SEARCH_FIELDS,
                        }
                    }
                )

            raw["query"] = {
                "function_score": {
                    "query": base_query,
                    "functions": functions,
                    "score_mode": "sum",
                    "boost_mode": "sum",  # could also try `multiply`
                }
            }

            # print(json.dumps(raw, indent=2))
            # print("-----------")

            search = search.from_dict(raw)
            search = search.extra(explain=True)

            # Uncomment this to get a view on the query in development
            print("#########boosting - with query###############")
            import json

            print(json.dumps(search.to_dict()))

            return search

        # Uncomment this to get a view on the query in development
        print("#########boosting - no query###############")
        import json

        print(json.dumps(search.to_dict()))

        return search


def _wildcard_must(field: str, words: list[str]) -> dict:
    """Build a 'bool should' wildcard filter for any of the words in a field.

    Each word becomes a wildcard '*word*' on `field`.
    """
    must = [{"wildcard": {field: f"*{w}*"}} for w in words if w]
    if not must:
        # Match nothing if no words
        return {"bool": {"must_not": {"match_all": {}}}}
    return {"bool": {"must": must}}


def _wildcard_should(field: str, words: list[str]) -> dict:
    """Build a 'bool should' wildcard filter for any of the words in a field.

    Each word becomes a wildcard '*word*' on `field`.
    """
    should = [{"wildcard": {field: f"*{w}*"}} for w in words if w]
    if not should:
        # Match nothing if no words
        return {"bool": {"must_not": {"match_all": {}}}}
    return {"bool": {"should": should, "minimum_should_match": 1}}


def _match_phrase_any_field(fields: list[str], phrase: str) -> dict:
    """Return a bool should of match_phrase queries for the phrase across fields."""
    should = [{"match_phrase": {f: {"query": phrase}}} for f in fields]
    return {"bool": {"should": should, "minimum_should_match": 1}}


def _match_and_any_field(fields: list[str], phrase: str) -> dict:
    """Return a bool should of match (operator: and) queries across fields."""
    should = [{"match": {f: {"query": phrase, "operator": "and"}}} for f in fields]
    return {"bool": {"should": should, "minimum_should_match": 1}}
