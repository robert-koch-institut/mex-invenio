/* global $ */
import i18n from "./../i18n"

// Ensure global edges exists (library must already have created window.edges or this creates it)

window.edges = window.edges || {};
var edges = window.edges;

edges.instances = edges.instances || {};
edges.active = edges.active || {};
edges.es = edges.es || {};

window.es = window.es || {};
var es = window.es;

// Ensure mex namespace lives under edges, not as a random global
edges.mex = edges.mex || {};
const mex = edges.mex;

// Ensure sub-namespaces
mex.state = mex.state || {};
mex.constants = mex.constants || {};
mex.renderers = mex.renderers || {};
mex.components = mex.components || {};
mex.VOCABULARY = mex.VOCABULARY || {};
mex.babel = mex.babel || {};


///////////////////////////////////////////////////
// State management
mex.state.lang = "en";

// keyword fields for facets and sorting
mex.constants.ACCESS_RESTRICTION_KW = "custom_fields.mex:accessRestriction.keyword"
mex.constants.JOURNAL_KW = "custom_fields.mex:journal.value.keyword"
mex.constants.KEYWORD_KW = "custom_fields.mex:keyword.value.keyword"
mex.constants.ACTIVITY_TYPE_KW = "custom_fields.mex:activityType.keyword"
mex.constants.THEME_KW = "custom_fields.mex:theme.keyword"
mex.constants.PERSONAL_DATA_KW = "custom_fields.mex:hasPersonalData.keyword"
mex.constants.CREATION_METHOD_KW = "custom_fields.mex:resourceCreationMethod.keyword"
mex.constants.TITLE_KW = "custom_fields.mex:title.value.keyword"
mex.constants.BELONGS_TO_LABEL_KW = "index_data.belongsToLabel.keyword"
mex.constants.MEX_ID_KW = "custom_fields.mex:identifier.keyword"
mex.constants.USED_IN_ID_KW = "custom_fields.mex:usedIn.keyword"
mex.constants.BELONGS_TO_ID_KW = "custom_fields.mex:belongsTo.keyword"

mex.constants.FUNDER_DE_KW = "index_data.deFunderOrCommissioners.keyword"
mex.constants.FUNDER_EN_KW = "index_data.enFunderOrCommissioners.keyword"
// FIXME: labels are multi-lingual, so which KW you use depends on the language, but this currently
// isn't indexed to be used this way, so this will sort by whatever the first value is
mex.constants.LABEL_KW = "custom_fields.mex:label.value.keyword"
mex.constants.USED_IN_EN_KW = "index_data.enUsedInResource.keyword"
mex.constants.USED_IN_DE_KW = "index_data.deUsedInResource.keyword"

// range fields for date histograms
mex.constants.CREATED_RANGE = "custom_fields.mex:created.date_range"
mex.constants.END_RANGE = "custom_fields.mex:end.date_range"
mex.constants.START_RANGE = "custom_fields.mex:start.date_range"
mex.constants.PUBLICATION_YEAR_RANGE = "custom_fields.mex:publicationYear.date_range"

// field containers, for those with language/value sub fields
mex.constants.DESCRIPTION_CONTAINER = "custom_fields.mex:description"
mex.constants.ABSTRACT_CONTAINER = "custom_fields.mex:abstract"
mex.constants.SUBTITLE_CONTAINER = "custom_fields.mex:subtitle"
mex.constants.LABEL_CONTAINER = "custom_fields.mex:label"
mex.constants.TITLE_CONTAINER = "custom_fields.mex:title"
mex.constants.ALT_TITLE_CONTAINER = "custom_fields.mex:alternativeTitle"
mex.constants.KEYWORD_CONTAINER = "custom_fields.mex:keyword"

// data fields for content, where content is available as literal (or as a list of literals)
// for display and free-text searching
mex.constants.VARIABLE_GROUPS_EN = "index_data.enVariableGroups"
mex.constants.VARIABLE_GROUPS_DE = "index_data.deVariableGroups"
mex.constants.DESCRIPTION = "custom_fields.mex:description.value"
mex.constants.CREATED = "custom_fields.mex:created.date"
mex.constants.ABSTRACT = "custom_fields.mex:abstract.value"
mex.constants.START = "custom_fields.mex:start.date"
mex.constants.END = "custom_fields.mex:end.date"
mex.constants.PUBLICATION_YEAR = "custom_fields.mex:publicationYear.date"
mex.constants.USED_IN_EN = "index_data.enUsedInResource"
mex.constants.USED_IN_DE = "index_data.deUsedInResource"
mex.constants.USED_IN_DISPLAY = "display_data.linked_records.mex:usedIn"
mex.constants.BELONGS_TO_LABEL = "index_data.belongsToLabel"
mex.constants.BELONGS_TO_DISPLAY = "display_data.linked_records.mex:belongsTo"
mex.constants.DATA_TYPE = "custom_fields.mex:dataType"
mex.constants.CODING_SYSTEM = "custom_fields.mex:codingSystem"
mex.constants.TITLE = "custom_fields.mex:title.value"
mex.constants.ALT_TITLE = "custom_fields.mex:alternativeTitle.value"
mex.constants.CONTRIBUTORS = "index_data.contributors"
mex.constants.EXTERNAL_PARTNERS = "index_data.externalPartners"
mex.constants.ICD10 = "custom_fields.mex:icd10code.value"
mex.constants.SHORT_NAME = "custom_fields.mex:shortName.value"
mex.constants.EXTERNAL_ASSOCIATE = "index_data.externalAssociates"
mex.constants.INVOLVED_PERSON = "index_data.involvedPersons"
mex.constants.SUBTITLE = "custom_fields.mex:subtitle.value"
mex.constants.CREATOR = "index_data.creators"
mex.constants.KEYWORD = "custom_fields.mex:keyword.value"

///////////////////////////////////////////////////
// General Functions

mex.countFormat = edges.util.numFormat({
    thousandsSeparator: ",",
});

mex.fullDateFormatter = function (datestr) {
    let date = new Date(datestr);
    return date.toLocaleString("default", {
        day: "numeric",
        month: "long",
        year: "numeric",
        timeZone: "UTC",
    });
};

mex.yearFormatter = function (val) {
    let date = new Date(parseInt(val));
    return date.toLocaleString("default", {year: "numeric", timeZone: "UTC"});
};

mex.monthFormatter = function (val) {
    let date = new Date(parseInt(val));
    return date.toLocaleString("default", {
        month: "long",
        year: "numeric",
        timeZone: "UTC",
    });
};

mex.displayYearMonthPeriod = function (params) {
    let from = params.from;
    let to = params.to;

    let frdisplay = false;
    if (from) {
        frdisplay = new Date(parseInt(from)).toLocaleString('default', {
            month: 'long',
            year: 'numeric',
            timeZone: "UTC"
        });
    }

    let todisplay = false;
    if (to) {
        todisplay = new Date(parseInt(to - 1)).toLocaleString('default', {
            month: 'long',
            year: 'numeric',
            timeZone: "UTC"
        });
    }

    let range = frdisplay;
    if (to) {
        if (todisplay !== frdisplay) {
            range += ` to ${todisplay}`;
        }
    } else {
        range += "+";
    }

    return {to: to, toType: "lt", from: from, fromType: "gte", display: range}
}

mex._register = [];
mex._keymode = false;
// mex._ = function (key) {
//     if (!mex._register.includes(key)) {
//         mex._register.push(key);
//     }
//     // FIXME: embedding this here probably doesn't help with extracting the translation keys,
//     // need to replace calls to mex._ with i18n.t directly in the source code
//     // but want to see how key extraction works first
//     return i18n.t(key);
//     // if (mex._keymode === false) {
//     //     return i18n.t(key);
//     //     if (key in mex.babel) {
//     //         return mex.babel[key];
//     //     }
//     //     return key;
//     // } else {
//     //     let val = key;
//     //     if (key in mex.babel) {
//     //         val = `*${val}*`;
//     //     } else {
//     //         val = `~~${val}~~`;
//     //     }
//     //     return val;
//     // }
// };

mex._jinja_babel = function () {
    let temp = "";
    for (let r in mex._register) {
        temp += `"${mex._register[r]}": "{{ _("${mex._register[r]}") }}",\n`;
    }
    return temp;
};

mex.getLangVal = function (path, res, def) {
    let preferred = "";
    let field = edges.util.pathValue(path, res, []);
    if (field.length === 0) {
        return def;
    }
    let priority = [edges.mex.state.lang, "de", "en"];
    for (let p of priority) {
        for (let i = 0; i < field.length; i++) {
            if (p === field[i].language) {
                return field[i].value;
            }
        }
    }

    return field[0].value;
};

mex.getAllLangVals = function (path, res) {
    let fields = edges.util.pathValue(path, res, []);
    let selected = [];
    let en = [];
    let de = [];
    for (let i = 0; i < fields.length; i++) {
        let field = fields[i];
        if (field.language === mex.state.lang) {
            selected.push(field.value);
        }
        if (field.language === "en") {
            en.push(field.value);
        }
        if (field.language === "de") {
            de.push(field.value);
        }
    }
    if (selected.length === 0) {
        if (de.length > 0) {
            return de;
        } else {
            return en;
        }
    }
    return selected;
};

mex.rankedByLang = function (path, res) {
    let fields = edges.util.pathValue(path, res, []);
    let preferred = [];
    let de = [];
    let en = [];

    for (let i = 0; i < fields.length; i++) {
        let field = fields[i];
        if (field.language === mex.state.lang) {
            preferred.push(field.value);
        } else if (field.language === "de") {
            de.push(field.value);
        } else if (field.language === "en") {
            en.push(field.value);
        }
    }

    let ranked = preferred.concat(de).concat(en);
    return ranked;
};

mex.resolveOpeningQuery = function(openingQuery) {
    // we need to account for the possibility that we've been given a source argument in the url
    // but we don't want edges managing the url space
    const params = new URLSearchParams(window.location.search);
    const initialQueryObject = params.get("source") ?? "";
    const initialQueryString = params.get("q") ?? "";

    if (initialQueryObject !== "" || initialQueryString !== "") {
        const url = new URL(window.location.href);
        url.search = "";
        window.history.replaceState("", "", url.toString());
    }

    if (initialQueryObject) {
        const obj = JSON.parse(initialQueryObject);
        return new es.Query({raw: obj});
    } else if (initialQueryString) {
        openingQuery.setQueryString(initialQueryString);
        return openingQuery;
    }
}


mex.extractMultiDate = function(path, res, def) {
    let out = def;
    let dates = edges.util.pathValue(path, res, []);
    if (dates.length > 0) {
        out = dates.map((d) => { return d.date }).join(i18n.t(" or "));
        if (dates.length > 1) {
            out = `(${out})`;
        }
    }
    return out;
}

mex.refiningAndFacet = function (params) {
    let valueMap = params.valueMap || false;
    let valueFunction = params.valueFunction || false;
    let size = params.size || 10;
    return new edges.components.RefiningANDTermSelector({
        id: params.id,
        category: params.category || "left",
        field: params.field,
        size: size,
        valueMap: valueMap,
        valueFunction: valueFunction,
        renderer: new mex.renderers.RefiningANDTermSelector({
            open: true,
            controls: false,
            hideIfEmpty: true,
            title: params.title,
            useCheckboxes: true,
            showSelected: false,
            togglable: false,
            countFormat: mex.countFormat,
        }),
    });
};

mex.dateHistogram = function (params) {
    let interval = params.interval || "year";
    let displayFormatter = params.displayFormatter || mex.yearFormatter;
    if (interval === "month") {
        displayFormatter = mex.monthFormatter;
    }

    return new edges.components.DateHistogram({
        id: params.id,
        category: params.category || "left",
        field: params.field,
        interval: interval,
        displayFormatter: displayFormatter,
        sortFunction: function (values) {
            values.reverse();
            return values;
        },
        renderer: new mex.renderers.DateHistogramSelector({
            title: params.title || i18n.t("Date Histogram"),
            open: true,
            togglable: false,
            useCheckboxes: params.useCheckboxes ?? false,
            showSelected: params.showSelected ?? true,
            countFormat: mex.countFormat,
            shortDisplay: 10
        }),
    });
};

mex.fullSearchController = function (params) {
    return new edges.components.FullSearchController({
        id: params.id || "search_controller",
        category: params.category || "full",
        sortOptions: params.sortOptions || [],
        fieldOptions: params.fieldOptions || [],
        defaultField: params.defaultField || false,
        renderer: new mex.renderers.SidebarSearchController({
            searchButton: params.searchButton ?? true,
            clearButton: params.clearButton ?? false,
            searchPlaceholder: params.searchPlaceholder || i18n.t("Search..."),
            searchButtonText: params.searchButtonText || i18n.t("Search"),
            freetextSubmitDelay: params.freetextSubmitDelay || -1,
            searchTitle: params.searchTitle || i18n.t("Search"),
            compactDesign : params.compactDesign ?? false,
            label: params.label ?? i18n.t("Search"),
            inlineLabel: params.inlineLabel || false
        }),
    });
};

mex.staticHeading = function (params) {
    return new mex.components.StaticHeader({
        id : params.id || "static_header",
        category: params.category || "full",
        renderer : new mex.renderers.StaticHeaderRenderer({
            staticTitle: params.staticTitle || "",
            fontStyle : params.fontStyle || "small"
        })
    })
}

mex.pager = function (params) {
    return new edges.components.Pager({
        id: params.id || "pager",
        category: params.category || "middle",
        renderer: new mex.renderers.Pager({
            showSizeSelector: false,
            showPageNavigation: params.showPageNavigation ?? true,
            showRecordCount: params.showRecordCount ?? true,
        }),
    });
};

mex.pagerSelector = function (params) {
    return new edges.components.Pager({
        id: params.id || "pager-selector",
        category: params.category || "middle",
        renderer: new mex.renderers.Pager({
            showSizeSelector: true,
            sizePrefix: i18n.t("Show"),
            sizeSuffix: i18n.t("results per page"),
            showPageNavigation: params.showPageNavigation ?? false,
            showRecordCount: true,
            customClassForSizeSelector: "page-size-selector",
        }),
    });
};

mex.previewer = function (params) {
    return new mex.components.Previewer({
        id: params.id || "previewer",
        category: params.category || "right",
        renderer: new mex.renderers.RecordPreview({}),
    });
};

mex.recordSelector = function (params) {
    if (!params) {
        params = {};
    }

  return new mex.components.Selector({
    id: params.id || "selector",
    category: params.category || "right",
    renderer: new mex.renderers.SelectedRecords({
      title: i18n.t("Datasets for Variables Search"),
    }),
  });
};

mex.recordSelectorCompact = function (params) {
    if (!params) {
        params = {};
    }
    return new mex.components.Selector({
        id: params.id || "selector",
        category: params.category || "right",
        secondaryResults: params.secondaryResults || false,
        preSeed: params.preSeed || false,
        preSeedLoadedCallback: params.preSeedLoadedCallback || false,
        renderer: new mex.renderers.CompactSelectedRecords({
            showIfEmpty: false,
            title: i18n.t("Selected Data Sources & Datasets"),
            onSelectToggle: params.onSelectToggle || false,
            resourceComponentIds: params.resourceComponentIds || ["results"],
        }),
    });
};

mex.typeSpecificJumpOff = function(params) {

    return new mex.components.TypeSpecificJumpOff({
        id: params.id || "jump-off",
        category: params.category || "full",
        preamble: params.preamble || i18n.t("Search on specific resource type: "),
        targets: params.targets || { },
    });
}

mex.makeEdge = function (params) {
    let current_domain = document.location.host;
    let current_scheme = window.location.protocol;
    let selector = params.selector || "#edge-container";
    let search_url =
        current_scheme +
        "//" +
        current_domain +
        "/query/api/" +
        params.resourceType;
    let template =
        params.template || new mex.templates.MainSearchTemplate({
            includeVerticalTab: params.includeVerticalTab || false,
        });
    let callbacks = params.callbacks || {};

    let defaultQuery = new es.Query({size: 50});
    let oq = defaultQuery;
    if (params.openingQuery) {
        oq.merge(params.openingQuery);
    }
    return new edges.Edge({
        selector: selector,
        template: template,
        searchUrl: search_url,
        openingQuery: oq,
        components: params.components,
        secondaryQueries: params.secondaryQueries || false,
        callbacks: callbacks,
    });
};

////////////////////////////////////////////////////
// Specific functions for generating field-specific widgets

// Resources
mex.resourceDisplay = function (params) {
    if (!params) {
        params = {};
    }
    return new edges.components.ResultsDisplay({
        id: params.id || "results",
        category: params.category || "middle",
        renderer: new mex.renderers.ResourcesResults({
            noResultsText: params.noResultsText || i18n.t("No resources found."),
            onSelectToggle: params.onSelectToggle || false,
        }),
    });
};

mex.resourceDisplayCompact = function (params) {
    if (!params) {
        params = {};
    }
    return new edges.components.ResultsDisplay({
        id: params.id || "results",
        category: params.category || "middle",
        secondaryResults: params.secondaryResults || false,
        renderer: new mex.renderers.CompactResourcesResults({
            title: params.title || i18n.t("Resources"),
            noResultsText: params.noResultsText || i18n.t("No resources that match your search were found."),
            onSelectToggle: params.onSelectToggle || false,
            hideIfNoResults: params.hideIfNoResults || false,
        }),
    });
};

mex.resourcePreview = function () {
    return mex.previewer({});
};

mex.resourceSelector = function () {
    return mex.recordSelector({});
};
/////////////

// Activities
mex.activitiesDisplay = function (params) {
    if (!params) {
        params = {};
    }
    return new edges.components.ResultsDisplay({
        id: params.id || "results",
        category: params.category || "middle",
        renderer: new mex.renderers.ActivitiesResults({
            // noResultsText:
            //     params.noResultsText || i18n.t("No activities found."),
        }),
    });
};

mex.activityPreview = function () {
    return mex.previewer({});
};

///////////

// Bibliographic Resources
mex.bibliographicResourcesDisplay = function (params) {
    if (!params) {
        params = {};
    }
    return new edges.components.ResultsDisplay({
        id: params.id || "results",
        category: params.category || "middle",
        renderer: new mex.renderers.BibliographicResourcesResults({
            noResultsText:
                params.noResultsText ||
                i18n.t("No bibliographic resources found."),
        }),
    });
};

mex.bibliographicResourcesPreview = function () {
    return mex.previewer({});
};

///////////

// Variables
mex.variablesDisplay = function (params) {
    if (!params) {
        params = {};
    }
    return new edges.components.ResultsDisplay({
        id: params.id || "variables-results",
        category: params.category || "column",
        renderer: new mex.renderers.VariablesResults({
            noResultsText: params.noResultsText || i18n.t("No variables found."),
        }),
    });
};

//////////////

// Global View
mex.globalDisplay = function (params) {
    if (!params) {
        params = {};
    }
    return new edges.components.ResultsDisplay({
        id: params.id || "results",
        category: params.category || "middle",
        renderer: new mex.renderers.GlobalResults({
            noResultsText:
                params.noResultsText || i18n.t("No results found."),
        }),
    });
};

///////////

mex.accessRestrictionFacet = function () {
    return mex.refiningAndFacet({
        id: "access_restriction",
        field: mex.constants.ACCESS_RESTRICTION_KW,
        title: i18n.t("Access Restriction"),
        valueFunction: mex.vocabularyLookup,
        category: "left",
    });
};

mex.createdFacet = function () {
    return mex.dateHistogram({
        id: "created",
        field: mex.constants.CREATED_RANGE,
        title: i18n.t("Created"),
        category: "left",
        interval: "month",
        useCheckboxes: true,
        showSelected: false,
    });
};

mex.endFacet = function () {
    return mex.dateHistogram({
        id: "end",
        field: mex.constants.END_RANGE,
        title: i18n.t("Activity End"),
        category: "left",
        interval: "year",
        useCheckboxes: true,
        showSelected: false,
    });
};

mex.startFacet = function () {
    return mex.dateHistogram({
        id: "start",
        field: mex.constants.START_RANGE,
        title: i18n.t("Activity Start"),
        category: "left",
        interval: "year",
        useCheckboxes: true,
        showSelected: false,
    });
};

mex.publicationYearFacet = function () {
    return mex.dateHistogram({
        id: "publication_year",
        field: mex.constants.PUBLICATION_YEAR_RANGE,
        title: i18n.t("Publication Year"),
        category: "left",
        interval: "year",
        useCheckboxes: true,
        showSelected: false,
    });
};

mex.journalFacet = function () {
    return mex.refiningAndFacet({
        id: "journal",
        field: mex.constants.JOURNAL_KW,
        title: i18n.t("Journal"),
        category: "left",
    });
};

mex.keywordFacet = function () {
    return mex.refiningAndFacet({
        id: "keyword",
        field: mex.constants.KEYWORD_KW,
        title: i18n.t("Keyword"),
        size: 5,
        category: "left",
    });
};

mex.activityTypeFacet = function () {
    return mex.refiningAndFacet({
        id: "activity_type",
        field: mex.constants.ACTIVITY_TYPE_KW,
        title: i18n.t("Activity Type"),
        category: "left",
        valueFunction: mex.vocabularyLookup,
    });
};

mex.funderOrCommissionerFacet = function () {
    let field = mex.constants.FUNDER_DE_KW;
    if (mex.state.lang === "en") {
        field = mex.constants.FUNDER_EN_KW;
    }
    return mex.refiningAndFacet({
        id: "funder_or_commissioner",
        field: field,
        title: i18n.t("Funder or Commissioner"),
        category: "left",
    });
};

mex.themeFacet = function () {
    return mex.refiningAndFacet({
        id: "theme",
        field: mex.constants.THEME_KW,
        title: i18n.t("Theme"),
        category: "left",
        valueFunction: mex.vocabularyLookup,
    });
};

mex.hasPersonalDataFacet = function () {
    return mex.refiningAndFacet({
        id: "has_personal_data",
        field: mex.constants.PERSONAL_DATA_KW,
        title: i18n.t("Has Personal Data"),
        category: "left",
        valueFunction: mex.vocabularyLookup,
    });
};

mex.resourceCreationMethodFacet = function () {
    return mex.refiningAndFacet({
        id: "resource_creation_method",
        field: mex.constants.CREATION_METHOD_KW,
        title: i18n.t("Resource Creation Method"),
        category: "left",
        valueFunction: mex.vocabularyLookup,
    });
};

mex.defaultPager = function () {
    return mex.pager({});
};

mex.bottomPager = function () {
    return mex.pagerSelector({});
};

mex.resultCount = function (params) {
    if (!params) {
        params = {};
    }
    return new edges.components.Pager({
        id: params.id || "result-count",
        category: params.category || "left-middle-top",
        renderer: new mex.renderers.Pager({
            showSizeSelector: false,
            showPageNavigation: false,
            showRecordCount: true,
        }),
    });
}

mex.sorter = function (params) {
    if (!params) {
        params = {};
    }
    return new edges.components.FullSearchController({
        id: params.id || "sorter",
        category: params.category || "right-middle-top",
        sortOptions: params.sortOptions || [],
        renderer: new mex.renderers.Sorter({}),
    });
}

mex.selectedFilters = function (params) {
    if (!params) {
        params = {};
    }
    let defaultFieldDisplays = {}
    defaultFieldDisplays[mex.constants.ACCESS_RESTRICTION_KW] = i18n.t("Access Restriction")
    defaultFieldDisplays[mex.constants.JOURNAL_KW] = i18n.t("Journal")
    defaultFieldDisplays[mex.constants.KEYWORD_KW] = i18n.t("Keyword")
    defaultFieldDisplays[mex.constants.ACTIVITY_TYPE_KW] = i18n.t("Activity Type")
    defaultFieldDisplays[mex.constants.THEME_KW] = i18n.t("Theme")
    defaultFieldDisplays[mex.constants.PERSONAL_DATA_KW] = i18n.t("Personal Data")
    defaultFieldDisplays[mex.constants.CREATION_METHOD_KW] = i18n.t("Resource Creation Method")
    defaultFieldDisplays[mex.constants.FUNDER_DE_KW] = i18n.t("Funder or Commissioner")
    defaultFieldDisplays[mex.constants.FUNDER_EN_KW] = i18n.t("Funder or Commissioner")
    defaultFieldDisplays[mex.constants.CREATED_RANGE] = i18n.t("Created")
    defaultFieldDisplays[mex.constants.START_RANGE] = i18n.t("Activity Start")
    defaultFieldDisplays[mex.constants.END_RANGE] = i18n.t("Activity End")
    defaultFieldDisplays[mex.constants.PUBLICATION_YEAR_RANGE] = i18n.t("tPublication Year")

    let defaultValueFunctions = {}
    defaultValueFunctions[mex.constants.ACCESS_RESTRICTION_KW] = mex.vocabularyLookup
    // defaultValueFunctions[mex.constants.JOURNAL_KW] = false
    // defaultValueFunctions[mex.constants.KEYWORD_KW] = false
    defaultValueFunctions[mex.constants.ACTIVITY_TYPE_KW] = mex.vocabularyLookup
    defaultValueFunctions[mex.constants.THEME_KW] = mex.vocabularyLookup
    defaultValueFunctions[mex.constants.PERSONAL_DATA_KW] = mex.vocabularyLookup
    defaultValueFunctions[mex.constants.CREATION_METHOD_KW] = mex.vocabularyLookup
    // defaultValueFunctions[mex.constants.FUNDER_DE_KW] = i18n.t("Funder or Commissioner")
    // defaultValueFunctions[mex.constants.FUNDER_EN_KW] = i18n.t("Funder or Commissioner")

    let defaultRangeFunctions = {}
    defaultRangeFunctions[mex.constants.CREATED_RANGE] = mex.displayYearMonthPeriod
    defaultRangeFunctions[mex.constants.START_RANGE] = mex.displayYearMonthPeriod
    defaultRangeFunctions[mex.constants.END_RANGE] = mex.displayYearMonthPeriod
    defaultRangeFunctions[mex.constants.PUBLICATION_YEAR_RANGE] = mex.displayYearMonthPeriod

    return new edges.components.SelectedFilters({
        id: params.id || "selected-filters",
        category: "middle-top",
        fieldDisplays: params.fieldDisplays || defaultFieldDisplays,
        valueFunctions: params.valueFunctions || defaultValueFunctions,
        rangeFunctions: params.rangeFunctions || defaultRangeFunctions,
        renderer: new mex.renderers.SelectedFilters({})
    });
}

/////////////////////////////////////////
// Vocabulary lookup

mex.vocabularyLookup = function (value) {
    if (value in mex.VOCABULARY) {
        let lang = mex.state.lang;
        if (lang in mex.VOCABULARY[value]) {
            return mex.VOCABULARY[value][lang];
        } else if ("en" in mex.VOCABULARY[value]) {
            return mex.VOCABULARY[value]["en"];
        } else if ("de" in mex.VOCABULARY[value]) {
            return mex.VOCABULARY[value]["de"];
        } else {
            let keys = Object.keys(mex.VOCABULARY[value]);
            if (keys.length > 0) {
                return mex.VOCABULARY[value][keys[0]];
            }
        }
    }
    return value;
};

/////////////////////////////////////////
// Template(s)

if (!mex.hasOwnProperty("templates")) {
    mex.templates = {};
}

mex.templates.MainSearchTemplate = class extends edges.Template {
    constructor(params) {
        super(params);

        this.includeVerticalTab = edges.util.getParam(params, "includeVerticalTab", false);

        this.namespace = "mex-main-search-template";
    }

    draw(edge) {
        //////////////////////////////////
        // assemble the left side components
        let facets = edge.category("left");
        let facetContainers = "";
        let facetClass = edges.util.styleClasses(this.namespace, "facet");

        if (facets.length > 0) {
            for (let i = 0; i < facets.length; i++) {
                let container = `<div class="${facetClass}"><div id="${facets[i].id}"></div></div>`;
                facetContainers += container;
            }
        }

        ///////////////////////////////////
        // top middle components
        let topMiddle = edge.category("middle-top")
        let topMiddleClass = edges.util.styleClasses(this.namespace, "top-middle");
        let topMiddleContainers = "";

        if (topMiddle.length > 0) {
            for (let i = 0; i < topMiddle.length; i++) {
                topMiddleContainers += `<div class="${topMiddleClass}"><div id="${topMiddle[i].id}"></div></div>`;
            }
        }

        ///////////////////////////////////
        // left middle top
        let leftMiddleTop = edge.category("left-middle-top");
        let leftMiddleTopClass = edges.util.styleClasses(this.namespace, "left-middle-top");
        let leftMiddleTopContainers = "";

        if (leftMiddleTop.length > 0) {
            for (let i = 0; i < leftMiddleTop.length; i++) {
                leftMiddleTopContainers += `<div class="${leftMiddleTopClass}"><div id="${leftMiddleTop[i].id}"></div></div>`;
            }
        }

        ///////////////////////////////////
        // right middle top
        let rightMiddleTop = edge.category("right-middle-top");
        let rightMiddleTopClass = edges.util.styleClasses(this.namespace, "right-middle-top");
        let rightMiddleTopContainers = "";

        if (rightMiddleTop.length > 0) {
            for (let i = 0; i < rightMiddleTop.length; i++) {
                rightMiddleTopContainers += `<div class="${rightMiddleTopClass}"><div id="${rightMiddleTop[i].id}"></div></div>`;
            }
        }

        ///////////////////////////////////
        // assemble the middle components
        let mid = edge.category("middle");
        let midClass = edges.util.styleClasses(this.namespace, "middle");
        let middleContainers = "";

        if (mid.length > 0) {
            for (let i = 0; i < mid.length; i++) {
                middleContainers += `<div class="${midClass} px-0"><div id="${mid[i].id}"></div></div>`;
            }
        }

        //////////////////////////////////
        // assemble the right side components
        let right = edge.category("right");
        // Hiding right section and enabling it when any component
        let rightContainerStyle = "display:none;";
        let rightClass = edges.util.styleClasses(this.namespace, "right");
        let rightContainers = "";
        if (right.length > 0) {
            for (let i = 0; i < right.length; i++) {
                if (right[i].length > 0) {
                    rightContainerStyle = 'display:""';
                }
                rightContainers += `<div class="${rightClass}"><div id="${right[i].id}"></div></div>`;
            }
        }

        //////////////////////////////////
        // assemble the full side components
        let full = edge.category("full");
        let fullClass = edges.util.styleClasses(this.namespace, "full");
        let fullContainers = "";
        if (full.length > 0) {
            for (let i = 0; i < full.length; i++) {
                fullContainers += `<div class="${fullClass}"><div id="${full[i].id}"></div></div>`;
            }
        }

        let verticalTabFrag = "";
        if (this.includeVerticalTab) {
            let verticalTabClass = edges.util.jsClasses(
                this.namespace,
                "verticalTab",
                ""
            );
            verticalTabFrag = `<button id="vertical-tab" class="vertical-tab ${verticalTabClass}"></button>`;
        }

        let facetSidebar = "";
        if (facets.length > 0) {
            facetSidebar = `<div class="three wide column pl-0">${facetContainers}</div>`;
        }

        let frag = `
            <div class="ui grid" style="position: relative">
                <div class="sixteen wide column px-0">
                    ${fullContainers}
                </div>
                ${facetSidebar}
                <div class="wide column pr-0" style="flex: 1;">
                    <div class="ui grid" style="margin-left: 0">
                        <div class="ui grid">
                            ${topMiddleContainers}
                        </div>
                        <div class="eight wide column" style="padding-left: 0">
                            ${leftMiddleTopContainers}
                        </div>
                        <div class="eight wide column" style="padding-right: 0">
                            ${rightMiddleTopContainers}
                        </div>
                    </div>
                    <div class="ui grid" style="margin-left:0">
                        ${middleContainers}
                    </div>
                </div>
                <div id="right-col" class="five wide column" style="${rightContainerStyle} padding-right:0">
                    ${rightContainers}
                </div>
                ${verticalTabFrag}
            </div>
        `;
        edge.context.html(frag);

        let verticalTabSelector = edges.util.jsClassSelector(
            this.namespace,
            "verticalTab",
            ""
        );
        edges.on(verticalTabSelector, "click", this, "showTabContent");
    }

    showTabContent() {
        const doc = document.getElementById("right-col");
        if (doc) {
            doc.style.display = (doc.style.display === "none") ? "" : "none";
        }
    }
};

mex.templates.SingleColumnTemplate = class extends edges.Template {
    constructor(params) {
        super(params);

        this.preamble = edges.util.getParam(params, "preamble", null);
        this.hideComponentsInitially = edges.util.getParam(
            params,
            "hideComponentsInitially",
            false
        );

        this.namespace = "mex-single-column-template";
    }

    draw(edge) {
        let preambleFrag = "";
        if (this.preamble) {
            let preambleClass = edges.util.styleClasses(this.namespace, "preamble");
            preambleFrag = `<div class="${preambleClass}">${this.preamble}</div>`;
        }

        //////////////////////////////////
        // assemble displayable components
        let comps = edge.category("column");
        let compContainers = "";
        let compClass = edges.util.styleClasses(this.namespace, "component");

        if (comps.length > 0) {
            for (let i = 0; i < comps.length; i++) {
                let style = "";
                if (this.hideComponentsInitially !== false && this.hideComponentsInitially.includes(comps[i].id)) {
                    style = ` style="display:none;" `;
                }

                let container = `<div class="${compClass}"><div id="${comps[i].id}"${style}></div></div>`;
                compContainers += container;
            }
        }

        // left middle top
        let leftMiddleTop = edge.category("left-middle-top");
        let leftMiddleTopClass = edges.util.styleClasses(this.namespace, "left-middle-top");
        let leftMiddleTopContainers = "";

        if (leftMiddleTop.length > 0) {
            for (let i = 0; i < leftMiddleTop.length; i++) {
                leftMiddleTopContainers += `<div class="${leftMiddleTopClass}"><div id="${leftMiddleTop[i].id}"></div></div>`;
            }
        }

        ///////////////////////////////////
        // right middle top
        let rightMiddleTop = edge.category("right-middle-top");
        let rightMiddleTopClass = edges.util.styleClasses(this.namespace, "right-middle-top");
        let rightMiddleTopContainers = "";

        if (rightMiddleTop.length > 0) {
            for (let i = 0; i < rightMiddleTop.length; i++) {
                rightMiddleTopContainers += `<div class="${rightMiddleTopClass}"><div id="${rightMiddleTop[i].id}"></div></div>`;
            }
        }

        let frag = `
            <div class="ui grid" style="margin-left: 0">
                <div class="sixteen wide column">
                    ${preambleFrag}
                    ${leftMiddleTopContainers}
                    ${rightMiddleTopContainers}
                    ${compContainers}
                </div>
            </div>
        `;
        edge.context.html(frag);
    }
};

//////////////////////////////////////////////
// Components
if (!mex.hasOwnProperty("components")) {
    mex.components = {};
}

mex.components.TypeSpecificJumpOff = class extends edges.Component {
    constructor(params) {
        super(params)

        this.preamble = edges.util.getParam(params, "preamble", "");
        this.targets = edges.util.getParam(params, "targets", {});
    }

    draw() {
        if (!this.edge.currentQuery) {
            this.context.html("");
            return;
        }

        if (this.targets.length === 0) {
            this.context.html("");
            return;
        }

        let frag = `<div class="search-specific-types-container">
        <p>${this.preamble}</p>
                                ${this.renderTargets()}
                            </div>`;
        this.context.html(frag);
    }

    renderTargets() {
        const qs = this.queryString();
        let frag = ``;
        for (let url in this.targets) {
            let display = this.targets[url];
            frag += `<a href="${url}?${qs}" class="button-like">${display}</a>`;
        }
        return frag;
    }

    queryString() {
        const objectify_options = {
            include_query_string : true,
            include_filters : false,
            include_paging : false,
            include_sort : true,
            include_fields : false,
            include_aggregations : false
        }
        const q = JSON.stringify(this.edge.currentQuery.objectify(objectify_options));
        let obj = {};
        obj["source"] = encodeURIComponent(q);
        const qs = this.edge._makeUrlQuery(obj)
        return qs;
    }
}

mex.components.StaticHeader = class extends edges.Component {
    constructor(params) {
        super(params)
    }
}

mex.components.Selector = class extends edges.Component {
    constructor(params) {
        super(params);

        this._resources = {};
        this._variable_groups = {};

        this.preSeed = edges.util.getParam(params, "preSeed", false);
        this.preSeedLoadedCallback = edges.util.getParam(
            params,
            "preSeedLoadedCallback",
            function () {}
        );
    }

    init(edge) {
        super.init(edge);

        if (this.preSeed && this.preSeed.length > 0) {
            this.clearAll(false);
            this.loadPreSeed();
        } else {

            let ids = window.localStorage.getItem("selection");
            ids = JSON.parse(ids);
            if (ids) {
                for (let id of ids) {
                    let object = window.localStorage.getItem(id);
                    if (object) {
                        object = JSON.parse(object);
                        this._resources[id] = object;
                    }
                }
            }

            let vgs = window.localStorage.getItem("variable_groups");
            vgs = JSON.parse(vgs);
            if (vgs) {
                for (let vg of vgs) {
                    let sel = window.localStorage.getItem(vg);
                    this._variable_groups[vg] = sel === "t";
                }
            }
        }
    }

    loadPreSeed() {
        // register blank records for the moment, so downstream
        // queries can use the ids
        // for (let id of this.preSeed) {
        //     this.registerRecord(id, {});
        // }

        let resourceQuery = new es.Query({size: this.preSeed.length});
        resourceQuery.addMust(
            new es.TermsFilter({
                field: "custom_fields.mex:identifier.keyword",
                values: this.preSeed,
            })
        );

        // issue the query to elasticsearch
        this.edge.queryAdapter.doQuery({
            edge: this.edge,
            query: resourceQuery,
            success: edges.util.objClosure(this, "preSeedQuerySuccess", ["result"]),
            error: edges.util.objClosure(this, "preSeedQueryFail")
        });
    }

    preSeedQuerySuccess(params) {
        let hits = params.result.results();
        if (hits == null || hits.length === 0) {
            // no resources found, so just init normally
            alert("No matching resources found for pre-selection");
            this.preSeedLoadedCallback();
            return;
        }

        // we have found the resource, so set it into local storage
        for (let hit of hits) {
            this.registerRecord(hit.id, hit);
        }

        this.preSeedLoaded = true;
        this.draw();
        this.preSeedLoadedCallback();
    }

    preSeedQueryFail() {
        alert("Failed to load resource details for pre-selection");
    }

    // isSeedLoaded() {
    //     let hadSeed = this.preSeed && this.preSeed.length > 0;
    //     if (!hadSeed) {
    //         return true;
    //     }
    //     return this.preSeedLoaded;
    // }

    ////////////////////////////////////////
    // pure data access functions

    get length() {
        return this.ids().length;
    }

    get(id) {
        return this._resources[id];
    }

    set(id, data) {
        this._resources[id] = data;
        window.localStorage.setItem(id, JSON.stringify(data));
        window.localStorage.setItem("selection", JSON.stringify(this.ids()));
    }

    delete(id) {
        delete this._resources[id];
        window.localStorage.removeItem(id);
        window.localStorage.setItem("selection", JSON.stringify(this.ids()));
    }

    clearAll(draw=true) {
        this._resources = {};
        this._variable_groups = {};
        window.localStorage.clear();
        if (draw) {
            this.draw();
        }
    }

    ids() {
        return Object.keys(this._resources);
    }

    isSelected(id) {
        return this._resources.hasOwnProperty(id);
    }

    registerRecord(id, data) {
        this.set(id, data);

        let en = edges.util.pathValue(
            mex.constants.VARIABLE_GROUPS_EN,
            data,
            []
        );
        for (let group of en) {
            this.recordVariableGroup(group.mex_id, true);
        }

        let de = edges.util.pathValue(
            mex.constants.VARIABLE_GROUPS_DE,
            data,
            []
        );
        for (let group of de) {
            this.recordVariableGroup(group.mex_id, true);
        }
    }

    //////////////////////////////////////
    // component behavioural functions

    selectRecord(id) {
        for (let hit of this.edge.result.data.hits.hits) {
            if (id === hit._source.id) {
                this.registerRecord(id, hit._source);
                break;
            }
        }
        this.draw();
    }

    unselectRecord(id) {
        let record = this.get(id);
        if (!record) {
            return;
        }
        let en = edges.util.pathValue(mex.constants.VARIABLE_GROUPS_EN, record, []);
        for (let group of en) {
            this.removeVariableGroup(group.mex_id, true);
        }

        let de = edges.util.pathValue(mex.constants.VARIABLE_GROUPS_DE, record, []);
        for (let group of de) {
            this.removeVariableGroup(group.mex_id, true);
        }

        this.delete(id);
        this.draw();
    }

    recordVariableGroup(id, defaultSelection) {
        if (this._variable_groups.hasOwnProperty(id)) {
            return;
        }

        this._variable_groups[id] = defaultSelection;
        window.localStorage.setItem(id, defaultSelection ? "t" : "f");
        window.localStorage.setItem(
            "variable_groups",
            JSON.stringify(Object.keys(this._variable_groups))
        );
    }

    removeVariableGroup(id) {
        if (!this._variable_groups.hasOwnProperty(id)) {
            return;
        }

        delete this._variable_groups[id];
        window.localStorage.removeItem(id);
        window.localStorage.setItem(
            "variable_groups",
            JSON.stringify(Object.keys(this._variable_groups))
        );
    }

    variableGroupRecorded(id) {
        return this._variable_groups.hasOwnProperty(id);
    }

    selectVariableGroup(id) {
        this._variable_groups[id] = true;
        window.localStorage.setItem(id, "t");
        window.localStorage.setItem(
            "variable_groups",
            JSON.stringify(Object.keys(this._variable_groups))
        );
    }

    unselectVariableGroup(id) {
        this._variable_groups[id] = false;
        window.localStorage.setItem(id, "f");
        window.localStorage.setItem(
            "variable_groups",
            JSON.stringify(Object.keys(this._variable_groups))
        );
    }

    variableGroupSelected(id) {
        if (this._variable_groups.hasOwnProperty(id)) {
            return this._variable_groups[id];
        }
        return false;
    }

    selectedVariableGroups() {
        let all = window.localStorage.getItem("variable_groups");
        all = JSON.parse(all);
        let selected = [];
        if (all) {
            for (let id of all) {
                let sel = window.localStorage.getItem(id);
                if (sel === "t") {
                    selected.push(id);
                }
            }
        }
        return selected;
    }
};

//////////////////////////////////////////////
// Renderers

if (!mex.hasOwnProperty("renderers")) {
    mex.renderers = {};
}

mex.renderers.SelectedFilters = class extends edges.Renderer {
    constructor(params) {
        super(params);

        this.showFilterField = edges.util.getParam(params, "showFilterField", true);

        this.allowRemove = edges.util.getParam(params, "allowRemove", true);

        this.showSearchString = edges.util.getParam(params, "showSearchString", false);

        this.ifNoFilters = edges.util.getParam(params, "ifNoFilters", false);

        this.hideValues = edges.util.getParam(params, "hideValues", []);

        this.omit = edges.util.getParam(params, "omit", []);

        this.namespace = "edges-mex-selected-filters";
    }

    draw() {
        // for convenient short references
        let sf = this.component;
        let ns = this.namespace;

        // sort out the classes we are going to use
        let fieldClass = edges.util.styleClasses(ns, "field", this);
        let fieldNameClass = edges.util.styleClasses(ns, "fieldname", this);
        let valClass = edges.util.styleClasses(ns, "value", this);
        let clearAllClass = edges.util.styleClasses(ns, "clear-all", this);
        let containerClass = edges.util.styleClasses(ns, "container", this);

        let filters = "";

        if (this.showSearchString && sf.searchString) {
            let field = sf.searchField;
            let text = sf.searchString;
            filters += `<span class="filters ${fieldClass}">`;
            if (field) {
                if (field in sf.fieldDisplays) {
                    field = sf.fieldDisplays[field];
                }
                filters += `<span class="${fieldNameClass}">${field}:&nbsp;</span>`;
            }
            filters += `<span class="${valClass}">${text}</span></span>`;
        }

        var fields = Object.keys(sf.mustFilters);
        var showClear = false;
        for (var i = 0; i < fields.length; i++) {
            var field = fields[i];
            var def = sf.mustFilters[field];
            var removeClass = edges.util.allClasses(ns, "remove", this);

            // render any compound filters
            if (def.filter === "compound") {
                filters += `<li class="${valClass}">
                                <a href="DELETE" class="${removeClass}" data-compound="${field}" title="Remove">
                                    ${def.display}
                                    <span data-feather="x" aria-hidden="true"></span>
                                </a>
                            </li>`;
                showClear = true;
            } else {
                if ($.inArray(field, this.omit) > -1) {
                    continue;
                }
                showClear = true;
            }

            for (var j = 0; j < def.values.length; j++) {
                filters += `<span class="filters ${fieldClass}">`;
                if (this.showFilterField) {
                    filters += `<span class="${fieldNameClass}">${def.display}:&nbsp;</span>`;
                }
                let val = def.values[j];
                let valDisplay = ": " + val.display;
                if ($.inArray(field, this.hideValues) > -1) {
                    valDisplay = "";
                }
                filters += `<span class="${valClass}">${val.display}</span>`;

                // the remove block looks different, depending on the kind of filter to remove
                if (this.allowRemove) {
                    if (def.filter === "term" || def.filter === "terms") {
                        filters += `<button class="${removeClass} img-button" data-bool="must" data-filter="${def.filter}" data-field="${field}" data-value="${val.val}" title="Remove" href="#">
                                        <img src="/static/images/close.svg" alt="Remove" title="Remove" style="width:24px;height:24px;vertical-align:middle"/>
                                    </button>`;
                    } else if (def.filter === "range") {
                        var from = val.from ? ' data-' + val.fromType + '="' + val.from + '" ' : "";
                        var to = val.to ? ' data-' + val.toType + '="' + val.to + '" ' : "";
                        filters += `<button class="${removeClass} img-button" data-bool="must" data-filter="${def.filter}" data-field="${field}" ${from} ${to} title="Remove" href="#">
                                        <img src="/static/images/close.svg" alt="Remove" title="Remove" style="width:24px;height:24px;vertical-align:middle"/>
                                    </button>`;
                    }
                }

                filters += "</span>";
            }
        }

        if (showClear) {
            let clearClass = edges.util.allClasses(this.namespace, "clear", this);
            let clearFrag = `<button type="button" class="filters ${clearClass} ui black basic button" title="Clear all search and sort parameters and start again">
                    Clear all
                </button>`;

            filters += '<span class="' + clearAllClass + '">' + clearFrag + '</span>';
        }

        if (filters === "" && this.ifNoFilters) {
            filters = this.ifNoFilters;
        }

        if (filters !== "") {
            let frag = `<div class="ui grid ${containerClass}"><div class="sixteen wide column">${filters}</div></div>`;
            sf.context.parent().show();
            sf.context.html(frag);

            // click handler for when a filter remove button is clicked
            let removeSelector = edges.util.jsClassSelector(ns, "remove", this);
            edges.on(removeSelector, "click", this, "removeFilter");

            // click handler for when the clear button is clicked
            let clearSelector = edges.util.jsClassSelector(ns, "clear", this);
            edges.on(clearSelector, "click", this, "clearFilters");
        } else {
            sf.context.parent().hide();
        }
    }

    /////////////////////////////////////////////////////
    // event handlers

    removeFilter(element) {
        var el = this.component.jq(element);

        // if this is a compound filter, remove it by id
        var compound = el.attr("data-compound");
        if (compound) {
            this.component.removeCompoundFilter({compound_id: compound});
            return;
        }

        // otherwise follow the usual instructions for removing a filter
        var field = el.attr("data-field");
        var ft = el.attr("data-filter");
        var bool = el.attr("data-bool");

        var value = false;
        if (ft === "terms" || ft === "term") {
            var val = el.attr("data-value");
            // translate string value to a type required by a model
            if (val === "true") {
                value = true;
            } else if (val === "false") {
                value = false;
            } else if (!isNaN(parseInt(val))) {
                value = parseInt(val);
            } else {
                value = val;
            }
        } else if (ft === "range") {
            value = {};

            var from = el.attr("data-gte");
            var fromType = "gte";
            if (!from) {
                from = el.attr("data-gt");
                fromType = "gt";
            }

            var to = el.attr("data-lt");
            var toType = "lt";
            if (!to) {
                to = el.attr("data-lte");
                toType = "lte";
            }

            if (from) {
                value["from"] = parseInt(from);
                value["fromType"] = fromType;
            }
            if (to) {
                value["to"] = parseInt(to);
                value["toType"] = toType;
            }
        }

        this.component.removeFilter(bool, ft, field, value);
    }

    clearFilters() {
        this.component.clearSearch();
    }
}

mex.renderers.SelectedRecords = class extends edges.Renderer {
    constructor(params) {
        super(params);
        this.title = edges.util.getParam(params, "title", "Selected Resources");
        this.showIfEmpty = edges.util.getParam(params, "showIfEmpty", false);
        this.namespace = "select-records";

        this.resourceComponentIds = edges.util.getParam(params, "resourceComponentIds", ["results"]);

        this.resourceComponents = [];
    }

    init(component) {
        super.init(component);
        for (let id of this.resourceComponentIds) {
            let resComp = this.component.edge.getComponent({
                id: id,
            });
            this.resourceComponents.push(resComp);
        }
        // this.resourceComponent = this.component.edge.getComponent({
        //     id: "results",
        // });
    }

    draw() {
        if (this.component.length === 0 && this.showIfEmpty) {
            let frag = `<div class="card card-shadow">
                <div class="divider"></div>

                <h4 class="title" style="margin:0px">${this.title}</h4>
                <div>
                    <p>${i18n.t(
                "Select resources from the search results to save them here."
            )}</p>
                </div>
            </div>`;
            this.component.context.html(frag);
            return;
        }

        let recordsFrag = ``;
        let selectClass = edges.util.jsClasses(
            this.namespace,
            "select",
            this.component.id
        );
        let hideClass = edges.util.jsClasses(
            this.namespace,
            "hide",
            this.component.id
        );
        let clearAllRecordsClass = edges.util.jsClasses(
            this.namespace,
            "clear-all",
            this.component.id
        );


        for (let id of this.component.ids()) {
            let record = this.component.get(id);

            let title = mex.getLangVal(
                mex.constants.TITLE_CONTAINER,
                record,
                i18n.t("No title")
            );

            let variableGroups = edges.util.pathValue(mex.constants.VARIABLE_GROUPS_DE, record, []);
            if (mex.state.lang === "en") {
                variableGroups = edges.util.pathValue(mex.constants.VARIABLE_GROUPS_EN, record, []);
            }

            let vgCount = variableGroups.length;
            let vgFrag = variableGroups.length > 0 ? `${vgCount} ${i18n.t("Variable Groups")}` : i18n.t("No Variable Groups");
            let vCount = 0;
            if ("backwards_linked" in record["display_data"]["linked_records"]) {
                if ("mex:usedIn" in record["display_data"]["linked_records"]["backwards_linked"]) {
                    vCount = record["display_data"]["linked_records"]["backwards_linked"]["mex:usedIn"].length
                }
            }
            let vFrag = `${vCount} ${i18n.t("Variables")}`
            let frag = [vFrag, i18n.t("in"), vgFrag].join(" ");

            recordsFrag += `
                <div class="selected-list">
                    <button class="img-button">
                      <img
                        data-id="${id}"
                        class="${selectClass} controls close-icon" src="/static/images/close.svg" alt="Slide right" />
                    </button>
                    <div>
                        <div class="selected-list-item">
                            <a href="/records/${id}" target="_blank" class="max-line-3">${title}</a>
                            <p class="variables-count muted" style="margin-bottom: 0">
                                (${frag})
                            </p>
                        </div>
                    </div>
                </div>`;
        }

        let title = `go to the variables search page to list the variables of ${this.component.length} resources`;

        let frag = `
            <div class="card card-shadow">
                <div id="control-section">
                    <button class="img-button">
                    <img class="${hideClass} controls slide-icon" src="/static/images/slide-right.svg" alt="Slide right" />
                    </button>
                </div>

                <div class="divider"></div>

                <div class="title-container" style="margin-top: 1rem; margin-bottom: 1rem;">
                    <h4 class="title" style="margin:0px">${this.title}</h4>
                    <button class="ui button tetriary ${clearAllRecordsClass}"> Clear All </button>
                </div>`
        if (recordsFrag) {
            frag += `<div>
                        ${recordsFrag}
                    </div>
                    <a class="link-button" href="/search/variables" title="${title}">
                        ${i18n.t("Explore Variables for Chosen Datasets")}
                    </a>
        `;
        }
        else {
            frag += `<p class="muted" style="font-size: 1rem; font-style: italic"> Nothing here yet. Click the plus button on the results list to add the Data Source/Dataset to the Variables Filter</p>`
        }
        frag += `</div>`

        let verticalBar = document.getElementById("vertical-tab");
        if (verticalBar) {
            const length = this.component.length;
            verticalBar.innerHTML = `<span> ${i18n.t(
                "Variables Filter"
            )} ${length > 0 ? `(${length})` : ""} </span>`;
        }

        this.component.context.html(frag);

        let selectSelector = edges.util.jsClassSelector(
            this.namespace,
            "select",
            this.component.id
        );
        let hideSelector = edges.util.jsClassSelector(
            this.namespace,
            "hide",
            this.component.id
        );
        let clearAllSelector = edges.util.jsClassSelector(
            this.namespace,
            "clear-all",
            this.component.id
        );

        edges.on(selectSelector, "click", this, "selectResource");
        edges.on(hideSelector, "click", this, "hideSelectedRecords");
        edges.on(clearAllSelector, "click", this, "clearAllRecords");
    }

    hideSelectedRecords() {
        let doc = document.getElementById("right-col");
        if (doc) {
            doc.style.display = "none";
        }
    }

    clearAllRecords() {
        this.component.clearAll();
        this._resourceComponentsRefresh();

        // let conf = confirm("Are you sure you want to remove all the selected resources?")

        // if(conf) {
        //     this.component.clearAll();
        //     this._resourceComponentsRefresh();
            // this.resourceComponent.renderer.draw();
        // }
    }

    selectResource(element) {
        let el = $(element);
        let id = el.attr("data-id");

        this.component.unselectRecord(id);
        this._resourceComponentsSelectResource(id, true);

        // Syncing this with resource result component.
        // if (doc) {
        //     this._resourceComponentsSelectResource(doc);
        //     // this.resourceComponent.renderer.selectResource(doc);
        // }
        // else {
        //     this._resourceComponentsRefresh();
        //     //this.resourceComponent.renderer.draw();
        // }
    }

    _resourceComponentsRefresh() {
        for (let resComp of this.resourceComponents) {
            if (resComp && resComp.renderer) {
                resComp.renderer.draw();
            }
        }
    }

    _resourceComponentsSelectResource(id, propagate) {
        for (let resComp of this.resourceComponents) {
            if (resComp && resComp.renderer) {
                resComp.renderer.selectResourceIfVisible(id, propagate);
            }
        }
    }
};

mex.renderers.CompactSelectedRecords = class extends mex.renderers.SelectedRecords {
    constructor(params) {
        super(params);

        this.onSelectToggle = edges.util.getParam(params, "onSelectToggle", null);

        // FIXME: may want to change the namespace
        this.namespace = "select-records";
    }

    draw() {
        let header = this.title ? `<h5 class="tiny" style="margin:0.625rem 0rem">${this.title}</h5>` : ""

        let expandAllClass = edges.util.jsClasses(
            this.namespace,
            "variable-expand-all",
            this.component.id
        );

        let expandAllCheckbox = `
                <div class="checkbox" style="margin:1rem 0rem;">
                    <label>
                        ${i18n.t("Expand all")}
                        <input type="checkbox" class="${expandAllClass}"/>
                    </label>
                </div>`

        if (this.component.length === 0 && this.showIfEmpty) {

            let frag = `
                <div>
                ${header}
                <div>
                    <p>${i18n.t(
                `Search for resources here.  Selecting a resource will limit the variables displayed to
                        those associated with the selected resources.`
            )}</p>
                </div>
            </div>`;
            this.component.context.html(frag);
            return;
        }

        let recordsFrag = ``;
        let selectClass = edges.util.jsClasses(
            this.namespace,
            "select",
            this.component.id
        );
        let clearAllRecordsClass = edges.util.jsClasses(
            this.namespace,
            "clear-all",
            this.component.id
        );

        for (let id of this.component.ids()) {
            let record = this.component.get(id);

            let title = mex.getLangVal(
                mex.constants.TITLE_CONTAINER,
                record,
                i18n.t("No title")
            );

            if (this.component.edge.result) {
                let hits = this.component.edge.result.data.hits.hits;
                for (let hit of hits) {
                    if (record.uuid === hit._id) {
                        if (hit.highlight) {
                            if (hit.highlight[edges.mex.constants.TITLE]) {
                                title = hit.highlight[edges.mex.constants.TITLE][0];
                                title = title.replace(/<em>/g, "<code>");
                                title = title.replace(/<\/em>/g, "</code>");
                            }
                        }
                    }
                }
            }

            let lang = mex.state.lang;
            let vgField = lang === "en" ? mex.constants.VARIABLE_GROUPS_EN : mex.constants.VARIABLE_GROUPS_EN;
            let vgs = edges.util.pathValue(vgField, record, []);

            let vgFrag = "No variable groups";
            let variableToggleClass = edges.util.jsClasses(
                this.namespace,
                "variable-toggle",
                this.component.id
            );

            let vgSelectClass = edges.util.jsClasses(
                this.namespace,
                "group-select",
                this.component.id
            );
            if (vgs.length > 0) {
                vgFrag = `<button class="${variableToggleClass} ui button link-like button--dropdown" style="margin-bottom: .5rem">${i18n.t(
                    "Variable Groups"
                )}
                                <span class="dir">▾</span></button>
                          <div style="display:none;" class="checkbox dropdown-with-checkbox">`;
                for (let vg of vgs) {
                    const inputName = edges.util.htmlID(this.namespace, `vg-input-${vg.mex_id}`, this.component.id);

                    let selected = this.component.variableGroupSelected(vg.mex_id);
                    let selectedFrag = "";
                    if (selected) {
                        selectedFrag = 'checked="checked"';
                    }
                    vgFrag += `<div class="variables"><input type="checkbox" name="${inputName}" id="${inputName}" data-id="${vg.mex_id}" class="${vgSelectClass}" ${selectedFrag}/>
                                <label for="${inputName}" title="${vg.value}" class="max-line-2">${vg.value}</label></div>`;
                }
                vgFrag += `</div>`;
            }

            recordsFrag += `
                <div class="card">
                    <div class="selected-list-item">
                        <div class="selected-list-item--title">
                            <button class="img-button" style="margin-top: -0.25rem">
                                <img
                                    data-id="${id}"
                                    class="${selectClass} controls" src="/static/images/close.svg" alt="Slide right" width="24px" height="32px"/>
                            </button>
                            <span class="max-line-2">${title}</span>
                        </div>
                        <div class="selected-list-sub-item">
                            ${vgFrag}
                        </div>
                    </div>
                </div>`;
        }

        let frag = "";
        if (recordsFrag) {
            frag = `
                <div class="">
                    ${expandAllCheckbox}
                    ${header}
                    <div class="" style="margin-top:1.625rem">
                      <button class="ui button tetriary ${clearAllRecordsClass}"> Clear All </button>
                    </div>
                    <div>
                        ${recordsFrag}
                    </div>
                </div>
                `;
        }

        this.component.context.html(frag);

        let selectSelector = edges.util.jsClassSelector(
            this.namespace,
            "select",
            this.component.id
        );
        edges.on(selectSelector, "click", this, "selectResource");

        let toggleSelector = edges.util.jsClassSelector(
            this.namespace,
            "variable-toggle",
            this.component.id
        );
        edges.on(toggleSelector, "click", this, "toggleVariableGroups");

        let vgSelectSelector = edges.util.jsClassSelector(
            this.namespace,
            "group-select",
            this.component.id
        );
        edges.on(vgSelectSelector, "change", this, "toggleVariableGroupSelection");

        let clearAllSelector = edges.util.jsClassSelector(
            this.namespace,
            "clear-all",
            this.component.id
        );

        edges.on(clearAllSelector, "click", this, "clearAllRecords");

        let expandAllSelector = edges.util.jsClassSelector(
            this.namespace,
            "variable-expand-all",
            this.component.id
        );
        edges.on(expandAllSelector, "change", this, "toggleVariableExpandAll");
    }

    hideSelectedRecords() {
        // Do nothing, as this is a compact view
    }

    toggleVariableExpandAll(element){
        try {
            const $ctx = this.component.context;
            const isChecked = element.checked;
            const selector = "span.dir";
            const $dirs = $ctx.find(selector);
            const $nextElements = $dirs.parent().next();

            // Determine the symbol and visibility
            const currentSymbol = isChecked ? "▴" : "▾";

            // Toggle related elements
            if (isChecked) {
                $nextElements.show();
            } else {
                $nextElements.hide();
            }

            $dirs.text(currentSymbol);

        } catch (err) {
            console.error(`Error while expanding variable groups: ${err}`);
        }
    }

    clearAllRecords() {

        this.component.clearAll();
        this._resourceComponentsRefresh();

        if (this.onSelectToggle) {
            this.onSelectToggle({parent: this});
        }
    }

    selectResource(element) {
        let el = $(element);
        let id = el.attr("data-id");

        this.component.unselectRecord(id);
        this._resourceComponentsSelectResource(id, false);

        if (this.onSelectToggle) {
            this.onSelectToggle({parent: this, id: id});
        }
    }

    toggleVariableGroups(element) {
        let el = $(element);
        let dir = el.find("span.dir");
        if (dir.text() === "▾") {
            dir.text("▴");
        } else {
            dir.text("▾");
        }
        el.next().toggle();
    }

    toggleVariableGroupSelection(element) {
        let el = $(element);
        let id = el.attr("data-id");
        if (el.is(":checked")) {
            this.component.selectVariableGroup(id);
            this.component.context
                .find("input[data-id='" + id + "']")
                .prop("checked", true);
        } else {
            this.component.unselectVariableGroup(id);
            this.component.context
                .find("input[data-id='" + id + "']")
                .prop("checked", false);
        }

        if (this.onSelectToggle) {
            this.onSelectToggle({parent: this, id: id});
        }
    }
};

mex.renderers.RecordPreview = class extends edges.Renderer {
    constructor(params) {
        super(params);
    }

    draw() {
        if (this.component.currentPreview === null) {
            this.component.context.html("");
            return;
        }

        let fieldsFrag = `<h2>${i18n.t("Preview")}</h2>`;
        for (let fieldDef of this.component.fields) {
            let field = "custom_fields." + fieldDef.field;
            let display = fieldDef.name;
            let selectLang = fieldDef.lang || false;
            let displayFunction = fieldDef.valueFunction || null;

            let vals = [];
            if (selectLang) {
                vals = mex.getAllLangVals(field, this.component.currentPreview);
            } else {
                let vals = edges.util.pathValue(
                    field,
                    this.component.currentPreview,
                    []
                );
                if (vals !== "" && vals !== null && !Array.isArray(vals)) {
                    vals = [vals];
                }
            }

            if (vals.length === 0) {
                continue; // skip this field if no value
            }

            if (displayFunction) {
                vals = vals.map((val) => displayFunction(val, this));
            }

            let val = vals.join(", ");

            // render the field
            fieldsFrag += `<dt>${display}</dt><dd>${val}</dd>`;
        }

        let frag = `<dl>${fieldsFrag}</dl>`;
        this.component.context.html(frag);
    }
};

mex.renderers.StaticHeaderRenderer = class extends edges.Renderer{
    constructor(params) {
        super(params);

        // Just add static header
        this.staticTitle = edges.util.getParam(params, "staticTitle", "");

        // font size is added to the header
        this.fontStyle = edges.util.getParam(
            params,
            "fontStyle",
            "small"
        );
    }

    draw(){
        const frag = `
            <div class="ui sizer vertical segment">
                <div class="ui ${this.fontStyle} header">
                    ${this.staticTitle}
                </div>
            </div>
        `
        this.component.context.html(frag);
    }
}

mex.renderers.SidebarSearchController = class extends edges.Renderer {
    constructor(params) {
        super(params);

        // enable the search button
        this.searchButton = edges.util.getParam(params, "searchButton", false);

        // text to include on the search button.  If not provided, will just be the magnifying glass
        this.searchButtonText = edges.util.getParam(
            params,
            "searchButtonText",
            false
        );

        // should the clear button be rendered
        this.clearButton = edges.util.getParam(params, "clearButton", true);

        // enable sorting options
        this.enableSorting = edges.util.getParam(params, "clearButton", false);

        // set the placeholder text for the search box
        this.searchPlaceholder = edges.util.getParam(
            params,
            "searchPlaceholder",
            i18n.t("Search")
        );

        this.label = edges.util.getParam(
            params,
            "label",
            "Search"
        )

        this.labelInvisible = edges.util.getParam(
            params,
            "labelInvisible",
            false
        )

        this.inlineLabel = edges.util.getParam(
            params,
            "inlineLabel",
            false
        )

        // amount of time between finishing typing and when a query is executed from the search box
        this.freetextSubmitDelay = edges.util.getParam(
            params,
            "freetextSubmitDelay",
            500
        );

        this.searchTitle = edges.util.getParam(params, "searchTitle", "Search");
        this.compactDesign = edges.util.getParam(params, "compactDesign", false);

        ////////////////////////////////////////
        // state variables

        this.namespace = "mex-search-controller";
    }

    draw() {
        let comp = this.component;

        // if sort options are provided render the orderer and the order by
        let sortFrag = "";
        if (comp.sortOptions && comp.sortOptions.length > 0) {
            // classes that we'll use
            let directionClass = edges.util.allClasses(
                this.namespace,
                "direction",
                this
            );
            let sortFieldClass = edges.util.allClasses(
                this.namespace,
                "sortby",
                this
            );

            let sortOptions = "";
            for (let i = 0; i < comp.sortOptions.length; i++) {
                let field = comp.sortOptions[i].field;
                let display = comp.sortOptions[i].display;
                sortOptions += `<option value="${field}">${edges.util.escapeHtml(
                    display
                )}</option>`;
            }

            let sortId = edges.util.htmlID(this.namespace, "sort", this);

            sortFrag = `<div class="ui form">
                            <div class="field">
                                <label for="${sortId} class="sr-only"> Sort by </label>
                                <select class="ui fluid dropdown ${sortFieldClass}">
                                    <option value="_score">${i18n.t("Relevance")}</option>
                                    ${sortOptions}
                                </select>
                            </div>
                        </div>`;
        }

        // select box for fields to search on
        let field_select = "";
        if (comp.fieldOptions && comp.fieldOptions.length > 0) {
            // classes that we'll use
            let searchFieldClass = edges.util.allClasses(
                this.namespace,
                "field",
                this
            );

            let selectId = edges.util.htmlID(this.namespace, "selectId", this);

            let fieldOptions = "";
            for (let i = 0; i < comp.fieldOptions.length; i++) {
                let obj = comp.fieldOptions[i];
                fieldOptions += `<option value="${
                    obj["field"]
                }">${edges.util.escapeHtml(obj["display"])}</option>`;
            }

            field_select += `<label for="${selectId}" class="sr-only">Search by</label>
                                <select class="ui dropdown ${searchFieldClass}" id="${selectId}">
                                    <option value="">${i18n.t("all fields")}</option>
                                    ${fieldOptions}
                                </select>`;
        }

        // more classes that we'll use
        let resetClass = edges.util.allClasses(this.namespace, "reset", this);
        let textClass = edges.util.allClasses(this.namespace, "text", this);
        let searchClass = edges.util.allClasses(this.namespace, "search", this);

        // text search box id
        let textId = edges.util.htmlID(this.namespace, "text", this);

        let clearFrag = "";
        if (this.clearButton) {
            clearFrag = `<div class="field">
                            <button type="button" class="ui button tertiary ${resetClass}" title="${i18n.t(
                                "Clear all search and sort parameters and start again"
                            )}">
                                ${i18n.t("Clear")}
                            </button>
                        </div>`;
        }

        let searchBtn = "";
        if (this.searchButton) {
            let text = '<span class="icon search"></span>';
            if (this.searchButtonText !== false) {
                text = this.searchButtonText;
            }
            searchBtn = `<button type="submit" class="ui button secondary ${searchClass} search-button">${text}</button>`;
        }

        let inline = "";
        if (this.inlineLabel) {
            inline = "inline";
        }
        let srOnly = "";
        if (this.labelInvisible) {
            srOnly = `sr-only`;
        }
        let searchBoxLabel = `<label for="${textId}" class="ui label label--search ${srOnly}"> ${this.label}</label>`
        let searchBoxInput = `<input type="text"
                            id="${textId}"
                            class="ui input input--search ${textClass}"
                            name="q"
                            placeholder="${this.searchPlaceholder}"
                        />`;

        // assemble the final fragment and render it into the component's context
        let containerClass = edges.util.styleClasses(
            this.namespace,
            "container",
            this
        );

        let compactClass = "";
        if (this.compactDesign){
            compactClass = "form--compact";
        }

        if (this.sideBar) {

        }
        let frag = `
            <form class="ui form ${compactClass}">
                ${searchBoxLabel}
                ${searchBoxInput}
                ${field_select}
                ${searchBtn}
            </form>
        `

        comp.context.html(frag);

        // now populate all the dynamic bits
        if (comp.sortOptions && comp.sortOptions.length > 0) {
            this.setUISortDir();
            this.setUISortField();
        }
        if (comp.fieldOptions && comp.fieldOptions.length > 0) {
            this.setUISearchField();
        }
        this.setUISearchText();

        // attach all the bindings
        if (comp.sortOptions && comp.sortOptions.length > 0) {
            let directionSelector = edges.util.jsClassSelector(
                this.namespace,
                "direction",
                this
            );
            let sortSelector = edges.util.jsClassSelector(
                this.namespace,
                "sortby",
                this
            );
            edges.on(directionSelector, "click", this, "changeSortDir");
            edges.on(sortSelector, "change", this, "changeSortBy");
        }
        if (comp.fieldOptions && comp.fieldOptions.length > 0) {
            let fieldSelector = edges.util.jsClassSelector(
                this.namespace,
                "field",
                this
            );
            edges.on(fieldSelector, "change", this, "changeSearchField");
        }
        let textSelector = edges.util.jsClassSelector(this.namespace, "text", this);
        if (this.freetextSubmitDelay > -1) {
            edges.on(
                textSelector,
                "keyup",
                this,
                "setSearchText",
                this.freetextSubmitDelay
            );
        } else {
            function onlyEnter(event) {
                let code = event.keyCode ? event.keyCode : event.which;
                return code === 13;
            }

            edges.on(textSelector, "keyup", this, "setSearchText", false, onlyEnter);
        }

        let resetSelector = edges.util.jsClassSelector(
            this.namespace,
            "reset",
            this
        );
        edges.on(resetSelector, "click", this, "clearSearch");

        let searchSelector = edges.util.jsClassSelector(
            this.namespace,
            "search",
            this
        );
        edges.on(searchSelector, "click", this, "doSearch");

        if (this.shareLink) {
            let shareSelector = edges.util.jsClassSelector(
                this.namespace,
                "toggle-share",
                this
            );
            edges.on(shareSelector, "click", this, "toggleShare");

            let closeShareSelector = edges.util.jsClassSelector(
                this.namespace,
                "close-share",
                this
            );
            edges.on(closeShareSelector, "click", this, "toggleShare");

            if (this.component.urlShortener) {
                let shortenSelector = edges.util.jsClassSelector(
                    this.namespace,
                    "shorten",
                    this
                );
                edges.on(shortenSelector, "click", this, "toggleShorten");
            }
        }
    }

    ///////////////////////////////////////a///////////////
    // functions for setting UI values

    setUISortDir() {
        // get the selector we need
        let directionSelector = edges.util.jsClassSelector(
            this.namespace,
            "direction",
            this
        );
        let el = this.component.jq(directionSelector);
        if (this.component.sortDir === "asc") {
            el.html(`<i class="icon sort up"></i> ${i18n.t("sort by")}`);
            el.attr(
                "title",
                i18n.t("Current order ascending. Click to change to descending")
            );
        } else {
            el.html(`<i class="icon sort down"></i> ${i18n.t("sort by")}`);
            el.attr(
                "title",
                i18n.t("Current order descending. Click to change to ascending")
            );
        }
    }

    setUISortField() {
        if (!this.component.sortBy) {
            return;
        }
        // get the selector we need
        let sortSelector = edges.util.jsClassSelector(
            this.namespace,
            "sortby",
            this
        );
        let el = this.component.jq(sortSelector);
        el.val(this.component.sortBy);
    }

    setUISearchField() {
        if (!this.component.searchField || this.component.searchField === "*") {
            return;
        }
        // get the selector we need
        let fieldSelector = edges.util.jsClassSelector(
            this.namespace,
            "field",
            this
        );
        let el = this.component.jq(fieldSelector);
        el.val(this.component.searchField);
    }

    setUISearchText() {
        if (!this.component.searchString) {
            return;
        }
        // get the selector we need
        let textSelector = edges.util.jsClassSelector(this.namespace, "text", this);
        let el = this.component.jq(textSelector);
        el.val(this.component.searchString);
    }

    ////////////////////////////////////////
    // event handlers

    changeSortDir = function (element) {
        this.component.changeSortDir();
    };

    changeSortBy = function (element) {
        let val = this.component.jq(element).val();
        this.component.setSortBy(val);
    };

    changeSearchField = function (element) {
        let val = this.component.jq(element).val();
        this.component.setSearchField(val);
    };

    setSearchText = function (element) {
        let val = this.component.jq(element).val();
        this.component.setSearchText(val);
    };

    clearSearch = function (element) {
        this.component.clearSearch();
    };

    doSearch = function (element) {
        let textId = edges.util.idSelector(this.namespace, "text", this);
        let text = this.component.jq(textId).val();
        this.component.setSearchText(text);
    };
};

mex.renderers.Sorter = class extends edges.Renderer {
    constructor(params) {
        super(params);

        ////////////////////////////////////////
        // state variables

        this.namespace = "mex-sorter";
    }

    draw() {
        let comp = this.component;

        // if sort options are provided render the orderer and the order by
        let sortFrag = "";
        if (comp.sortOptions && comp.sortOptions.length > 0) {
            // classes that we'll use
            let sortFieldClass = edges.util.allClasses(
                this.namespace,
                "sortby",
                this
            );

            let sortOptions = "";
            for (let i = 0; i < comp.sortOptions.length; i++) {
                let field = comp.sortOptions[i].field;
                let display = comp.sortOptions[i].display;
                sortOptions += `<option value="${field}">${edges.util.escapeHtml(
                    display
                )}</option>`;
            }

            sortFrag = `<div class="form">
                <div class="field">
                    ${i18n.t("Sort by")}
                    <select class="ui dropdown ${sortFieldClass}">
                        <option value="_score">${i18n.t("Relevance")}</option>
                        ${sortOptions}
                    </select>
                </div>
            </div>`;
        }

        // assemble the final fragment and render it into the component's context
        let containerClass = edges.util.styleClasses(
            this.namespace,
            "container",
            this
        );

        // Upgrading the search UI as per sematic ui
        let frag = `
            <div class="ui grid ${containerClass}">
                <div class="ui right aligned column" style="padding-right: 0;">
                ${sortFrag}
                </div>
            </div>`;

        comp.context.html(frag);

        // now populate all the dynamic bits
        if (comp.sortOptions && comp.sortOptions.length > 0) {
            this.setUISortDir();
            this.setUISortField();
        }

        // attach all the bindings
        if (comp.sortOptions && comp.sortOptions.length > 0) {
            let directionSelector = edges.util.jsClassSelector(
                this.namespace,
                "direction",
                this
            );
            let sortSelector = edges.util.jsClassSelector(
                this.namespace,
                "sortby",
                this
            );
            edges.on(directionSelector, "click", this, "changeSortDir");
            edges.on(sortSelector, "change", this, "changeSortBy");
        }
    }

    ///////////////////////////////////////a///////////////
    // functions for setting UI values

    setUISortDir() {
        // get the selector we need
        let directionSelector = edges.util.jsClassSelector(
            this.namespace,
            "direction",
            this
        );
        let el = this.component.jq(directionSelector);
        if (this.component.sortDir === "asc") {
            el.html(`<i class="icon sort up"></i> ${i18n.t("sort by")}`);
            el.attr(
                "title",
                i18n.t("Current order ascending. Click to change to descending")
            );
        } else {
            el.html(`<i class="icon sort down"></i> ${i18n.t("sort by")}`);
            el.attr(
                "title",
                i18n.t("Current order descending. Click to change to ascending")
            );
        }
    }

    setUISortField() {
        if (!this.component.sortBy) {
            return;
        }
        // get the selector we need
        let sortSelector = edges.util.jsClassSelector(
            this.namespace,
            "sortby",
            this
        );
        let el = this.component.jq(sortSelector);
        el.val(this.component.sortBy);
    }

    ////////////////////////////////////////
    // event handlers

    changeSortDir = function (element) {
        this.component.changeSortDir();
    };

    changeSortBy = function (element) {
        let val = this.component.jq(element).val();
        this.component.setSortBy(val);
    };
};

mex.renderers.Sorter = class extends edges.Renderer {
    constructor(params) {
        super(params);

        ////////////////////////////////////////
        // state variables

        this.namespace = "mex-sorter";
    }

    draw() {
        let comp = this.component;

        // if sort options are provided render the orderer and the order by
        let sortFrag = "";
        if (comp.sortOptions && comp.sortOptions.length > 0) {
            // classes that we'll use
            let sortFieldClass = edges.util.allClasses(
                this.namespace,
                "sortby",
                this
            );

            let sortOptions = "";
            for (let i = 0; i < comp.sortOptions.length; i++) {
                let field = comp.sortOptions[i].field;
                let display = comp.sortOptions[i].display;
                sortOptions += `<option value="${field}">${edges.util.escapeHtml(
                    display
                )}</option>`;
            }

            sortFrag = `<div class="form">
                <div class="field">
                    ${i18n.t("Sort by")}
                    <select class="ui dropdown ${sortFieldClass}">
                        <option value="_score">${i18n.t("Relevance")}</option>
                        ${sortOptions}
                    </select>
                </div>
            </div>`;
        }

        // assemble the final fragment and render it into the component's context
        let containerClass = edges.util.styleClasses(
            this.namespace,
            "container",
            this
        );

        // Upgrading the search UI as per sematic ui
        let frag = `
            <div class="ui grid ${containerClass}" style="margin-left:0;">
                <div class="ui right aligned column" style="padding-right: 0;">
                ${sortFrag}
                </div>
            </div>`;

        comp.context.html(frag);

        // now populate all the dynamic bits
        if (comp.sortOptions && comp.sortOptions.length > 0) {
            this.setUISortDir();
            this.setUISortField();
        }

        // attach all the bindings
        if (comp.sortOptions && comp.sortOptions.length > 0) {
            let directionSelector = edges.util.jsClassSelector(
                this.namespace,
                "direction",
                this
            );
            let sortSelector = edges.util.jsClassSelector(
                this.namespace,
                "sortby",
                this
            );
            edges.on(directionSelector, "click", this, "changeSortDir");
            edges.on(sortSelector, "change", this, "changeSortBy");
        }
    }

    ///////////////////////////////////////a///////////////
    // functions for setting UI values

    setUISortDir() {
        // get the selector we need
        let directionSelector = edges.util.jsClassSelector(
            this.namespace,
            "direction",
            this
        );
        let el = this.component.jq(directionSelector);
        if (this.component.sortDir === "asc") {
            el.html(`<i class="icon sort up"></i> ${i18n.t("sort by")}`);
            el.attr(
                "title",
                i18n.t("Current order ascending. Click to change to descending")
            );
        } else {
            el.html(`<i class="icon sort down"></i> ${i18n.t("sort by")}`);
            el.attr(
                "title",
                i18n.t("Current order descending. Click to change to ascending")
            );
        }
    }

    setUISortField() {
        if (!this.component.sortBy) {
            return;
        }
        // get the selector we need
        let sortSelector = edges.util.jsClassSelector(
            this.namespace,
            "sortby",
            this
        );
        let el = this.component.jq(sortSelector);
        el.val(this.component.sortBy);
    }

    ////////////////////////////////////////
    // event handlers

    changeSortDir = function (element) {
        this.component.changeSortDir();
    };

    changeSortBy = function (element) {
        let val = this.component.jq(element).val();
        this.component.setSortBy(val);
    };
};

mex.renderers.RefiningANDTermSelector = class extends edges.Renderer {
    constructor(params) {
        super(params);

        ///////////////////////////////////////
        // parameters that can be passed in

        this.title = edges.util.getParam(params, "title", i18n.t("Select"));

        // whether to hide or just disable the facet if not active
        this.hideInactive = edges.util.getParam(params, "hideInactive", false);

        // should the facet sort/size controls be shown?
        this.controls = edges.util.getParam(params, "controls", true);

        // whether the facet should be open or closed
        // can be initialised and is then used to track internal state
        this.open = edges.util.getParam(params, "open", false);

        this.togglable = edges.util.getParam(params, "togglable", true);

        // whether to display selected filters
        this.showSelected = edges.util.getParam(params, "showSelected", true);

        // sort cycle to use
        this.sortCycle = edges.util.getParam(params, "sortCycle", [
            "count desc",
            "count asc",
            "term desc",
            "term asc",
        ]);

        // formatter for count display
        this.countFormat = edges.util.getParam(params, "countFormat", false);

        // Hides facet when there is no data
        this.hideIfEmpty = edges.util.getParam(params, "hideIfEmpty", false);

        // Displays checkboxes for facet selection
        this.useCheckboxes = edges.util.getParam(params, "useCheckboxes", false);

        // a short tooltip and a fuller explanation
        this.tooltipText = edges.util.getParam(params, "tooltipText", false);
        this.tooltip = edges.util.getParam(params, "tooltip", false);
        this.tooltipState = "closed";

        // namespace to use in the page
        this.namespace = "mex-refining-and-term-selector";
    }

    draw() {
        let ts = this.component;

        if (!ts.active && this.hideInactive) {
            ts.context.html("");
            return;
        }

        let valClass = edges.util.allClasses(
            this.namespace,
            "value",
            this.component.id
        );
        let filterRemoveClass = edges.util.allClasses(
            this.namespace,
            "filter-remove",
            this.component.id
        );

        let resultsListClass = edges.util.styleClasses(
            this.namespace,
            "results-list",
            this.component.id
        );
        let resultClass = edges.util.styleClasses(
            this.namespace,
            "result",
            this.component.id
        );
        let controlClass = edges.util.styleClasses(
            this.namespace,
            "controls",
            this.component.id
        );
        let facetClass = edges.util.styleClasses(
            this.namespace,
            "facet",
            this.component.id
        );
        let headerClass = edges.util.styleClasses(
            this.namespace,
            "header",
            this.component.id
        );
        let selectedClass = edges.util.styleClasses(
            this.namespace,
            "selected",
            this.component.id
        );

        let controlId = edges.util.htmlID(
            this.namespace,
            "controls",
            this.component.id
        );
        let sizeId = edges.util.htmlID(this.namespace, "size", this.component.id);
        let orderId = edges.util.htmlID(this.namespace, "order", this.component.id);
        let toggleId = edges.util.htmlID(
            this.namespace,
            "toggle",
            this.component.id
        );
        let resultsId = edges.util.htmlID(
            this.namespace,
            "results",
            this.component.id
        );

        let showFacet = ts.values && ts.values.length > 0;
        if (!showFacet && this.hideIfEmpty) {
            ts.context.html("");
            return;
        }

        let results = showFacet ? "" : i18n.t("No data available");
        let filterTerms = ts.filters.map((f) => f.term.toString());

        if (showFacet) {
            results = "";

            for (let val of ts.values) {
                let count = this.countFormat ? this.countFormat(val.count) : val.count;
                let escapedTerm = edges.util.escapeHtml(val.term);
                let escapedDisplay = edges.util.escapeHtml(val.display);

                let checked = filterTerms.includes(val.term) ? "checked" : "";
                // This will allow us to remove filter if already selected this can seamlessly work for checkboxes and button
                let activeClass = filterTerms.includes(val.term)
                    ? filterRemoveClass
                    : valClass;

                if (this.useCheckboxes) {
                    results += `
                            <label class="checkbox">
                                <input type="checkbox" class="${activeClass}" data-key="${escapedTerm}" ${checked}/>
                                ${edges.util.escapeHtml(escapedDisplay)} (${count})
                            </label>`;
                } else {
                    results += `
                        <div class="${resultClass}">
                            <a href="#" class="${valClass}" data-key="${escapedTerm}">${escapedDisplay}</a> (${count})
                            ${
                        activeClass === valClass && !this.showSelected
                            ? ""
                            : `<i class="icon delete"></i>`
                    }
                        </div>`;
                }
            }
        }

        // Tooltip
        let tooltipFrag = "";
        if (this.tooltipText) {
            let tooltipClass = edges.util.styleClasses(
                this.namespace,
                "tooltip",
                this.component.id
            );
            let tooltipId = edges.util.htmlID(
                this.namespace,
                "tooltip",
                this.component.id
            );
            let tt = this._shortTooltip();
            tooltipFrag = `
                <div id="${tooltipId}" class="${tooltipClass}" style="display:none">
                    <div class="ui grid">
                        <div class="sixteen wide column">${tt}</div>
                    </div>
                </div>`;
        }

        // Controls
        let controlFrag = "";
        if (this.controls) {
            controlFrag = `
                <div class="${controlClass}" style="display:none" id="${controlId}">
                    <div class="ui grid">
                        <div class="sixteen wide column">
                            <div class="ui buttons">
                                <button type="button" class="ui button mini" id="${sizeId}" title="List Size" href="#">0</button>
                                <button type="button" class="ui button mini" id="${orderId}" title="List Order" href="#"></button>
                            </div>
                        </div>
                    </div>
                </div>`;
        }

        // Selected filters
        let filterFrag = "";
        if (ts.filters.length > 0 && this.showSelected) {
            for (let filt of ts.filters) {
                filterFrag += `
                    <div class="${resultClass}">
                        <strong>${edges.util.escapeHtml(filt.display)}&nbsp;
                            <a href="#" class="${filterRemoveClass}" data-key="${edges.util.escapeHtml(
                    filt.term
                )}">
                                <i class="delete icon"></i>
                            </a>
                        </strong>
                    </div>`;
            }
        }

        // Header toggle
        let tog = `<h4 class="facet-title"> ${this.title} </h4>`;
        if (this.togglable) {
            tog = `<a href="#" id="${toggleId}"><i class="plus icon"></i>&nbsp;
                <h4 class="facet-title"> ${this.title} </h4>
            </a>`;
        }

        // Final HTML fragment
        let frag = `
            <div class="ui ${facetClass}" style="margin-bottom: 1rem">
                <div class="${headerClass}">
                    <div class="ui grid">
                        <div class="sixteen wide column .search-facets-container">${tog}</div>
                    </div>
                </div>
                ${tooltipFrag}
                ${controlFrag}
                <br/>
                <div class="ui grid" style="display:none" id="${resultsId}">
                    <div class="sixteen wide column">
                        <div class="${selectedClass}">${filterFrag}</div>
                        <div class="${resultsListClass}">${results}</div>
                    </div>
                </div>
            </div>`;

        // Render to page
        ts.context.html(frag);

        // UI Setup
        this.setUISize();
        this.setUISort();
        this.setUIOpen();

        // Event Bindings
        let valueSelector = edges.util.jsClassSelector(
            this.namespace,
            "value",
            this.component.id
        );
        let filterRemoveSelector = edges.util.jsClassSelector(
            this.namespace,
            "filter-remove",
            this
        );
        let toggleSelector = edges.util.idSelector(this.namespace, "toggle", this);
        let sizeSelector = edges.util.idSelector(
            this.namespace,
            "size",
            this.component.id
        );
        let orderSelector = edges.util.idSelector(
            this.namespace,
            "order",
            this.component.id
        );
        let tooltipSelector = edges.util.idSelector(
            this.namespace,
            "tooltip-toggle",
            this.component.id
        );

        let valueSelectorEvent = this.useCheckboxes ? "change" : "click";

        edges.on(valueSelector, valueSelectorEvent, this, "termSelected");
        edges.on(toggleSelector, "click", this, "toggleOpen");
        edges.on(filterRemoveSelector, "click", this, "removeFilter");
        edges.on(sizeSelector, "click", this, "changeSize");
        edges.on(orderSelector, "click", this, "changeSort");
        edges.on(tooltipSelector, "click", this, "toggleTooltip");

        // Checkbox controls
        if (this.useCheckboxes) {
            const selector = `#${resultsId} .${valClass.replace(
                /\s+/g,
                "."
            )} input[type=checkbox]`;
            $(`#select-all-${ts.id}`).on("click", () => {
                $(selector).prop("checked", true);
            });
            $(`#deselect-all-${ts.id}`).on("click", () => {
                $(selector).prop("checked", false);
            });
        }
    }

    /////////////////////////////////////////////////////
    // UI behaviour functions

    setUIOpen() {
        // the selectors that we're going to use
        let resultsSelector = edges.util.idSelector(
            this.namespace,
            "results",
            this.component.id
        );
        let controlsSelector = edges.util.idSelector(
            this.namespace,
            "controls",
            this.component.id
        );
        let tooltipSelector = edges.util.idSelector(
            this.namespace,
            "tooltip",
            this.component.id
        );
        let toggleSelector = edges.util.idSelector(
            this.namespace,
            "toggle",
            this.component.id
        );

        let results = this.component.jq(resultsSelector);
        let controls = this.component.jq(controlsSelector);
        let tooltip = this.component.jq(tooltipSelector);
        let toggle = this.component.jq(toggleSelector);

        if (this.open) {
            toggle.find("i").removeClass("plus icon").addClass("minus icon");
            controls.show();
            results.show();
            tooltip.show();
        } else {
            toggle.find("i").removeClass("minus icon").addClass("plus icon");
            controls.hide();
            results.hide();
            tooltip.hide();
        }
    }

    setUISize() {
        let sizeSelector = edges.util.idSelector(
            this.namespace,
            "size",
            this.component.id
        );
        this.component.jq(sizeSelector).html(this.component.size);
    }

    setUISort() {
        let orderSelector = edges.util.idSelector(
            this.namespace,
            "order",
            this.component.id
        );
        let el = this.component.jq(orderSelector);

        if (this.component.orderBy === "count") {
            if (this.component.orderDir === "asc") {
                el.html('count <i class="sort down icon"></i>');
            } else if (this.component.orderDir === "desc") {
                el.html('count <i class="sort up icon"></i>');
            }
        } else if (this.component.orderBy === "term") {
            if (this.component.orderDir === "asc") {
                el.html('a-z <i class="sort down icon"></i>');
            } else if (this.component.orderDir === "desc") {
                el.html('a-z <i class="sort up icon"></i>');
            }
        }
    }

    /////////////////////////////////////////////////////
    // event handlers

    termSelected(element) {
        let term = this.component.jq(element).attr("data-key");
        this.component.selectTerm(term);
    }

    removeFilter(element) {
        let term = this.component.jq(element).attr("data-key");
        this.component.removeFilter(term);
    }

    toggleOpen(element) {
        this.open = !this.open;
        this.setUIOpen();
    }

    changeSize(element) {
        let newSize = prompt(
            `${i18n.t("Currently displaying")} ${
                this.component.size
            } ${i18n.t("results per page. How many would you like instead?")}`
        );
        if (newSize) {
            this.component.changeSize(parseInt(newSize));
        }
    }

    changeSort(element) {
        let current = this.component.orderBy + " " + this.component.orderDir;
        let idx = $.inArray(current, this.sortCycle);
        let next = this.sortCycle[(idx + 1) % 4];
        let bits = next.split(" ");
        this.component.changeSort(bits[0], bits[1]);
    }

    toggleTooltip(element) {
        let tooltipSpanSelector = edges.util.idSelector(
            this.namespace,
            "tooltip-span",
            this.component.id
        );
        let container = this.component.jq(tooltipSpanSelector).parent();
        let tt = "";
        if (this.tooltipState === "closed") {
            tt = this._longTooltip();
            this.tooltipState = "open";
        } else {
            tt = this._shortTooltip();
            this.tooltipState = "closed";
        }
        container.html(tt);
        let tooltipSelector = edges.util.idSelector(
            this.namespace,
            "tooltip-toggle",
            this.component.id
        );
        // refresh the event binding
        edges.on(tooltipSelector, "click", this, "toggleTooltip");
    }

    //////////////////////////////////////////////////////////
    // some useful reusable components

    _shortTooltip() {
        let tt = this.tooltipText;
        let tooltipLinkId = edges.util.htmlID(
            this.namespace,
            "tooltip-toggle",
            this.component.id
        );
        let tooltipSpan = edges.util.htmlID(
            this.namespace,
            "tooltip-span",
            this.component.id
        );
        if (this.tooltip) {
            let tooltipLinkClass = edges.util.styleClasses(
                this.namespace,
                "tooltip-link",
                this.component.id
            );
            tt = `<span id="${tooltipSpan}"><a id="${tooltipLinkId}" class="${tooltipLinkClass}" href="#">${tt}</a></span>`;
        }
        return tt;
    }

    _longTooltip = function () {
        let tt = this.tooltip;
        let tooltipLinkId = edges.util.htmlID(
            this.namespace,
            "tooltip-toggle",
            this.component.id
        );
        let tooltipLinkClass = edges.util.styleClasses(
            this.namespace,
            "tooltip-link",
            this.component.id
        );
        let tooltipSpan = edges.util.htmlID(
            this.namespace,
            "tooltip-span",
            this.component.id
        );
        tt = `<span id="${tooltipSpan}">${
            this.tooltip
        } <a id="${tooltipLinkId}" class="${tooltipLinkClass}" href="#">${i18n.t(
            "less"
        )}</a></span>`;
        return tt;
    };
};

mex.renderers.DateHistogramSelector = class extends edges.Renderer {
    constructor(params) {
        super(params);

        // whether to hide or just disable the facet if not active
        this.hideInactive = edges.util.getParam(params, "hideInactive", false);

        // whether the facet should be open or closed
        // can be initialised and is then used to track internal state
        this.open = edges.util.getParam(params, "open", false);

        this.togglable = edges.util.getParam(params, "togglable", true);

        // whether to display selected filters
        this.showSelected = edges.util.getParam(params, "showSelected", true);

        // formatter for count display
        this.countFormat = edges.util.getParam(params, "countFormat", false);

        this.title = edges.util.getParam(
            params,
            "title",
            i18n.t("Select Date Range")
        );

        // a short tooltip and a fuller explanation
        this.tooltipText = edges.util.getParam(params, "tooltipText", false);
        this.tooltip = edges.util.getParam(params, "tooltip", false);

        this.tooltipState = "closed";

        // whether to suppress display of date range with no values
        this.hideEmptyDateBin = edges.util.getParam(
            params,
            "hideEmptyDateBin",
            true
        )

        // Hides facet when there is no data
        this.hideIfEmpty = edges.util.getParam(params, "hideIfEmpty", false);

        // Displays checkboxes for facet selection
        this.useCheckboxes = edges.util.getParam(params, "useCheckboxes", false);

        // how many of the values to display initially, with a "show all" option for the rest
        this.shortDisplay = edges.util.getParam(params, "shortDisplay", false);

        // namespace to use in the page
        this.namespace = "mex-datehistogram-selector";
    }

    draw() {
        let ts = this.component;
        let namespace = this.namespace;

        if (!ts.active && this.hideInactive) {
            ts.context.html("");
            return;
        }

        let resultsListClass = edges.util.allClasses(
            namespace,
            "results-list",
            this
        );
        let resultClass = edges.util.allClasses(namespace, "result", this);
        let valClass = edges.util.allClasses(namespace, "value", this);
        let filterRemoveClass = edges.util.allClasses(
            namespace,
            "filter-remove",
            this
        );
        let facetClass = edges.util.allClasses(namespace, "facet", this);
        let headerClass = edges.util.allClasses(namespace, "header", this);
        let selectedClass = edges.util.allClasses(namespace, "selected", this);

        let toggleId = edges.util.htmlID(namespace, "toggle", this);
        let resultsId = edges.util.htmlID(namespace, "results", this);

        let results = i18n.t("Loading...");
        if (ts.values !== false) {
            results = i18n.t("No data available");
        }

        if (ts.values && ts.values.length > 0) {
            results = "";

            let filterTerms = ts.filters.map((f) => f.display);
            let longClass = edges.util.allClasses(namespace, "long", this);
            let short = true;

            let displayedCount = -1;    // start counting from -1 to account 0-based index
            for (let i = 0; i < ts.values.length; i++) {
                let val = ts.values[i];

                // skip empty date bins if requested
                if (this.hideEmptyDateBin && val.count === 0) {
                    continue;
                }
                displayedCount += 1;

                let checked = filterTerms.includes(val.display) ? "checked" : "";
                // This will allow us to remove filter if already selected this can seamlessly work for checkboxes and button
                let activeClass = filterTerms.includes(val.display)
                    ? filterRemoveClass
                    : valClass;
                let myLongClass = "";
                let styles = "";

                if (this.shortDisplay && this.shortDisplay <= displayedCount) {
                    myLongClass = longClass;
                    styles = 'style="display:none"';
                    short = false;
                }

                let count = this.countFormat ? this.countFormat(val.count) : val.count;
                let ltData = val.lt
                    ? ` data-lt="${edges.util.escapeHtml(val.lt)}"`
                    : "";

                if (this.useCheckboxes) {
                    results += `
                    <div class="${resultClass} ${myLongClass} checkbox" ${styles}>
                        <label>
                            <input type="checkbox" class="${activeClass}" data-gte="${edges.util.escapeHtml(
                        val.gte
                    )}" ${ltData} ${checked}>
                            ${edges.util.escapeHtml(val.display)} (${count})
                        </label>
                    </div>`;
                } else {
                    results += `
                        <div class="${resultClass} ${myLongClass}" ${styles}>
                            <a href="#" class="${activeClass}" data-gte="${edges.util.escapeHtml(
                        val.gte
                    )}" ${ltData}>
                                ${edges.util.escapeHtml(val.display)}
                            </a> (${count}) ${
                        activeClass === valClass && !this.showSelected
                            ? ""
                            : `<i class="icon delete"></i>`
                    }
                        </div>`;
                }
            }

            if (!short) {
                let showClass = edges.util.allClasses(namespace, "show-link", this);
                let showId = edges.util.htmlID(namespace, "show-link", this);
                let slToggleId = edges.util.htmlID(namespace, "sl-toggle", this);
                results += `<div class="${showClass}" id="${showId}">
                    <a href="#" id="${slToggleId}">
                        <span class="all">show all</span>
                        <span class="less" style="display:none">${i18n.t(
                    "show less"
                )}</span>
                    </a>
                </div>`;
            }
        }

        let tooltipFrag = "";
        if (this.tooltipText) {
            let tt = this._shortTooltip();
            let tooltipClass = edges.util.allClasses(namespace, "tooltip", this);
            let tooltipId = edges.util.htmlID(namespace, "tooltip", this);
            tooltipFrag = `<div id="${tooltipId}" class="${tooltipClass}" style="display:none">
                <div class="row"><div class="col-md-12">${tt}</div></div>
            </div>`;
        }

        let filterFrag = "";
        if (ts.filters.length > 0 && this.showSelected) {
            for (let i = 0; i < ts.filters.length; i++) {
                let filt = ts.filters[i];
                let ltData = filt.lt
                    ? ` data-lt="${edges.util.escapeHtml(filt.lt)}"`
                    : "";
                filterFrag += `<div class="${resultClass}">
                    <strong>${edges.util.escapeHtml(filt.display)}&nbsp;
                        <a href="#" class="${filterRemoveClass}" data-gte="${edges.util.escapeHtml(
                    filt.gte
                )}" ${ltData}>
                            <i class="icon delete"></i>
                        </a>
                    </strong>
                </div>`;
            }
        }

        let tog = `<h4 class="facet-title"> ${this.title} </h4>`;
        if (this.togglable) {
            tog = `<a href="#" id="${toggleId}"><i class="icon plus"></i>&nbsp;${tog}</a>`;
        }

        let frag = `
            <div class="${facetClass}" style="margin-bottom:15px">
                <div class="${headerClass}"><div class="row">
                    <div class="col-md-12">${tog}</div>
                </div></div>
                ${tooltipFrag}
                <br/>
                <div class="row" style="display:none" id="${resultsId}">
                    <div class="col-md-12">
                        <div class="${selectedClass}">${filterFrag}</div>
                        <div class="${resultsListClass}">${results}</div>
                    </div>
                </div>
            </div>`;

        ts.context.html(frag);

        this.setUIOpen();

        let valueSelector = edges.util.jsClassSelector(namespace, "value", this);
        let filterRemoveSelector = edges.util.jsClassSelector(
            namespace,
            "filter-remove",
            this
        );
        let toggleSelector = edges.util.idSelector(namespace, "toggle", this);
        let tooltipSelector = edges.util.idSelector(
            namespace,
            "tooltip-toggle",
            this
        );
        let shortLongToggleSelector = edges.util.idSelector(
            namespace,
            "sl-toggle",
            this
        );

        let valueSelectorEvent = this.useCheckboxes ? "change" : "click";

        edges.on(valueSelector, valueSelectorEvent, this, "termSelected");
        edges.on(filterRemoveSelector, "click", this, "removeFilter");
        edges.on(toggleSelector, "click", this, "toggleOpen");
        edges.on(tooltipSelector, "click", this, "toggleTooltip");
        edges.on(shortLongToggleSelector, "click", this, "toggleShortLong");
    }

    setUIOpen() {
        // the selectors that we're going to use
        let resultsSelector = edges.util.idSelector(
            this.namespace,
            "results",
            this.component.id
        );
        let tooltipSelector = edges.util.idSelector(
            this.namespace,
            "tooltip",
            this
        );
        let toggleSelector = edges.util.idSelector(this.namespace, "toggle", this);

        let results = this.component.jq(resultsSelector);
        let tooltip = this.component.jq(tooltipSelector);
        let toggle = this.component.jq(toggleSelector);

        if (this.open) {
            toggle.find("i").removeClass("icon plus").addClass("icon minus");
            results.show();
            tooltip.show();
        } else {
            toggle.find("i").removeClass("icon minus").addClass("icon plus");
            results.hide();
            tooltip.hide();
        }
    }

    /////////////////////////////////////////////////////
    // event handlers

    termSelected(element) {
        let gte = this.component.jq(element).attr("data-gte");
        let lt = this.component.jq(element).attr("data-lt");
        this.component.selectRange({gte: gte, lt: lt});
    }

    removeFilter(element) {
        let gte = this.component.jq(element).attr("data-gte");
        let lt = this.component.jq(element).attr("data-lt");
        this.component.removeFilter({gte: gte, lt: lt});
    }

    toggleOpen(element) {
        this.open = !this.open;
        this.setUIOpen();
    }

    toggleTooltip(element) {
        let tooltipSpanSelector = edges.util.idSelector(
            this.namespace,
            "tooltip-span",
            this
        );
        let container = this.component.jq(tooltipSpanSelector).parent();
        let tt = "";
        if (this.tooltipState === "closed") {
            tt = this._longTooltip();
            this.tooltipState = "open";
        } else {
            tt = this._shortTooltip();
            this.tooltipState = "closed";
        }
        container.html(tt);
        let tooltipSelector = edges.util.idSelector(
            this.namespace,
            "tooltip-toggle",
            this
        );
        // refresh the event binding
        edges.on(tooltipSelector, "click", this, "toggleTooltip");
    }

    toggleShortLong(element) {
        let longSelector = edges.util.jsClassSelector(this.namespace, "long", this);
        let showSelector = edges.util.idSelector(this.namespace, "show-link", this);
        let container = this.component.jq(longSelector);
        let show = this.component.jq(showSelector);

        container.slideToggle(200);
        show.find(".all").toggle();
        show.find(".less").toggle();
    }

    //////////////////////////////////////////////////////////
    // some useful reusable components

    _shortTooltip() {
        let tt = this.tooltipText;
        let tooltipLinkId = edges.util.htmlID(
            this.namespace,
            "tooltip-toggle",
            this
        );
        let tooltipSpan = edges.util.htmlID(this.namespace, "tooltip-span", this);
        if (this.tooltip) {
            let tooltipLinkClass = edges.util.allClasses(
                this.namespace,
                "tooltip-link",
                this
            );
            tt =
                '<span id="' +
                tooltipSpan +
                '"><a id="' +
                tooltipLinkId +
                '" class="' +
                tooltipLinkClass +
                '" href="#">' +
                tt +
                "</a></span>";
        }
        return tt;
    }

    _longTooltip() {
        let tt = this.tooltip;
        let tooltipLinkId = edges.util.htmlID(
            this.namespace,
            "tooltip-toggle",
            this
        );
        let tooltipLinkClass = edges.util.allClasses(
            this.namespace,
            "tooltip-link",
            this
        );
        let tooltipSpan = edges.util.htmlID(this.namespace, "tooltip-span", this);
        tt =
            '<span id="' +
            tooltipSpan +
            '">' +
            this.tooltip +
            ' <a id="' +
            tooltipLinkId +
            '" class="' +
            tooltipLinkClass +
            '" href="#">less</a></span>';
        return tt;
    }
};

mex.renderers.Pager = class extends edges.Renderer {
    constructor(params) {
        super(params);

        this.scroll = edges.util.getParam(params, "scroll", true);

        this.scrollSelector = edges.util.getParam(params, "scrollSelector", "body");

        this.showSizeSelector = edges.util.getParam(
            params,
            "showSizeSelector",
            true
        );

        this.sizeOptions = edges.util.getParam(
            params,
            "sizeOptions",
            [10, 25, 50, 100]
        );

        this.sizePrefix = edges.util.getParam(params, "sizePrefix", "");

        this.sizeSuffix = edges.util.getParam(
            params,
            "sizeSuffix",
            i18n.t(" per page")
        );

        this.showRecordCount = edges.util.getParam(params, "showRecordCount", true);

        this.showPageNavigation = edges.util.getParam(
            params,
            "showPageNavigation",
            true
        );

        this.numberFormat = edges.util.getParam(params, "numberFormat", false);

        this.customClassForSizeSelector = edges.util.getParam(
            params,
            "customClassForSizeSelector",
            ""
        );

        this.namespace = "mex-pager";
    }

    draw() {
        if (this.component.total === false || this.component.total === 0) {
            this.component.context.html("");
            return;
        }

        // classes we'll need
        let containerClass = edges.util.allClasses(
            this.namespace,
            "container",
            this
        );
        let totalClass = edges.util.allClasses(this.namespace, "total", this);
        let navClass = edges.util.allClasses(this.namespace, "nav", this);
        let firstClass = edges.util.allClasses(this.namespace, "first", this);
        let prevClass = edges.util.allClasses(this.namespace, "prev", this);
        let pageClass = edges.util.allClasses(this.namespace, "page", this);
        let nextClass = edges.util.allClasses(this.namespace, "next", this);
        let lastClass = edges.util.allClasses(this.namespace, "last", this);
        let sizeSelectClass = edges.util.allClasses(this.namespace, "size", this);

        // the total number of records found
        let recordCount = "";
        if (this.showRecordCount) {
            let total = this.component.total;
            if (this.numberFormat) {
                total = this.numberFormat(total);
            }

            recordCount = `
            <div class="id-tags"><div class="id-tag">
                <div class="result-counter label" style="margin-right: .5rem;">
                    <div class="circle"></div>
                    <div class="value ${totalClass} text"> ${total} </div>
                </div>
                <div class="label">${i18n.t("results")}</div>
            </div></div>
            `;
        }

        // the number of records per page
        let sizer = "";
        if (this.showSizeSelector) {
            let sizeopts = "";
            let optarr = this.sizeOptions.slice(0);
            if ($.inArray(this.component.pageSize, optarr) === -1) {
                optarr.push(this.component.pageSize);
            }
            optarr.sort(function (a, b) {
                return a - b;
            }); // sort numerically
            for (let i = 0; i < optarr.length; i++) {
                let so = optarr[i];
                let selected = "";
                if (so === this.component.pageSize) {
                    selected = "selected='selected'";
                }
                sizeopts += `<option name="${so}" ${selected}>${so}</option>`;
            }

            let selectName = edges.util.htmlID(
                this.namespace,
                "page-size",
                this.component.id
            );
            sizer = `<div class="ui form ${this.customClassForSizeSelector}">
                <div class="inline fields">
                    <div class="field">${recordCount}${this.sizePrefix}</div>
                    <div class="field">
                        <select class="${sizeSelectClass}" name="${selectName}">
                            ${sizeopts}
                        </select>
                        <label for="${selectName}">${this.sizeSuffix}</label>
                    </div>
                </div>
            </div>`;
        } else {
            sizer = `<div class="ui form">
                <div class="inline fields">
                    <div class="field">${recordCount}</div>
                </div>
            </div>`;
        }

        let nav = "";
        if (this.showPageNavigation) {
            let first = `<a href="#" class="${firstClass} cursor-pointer">${i18n.t(
                "First"
            )}</a>`;
            let prev = `<a href="#" class="${prevClass} cursor-pointer">${i18n.t(
                "Prev"
            )}</a>`;
            if (this.component.page === 1) {
                first = `<span class="${firstClass} disabled cursor-not-allowed">${i18n.t(
                    "First"
                )}</span>`;
                prev = `<span class="${prevClass} disabled cursor-not-allowed">${i18n.t(
                    "Prev"
                )}</span>`;
            }

            let next = `<a href="#" class="${nextClass} cursor-pointer">${i18n.t(
                "Next"
            )}</a>`;
            let last = `<a href="#" class="${lastClass} cursor-pointer">${i18n.t(
                "Last"
            )}</a>`;

            if (this.component.page === this.component.totalPages) {
                next = `<span class="${nextClass} disabled cursor-not-allowed">${i18n.t(
                    "Next"
                )}</a>`;
                last = `<span class="${lastClass} disabled cursor-not-allowed">${i18n.t(
                    "Last"
                )}</a>`;
            }

            let pageNum = this.component.page;
            let totalPages = this.component.totalPages;
            if (this.numberFormat) {
                pageNum = this.numberFormat(pageNum);
                totalPages = this.numberFormat(totalPages);
            }
            nav = `<div class="ui grid ${navClass}">
                        <div class="three wide column pagination-item">
                            <i class="angle double left icon pagination-icon"></i>
                            ${first}
                        </div>
                        <div class="three wide column pagination-item">
                            <i class="angle left icon pagination-icon"></i>
                            ${prev}
                        </div>
                        <div class="four wide column pagination-item" style="display: flex;justify-content: center;">
                            <span class="${pageClass}">${i18n.t(
                "Page"
            )} ${pageNum} ${i18n.t("of")} ${totalPages}</span>
                        </div>
                        <div class="three wide column pagination-item" style="display: flex;justify-content: flex-end;">
                            ${next}
                            <i class="angle right icon pagination-icon"></i>
                        </div>
                        <div class="three wide column pagination-item" style="display: flex;justify-content: flex-end;">
                            ${last}
                            <i class="angle double right icon pagination-icon"></i>
                        </div>
                   </div>`;
        }

        let frag = `<div class="ui grid ${containerClass}" style="margin-left: 0">`;

        if (this.showPageNavigation) {
            frag += `<div class="sixteen wide column px-0">${nav}</div>`;
        }

        frag += `<div class="sixteen wide column">${sizer}</div>`;

        frag += `</div>`;

        this.component.context.html(frag);

        // now create the selectors for the functions
        if (this.showPageNavigation) {
            let firstSelector = edges.util.jsClassSelector(
                this.namespace,
                "first",
                this
            );
            let prevSelector = edges.util.jsClassSelector(
                this.namespace,
                "prev",
                this
            );
            let nextSelector = edges.util.jsClassSelector(
                this.namespace,
                "next",
                this
            );
            let lastSelector = edges.util.jsClassSelector(
                this.namespace,
                "last",
                this
            );

            // bind the event handlers
            if (this.component.page !== 1) {
                edges.on(firstSelector, "click", this, "goToFirst");
                edges.on(prevSelector, "click", this, "goToPrev");
            }
            if (this.component.page !== this.component.totalPages) {
                edges.on(nextSelector, "click", this, "goToNext");
                edges.on(lastSelector, "click", this, "goToLast");
            }
        }

        if (this.showSizeSelector) {
            let sizeSelector = edges.util.jsClassSelector(
                this.namespace,
                "size",
                this
            );
            edges.on(sizeSelector, "change", this, "changeSize");
        }
    }

    doScroll() {
        $("html, body").animate(
            {
                scrollTop: $(this.scrollSelector).offset().top,
            },
            1
        );
    }

    goToFirst(element) {
        if (this.scroll) {
            this.doScroll();
        }
        this.component.setFrom(1);
    }

    goToPrev(element) {
        if (this.scroll) {
            this.doScroll();
        }
        this.component.decrementPage();
    }

    goToNext(element) {
        if (this.scroll) {
            this.doScroll();
        }
        this.component.incrementPage();
    }

    goToLast(element) {
        if (this.scroll) {
            this.doScroll();
        }
        const from = (this.component.totalPages - 1) * this.component.pageSize + 1;

        if (from) {
            this.component.setFrom(from);
        }
    }

    changeSize(element) {
        let size = $(element).val();
        this.component.setSize(size);
    }
};

mex.renderers.ResourcesResults = class extends edges.Renderer {
    constructor(params) {
        super(params);

        //////////////////////////////////////////////
        // parameters that can be passed in

        // what to display when there are no results
        this.noResultsText = edges.util.getParam(
            params,
            "noResultsText",
            i18n.t("No results to display")
        );

        // callback to trigger when resource is selected or unselected
        this.onSelectToggle = edges.util.getParam(params, "onSelectToggle", null);

        this.selector = null; // will be set in init()

        this.namespace = "mex-resources-results";
    }

    init(component) {
        super.init(component);
        this.selector = this.component.edge.getComponent({id: "selector"});
    }

    draw() {
        var frag = this.noResultsText;
        if (this.component.results === false) {
            frag = "";
        }

        var results = this.component.results;
        if (results && results.length > 0) {
            // list the css classes we'll require
            var recordClasses = edges.util.styleClasses(
                this.namespace,
                "record",
                this.component.id
            );

            // now call the result renderer on each result to build the records
            frag = "";
            for (var i = 0; i < results.length; i++) {
                var rec = this._renderResult(results[i]);
                frag += `<div class="${recordClasses}">${rec}</div>`;
            }
        }

        // finally stick it all together into the container
        var containerClasses = edges.util.styleClasses(
            this.namespace,
            "container",
            this.component.id
        );
        var container = `<div class="${containerClasses}">${frag}</div>`;
        this.component.context.html(container);

        let selectSelector = edges.util.jsClassSelector(
            this.namespace,
            "select",
            this.component.id
        );

        // Checking sidebar status
        this.checkSidebarStatus();
        edges.on(selectSelector, "click", this, "selectResource");
    }

    selectResource(element) {
        let el = $(element);
        let id = el.attr("data-id");
        let state = el.attr("data-state");

        if (state === "unselected") {
            this.selector.selectRecord(id);
            el.attr("data-state", "selected");
        } else {
            this.selector.unselectRecord(id);
            el.attr("data-state", "unselected");
        }

        if (this.onSelectToggle) {
            this.onSelectToggle({parent: this, id: id});
        }

        this.checkSidebarStatus();
    }

    checkSidebarStatus() {
        // PATCH: to hide the right section on resources, since edges don't have template sync function
        let doc = document.getElementById("right-col");
        if (doc) {
            if (this.selector && this.selector.length > 0) {
                doc.style.display = "";
            } else {
                doc.style.display = "none";
            }
        }
    }

    _renderResult(res) {
        let title = edges.util.escapeHtml(
            this._getLangVal(mex.constants.TITLE_CONTAINER, res, i18n.t("No title"))
        );

        let alt = this._getLangVal(mex.constants.ALT_TITLE_CONTAINER, res);
        if (alt) {
            alt = edges.util.escapeHtml(alt);
        } else {
            alt = "";
        }

        let desc = this._getLangVal(mex.constants.DESCRIPTION_CONTAINER, res, "");
        if (desc.length > 300) {
            desc = edges.util.escapeHtml(desc.substring(0, 300)) + "...";
        }

        // FIXME: getting highlights out is difficult with the existing component, and the es integration.  They will
        // need reworking to do this properly.  For the moment this workaround will deal with it, but it is not
        // great, and will slow down large result sets
        let hits = this.component.edge.result.data.hits.hits;
        for (let hit of hits) {
            if (res.uuid === hit._id) {
                if (hit.highlight) {
                    if (hit.highlight[mex.constants.DESCRIPTION]) {
                        desc = hit.highlight[mex.constants.DESCRIPTION][0];
                        desc = desc.replace(/<em>/g, "<code>");
                        desc = desc.replace(/<\/em>/g, "</code>");
                    }
                    if (hit.highlight[mex.constants.TITLE]) {
                        title = hit.highlight[mex.constants.TITLE][0];
                        title = title.replace(/<em>/g, "<code>");
                        title = title.replace(/<\/em>/g, "</code>");
                    }
                }
            }
        }

        // let created = edges.util.escapeHtml(
        //     edges.util.pathValue("created", res, "")
        // );
        let created = res["custom_fields"]["mex:created"]
        // let createdDate = new Date(created);
        let created_ui = "";
        if (created && created.date) {
            created_ui = mex.fullDateFormatter(created.date);
            if (created_ui == "Invalid Date") {
                created_ui = created.date;
            }
        }



        let keywords = this._rankedByLang(mex.constants.KEYWORD_CONTAINER, res);
        if (keywords.length > 5) {
            keywords = keywords.slice(0, 5);
        }
        // keywords = keywords.map((k) => edges.util.escapeHtml(k)).join(", ");
        // if (keywords !== "") {
        //     keywords = `<span class="tag">${keywords}</span>`;
        // }

        let selectState = "unselected";

        if (this.selector && this.selector.isSelected(res.id)) {
            selectState = "selected";
            // currentImage = "/static/images/selected.svg";
            // selectText = i18n.t("Remove");
        }

        let previewClass = edges.util.jsClasses(
            this.namespace,
            "preview",
            this.component.id
        );
        let selectClass = edges.util.jsClasses(
            this.namespace,
            "select",
            this.component.id
        );

        let frag = `<div class="card"><div class="card-header" style="width: 100%">`

        if (created_ui) {
            frag += `
                <span class="date muted">${created_ui}</span>
            `
        }

        let vCount = 0;
            if ("backwards_linked" in res["display_data"]["linked_records"]) {
                if ("mex:usedIn" in res["display_data"]["linked_records"]["backwards_linked"]) {
                    vCount = res["display_data"]["linked_records"]["backwards_linked"]["mex:usedIn"].length
                }
            }


        frag += `
        <button type="button" class="ui icon button ${selectState} ${selectClass}"
                data-id="${res.id}"
                data-state="${selectState}"
                    title="${vCount ? selectState : i18n.t("This resource has no variables")}"
                    aria-label="${selectState}"
                    ${vCount ? "" : "disabled"}>
            ${vCount ? "" : "⊘"}</button></div>
        `

            let mex_id = res["custom_fields"]["mex:identifier"]
            frag += `<h3 class="title">
                <a href="/mex/${mex_id}" target="_blank">${title ? title : mex_id}</a>
            </h3>`

            if (alt) {
                frag += `<p class="subtitle">${alt}</strong>`
            }

            if (desc) {
                frag += `<p class="description">
                    ${desc.slice(0,600)}
                    ${desc.length > 600 ? "..." : ""}
                </p>`
            }

            if (keywords.length > 0) {
                frag += `<div class="tags">`
                for (let key of keywords)
                {
                    frag += `
                        <span class="tag">${key}</span>
                    `
                }
                frag += `</div>`
            }

            frag += `</div>`
        ;

        return frag;
    }

    _getLangVal(path, res, def) {
        return mex.getLangVal(path, res, def);
    }

    _rankedByLang(path, res) {
        return mex.rankedByLang(path, res);
    }
};

mex.renderers.CompactResourcesResults = class extends mex.renderers.ResourcesResults {
    constructor(params) {
        super(params);

        this.title = edges.util.getParam(params, "title", i18n.t("Resources"));

        this.hideIfNoResults = edges.util.getParam(
            params,
            "hideIfNoResults",
            false
        );

        // FIXME: may want to override namespace
        this.namespace = "mex-resources-results";
    }

    draw() {
        if (this.component.results === false || this.component.results.length === 0) {
            if (this.hideIfNoResults) {
                this.component.context.html("");
                return;
            }

            let frag = `<div class="">
                <div class="divider"></div>

                <h3 class="title" style="margin:0px">${this.title}</h4>
                <div>
                    <p>${this.noResultsText}</p>
                </div>
            </div>`;
            this.component.context.html(frag);
            return;
        }

        let results = this.component.results;

        // now call the result renderer on each result to build the records
        let resultsFrag = "";
        for (let i = 0; i < results.length; i++) {
            let rec = this._renderResult(results[i]);
            resultsFrag += `${rec}`;
        }

        let frag = `
            <div class="">
                <div class="divider"></div>

                <h4 class="title" style="margin:0px">${this.title}</h4>
                <div>
                    ${resultsFrag}
                </div>
            </div>
        `;

        this.component.context.html(frag);

        let selectSelector = edges.util.jsClassSelector(
            this.namespace,
            "select",
            this.component.id
        );

        // Checking sidebar status
        edges.on(selectSelector, "click", this, "selectResource");

        let toggleSelector = edges.util.jsClassSelector(
            this.namespace,
            "variable-toggle",
            this.component.id
        );
        edges.on(toggleSelector, "click", this, "toggleVariableGroups");

        let vgSelectSelector = edges.util.jsClassSelector(
            this.namespace,
            "group-select",
            this.component.id
        );
        edges.on(vgSelectSelector, "change", this, "toggleVariableGroupSelection");
    }

    selectResource(element, propagate=true) {
        let el = $(element);
        let id = el.attr("data-id");
        let state = el.attr("data-state");

        let vgsSelector = edges.util.idSelector(
            this.namespace,
            "vgs-" + edges.util.safeId(id),
            this.component.id
        );

        if (state === "unselected") {
            // we are selecting the resource
            this.selector.selectRecord(id);
            el.attr("data-state", "selected");
            el.removeClass("unselected").addClass("selected");

            $(vgsSelector).find("input[type='checkbox']").prop("disabled", false);
        } else {
            // we are unselecting the resource
            this.selector.unselectRecord(id);
            el.attr("data-state", "unselected");
            el.removeClass("selected").addClass("unselected");

            $(vgsSelector).find("input[type='checkbox']").prop("disabled", true);
        }

        if (this.onSelectToggle && propagate) {
            this.onSelectToggle({parent: this, id: id});
        }
    }

    selectResourceIfVisible(id, propagate=true) {
        let buttonSelector = edges.util.idSelector(
            this.namespace,
            `resource-${id}`,
            this.component.id
        );

        let button = this.component.jq(buttonSelector);
        if (button.length > 0) {
            this.selectResource(button[0], propagate);
        }
    }

    toggleVariableGroups(element) {
        let el = $(element);
        let dir = el.find("span.dir");
        if (dir.text() === "▾") {
            dir.text("▴");
        } else {
            dir.text("▾");
        }
        el.next().toggle();
    }

    toggleVariableGroupSelection(element) {
        // FIXME: this only works within the current component, but there could be multiple
        // components showing the variable groups, and they could all do with being updated
        let el = $(element);
        let id = el.attr("data-id");
        if (el.is(":checked")) {
            this.selector.selectVariableGroup(id);
            this.component.context
                .find("input[data-id='" + id + "']")
                .prop("checked", true);
        } else {
            this.selector.unselectVariableGroup(id);
            this.component.context
                .find("input[data-id='" + id + "']")
                .prop("checked", false);
        }

        if (this.onSelectToggle) {
            this.onSelectToggle({parent: this, id: id});
        }
    }

    _renderResult(record) {
        let title = mex.getLangVal(
            mex.constants.TITLE_CONTAINER,
            record,
            i18n.t("No title")
        );

        let truncated = title;
        if (truncated.length > 50) {
            truncated = truncated.substring(0, 47) + "...";
        }

        // FIXME: getting highlights out is difficult with the existing component, and the es integration.  They will
        // need reworking to do this properly.  For the moment this workaround will deal with it, but it is not
        // great, and will slow down large result sets
        let hits = this.component.edge.result.data.hits.hits;
        for (let hit of hits) {
            if (record.uuid === hit._id) {
                if (hit.highlight) {
                    if (hit.highlight[edges.mex.constants.TITLE]) {
                        truncated = hit.highlight[edges.mex.constants.TITLE][0];
                        truncated = truncated.replace(/<em>/g, "<code>");
                        truncated = truncated.replace(/<\/em>/g, "</code>");
                    }
                }
            }
        }

        let selectState = "unselected";
        if (this.selector && this.selector.isSelected(record.id)) {
            selectState = "selected";
        }

        // Variable groups
        let lang = mex.state.lang;
        let vgField = lang === "en" ? mex.constants.VARIABLE_GROUPS_EN : mex.constants.VARIABLE_GROUPS_DE;
        let vgs = edges.util.pathValue(vgField, record, []);

        let vgFrag = "No variable groups";
        let variableToggleClass = edges.util.jsClasses(
            this.namespace,
            "variable-toggle",
            this.component.id
        );

        let vgSelectClass = edges.util.jsClasses(
            this.namespace,
            "group-select",
            this.component.id
        );
        let variableGroupsId = edges.util.htmlID(
            this.namespace,
            "vgs-" + edges.util.safeId(record.id),
            this.component.id
        );
        if (vgs.length > 0) {
            vgFrag = `<button class="${variableToggleClass} ui button link-like" style="font-size: 1rem;">${i18n.t("Variable Groups")}
                            <span class="dir">▾</span></button>
                      <div id="${variableGroupsId}" style="display:none;">
                        <ul>`;
            for (let vg of vgs) {
                vgFrag += `<li class="ellipsis" style="line-height: 2.5rem; font-size: 1rem;">${vg.value}</li>`;
            }
            vgFrag += `</ul></div>`;
        }

        let selectClass = edges.util.jsClasses(
            this.namespace,
            "select",
            this.component.id
        );

        let id = edges.util.safeId(record.id);
        let buttonId = edges.util.htmlID(this.namespace, `resource-${id}`, this.component.id);
        const _setupAriaLabel = (title) => {
            let ariaLabelVerb = selectState === "unselected" ? i18n.t("add") : i18n.t("remove");
            let ariaLabelPreposition = selectState === "unselected" ? i18n.t("to") : i18n.t("from");
            let ariaLabel = [ariaLabelVerb, i18n.t("record"), edges.util.escapeHtml(title), ariaLabelPreposition, i18n.t("variables filter")].join(`&nbsp;`);
            return ariaLabel
        }

        let frag = `
            <div class="selected-list">
                <div class="card">
                    <div class="selected-list-item">
                        <div class="selected-list-item--title">
                            <button class="${selectClass} ui icon button ${selectState}"
                                id="${buttonId}"
                                data-id="${record.id}"
                                data-state="${selectState}"
                                title="${i18n.t("Select")}
                                aria-label="${_setupAriaLabel(title)}"
                                aria-selected="${i18n.t(selectState)}"
                                aria-live="polite"
                                ></button>
                            <span title="${edges.util.escapeHtml(title)}" class="max-line-2">
                                ${title}
                            </span>
                        </div>
                    </div>
                    <div class="selected-list-sub-item">
                        ${vgFrag}
                    </div>
                </div>
            </div>
        `;

        return frag;
    }

    _getLangVal(path, res, def) {
        return mex.getLangVal(path, res, def);
    }

    _rankedByLang(path, res) {
        return mex.rankedByLang(path, res);
    }
};

mex.renderers.activitiesResultView = function(res, highlights, include_resource_type=false) {
    if (!highlights) { highlights = {}}

    let title = edges.util.escapeHtml(
        mex.getLangVal(mex.constants.TITLE_CONTAINER, res, "No title")
    );

    let alt = mex.getLangVal(mex.constants.ALT_TITLE_CONTAINER, res);
    if (alt) {
        alt = edges.util.escapeHtml(alt);
    } else {
        alt = "";
    }

    let desc = mex.getLangVal(mex.constants.ABSTRACT_CONTAINER, res, "");
    if (desc.length > 300) {
        desc = edges.util.escapeHtml(desc.substring(0, 300)) + "...";
    }

    if (highlights) {
        if (highlights[mex.constants.ABSTRACT]) {
            desc = highlights[mex.constants.ABSTRACT][0];
            desc = desc.replace(/<em>/g, "<code>");
            desc = desc.replace(/<\/em>/g, "</code>");
        }
        if (highlights[mex.constants.TITLE]) {
            title = highlights[mex.constants.TITLE][0];
            title = title.replace(/<em>/g, "<code>");
            title = title.replace(/<\/em>/g, "</code>");
        }
    }

    // let start = i18n.t("Unknown start date");
    // start = mex.extractMultiDate(mex.constants.START, res, start);

    // let end = i18n.t("Unknown end date");
    // end = mex.extractMultiDate(mex.constants.END, res, end);

    function resourceTypeMacro() {
        if (include_resource_type) {
            return `<div class="tags"><div class="tag resource-type">${i18n.t('ACTIVITY')}</div></div>`
        }
        return "";
    }

    let mex_id = res["custom_fields"]["mex:identifier"]

    let frag = `
        <div class="card activity-card">
            ${resourceTypeMacro()}
            <h3 class="title">
                <a href="/mex/${mex_id}" target="_blank">${title ? title : mex_id}</a>
            </h3>`

    if (alt) {
        frag += `<p class="subtitle">${alt}</strong>`
    }

    if (desc) {
        frag += `<p class="description">
            ${desc.slice(0,600)}
            ${desc.length > 600 ? "..." : ""}
        </p>`;
    }

    function date_ui(date) {
        let date_ui = ""
        if (date) {
            if (Array.isArray(date)) {
                date = date[0]
            }
            date = date.date
            date_ui = mex.fullDateFormatter(date);
            if (date_ui == "Invalid Date") {
                date_ui = date;
            }
        }
        return date_ui
    }

    let start = res["custom_fields"]["mex:start"];
    let start_ui = date_ui(start)
    let end = res["custom_fields"]["mex:end"];
    let end_ui = date_ui(end)

    let date = '';

    if (start || end) {
    frag += `<p class="date muted">
        ${start_ui ?? ''}
        ${start && end ? i18n.t('to') : ''}
        ${end_ui ?? ''}
    </p>`;
    }

    frag += `</div>`

    return frag;
}

mex.renderers.bibliographicResourcesView = function(res, highlights, include_resource_type=false) {
    let title = edges.util.escapeHtml(
        mex.getLangVal(mex.constants.TITLE_CONTAINER, res, "No title")
    );

    let alt = mex.getLangVal(mex.constants.ALT_TITLE_CONTAINER, res);
    if (alt) {
        alt = edges.util.escapeHtml(alt);
    } else {
        alt = "";
    }

    let sub = mex.getLangVal(mex.constants.SUBTITLE_CONTAINER, res);
    if (sub) {
        sub = edges.util.escapeHtml(alt);
    } else {
        sub = "";
    }

    let desc = mex.getLangVal(mex.constants.ABSTRACT_CONTAINER, res, "");
    if (desc.length > 300) {
        desc = edges.util.escapeHtml(desc.substring(0, 300)) + "...";
    }

    if (highlights) {
        if (highlights[mex.constants.ABSTRACT]) {
            desc = highlights[mex.constants.ABSTRACT][0];
            desc = desc.replace(/<em>/g, "<code>");
            desc = desc.replace(/<\/em>/g, "</code>");
        }
        if (highlights[mex.constants.TITLE]) {
            title = highlights[mex.constants.TITLE][0];
            title = title.replace(/<em>/g, "<code>");
            title = title.replace(/<\/em>/g, "</code>");
        }
    }

    // let creators = edges.util.pathValue(mex.constants.CREATOR, res, []);

    function getCreatorsNames(field) {
        let names = ""
        for (let i = 0; i++; i < field.length) {
            names += field[i].display_value[0].value;
            console.log(names);
            if (i != field.length - 1) {
                names += ", ";
            }
        }
        console.log("return: ", names)
        return names;
    }

    let creators = getCreatorsNames(res["display_data"]["linked_records"]["mex:creator"] ?? [])

    // let pubYear = edges.util.pathValue(
    //     "custom_fields.mex:publicationYear.date",
    //     res,
    //     ""
    // );

    function resourceTypeMacro() {
        if (include_resource_type) {
            return `<div class="tags"><div class="tag resource-type">${i18n.t('PUBLICATION')}</div></div>`
        }
        return "";
    }

    function titleMacro(title, id) {

        const mex_id = res["custom_fields"]["mex:identifier"]

        return `
        <h3 class="title">
            <a href="/mex/${mex_id}" target="_blank">${title ? title : mex_id}</a>
        </h3>`;
    }

    let pubYear = res["custom_fields"]["mex:issued"]

    let frag = `<div class="card">`

    if (creators || pubYear){
        frag += `<div class="card-header"><span class="date muted">
            ${creators ?? ''}
            ${pubYear ? `(${mex.fullDateFormatter(pubYear)})` : ''}
            </span></div>
        `
    }
    frag += `
        ${resourceTypeMacro()}
        ${titleMacro(title, res.id)}
    `

    if (alt) {
        frag += `<p class="subtitle">${alt}</strong>`
    }

    if (desc) {
        frag += `<p class="description">${sub}</p>`;
    }
        frag += `</div>`;
    return frag;
}

mex.renderers.ActivitiesResults = class extends edges.Renderer {
    constructor(params) {
        super(params);

        //////////////////////////////////////////////
        // parameters that can be passed in

        // what to display when there are no results
        this.noResultsText = edges.util.getParam(params, "noResultsText", i18n.t("No results to display"));

        this.namespace = "mex-activities-results";
    }

    draw() {
        var frag = this.noResultsText;
        if (this.component.results === false) {
            frag = "";
        }

        var results = this.component.results;
        if (results && results.length > 0) {
            // list the css classes we'll require
            var recordClasses = edges.util.styleClasses(
                this.namespace,
                "record",
                this.component.id
            );

            // now call the result renderer on each result to build the records
            frag = "";
            for (var i = 0; i < results.length; i++) {
                var rec = this._renderResult(results[i]);
                frag += `<div class="${recordClasses}">${rec}</div>`;
            }
        }

        // finally stick it all together into the container
        var containerClasses = edges.util.styleClasses(
            this.namespace,
            "container",
            this.component.id
        );
        var container = `<div class="${containerClasses}">${frag}</div>`;
        this.component.context.html(container);
    }

    _renderResult(res) {
        // FIXME: getting highlights out is difficult with the existing component, and the es integration.  They will
        // need reworking to do this properly.  For the moment this workaround will deal with it, but it is not
        // great, and will slow down large result sets
        let highlights = {};
        let hits = this.component.edge.result.data.hits.hits;
        for (let hit of hits) {
            if (res.uuid === hit._id) {
                if (hit.highlight) {
                    highlights = hit.highlight;
                }
            }
        }

        return mex.renderers.activitiesResultView(res, highlights);
    }
};

mex.renderers.BibliographicResourcesResults = class extends edges.Renderer {
    constructor(params) {
        super(params);

        //////////////////////////////////////////////
        // parameters that can be passed in

        // what to display when there are no results
        this.noResultsText = edges.util.getParam(
            params,
            "noResultsText",
            i18n.t("No results to display")
        );

        this.namespace = "mex-bibliographic-resources-results";
    }

    draw() {
        var frag = this.noResultsText;
        if (this.component.results === false) {
            frag = "";
        }

        var results = this.component.results;
        if (results && results.length > 0) {
            // list the css classes we'll require
            var recordClasses = edges.util.styleClasses(
                this.namespace,
                "record",
                this.component.id
            );

            // now call the result renderer on each result to build the records
            frag = "";
            for (var i = 0; i < results.length; i++) {
                var rec = this._renderResult(results[i]);
                frag += `<div class="${recordClasses}">${rec}</div>`;
            }
        }

        // finally stick it all together into the container
        var containerClasses = edges.util.styleClasses(
            this.namespace,
            "container",
            this.component.id
        );
        var container = `<div class="${containerClasses}">${frag}</div>`;
        this.component.context.html(container);
    }

    _renderResult(res) {
        // FIXME: getting highlights out is difficult with the existing component, and the es integration.  They will
        // need reworking to do this properly.  For the moment this workaround will deal with it, but it is not
        // great, and will slow down large result sets
        let highlights = {};
        let hits = this.component.edge.result.data.hits.hits;
        for (let hit of hits) {
            if (res.uuid === hit._id) {
                if (hit.highlight) {
                    highlights = hit.highlight;
                }
            }
        }

        return mex.renderers.bibliographicResourcesView(res, highlights);
    }
};

mex.renderers.VariablesResults = class extends edges.Renderer {
    constructor(params) {
        super(params);

        //////////////////////////////////////////////
        // parameters that can be passed in

        // what to display when there are no results
        this.noResultsText = edges.util.getParam(params, "noResultsText", i18n.t("No results to display"));

        this.sortCycle = ["asc", "desc"];

        this.namespace = "mex-variables-results";
    }

    draw() {

        // obtain the current sort state from the query
        let sort = [];
        if (this.component.edge.currentQuery) {
            sort = this.component.edge.currentQuery.getSortBy();
        }

        let frag = `<div class="ui message">${this.noResultsText}</div>`;
        if (this.component.results === false) {
            frag = `<div class="ui active inline loader"></div>`;
        }

        let results = this.component.results;
        if (results && results.length > 0) {
            frag = "";
            for (var i = 0; i < results.length; i++) {
                frag += this._renderResult(results[i]);
            }
        }

        let containerClasses = edges.util.allClasses(this.namespace, "container", this.component.id);
        let expandAllClass = edges.util.jsClasses(this.namespace, "expand-all", this.component.id);

        let expandAllCheckbox = `
                <div class="checkbox" style="float:right;">
                    <label>
                        ${i18n.t("Expand all")}
                        <input type="checkbox" class="${expandAllClass}"/>
                    </label>
                </div>
                <br/>
        `

        let sortClasses = edges.util.jsClasses(this.namespace, "sort-button", this.component.id)

        function currentDir(field, short=true) {
            let longs = {"asc": "ascending", "desc": "descending"};
            for (let s of sort) {
                if (s.field === field) {
                    return short ? s.order : longs[s.order];
                }
            }
            return short ? "" : "none";
        }

        function sortButtonMacro(field) {
            function iconMacro() {
                for (let s of sort) {
                    if (s.field === field) {
                        if (s.order === "asc") {
                            return `&#9650;`;
                        } else if (s.order === "desc") {
                            return `&#9660;`;
                        }
                    }
                }
                return `&#9651;&#9661`
            }

            return `
                <button
                    class="img-button ${sortClasses}"
                    data-field="${field}"
                    data-dir="${currentDir(field)}">
                    ${iconMacro()}
                </button>`;
        }

        let langPrefix = edges.mex.state.lang;
        let rpath = langPrefix === "en" ? edges.mex.constants.USED_IN_EN_KW : edges.mex.constants.USED_IN_DE_KW;

        // Main table
        var container = `
        ${expandAllCheckbox}
        <table class="${containerClasses} ui celled table unstackable" style="border: none;background: transparent !important;">
            <colgroup>
                <col class="narrow" />
                <col span="4"/>
            </colgroup>
            <thead>
            <tr>
                <th></th>
                <th aria-sort="${currentDir(mex.constants.LABEL_KW, false)}">
                    ${i18n.t("Variables")}
                    ${sortButtonMacro(mex.constants.LABEL_KW)}
                </th>
                <th aria-sort="${currentDir(rpath, false)}">
                    ${i18n.t("Data Source")}
                    ${sortButtonMacro(rpath)}
                </th>
                <th aria-sort="${currentDir(mex.constants.BELONGS_TO_LABEL_KW, false)}">
                    ${i18n.t("Variable Group")}
                    ${sortButtonMacro(mex.constants.BELONGS_TO_LABEL_KW)}
                </th>
                <th>${i18n.t("Data Type")}</th>
            </tr>
            </thead>
            <tbody>
                ${frag}
            </tbody>
        </table>
        `;

        // render
        this.component.context.html(container);

        // event bindings
        let collapsedViewSelector = edges.util.jsClassSelector(this.namespace, "collapsed-view", this.component.id);
        edges.on(collapsedViewSelector, "click", this, "showExpanded");

        let expandedViewSelector = edges.util.jsClassSelector(this.namespace, "expanded-view", this.component.id);
        edges.on(expandedViewSelector, "click", this, "hideExpanded");

        let expandAllSelector = edges.util.jsClassSelector(this.namespace, "expand-all", this.component.id);
        edges.on(expandAllSelector, "change", this, "toggleExpandAll");

        let sortSelector = edges.util.jsClassSelector(this.namespace, "sort-button", this.component.id);
        edges.on(sortSelector, "click", this, "applySort");
    }

    _renderResult(res) {
        // get fields (escaped)
        let label = edges.util.escapeHtml(
            this._getLangVal(mex.constants.LABEL_CONTAINER, res, "No label")
        );

        const getTitle = (v) => {
            let langPrefix = mex.state.lang;
            const combineTitles = (items) => items.map(d => d.value).join(', ');

            const dd = v.display_value || [];
            const correctLang = dd.filter(d => d.language === langPrefix);
            const emptyLang = dd.filter(d => d.language === '');

            const selected =
                correctLang.length > 0
                ? [...correctLang, ...emptyLang]
                : dd;

            return combineTitles(selected);
        }

        // let langPrefix = edges.mex.state.lang;
        // let rpath = langPrefix === "en" ? edges.mex.constants.USED_IN_EN : edges.mex.constants.USED_IN_DE;
        let resources = edges.util.pathValue(edges.mex.constants.USED_IN_DISPLAY, res, []);
        // let resources = edges.util.pathValue("display_data.linked_records.mex:usedIn", res, []);
        let resourceFrag = "";
        if (resources) {
            for (let r of resources) {
                resourceFrag += `<p class="results-value"><a href="/records/mex/${r.link_id}" target="_blank" class="results-value--resource-title">${getTitle(r)}</a></p>`
            }
        }

        let groups = edges.util.pathValue(edges.mex.constants.BELONGS_TO_DISPLAY, res, []);
        let groupFrag = "";
        if (groups) {
            for (let g of groups){
                groupFrag += `<p class="results-value results-value--variable-group">${getTitle(g)}</p>`
            }
        }

        let dataType = edges.util.escapeHtml(
            edges.util.pathValue(
                "custom_fields.mex:dataType",
                res,
                i18n.t("Unknown")
            )
        );

        let desc = edges.util.escapeHtml(
            this._getLangVal(mex.constants.DESCRIPTION_CONTAINER, res, "")
        );

        let codingSystem = edges.util.pathValue(
            mex.constants.CODING_SYSTEM,
            res,
            []
        );
        if (!Array.isArray(codingSystem)) {
            codingSystem = [codingSystem];
        }
        let codingFrag = "";
        if (codingSystem.length > 0) {
            codingFrag = `
                    ${codingSystem.map((c) => edges.util.escapeHtml(c)).join(", ")}`;
        }

        let collapsedClass = edges.util.jsClasses(this.namespace, "collapsed-view", this.component.id);
        let expandedClass = edges.util.jsClasses(this.namespace, "expanded-view", this.component.id);
        let collapsedRowIdClass = edges.util.jsClasses(this.namespace, "collapsed-row-" + res.id, this.component.id);
        let expandedRowIdClass = edges.util.jsClasses(this.namespace, "expanded-row-" + res.id, this.component.id);
        let collapsedRowClass = edges.util.jsClasses(this.namespace, "collapsed-row", this.component.id);
        let expandedRowClass = edges.util.jsClasses(this.namespace, "expanded-row", this.component.id);

        let detailFrag = i18n.t("No additional details");
        if (desc || codingFrag || groupFrag || dataType) {
            detailFrag = `
                    ${desc && `<div class="${expandedRowClass}--details ${expandedRowClass}--desc">${desc}</p>`}
                    ${resourceFrag && `<div class="${expandedRowClass}--details ${expandedRowClass}--resource"><span class="attribute-label">${i18n.t("Data Source")}</span>:${resourceFrag}</div>`}
                    ${groupFrag && `<div class="${expandedRowClass}--details ${expandedRowClass}--group"><span class="attribute-label">${i18n.t("Variable Group")}:</span> ${groupFrag}</div>`}
                    ${dataType && `<div class="${expandedRowClass}--details ${expandedRowClass}--datatype"><span class="attribute-label">${i18n.t("Data type")}:</span> ${dataType}</div>`}
                    ${codingFrag && `<div class="${expandedRowClass}--details ${expandedRowClass}--coding"><span class="attribute-label">${i18n.t("Coding system")}:</span> ${codingFrag}</div>`}
                `;

            //   detailFrag = `<div class="details-extra">
            //                 ${descFrag}
            //                 ${codingFrag}
            //               </div>`;
        }


        // removed from now.


        let frag = `
            <tr class="${collapsedRowIdClass} ${collapsedRowClass}" data-label="${label}" role="row" data-id="${res.id}">
                <td>
                    <button class="img-button ${collapsedClass}">
                      <img
                        class="controls" src="/static/images/expand.svg" alt="expand icon" />
                    </button>
                </td>
                <td class="${collapsedRowIdClass}${collapsedRowClass}--label">${label}</td>
                <td class="${collapsedRowIdClass}${collapsedRowClass}--resource">${resourceFrag}</td>
                <td class="${collapsedRowIdClass}${collapsedRowClass}--group">${groupFrag}</td>
                <td class="${collapsedRowIdClass}${collapsedRowClass}--data-type">${dataType}</td>
            </tr>

            <tr class="${expandedRowIdClass} ${expandedRowClass} variable-row variable-row-top" data-label="${label}" role="row" data-id="${res.id}" style="display:none; border-bottom: 0;">
                <td>
                    <button class="img-button ${expandedClass}">
                      <img
                        class="controls" src="/static/images/shrink.svg" alt="shrink icon" />
                    </button>
                </td>
                <td class="${expandedRowIdClass}${expandedRowClass}--label"><h4>${label}</h4></td>
                <td class="${expandedRowIdClass}${expandedRowClass}--resource">${resourceFrag}</td>
                <td class="${expandedRowIdClass}${expandedRowClass}--group">${groupFrag}</td>
                <td class="${expandedRowIdClass}${expandedRowClass}--data-type">${dataType}</td>
            </tr>

            <tr class="${expandedRowIdClass} ${expandedRowClass} variable-row variable-row-bottom" role="row" style="display:none; border-top: 0;">
                <td />
                <td colspan="4">
                    ${detailFrag}
                </td>
            </tr>
          `;
        return frag;
    }

    showExpanded(cell) {
        // let cell = e.currentTarget;
        let tr = $(cell).parents("tr");
        let id = tr.attr("data-id");

        let toExpand = edges.util.jsClassSelector(
            this.namespace,
            "expanded-row-" + id,
            this.component.id
        );

        let toCollapse = edges.util.jsClassSelector(
            this.namespace,
            "collapsed-row-" + id,
            this.component.id
        );

        $(toCollapse).hide();
        $(toExpand).show();
    }

    hideExpanded(cell) {
        // let cell = e.currentTarget;
        let tr = $(cell).parents("tr");
        let id = tr.attr("data-id");

        let toExpand = edges.util.jsClassSelector(
            this.namespace,
            "expanded-row-" + id,
            this.component.id
        );

        let toCollapse = edges.util.jsClassSelector(
            this.namespace,
            "collapsed-row-" + id,
            this.component.id
        );

        $(toCollapse).show();
        $(toExpand).hide();
    }

    toggleExpandAll(element) {
        let isChecked = element.checked;
        let $ctx = this.component.context;

        let collapsedSelector = edges.util.jsClassSelector(
            this.namespace,
            "collapsed-row",
            this.component.id
        );

        let expandedSelector = edges.util.jsClassSelector(
            this.namespace,
            "expanded-row",
            this.component.id
        );

        if (isChecked) {
            $ctx.find(collapsedSelector).hide();
            $ctx.find(expandedSelector).show();
        } else {
            $ctx.find(collapsedSelector).show();
            $ctx.find(expandedSelector).hide();
        }
    }

    applySort(element) {
        let el = $(element);
        let field = el.attr("data-field");
        let dir = el.attr("data-dir");

        let currentIndex = this.sortCycle.indexOf(dir);
        let nextIndex = 0;
        if (currentIndex > -1) {
            nextIndex = (currentIndex + 1) % this.sortCycle.length;
        }
        let nextDir = this.sortCycle[nextIndex];

        let nq = this.component.edge.cloneQuery();
        nq.setSortBy(new es.Sort({field: field, order: nextDir}));
        this.component.edge.pushQuery(nq);
        this.component.edge.cycle();
    }

    toggleRow(evOrEl) {
        // tolerant toggleRow: supports being called with an event (edges.on) or an element/jQuery
        var $row = null;
        try {
            if (!evOrEl) return;
            if (evOrEl.currentTarget) {
                // called as event handler
                $row = $(evOrEl.currentTarget).closest("tr.variable-summary");
            } else if (evOrEl.target) {
                // event-like
                $row = $(evOrEl.target).closest("tr.variable-summary");
            } else {
                $row = $(evOrEl);
            }
        } catch (e) {
            return;
        }
        if (!$row || $row.length === 0) return;

        var $details = $row.next("tr.variable-details");
        var willOpen = !$details.is(":visible");
        $details.toggle();
        $row.toggleClass("expanded", willOpen);
    }

    _getLangVal(path, res, def) {
        return mex.getLangVal(path, res, def);
    }

    _rankedByLang(path, res) {
        return mex.rankedByLang(path, res);
    }
};

mex.renderers.GlobalResults = class extends edges.Renderer {
    constructor(params) {
        super(params);

        //////////////////////////////////////////////
        // parameters that can be passed in

        // what to display when there are no results
        this.noResultsText = edges.util.getParam(
            params,
            "noResultsText",
            i18n.t("No results to display")
        );

        this.namespace = "mex-global-results";
    }

    draw() {
        var frag = this.noResultsText;
        if (this.component.results === false) {
            frag = "";
        }

        var results = this.component.results;
        if (results && results.length > 0) {
            // list the css classes we'll require
            var recordClasses = edges.util.styleClasses(
                this.namespace,
                "record",
                this.component.id
            );

            // now call the result renderer on each result to build the records
            frag = "";
            for (var i = 0; i < results.length; i++) {
                let rec = this._renderResult(results[i]);
                frag += `<div class="${recordClasses}">${rec}</div>`;
            }
        }

        // finally stick it all together into the container
        var containerClasses = edges.util.styleClasses(
            this.namespace,
            "container",
            this.component.id
        );
        var container = `<div class="${containerClasses}">${frag}</div>`;
        this.component.context.html(container);
    }

    _renderResult(res) {
        let resType = edges.util.pathValue("metadata.resource_type.id", res, "resource");

        if (resType === "bibliographicresource") {
            return this._renderBibliographicResource(res);
        } else if (resType === "activity") {
            return this._renderActivity(res);
        } else if (resType === "variable") {
            return this._renderVariable(res);
        } else if (resType === "resource") {
            return this._renderResource(res);
        }
    }

    _renderResource(res) {
        let title = edges.util.escapeHtml(
            mex.getLangVal(mex.constants.TITLE_CONTAINER, res, i18n.t("No title"))
        );

        let alt = mex.getLangVal(mex.constants.ALT_TITLE_CONTAINER, res);
        if (alt) {
            alt = edges.util.escapeHtml(alt);
        } else {
            alt = "";
        }

        let desc = mex.getLangVal(mex.constants.DESCRIPTION_CONTAINER, res, "");
        if (desc.length > 300) {
            desc = edges.util.escapeHtml(desc.substring(0, 300)) + "...";
        }

        // FIXME: getting highlights out is difficult with the existing component, and the es integration.  They will
        // need reworking to do this properly.  For the moment this workaround will deal with it, but it is not
        // great, and will slow down large result sets
        let hits = this.component.edge.result.data.hits.hits;
        for (let hit of hits) {
            if (res.uuid === hit._id) {
                if (hit.highlight) {
                    if (hit.highlight[mex.constants.DESCRIPTION]) {
                        desc = hit.highlight[mex.constants.DESCRIPTION][0];
                        desc = desc.replace(/<em>/g, "<code>");
                        desc = desc.replace(/<\/em>/g, "</code>");
                    }
                    if (hit.highlight[mex.constants.TITLE]) {
                        title = hit.highlight[mex.constants.TITLE][0];
                        title = title.replace(/<em>/g, "<code>");
                        title = title.replace(/<\/em>/g, "</code>");
                    }
                }
            }
        }

        let created = edges.util.escapeHtml(
            edges.util.pathValue("created", res, "")
        );
        created = mex.fullDateFormatter(created);
        created = `<span class="tag">${created}</span>`;

        let keywords = mex.rankedByLang(mex.constants.KEYWORD_CONTAINER, res);
        if (keywords.length > 5) {
            keywords = keywords.slice(0, 5);
        }
        keywords = keywords.map((k) => edges.util.escapeHtml(k)).join(", ");
        if (keywords !== "") {
            keywords = `<span class="tag">${keywords}</span>`;
        }

        let selectState = "unselected";

        if (this.selector && this.selector.isSelected(res.id)) {
            selectState = "selected";
        }

        let frag = `
            <div class="card">
                <div class="tags"><div class="tag resource-type">${i18n.t('DATA SOURCE OR DATASET')}</div></div>
                <h4 class="title">
                    <a href="/records/${res.id}" target="_blank">${title ? title : res.id}</a>
                </div>

                <div class="subtitle ${alt ? "" : "hide"}">
                    <strong>${alt}</strong>
                </div>

                <div class="description ${desc ? "" : "hide"}">
                    ${desc}
                </div>

                <div class="tags ${keywords ? "" : "hide"}">
                    ${keywords}
                    ${created}
                </div>
            </div>
        `;

        return frag;
    }

    _renderBibliographicResource(res) {
        return mex.renderers.bibliographicResourcesView(res, null, true);
    }

    _renderActivity(res) {
        return mex.renderers.activitiesResultView(res, null, true);
    }

    _renderVariable(res) {
        let label = edges.util.escapeHtml(
            mex.getLangVal(mex.constants.LABEL_CONTAINER, res, "No label")
        );

        let langPrefix = mex.state.lang;
        let rpath = langPrefix === "en" ? mex.constants.USED_IN_EN : mex.constants.USED_IN_DE;
        let resources = edges.util.pathValue(
            rpath,
            res,
            []
        );

        let resourceFrag = "";
        if (resources.length > 1) {
            resourceFrag =
                "<ul><li>" +
                resources.map((r) => edges.util.escapeHtml(r)).join("</li><li>") +
                "</li></ul>";
        }

        let groups = edges.util.pathValue(mex.constants.BELONGS_TO_LABEL, res, []);
        let groupFrag = "";
        if (groups.length > 1) {
            groupFrag =
                "<ul><li>" +
                groups.map((g) => edges.util.escapeHtml(g)).join("</li><li>") +
                "</li></ul>";
        }

        let dataType = edges.util.escapeHtml(
            edges.util.pathValue(
                "custom_fields.mex:dataType",
                res,
                i18n.t("Unknown")
            )
        );

        // let desc = edges.util.escapeHtml(
        //     this._getLangVal(mex.constants.DESCRIPTION_CONTAINER, res, "")
        // );

        let frag = `
            <div class="card">
                <div class="tag">${i18n.t('VARIABLE')}</div>
                <h4 class="title">
                    <a href="/records/${res.id}" target="_blank">${label ? label : res.id}</a>
                </div>

                <div class="subtitle ${resourceFrag ? "" : "hide"}">
                    ${resourceFrag}
                </div>

                <div class="description ${groupFrag ? "" : "hide"}">
                    ${groupFrag}
                </div>

                <div class="tags ${dataType ? "" : "hide"}">
                    ${dataType}
                </div>
            </div>
        `;

        return frag;
    }
};

window.mex = mex;
export { edges, es, mex };
