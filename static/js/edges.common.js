if (!window.hasOwnProperty("edges")) {
  edges = {};
}
if (!edges.hasOwnProperty("instances")) {
  edges.instances = {};
}
if (!edges.hasOwnProperty("active")) {
  edges.active = {};
}
if (!edges.hasOwnProperty("mex")) {
  edges.mex = {};
}
if (!edges.mex.hasOwnProperty("state")) {
  edges.mex.state = {};
}
if (!edges.mex.hasOwnProperty("babel")) {
  edges.mex.babel = {};
}

///////////////////////////////////////////////////
// State management
edges.mex.state.lang = "en";

///////////////////////////////////////////////////
// Constants, especially for identifying fields

edges.mex.constants = {}

// keyword fields for facets and sorting
edges.mex.constants.ACCESS_RESTRICTION_KW = "custom_fields.mex:accessRestriction.keyword"
edges.mex.constants.JOURNAL_KW = "custom_fields.mex:journal.value.keyword"
edges.mex.constants.KEYWORD_KW = "custom_fields.mex:keyword.value.keyword"
edges.mex.constants.ACTIVITY_TYPE_KW = "custom_fields.mex:activityType.keyword"
edges.mex.constants.THEME_KW = "custom_fields.mex:theme.keyword"
edges.mex.constants.PERSONAL_DATA_KW = "custom_fields.mex:hasPersonalData.keyword"
edges.mex.constants.CREATION_METHOD_KW = "custom_fields.mex:resourceCreationMethod.keyword"
edges.mex.constants.TITLE_KW = "custom_fields.mex:title.value.keyword"

edges.mex.constants.FUNDER_DE_KW = "index_data.deFunderOrCommissioners.keyword"
edges.mex.constants.FUNDER_EN_KW = "index_data.enFunderOrCommissioners.keyword"

// range fields for date histograms
edges.mex.constants.CREATED_RANGE = "custom_fields.mex:created.date_range"
edges.mex.constants.END_RANGE = "custom_fields.mex:end.date_range"
edges.mex.constants.START_RANGE = "custom_fields.mex:start.date_range"
edges.mex.constants.PUBLICATION_YEAR_RANGE = "custom_fields.mex:publicationYear.date_range"

// field containers, for those with language/value sub fields
edges.mex.constants.DESCRIPTION_CONTAINER = "custom_fields.mex:description"
edges.mex.constants.ABSTRACT_CONTAINER = "custom_fields.mex:abstract"
edges.mex.constants.SUBTITLE_CONTAINER = "custom_fields.mex:subtitle"
edges.mex.constants.CREATOR_CONTAINER = "custom_fields.mex:creator"
edges.mex.constants.LABEL_CONTAINER = "custom_fields.mex:label"
edges.mex.constants.TITLE_CONTAINER = "custom_fields.mex:title"
edges.mex.constants.ALT_TITLE_CONTAINER = "custom_fields.mex:alternativeTitle"
edges.mex.constants.KEYWORD_CONTAINER = "custom_fields.mex:keyword"

// data fields for content, where content is available as literal (or as a list of literals)
// for display and free-text searching
edges.mex.constants.VARIABLE_GROUPS_EN = "index_data.enVariableGroups"
edges.mex.constants.VARIABLE_GROUPS_DE = "index_data.deVariableGroups"
edges.mex.constants.DESCRIPTION = "custom_fields.mex:description.value"
edges.mex.constants.CREATED = "custom_fields.mex:created.date"
edges.mex.constants.ABSTRACT = "custom_fields.mex:abstract.value"
edges.mex.constants.START = "custom_fields.mex:start"
edges.mex.constants.END = "custom_fields.mex:end"
edges.mex.constants.PUBLICATION_YEAR = "custom_fields.mex:publicationYear.date"
edges.mex.constants.USED_IN_EN = "index_data.enUsedInResource"
edges.mex.constants.USED_IN_DE = "index_data.deUsedInResource"
edges.mex.constants.BELONGS_TO_LABEL = "index_data.belongsToLabel"
edges.mex.constants.DATA_TYPE = "custom_fields.mex:dataType"
edges.mex.constants.CODING_SYSTEM = "custom_fields.mex:codingSystem"
edges.mex.constants.TITLE = "custom_fields.mex:title.value"
edges.mex.constants.ALT_TITLE = "custom_fields.mex:alternativeTitle.value"
edges.mex.constants.CONTRIBUTORS = "index_data.contributors"
edges.mex.constants.EXTERNAL_PARTNERS = "index_data.externalPartners"
edges.mex.constants.ICD10 = "custom_fields.mex:icd10code.value"

///////////////////////////////////////////////////
// General Functions

edges.mex.countFormat = edges.util.numFormat({
  thousandsSeparator: ",",
});

edges.mex.fullDateFormatter = function (datestr) {
  let date = new Date(datestr);
  return date.toLocaleString("default", {
    day: "numeric",
    month: "long",
    year: "numeric",
    timeZone: "UTC",
  });
};

edges.mex.yearFormatter = function (val) {
  let date = new Date(parseInt(val));
  return date.toLocaleString("default", { year: "numeric", timeZone: "UTC" });
};

edges.mex.monthFormatter = function (val) {
  let date = new Date(parseInt(val));
  return date.toLocaleString("default", {
    month: "long",
    year: "numeric",
    timeZone: "UTC",
  });
};

edges.mex.displayYearMonthPeriod = function (params) {
    let from = params.from;
    let to = params.to;

    let frdisplay = false;
    if (from) {
        frdisplay = new Date(parseInt(from)).toLocaleString('default', { month: 'long', year: 'numeric', timeZone: "UTC" });
    }

    let todisplay = false;
    if (to) {
        todisplay = new Date(parseInt(to - 1)).toLocaleString('default', { month: 'long', year: 'numeric', timeZone: "UTC" });
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

edges.mex._register = [];
edges.mex._keymode = false;
edges.mex._ = function (key) {
    if (!edges.mex._register.includes(key)) {
        edges.mex._register.push(key);
    }
    // FIXME: embedding this here probably doesn't help with extracting the translation keys,
    // need to replace calls to edges.mex._ with i18next.t directly in the source code
    // but want to see how key extraction works first
    return i18next.t(key);
    // if (edges.mex._keymode === false) {
    //     return i18next.t(key);
    //     if (key in edges.mex.babel) {
    //         return edges.mex.babel[key];
    //     }
    //     return key;
    // } else {
    //     let val = key;
    //     if (key in edges.mex.babel) {
    //         val = `*${val}*`;
    //     } else {
    //         val = `~~${val}~~`;
    //     }
    //     return val;
    // }
};

edges.mex._jinja_babel = function () {
  let temp = "";
  for (let r in edges.mex._register) {
    temp += `"${edges.mex._register[r]}": "{{ _("${edges.mex._register[r]}") }}",\n`;
  }
};

edges.mex.getLangVal = function (path, res, def) {
  let preferred = "";
  let field = edges.util.pathValue(path, res, []);
  for (let i = 0; i < field.length; i++) {
    let lang = field[i].language;
    if (lang === edges.mex.state.lang) {
      return field[i].value;
    }
    if (lang === "en" && preferred === "") {
      preferred = field[i].value;
    }
    if (lang === "de") {
      preferred = field[i].value;
    }
  }
  if (preferred !== "") {
    return preferred;
  }
  return def;
};

edges.mex.getAllLangVals = function (path, res) {
  let fields = edges.util.pathValue(path, res, []);
  let selected = [];
  let en = [];
  let de = [];
  for (let i = 0; i < fields.length; i++) {
    let field = fields[i];
    if (field.language === edges.mex.state.lang) {
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

edges.mex.rankedByLang = function (path, res) {
  let fields = edges.util.pathValue(path, res, []);
  let preferred = [];
  let de = [];
  let en = [];

  for (let i = 0; i < fields.length; i++) {
    let field = fields[i];
    if (field.language === edges.mex.state.lang) {
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

edges.mex.refiningAndFacet = function (params) {
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
    renderer: new edges.mex.renderers.RefiningANDTermSelector({
      open: true,
      controls: false,
      hideIfEmpty: true,
      title: params.title,
      useCheckboxes: true,
      showSelected: false,
      togglable: false,
      countFormat: edges.mex.countFormat,
    }),
  });
};

edges.mex.dateHistogram = function (params) {
  let interval = params.interval || "year";
  let displayFormatter = params.displayFormatter || edges.mex.yearFormatter;
  if (interval === "month") {
    displayFormatter = edges.mex.monthFormatter;
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
    renderer: new edges.mex.renderers.DateHistogramSelector({
      title: params.title || edges.mex._("Date Histogram"),
      open: true,
      togglable: false,
      useCheckboxes: params.useCheckboxes ?? false,
      showSelected: params.showSelected ?? true,
      countFormat: edges.mex.countFormat,
    }),
  });
};

edges.mex.fullSearchController = function (params) {
  return new edges.components.FullSearchController({
    id: params.id || "search_controller",
    category: params.category || "full",
    sortOptions: params.sortOptions || [],
    fieldOptions: params.fieldOptions || [],
    defaultField: params.defaultField || "*",
    renderer: new edges.mex.renderers.SidebarSearchController({
      searchButton: true,
      clearButton: params.clearButton || false,
      searchPlaceholder: params.searchPlaceholder || edges.mex._("Search..."),
      searchButtonText: params.searchButtonText || edges.mex._("Search"),
      freetextSubmitDelay: params.freetextSubmitDelay || -1,
      searchTitle: params.searchTitle || edges.mex._("Search")
    }),
  });
};

edges.mex.pager = function (params) {
  return new edges.components.Pager({
    id: params.id || "pager",
    category: params.category || "middle",
    renderer: new edges.mex.renderers.Pager({
      showSizeSelector: false,
      showPageNavigation: params.showPageNavigation ?? true,
            showRecordCount: false,
    }),
  });
};

edges.mex.pagerSelector = function (params) {
  return new edges.components.Pager({
    id: params.id || "pager-selector",
    category: params.category || "middle",
    renderer: new edges.mex.renderers.Pager({
      showSizeSelector: true,
      sizePrefix: edges.mex._("Show"),
      sizeSuffix: edges.mex._("results per page"),
      showPageNavigation: params.showPageNavigation ?? false,
      showRecordCount: false,
      customClassForSizeSelector: "page-size-selector",
    }),
  });
};

edges.mex.previewer = function (params) {
  return new edges.mex.components.Previewer({
    id: params.id || "previewer",
    category: params.category || "right",
    renderer: new edges.mex.renderers.RecordPreview({}),
  });
};

edges.mex.recordSelector = function (params) {
  if (!params) {
    params = {};
  }

  return new edges.mex.components.Selector({
    id: params.id || "selector",
    category: params.category || "right",
    renderer: new edges.mex.renderers.SelectedRecords({
      title: edges.mex._("Variables Query Filters"),
    }),
  });
};

edges.mex.recordSelectorCompact = function (params) {
  if (!params) {
    params = {};
  }
  return new edges.mex.components.Selector({
    id: params.id || "selector",
    category: params.category || "right",
    secondaryResults: params.secondaryResults || false,
    renderer: new edges.mex.renderers.CompactSelectedRecords({
      showIfEmpty: true,
      title: edges.mex._("Selected Resources"),
      onSelectToggle: params.onSelectToggle || false,
    }),
  });
};

edges.mex.makeEdge = function (params) {
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
    params.template || new edges.mex.templates.MainSearchTemplate();
  let callbacks = params.callbacks || {};

  let defaultQuery = new es.Query({ size: 50 });
  let oq = params.openingQuery || null;
  if (oq) {
    oq.merge(defaultQuery);
  } else {
    oq = defaultQuery;
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
edges.mex.resourceDisplay = function (params) {
  if (!params) {
    params = {};
  }
  return new edges.components.ResultsDisplay({
    id: params.id || "results",
    category: params.category || "middle",
    renderer: new edges.mex.renderers.ResourcesResults({
      noResultsText: params.noResultsText || edges.mex._("No resources found."),
      onSelectToggle: params.onSelectToggle || false,
      displayOnSidebar : params.displayOnSidebar ?? false,
    }),
  });
};

edges.mex.resourceDisplayCompact = function (params) {
  if (!params) {
    params = {};
  }
  return new edges.components.ResultsDisplay({
    id: params.id || "results",
    category: params.category || "middle",
    secondaryResults: params.secondaryResults || false,
    renderer: new edges.mex.renderers.CompactResourcesResults({
      title: params.title || edges.mex._("Resources"),
      noResultsText: params.noResultsText || edges.mex._("No resources found."),
      onSelectToggle: params.onSelectToggle || false,
    }),
  });
};

edges.mex.resourcePreview = function () {
  return edges.mex.previewer({});
};

edges.mex.resourceSelector = function () {
  return edges.mex.recordSelector({});
};
/////////////

// Activities
edges.mex.activitiesDisplay = function (params) {
  if (!params) {
    params = {};
  }
  return new edges.components.ResultsDisplay({
    id: params.id || "results",
    category: params.category || "middle",
    renderer: new edges.mex.renderers.ActivitiesResults({
      noResultsText:
        params.noResultsText || edges.mex._("No activities found."),
    }),
  });
};

edges.mex.activityPreview = function () {
  return edges.mex.previewer({});
};

///////////

// Bibliographic Resources
edges.mex.bibliographicResourcesDisplay = function (params) {
  if (!params) {
    params = {};
  }
  return new edges.components.ResultsDisplay({
    id: params.id || "results",
    category: params.category || "middle",
    renderer: new edges.mex.renderers.BibliographicResourcesResults({
      noResultsText:
        params.noResultsText ||
        edges.mex._("No bibliographic resources found."),
    }),
  });
};

edges.mex.bibliographicResourcesPreview = function () {
  return edges.mex.previewer({});
};

///////////

// Variables
edges.mex.variablesDisplay = function (params) {
  if (!params) {
    params = {};
  }
  return new edges.components.ResultsDisplay({
    id: params.id || "variables-results",
    category: params.category || "column",
    renderer: new edges.mex.renderers.VariablesResults({
      noResultsText: params.noResultsText || edges.mex._("No variables found."),
    }),
  });
};

//////////////

edges.mex.accessRestrictionFacet = function () {
  return edges.mex.refiningAndFacet({
    id: "access_restriction",
    field: edges.mex.constants.ACCESS_RESTRICTION_KW,
    title: edges.mex._("Access Restriction"),
    valueFunction: edges.mex.vocabularyLookup,
    category: "left",
  });
};

edges.mex.createdFacet = function () {
  return edges.mex.dateHistogram({
    id: "created",
    field: edges.mex.constants.CREATED_RANGE,
    title: edges.mex._("Created"),
    category: "left",
    interval: "month",
    useCheckboxes: true,
    showSelected: false,
  });
};

edges.mex.endFacet = function () {
  return edges.mex.dateHistogram({
    id: "end",
    field: edges.mex.constants.END_RANGE,
    title: edges.mex._("Activity End"),
    category: "left",
    interval: "year",
    useCheckboxes: true,
    showSelected: false,
  });
};

edges.mex.startFacet = function () {
  return edges.mex.dateHistogram({
    id: "start",
    field: edges.mex.constants.START_RANGE,
    title: edges.mex._("Activity Start"),
    category: "left",
    interval: "year",
    useCheckboxes: true,
    showSelected: false,
  });
};

edges.mex.publicationYearFacet = function () {
  return edges.mex.dateHistogram({
    id: "publication_year",
    field: edges.mex.constants.PUBLICATION_YEAR_RANGE,
    title: edges.mex._("Publication Year"),
    category: "left",
    interval: "year",
    useCheckboxes: true,
    showSelected: false,
  });
};

edges.mex.journalFacet = function () {
  return edges.mex.refiningAndFacet({
    id: "journal",
    field: edges.mex.constants.JOURNAL_KW,
    title: edges.mex._("Journal"),
    category: "left",
  });
};

edges.mex.keywordFacet = function () {
  return edges.mex.refiningAndFacet({
    id: "keyword",
    field: edges.mex.constants.KEYWORD_KW,
    title: edges.mex._("Keyword"),
    size: 5,
    category: "left",
  });
};

edges.mex.activityTypeFacet = function () {
  return edges.mex.refiningAndFacet({
    id: "activity_type",
    field: edges.mex.constants.ACTIVITY_TYPE_KW,
    title: edges.mex._("Activity Type"),
    category: "left",
    valueFunction: edges.mex.vocabularyLookup,
  });
};

edges.mex.funderOrCommissionerFacet = function () {
  let field = edges.mex.constants.FUNDER_DE_KW;
  if (edges.mex.state.lang === "en") {
    field = edges.mex.constants.FUNDER_EN_KW;
  }
  return edges.mex.refiningAndFacet({
    id: "funder_or_commissioner",
    field: field,
    title: edges.mex._("Funder or Commissioner"),
    category: "left",
  });
};

edges.mex.themeFacet = function () {
  return edges.mex.refiningAndFacet({
    id: "theme",
    field: edges.mex.constants.THEME_KW,
    title: edges.mex._("Theme"),
    category: "left",
    valueFunction: edges.mex.vocabularyLookup,
  });
};

edges.mex.hasPersonalDataFacet = function () {
  return edges.mex.refiningAndFacet({
    id: "has_personal_data",
    field: edges.mex.constants.PERSONAL_DATA_KW,
    title: edges.mex._("Has Personal Data"),
    category: "left",
    valueFunction: edges.mex.vocabularyLookup,
  });
};

edges.mex.resourceCreationMethodFacet = function () {
  return edges.mex.refiningAndFacet({
    id: "resource_creation_method",
    field: edges.mex.constants.CREATION_METHOD_KW,
    title: edges.mex._("Resource Creation Method"),
    category: "left",
    valueFunction: edges.mex.vocabularyLookup,
  });
};

edges.mex.defaultPager = function () {
  return edges.mex.pager({});
};

edges.mex.bottomPager = function () {
  return edges.mex.pagerSelector({});
};

edges.mex.resultCount = function(params) {
    if (!params) { params = {}; }
    return new edges.components.Pager({
        id: params.id || "result-count",
        category: params.category || "left-middle-top",
        renderer: new edges.mex.renderers.Pager({
            showSizeSelector: false,
            showPageNavigation: false,
            showRecordCount: true,
        }),
    });
}

edges.mex.sorter = function (params) {
    if (!params) { params = {}; }
    return new edges.components.FullSearchController({
        id: params.id || "sorter",
        category: params.category || "right-middle-top",
        sortOptions: params.sortOptions || [],
        renderer: new edges.mex.renderers.Sorter({}),
    });
}

edges.mex.selectedFilters = function (params) {
    if (!params) { params = {}; }
    let defaultFieldDisplays = {}
    defaultFieldDisplays[edges.mex.constants.ACCESS_RESTRICTION_KW] = edges.mex._("Access Restriction")
    defaultFieldDisplays[edges.mex.constants.JOURNAL_KW] = edges.mex._("Journal")
    defaultFieldDisplays[edges.mex.constants.KEYWORD_KW] = edges.mex._("Keyword")
    defaultFieldDisplays[edges.mex.constants.ACTIVITY_TYPE_KW] = edges.mex._("Activity Type")
    defaultFieldDisplays[edges.mex.constants.THEME_KW] = edges.mex._("Theme")
    defaultFieldDisplays[edges.mex.constants.PERSONAL_DATA_KW] = edges.mex._("Has Personal Data")
    defaultFieldDisplays[edges.mex.constants.CREATION_METHOD_KW] = edges.mex._("Resource Creation Method")
    defaultFieldDisplays[edges.mex.constants.FUNDER_DE_KW] = edges.mex._("Funder or Commissioner")
    defaultFieldDisplays[edges.mex.constants.FUNDER_EN_KW] = edges.mex._("Funder or Commissioner")
    defaultFieldDisplays[edges.mex.constants.CREATED_RANGE] = edges.mex._("Created")
    defaultFieldDisplays[edges.mex.constants.START_RANGE] = edges.mex._("Activity Start")
    defaultFieldDisplays[edges.mex.constants.END_RANGE] = edges.mex._("Activity End")
    defaultFieldDisplays[edges.mex.constants.PUBLICATION_YEAR_RANGE] = edges.mex._("Publication Year")

    let defaultValueFunctions = {}
    defaultValueFunctions[edges.mex.constants.ACCESS_RESTRICTION_KW] = edges.mex.vocabularyLookup
    // defaultValueFunctions[edges.mex.constants.JOURNAL_KW] = false
    // defaultValueFunctions[edges.mex.constants.KEYWORD_KW] = false
    defaultValueFunctions[edges.mex.constants.ACTIVITY_TYPE_KW] = edges.mex.vocabularyLookup
    defaultValueFunctions[edges.mex.constants.THEME_KW] = edges.mex.vocabularyLookup
    defaultValueFunctions[edges.mex.constants.PERSONAL_DATA_KW] = edges.mex.vocabularyLookup
    defaultValueFunctions[edges.mex.constants.CREATION_METHOD_KW] = edges.mex.vocabularyLookup
    // defaultValueFunctions[edges.mex.constants.FUNDER_DE_KW] = edges.mex._("Funder or Commissioner")
    // defaultValueFunctions[edges.mex.constants.FUNDER_EN_KW] = edges.mex._("Funder or Commissioner")

    let defaultRangeFunctions = {}
    defaultRangeFunctions[edges.mex.constants.CREATED_RANGE] = edges.mex.displayYearMonthPeriod
    defaultRangeFunctions[edges.mex.constants.START_RANGE] = edges.mex.displayYearMonthPeriod
    defaultRangeFunctions[edges.mex.constants.END_RANGE] = edges.mex.displayYearMonthPeriod
    defaultRangeFunctions[edges.mex.constants.PUBLICATION_YEAR_RANGE] = edges.mex.displayYearMonthPeriod

    return new edges.components.SelectedFilters({
        id: params.id || "selected-filters",
        category: "full",
        fieldDisplays: params.fieldDisplays || defaultFieldDisplays,
        valueFunctions: params.valueFunctions || defaultValueFunctions,
        rangeFunctions: params.rangeFunctions || defaultRangeFunctions,
        renderer: new edges.mex.renderers.SelectedFilters({})
    });
}

/////////////////////////////////////////
// Vocabulary lookup

edges.mex.VOCABULARY = {};

edges.mex.vocabularyLookup = function (value) {
  if (value in edges.mex.VOCABULARY) {
    let lang = edges.mex.state.lang;
    if (lang in edges.mex.VOCABULARY[value]) {
      return edges.mex.VOCABULARY[value][lang];
    } else if ("en" in edges.mex.VOCABULARY[value]) {
      return edges.mex.VOCABULARY[value]["en"];
    } else if ("de" in edges.mex.VOCABULARY[value]) {
      return edges.mex.VOCABULARY[value]["de"];
    } else {
      let keys = Object.keys(edges.mex.VOCABULARY[value]);
      if (keys.length > 0) {
        return edges.mex.VOCABULARY[value][keys[0]];
      }
    }
  }
  return value;
};

/////////////////////////////////////////
// Template(s)

if (!edges.mex.hasOwnProperty("templates")) {
  edges.mex.templates = {};
}

edges.mex.templates.MainSearchTemplate = class extends edges.Template {
  constructor(params) {
    super(params);

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
        middleContainers += `<div class="${midClass}"><div id="${mid[i].id}"></div></div>`;
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

    let verticalTabClass = edges.util.jsClasses(
      this.namespace,
      "verticalTab",
      ""
    );

    let frag = `
            <div class="ui grid container">
                <div class="sixteen wide column">
                    ${fullContainers}
                </div>
                <div class="three wide column">
                    ${facetContainers}
                </div>
                <div class="wide column" style="flex: 1;">
                    <div class="ui grid container">
                        <div class="eight wide column">
                            ${leftMiddleTopContainers}
                        </div>
                        <div class="eight wide column">
                            ${rightMiddleTopContainers}
                        </div>
                    </div>
                    <div class="ui grid container">
                        ${middleContainers}
                    </div>
                </div>
                <div id="right-col" class="five wide column" style=${rightContainerStyle}>
                    ${rightContainers}
                </div>
                <div id="vertical-tab" class="vertical-tab ${verticalTabClass}">
                </div>
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
    let doc = document.getElementById("right-col");
    if (doc) {
      doc.style.display = "";
    }
  }
};

edges.mex.templates.SingleColumnTemplate = class extends edges.Template {
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
        if (
          this.hideComponentsInitially !== false &&
          this.hideComponentsInitially.includes(comps[i].id)
        ) {
          style = " style='display:none;' ";
        }

        let container = `<div class="${compClass}"><div id="${comps[i].id}"${style}></div></div>`;
        compContainers += container;
      }
    }

    let frag = `
            <div class="ui grid container">
                <div class="sixteen wide column">
                    ${preambleFrag}
                    ${compContainers}
                </div>
            </div>
        `;
    edge.context.html(frag);
  }
};

//////////////////////////////////////////////
// Components
if (!edges.mex.hasOwnProperty("components")) {
  edges.mex.components = {};
}

edges.mex.components.Previewer = class extends edges.Component {
  constructor(params) {
    super(params);

    this.currentPreview = null;

    this.fields = [
      {
        field: "mex:title",
        name: edges.mex._("Title"),
        lang: true,
        valueFunction: null,
      },
      {
        field: "mex:abstract",
        name: edges.mex._("Abstract"),
        lang: true,
        valueFunction: null,
      },
      {
        field: "mex:accessPlatform",
        name: edges.mex._("Access Platform"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:accessRestriction",
        name: edges.mex._("Access Restriction"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:accessService",
        name: edges.mex._("Access Service"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:accessURL.url",
        name: edges.mex._("Access URL"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:accrualPeriodicity",
        name: edges.mex._("Accrual Periodicity"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:affiliation",
        name: edges.mex._("Affiliation"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:alternateIdentifier",
        name: edges.mex._("Alternate Identifier"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:alternativeTitle",
        name: edges.mex._("Alternative Title"),
        lang: true,
        valueFunction: null,
      },
      {
        field: "mex:anonymizationPseudonymization",
        name: edges.mex._("Anonymization/Pseudonymization"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:belongsTo",
        name: edges.mex._("Belongs To"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:bibliographicResourceType",
        name: edges.mex._("Bibliographic Resource Type"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:codingSystem",
        name: edges.mex._("Coding System"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:conformsTo",
        name: edges.mex._("Conforms To"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:contact",
        name: edges.mex._("Contact"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:containedBy",
        name: edges.mex._("Contained By"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:contributingUnit",
        name: edges.mex._("Contributing Unit"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:contributor",
        name: edges.mex._("Contributor"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:created",
        name: edges.mex._("Created"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:creator",
        name: edges.mex._("Creator"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:dataType",
        name: edges.mex._("Data Type"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:description",
        name: edges.mex._("Description"),
        lang: true,
        valueFunction: null,
      },
      {
        field: "mex:distribution",
        name: edges.mex._("Distribution"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:documentation.url",
        name: edges.mex._("URL"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:doi",
        name: edges.mex._("DOI"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:downloadURL",
        name: edges.mex._("Download URL"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:edition",
        name: edges.mex._("Edition"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:editor",
        name: edges.mex._("Editor"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:editorOfSeries",
        name: edges.mex._("Editor of Series"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:email",
        name: edges.mex._("Email"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:end.date",
        name: edges.mex._("End"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:endpointDescription",
        name: edges.mex._("Endpoint Description"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:endpointType",
        name: edges.mex._("Endpoint Type"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:endpointURL",
        name: edges.mex._("Endpoint URL"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:externalAssociate",
        name: edges.mex._("External Associate"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:externalPartner",
        name: edges.mex._("External Partner"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:familyName",
        name: edges.mex._("Family Name"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:fullName",
        name: edges.mex._("Full Name"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:funderOrCommissioner",
        name: edges.mex._("Funder or Commissioner"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:fundingProgram",
        name: edges.mex._("Funding Program"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:geprisId",
        name: edges.mex._("Gepris ID"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:givenName",
        name: edges.mex._("Given Name"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:gndId",
        name: edges.mex._("GND ID"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:hasLegalBasis",
        name: edges.mex._("Has Legal Basis"),
        lang: true,
        valueFunction: null,
      },
      {
        field: "mex:hasPersonalData",
        name: edges.mex._("Has Personal Data"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:icd10code",
        name: edges.mex._("ICD10 Code"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:identifier",
        name: edges.mex._("MEX Identifier"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:instrumentToolOrApparatus",
        name: edges.mex._("Instrument/Tool/Aparatus"),
        lang: true,
        valueFunction: null,
      },
      {
        field: "mex:involvedPerson",
        name: edges.mex._("Involved Person"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:involvedUnit",
        name: edges.mex._("Involved Unit"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:isPartOf",
        name: edges.mex._("Is Part Of"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:isPartOfActivity",
        name: edges.mex._("Is Part Of Activity"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:isbnIssn",
        name: edges.mex._("ISBN/ISSN"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:isniId",
        name: edges.mex._("ISNI"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:issue",
        name: edges.mex._("Issue"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:issued",
        name: edges.mex._("Issued"),
        lang: false,
        valueFunction: null,
      },
      {
        field: "mex:journal",
        name: edges.mex._("Journal"),
        lang: true,
        valueFunction: null,
      },
      {
        field: "mex:keyword",
        name: edges.mex._("Keyword"),
        lang: true,
        valueFunction: null,
      },
      {
        field: "mex:label",
        name: edges.mex._("Label"),
        lang: true,
        valueFunction: null,
      },
    ];
  }

  setPreviewRecord(previewRecord) {
    this.currentPreview = previewRecord;
  }

  showPreview(previewRecord) {
    this.setPreviewRecord(previewRecord);
    this.draw();
  }
};

edges.mex.components.Selector = class extends edges.Component {
  constructor(params) {
    super(params);

    this._resources = {};
    this._variable_groups = {};

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

  clearAll() {
    // for (let id in this._resources) {
    //     window.localStorage.removeItem(id);
    // }
    // this._resources = {};
    // window.localStorage.removeItem("selection");
    this._resources = {};
    this._variable_groups = {};
    window.localStorage.clear();
  }

  ids() {
    return Object.keys(this._resources);
  }

  isSelected(id) {
    return this._resources.hasOwnProperty(id);
  }

  //////////////////////////////////////
  // component behavioural functions

  selectRecord(id) {
    for (let hit of this.edge.result.data.hits.hits) {
      if (id === hit._source.id) {
        this.set(id, hit._source);

        let en = edges.util.pathValue(
          edges.mex.constants.VARIABLE_GROUPS_EN,
          hit._source,
          []
        );
        for (let group of en) {
          this.recordVariableGroup(group.mex_id, true);
        }

        let de = edges.util.pathValue(
          edges.mex.constants.VARIABLE_GROUPS_DE,
          hit._source,
          []
        );
        for (let group of de) {
          this.recordVariableGroup(group.mex_id, true);
        }

        break;
      }
    }
    this.draw();
  }

  unselectRecord(id) {
    let record = this.get(id);
    let en = edges.util.pathValue(edges.mex.constants.VARIABLE_GROUPS_EN, record, []);
    for (let group of en) {
      this.removeVariableGroup(group.mex_id, true);
    }

    let de = edges.util.pathValue(edges.mex.constants.VARIABLE_GROUPS_DE, record, []);
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

if (!edges.mex.hasOwnProperty("renderers")) {
  edges.mex.renderers = {};
}

edges.mex.renderers.SelectedFilters = class extends edges.Renderer {
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
        ///static/images/close.svg
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
                        filters += `<a class="${removeClass}" data-bool="must" data-filter="${def.filter}" data-field="${field}" data-value="${val.val}" title="Remove" href="#">
                                        <img src="/static/images/close.svg" alt="Remove" title="Remove" style="width:24px;height:24px;vertical-align:middle"/>
                                    </a>`;
                    } else if (def.filter === "range") {
                        var from = val.from ? ' data-' + val.fromType + '="' + val.from + '" ' : "";
                        var to = val.to ? ' data-' + val.toType + '="' + val.to + '" ' : "";
                        filters += `<a class="${removeClass}" data-bool="must" data-filter="${def.filter}" data-field="${field}" ${from} ${to} title="Remove" href="#">
                                        <img src="/static/images/close.svg" alt="Remove" title="Remove" style="width:24px;height:24px;vertical-align:middle"/>
                                    </a>`;
                    }
                }

                filters += "</span>";
            }
        }

        if (showClear) {
            let clearClass = edges.util.allClasses(this.namespace, "clear", this);
            let clearFrag = `<button type="button" class="filters ${clearClass}" title="Clear all search and sort parameters and start again">
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
            if (val === "true"){
                value = true;
            }
            else if (val === "false"){
                value = false;
            }
            else if (!isNaN(parseInt(val))){
                value = parseInt(val);
            }
            else {
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

edges.mex.renderers.SelectedRecords = class extends edges.Renderer {
  constructor(params) {
    super(params);
    this.title = edges.util.getParam(params, "title", "Selected Resources");
    this.showIfEmpty = edges.util.getParam(params, "showIfEmpty", false);
    this.namespace = "select-records";

    this.resourceComponent = null;
  }

  init(component) {
    super.init(component);
    this.resourceComponent = this.component.edge.getComponent({
      id: "results",
    });
  }

  draw() {
    if (this.component.length === 0 && this.showIfEmpty) {
      let frag = `<div class="card card-shadow">
                <div class="divider"></div>

                <h4 class="title" style="margin:0px">${this.title}</h4>
                <div>
                    <p>${edges.mex._(
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

    for (let id of this.component.ids()) {
      let record = this.component.get(id);

      let title = edges.mex.getLangVal(
        edges.mex.constants.TITLE_CONTAINER,
        record,
        edges.mex._("No title")
      );


            let variables = edges.util.pathValue(edges.mex.constants.VARIABLE_GROUPS_DE, record, []);
            if (edges.mex.state.lang === "en") {
                variables = edges.util.pathValue(edges.mex.constants.VARIABLE_GROUPS_EN, record, []);
            }

            let vCount = variables.length;
      recordsFrag += `
                <div class="selected-list">
                    <button class="img-button">
                      <img
                        data-id="${id}"
                        class="${selectClass} controls close-icon" src="/static/images/close.svg" alt="Slide right" />
                    </button>
                    <div>
                        <div class="selected-list-item">
                            ${title}
                        </div>
                        <div class="muted">
                            ${vCount} ${edges.mex._("Variable Groups")}
                        </div>
                    </div>
                </div>`;
    }

    let frag = "";
    let title = `go to the variables search page to list the variables of ${this.component.length} resources`;
    if (recordsFrag) {
      frag = `
                <div class="card card-shadow">

                    <div id="control-section">
                      <button class="img-button">
                        <img class="${hideClass} controls slide-icon" src="/static/images/slide-right.svg" alt="Slide right" />
                      </button>
                    </div>

                    <div class="divider">
                    </div>

                    <h4 class="title" style="margin:0px">${this.title}</h4>
                    <div>
                        ${recordsFrag}
                    </div>
                    <a class="link-button" href="/search/variables" title="${title}">
                        ${edges.mex._("Explore Variables for Chosen Datasets")}
                    </a>
                </div>
                `;
    }

    let verticalBar = document.getElementById("vertical-tab");
    if (verticalBar) {
      const length = this.component.length;
      verticalBar.innerHTML = `<span> ${edges.mex._(
        "Variables Query Filters"
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
    edges.on(selectSelector, "click", this, "selectResource");
    edges.on(hideSelector, "click", this, "hideSelectedRecords");
  }

  hideSelectedRecords() {
    let doc = document.getElementById("right-col");
    if (doc) {
      doc.style.display = "none";
    }
  }

  selectResource(element) {
    let el = $(element);
    let id = el.attr("data-id");

    // Syncing this with resource result component.
    let doc = document.getElementById(`resource-list-${id}`);

    if (doc && this.resourceComponent && this.resourceComponent.renderer) {
      this.resourceComponent.renderer.selectResource(doc);
    } else {
      this.component.unselectRecord(id);
      this.resourceComponent.renderer.draw();
    }
  }
};

edges.mex.renderers.CompactSelectedRecords = class extends (
  edges.mex.renderers.SelectedRecords
) {
  constructor(params) {
    super(params);

    this.onSelectToggle = edges.util.getParam(params, "onSelectToggle", null);

    // FIXME: may want to change the namespace
    this.namespace = "select-records";
  }

  draw() {
    if (this.component.length === 0 && this.showIfEmpty) {
      let frag = `<div class="card card-shadow">
                <div class="divider"></div>

                <h4 class="title" style="margin:0px">${this.title}</h4>
                <div>
                    <p>${edges.mex._(
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

    for (let id of this.component.ids()) {
      let record = this.component.get(id);

      let title = edges.mex.getLangVal(
        edges.mex.constants.TITLE_CONTAINER,
        record,
        edges.mex._("No title")
      );

      let truncated = title;
      if (truncated.length > 50) {
        truncated = truncated.substring(0, 47) + "...";
      }

      let lang = edges.mex.state.lang;
      let vgField = lang === "en" ? edges.mex.constants.VARIABLE_GROUPS_EN : edges.mex.constants.VARIABLE_GROUPS_EN;
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
        vgFrag = `<a href="#" class="${variableToggleClass}">${edges.mex._(
          "Variable Groups"
        )}
                                <span class="dir">▾</span></a>
                          <div style="display:none;">`;
        for (let vg of vgs) {
          let vgshort = vg.value;
          if (vgshort.length > 30) {
            vgshort = vgshort.substring(0, 27) + "...";
          }

          let selected = this.component.variableGroupSelected(vg.mex_id);
          let selectedFrag = "";
          if (selected) {
            selectedFrag = 'checked="checked"';
          }
          vgFrag += `<input type="checkbox" data-id="${vg.mex_id}" class="${vgSelectClass}" ${selectedFrag}/>
                                <label for="" title="${vg}">${vgshort}</label><br>`;
        }
        vgFrag += `</div>`;
      }

      recordsFrag += `
                <div class="selected-list">
                    <!-- <img
                        data-id="${id}"
                        class="${selectClass} controls" src="/static/images/close.svg" alt="Slide right" width="24px" height="32px"/> -->
                    <div>
                        <div class="selected-list-item">
                            <button data-id="${id}" class="${selectClass} ui button mini">Unselect</button>
                            <span title="${title}">${truncated}</span>
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
                <div class="card card-shadow">
                    <div class="divider"></div>

                    <h4 class="title" style="margin:0px">${this.title}</h4>
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
  }

  hideSelectedRecords() {
    // Do nothing, as this is a compact view
  }

  selectResource(element) {
    let el = $(element);
    let id = el.attr("data-id");

    // Syncing this with resource result component.
    let doc = document.getElementById(`resource-list-${id}`);

    if (doc && this.resourceComponent && this.resourceComponent.renderer) {
      this.resourceComponent.renderer.selectResource(doc);
    } else {
      this.component.unselectRecord(id);
      this.resourceComponent.renderer.draw();
    }

    if (this.onSelectToggle) {
      this.onSelectToggle({ parent: this, id: id });
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
      this.onSelectToggle({ parent: this, id: id });
    }
  }
};

edges.mex.renderers.RecordPreview = class extends edges.Renderer {
  constructor(params) {
    super(params);
  }

  draw() {
    if (this.component.currentPreview === null) {
      this.component.context.html("");
      return;
    }

    let fieldsFrag = `<h2>${edges.mex._("Preview")}</h2>`;
    for (let fieldDef of this.component.fields) {
      let field = "custom_fields." + fieldDef.field;
      let display = fieldDef.name;
      let selectLang = fieldDef.lang || false;
      let displayFunction = fieldDef.valueFunction || null;

      let vals = [];
      if (selectLang) {
        vals = edges.mex.getAllLangVals(field, this.component.currentPreview);
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

edges.mex.renderers.SidebarSearchController = class extends edges.Renderer {
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
      edges.mex._("Search")
    );

    // amount of time between finishing typing and when a query is executed from the search box
    this.freetextSubmitDelay = edges.util.getParam(
      params,
      "freetextSubmitDelay",
      500
    );

    this.searchTitle = edges.util.getParam(params, "searchTitle", "Search");

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

      sortFrag = `<div class="ui form">
                <div class="field">
                    <select class="ui fluid dropdown ${sortFieldClass}">
                        <option value="_score">${edges.mex._(
                          "Relevance"
                        )}</option>
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

      let fieldOptions = "";
      for (let i = 0; i < comp.fieldOptions.length; i++) {
        let obj = comp.fieldOptions[i];
        fieldOptions += `<option value="${
          obj["field"]
        }">${edges.util.escapeHtml(obj["display"])}</option>`;
      }

      field_select += `<select class="${searchFieldClass}">
                                <option value="">${edges.mex._(
                                  "search all"
                                )}</option>
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
                <button type="button" class="ui button ${resetClass}" title="${edges.mex._(
        "Clear all search and sort parameters and start again"
      )}">
                    ${edges.mex._("Clear")}
                </button>
            </div>`;
    }

    let searchFrag = "";
    if (this.searchButton) {
      let text = '<span class="icon search"></span>';
      if (this.searchButtonText !== false) {
        text = this.searchButtonText;
      }
      searchFrag = `<div class="ui form"><div class="field"><button type="button" class="button ${searchClass} search-button">${text}</button></div></div>`;
    }

    let searchBox = `
            <div class="ui form" style="display: flex;">
                ${clearFrag}
                <div class="field" style="flex-grow: 1;">
                    <input type="text" id="${textId}" class="ui input ${textClass}" name="q" placeholder="${this.searchPlaceholder}" style="width: 100%;" />
                </div>
            </div>`;

    // assemble the final fragment and render it into the component's context
    let containerClass = edges.util.styleClasses(
      this.namespace,
      "container",
      this
    );

    let sortColumn = sortFrag
      ? `<div class="three wide column">${sortFrag}</div>`
      : "";

    let searchColumn = searchFrag
      ? `<div class="one wide column">${searchFrag}</div>`
      : "";

    // Upgrading the search UI as per sematic ui
    let frag = `
    <div class="ui grid ${containerClass}">
        <div class="row middle aligned">
            <div class="search-label">
                <label><h3>
                  ${this.searchTitle}
                </h3></label>
            </div>
            <div class="eleven wide column">
                ${searchBox}
            </div>
             ${sortColumn}
            ${searchColumn}
        </div>
    </div>`;

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
      el.html(`<i class="icon sort up"></i> ${edges.mex._("sort by")}`);
      el.attr(
        "title",
        edges.mex._("Current order ascending. Click to change to descending")
      );
    } else {
      el.html(`<i class="icon sort down"></i> ${edges.mex._("sort by")}`);
      el.attr(
        "title",
        edges.mex._("Current order descending. Click to change to ascending")
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

edges.mex.renderers.Sorter = class extends edges.Renderer {
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
                    ${edges.mex._("Sort by")}
                    <select class="ui dropdown ${sortFieldClass}">
                        <option value="_score">${edges.mex._("Relevance")}</option>
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
                <div class="ui right aligned column" style="text-align: right;">
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
            el.html(`<i class="icon sort up"></i> ${edges.mex._("sort by")}`);
            el.attr(
                "title",
                edges.mex._("Current order ascending. Click to change to descending")
            );
        } else {
            el.html(`<i class="icon sort down"></i> ${edges.mex._("sort by")}`);
            el.attr(
                "title",
                edges.mex._("Current order descending. Click to change to ascending")
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

edges.mex.renderers.Sorter = class extends edges.Renderer {
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
                    ${edges.mex._("Sort by")}
                    <select class="ui dropdown ${sortFieldClass}">
                        <option value="_score">${edges.mex._("Relevance")}</option>
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
                <div class="ui right aligned column" style="text-align: right;">
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
            el.html(`<i class="icon sort up"></i> ${edges.mex._("sort by")}`);
            el.attr(
                "title",
                edges.mex._("Current order ascending. Click to change to descending")
            );
        } else {
            el.html(`<i class="icon sort down"></i> ${edges.mex._("sort by")}`);
            el.attr(
                "title",
                edges.mex._("Current order descending. Click to change to ascending")
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

edges.mex.renderers.RefiningANDTermSelector = class extends edges.Renderer {
  constructor(params) {
    super(params);

    ///////////////////////////////////////
    // parameters that can be passed in

    this.title = edges.util.getParam(params, "title", edges.mex._("Select"));

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

    let results = showFacet ? "" : edges.mex._("No data available");
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
                        <div class="${resultClass} checkbox">
                            <label>
                                <input type="checkbox" class="${activeClass}" data-key="${escapedTerm}" ${checked}/>
                                ${edges.util.escapeHtml(
                                  escapedDisplay
                                )} (${count})
                            </label>
                        </div>`;
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
            <div class="ui ${facetClass}" style="margin-bottom:15px">
                <div class="${headerClass}">
                    <div class="ui grid">
                        <div class="sixteen wide column">${tog}</div>
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
      `${edges.mex._("Currently displaying")} ${
        this.component.size
      } ${edges.mex._("results per page. How many would you like instead?")}`
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
    } <a id="${tooltipLinkId}" class="${tooltipLinkClass}" href="#">${edges.mex._(
      "less"
    )}</a></span>`;
    return tt;
  };
};

edges.mex.renderers.DateHistogramSelector = class extends edges.Renderer {
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
      edges.mex._("Select Date Range")
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
    );
    Date;

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

    let results = edges.mex._("Loading...");
    if (ts.values !== false) {
      results = edges.mex._("No data available");
    }

    if (ts.values && ts.values.length > 0) {
      results = "";

      let filterTerms = ts.filters.map((f) => f.display);
      let longClass = edges.util.allClasses(namespace, "long", this);
      let short = true;

      for (let i = 0; i < ts.values.length; i++) {
        let val = ts.values[i];

                // skip empty date bins if requested
                if (this.hideEmptyDateBin && val.count === 0) {
                    continue;
                }

        let checked = filterTerms.includes(val.display) ? "checked" : "";
        // This will allow us to remove filter if already selected this can seamlessly work for checkboxes and button
        let activeClass = filterTerms.includes(val.display)
          ? filterRemoveClass
          : valClass;
        let myLongClass = "";
        let styles = "";

        if (this.shortDisplay && this.shortDisplay <= i) {
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
                        <span class="less" style="display:none">${edges.mex._(
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
    this.component.selectRange({ gte: gte, lt: lt });
  }

  removeFilter(element) {
    let gte = this.component.jq(element).attr("data-gte");
    let lt = this.component.jq(element).attr("data-lt");
    this.component.removeFilter({ gte: gte, lt: lt });
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

edges.mex.renderers.Pager = class extends edges.Renderer {
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
      edges.mex._(" per page")
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
                <div class="result-counter">
                    <div class="value ${totalClass}"> ${total} </div>
                    <div class="label">${edges.mex._("results")}</div>
                </div>
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
      let first = `<a href="#" class="${firstClass} cursor-pointer">${edges.mex._(
        "First"
      )}</a>`;
      let prev = `<a href="#" class="${prevClass} cursor-pointer">${edges.mex._(
        "Prev"
      )}</a>`;
      if (this.component.page === 1) {
        first = `<span class="${firstClass} disabled cursor-not-allowed">${edges.mex._(
          "First"
        )}</span>`;
        prev = `<span class="${prevClass} disabled cursor-not-allowed">${edges.mex._(
          "Prev"
        )}</span>`;
      }

      let next = `<a href="#" class="${nextClass} cursor-pointer">${edges.mex._(
        "Next"
      )}</a>`;
      let last = `<a href="#" class="${lastClass} cursor-pointer">${edges.mex._(
        "Last"
      )}</a>`;

      if (this.component.page === this.component.totalPages) {
        next = `<span class="${nextClass} disabled cursor-not-allowed">${edges.mex._(
          "Next"
        )}</a>`;
        last = `<span class="${lastClass} disabled cursor-not-allowed">${edges.mex._(
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
                            <span class="${pageClass}">${edges.mex._(
        "Page"
      )} ${pageNum} ${edges.mex._("of")} ${totalPages}</span>
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

    let frag = `<div class="ui grid ${containerClass}">`;

    if (this.showPageNavigation) {
      frag += `<div class="sixteen wide column">${nav}</div>`;
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

edges.mex.renderers.ResourcesResults = class extends edges.Renderer {
  constructor(params) {
    super(params);

    //////////////////////////////////////////////
    // parameters that can be passed in

    // what to display when there are no results
    this.noResultsText = edges.util.getParam(
      params,
      "noResultsText",
      edges.mex._("No results to display")
    );

    // callback to trigger when resource is selected or unselected
    this.onSelectToggle = edges.util.getParam(params, "onSelectToggle", null);
    this.displayOnSidebar = edges.util.getParam(params, "displayOnSidebar", false);

    this.selector = null; // will be set in init()

    this.namespace = "mex-resources-results";
  }

  init(component) {
    super.init(component);
    this.selector = this.component.edge.getComponent({ id: "selector" });
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
      el.html("-");
    } else {
      this.selector.unselectRecord(id);
      el.attr("data-state", "unselected");
      el.html("+");
    }

    if (this.onSelectToggle) {
      this.onSelectToggle({ parent: this, id: id });
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
      this._getLangVal(edges.mex.constants.TITLE_CONTAINER, res, edges.mex._("No title"))
    );

    let alt = this._getLangVal(edges.mex.constants.ALT_TITLE_CONTAINER, res);
    if (alt) {
      alt = edges.util.escapeHtml(alt);
    } else {
      alt = "";
    }

    let desc = this._getLangVal(edges.mex.constants.DESCRIPTION_CONTAINER, res, "");
    if (desc.length > 300) {
      desc = edges.util.escapeHtml(desc.substring(0, 300)) + "...";
    }

        // FIXME: getting highlights out is difficult with the existing component, and the es integration.  They will
        // need reworking to do this properly.  For the moment this workaround will deal with it, but it is not
        // great, and will slow down large result sets
        let hits = this.component.edge.result.data.hits.hits;
        for (let hit of hits) {
            if (res.uuid === hit._id) {
                if (
                    hit.highlight &&
                    hit.highlight[edges.mex.constants.DESCRIPTION]
                ) {
                    desc = hit.highlight[edges.mex.constants.DESCRIPTION][0];
                    desc = desc.replace(/<em>/g, "<code>");
                    desc = desc.replace(/<\/em>/g, "</code>");
                }
            }
        }

    let created = edges.util.escapeHtml(
      edges.util.pathValue("created", res, "")
    );
    // let createdDate = new Date(created);
    created = edges.mex.fullDateFormatter(created);

    let keywords = this._rankedByLang(edges.mex.constants.KEYWORD_CONTAINER, res);
    if (keywords.length > 5) {
      keywords = keywords.slice(0, 5);
    }
    keywords = keywords.map((k) => edges.util.escapeHtml(k)).join(", ");
    if (keywords !== "") {
      keywords = `<span class="tag">${keywords}</span>`;
    }

    let selectState = "unselected";
    let current = "+";

    if (this.selector && this.selector.isSelected(res.id)) {
      selectState = "selected";
      current = '-'
      // currentImage = "/static/images/selected.svg";
      // selectText = edges.mex._("Remove");
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

    let frag = ""

    if(this.displayOnSidebar) {
      // Frag TBD for variables page
    } else {
      frag = `
            <div class="resource-card card-shadow">
                <div class="card-header ${created ? "" : "hide"}" style="width: 100%">
                    <div class="ui grid">
                        <div class="ten wide column">
                            <span class="date">${created}</span>
                        </div>
                        <div class="six wide column" style="text-align: right">
                          <button type="button" class="ui icon button ${selectState} ${selectClass}"
                              data-id="${res.id}"
                              data-state="${selectState}"
                                    title="${selectState}"
                                    aria-label="${selectState}">
                                ${current}
                            </button>
                          </div>
                    </button>
                    </div>
                </div>

                <div class="title">
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
                </div>
            </div>
        `;
    }
    return frag;
  }

  _getLangVal(path, res, def) {
    return edges.mex.getLangVal(path, res, def);
  }

  _rankedByLang(path, res) {
    return edges.mex.rankedByLang(path, res);
  }
};

edges.mex.renderers.CompactResourcesResults = class extends (
  edges.mex.renderers.ResourcesResults
) {
  constructor(params) {
    super(params);

    this.title = edges.util.getParam(params, "title", edges.mex._("Resources"));

    // FIXME: may want to override namespace
    this.namespace = "mex-resources-results";
  }

  draw() {
    if (
      this.component.results === false ||
      this.component.results.length === 0
    ) {
      let frag = `<div class="card card-shadow">
                <div class="divider"></div>

                <h4 class="title" style="margin:0px">${this.title}</h4>
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
            <div class="card card-shadow">
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

  selectResource(element) {
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
      let selectButtonText = edges.mex._("Unselect");
      el.html(selectButtonText);

      $(vgsSelector).find("input[type='checkbox']").prop("disabled", false);
    } else {
      // we are unselecting the resource
      this.selector.unselectRecord(id);
      el.attr("data-state", "unselected");
      let selectButtonText = edges.mex._("Select");
      el.html(selectButtonText);

      $(vgsSelector).find("input[type='checkbox']").prop("disabled", true);
    }

    if (this.onSelectToggle) {
      this.onSelectToggle({ parent: this, id: id });
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
      this.onSelectToggle({ parent: this, id: id });
    }
  }

  _renderResult(record) {
    let title = edges.mex.getLangVal(
      edges.mex.constants.TITLE_CONTAINER,
      record,
      edges.mex._("No title")
    );

    let truncated = title;
    if (truncated.length > 50) {
      truncated = truncated.substring(0, 47) + "...";
    }

    let selectState = "unselected";
    let selectButtonText = edges.mex._("Select");
    if (this.selector && this.selector.isSelected(record.id)) {
      selectState = "selected";
      selectButtonText = edges.mex._("Unselect");
    }

    // Variable groups
    let lang = edges.mex.state.lang;
    let vgField = lang === "en" ? edges.mex.constants.VARIABLE_GROUPS_EN : edges.mex.constants.VARIABLE_GROUPS_DE;
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
      vgFrag = `<a href="#" class="${variableToggleClass}">${edges.mex._(
        "Variable Groups"
      )}
                            <span class="dir">▾</span></a>
                      <div id="${variableGroupsId}" style="display:none;">`;
      for (let vg of vgs) {
        let vgshort = vg.value;
        if (vgshort.length > 30) {
          vgshort = vgshort.substring(0, 27) + "...";
        }

        let selectedFrag = "";
        let disabledFrag = "";
        if (selectState === "unselected") {
          // If a record has not been selected, then we are going to check all the variable groups,
          // AND disable them (so you cannot interact with them while the record is unselected).
          // THEN if the variable group is known to the selector (e.g. by some other resource with the same
          // group) AND it has been unchecked elsewhere, then uncheck it here too.
          disabledFrag = "disabled";
          selectedFrag = 'checked="checked"';
          let isKnown = this.selector.variableGroupRecorded(vg.mex_id);
          if (isKnown) {
            let selected = this.selector.variableGroupSelected(vg.mex_id);
            if (!selected) {
              selectedFrag = "";
            }
          }
        } else {
          // If a record has been selected, then we should show all the variable groups according
          // to their current state in the selector, and allow interaction.
          let selected = this.selector.variableGroupSelected(vg.mex_id);
          if (selected) {
            selectedFrag = 'checked="checked"';
          }
        }

        vgFrag += `<input type="checkbox" data-id="${vg.mex_id}" class="${vgSelectClass}" ${selectedFrag} ${disabledFrag}/>
                            <label for="" title="${vg}">${vgshort}</label><br>`;
      }
      vgFrag += `</div>`;
    }

    let selectClass = edges.util.jsClasses(
      this.namespace,
      "select",
      this.component.id
    );

    let frag = `
            <div class="selected-list">
                <div>
                    <div class="selected-list-item">
                        <button class="${selectClass} ui button mini"
                            id="resource-list-${record.id}"
                            data-id="${record.id}"
                            data-state="${selectState}"
                            >${selectButtonText}</button>
                        <span title="${title}">
                            ${truncated}
                        </span>
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
    return edges.mex.getLangVal(path, res, def);
  }

  _rankedByLang(path, res) {
    return edges.mex.rankedByLang(path, res);
  }
};

edges.mex.renderers.ActivitiesResults = class extends edges.Renderer {
  constructor(params) {
    super(params);

    //////////////////////////////////////////////
    // parameters that can be passed in

    // what to display when there are no results
    this.noResultsText = edges.util.getParam(
      params,
      "noResultsText",
      edges.mex._("No results to display")
    );

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

    let previewSelector = edges.util.jsClassSelector(
      this.namespace,
      "preview",
      this.component.id
    );
    edges.on(previewSelector, "click", this, "previewActivity");
  }

  previewActivity(element) {
    let id = $(element).attr("data-id");
    let previewer = this.component.edge.getComponent({ id: "previewer" });

    // FIXME: poor abstraction, works fine, but feels wrong
    let hits = this.component.edge.result.data.hits.hits;
    for (let hit of hits) {
      if (hit._source.id === id) {
        previewer.showPreview(hit._source);
        break;
      }
    }
  }

  _renderResult(res) {
    let title = edges.util.escapeHtml(
      this._getLangVal(edges.mex.constants.TITLE_CONTAINER, res, "No title")
    );

    let alt = this._getLangVal(edges.mex.constants.ALT_TITLE_CONTAINER, res);
    if (alt) {
      alt = edges.util.escapeHtml(alt);
    } else {
      alt = "";
    }

    let desc = this._getLangVal(edges.mex.constants.ABSTRACT_CONTAINER, res, "");
    if (desc.length > 300) {
      desc = edges.util.escapeHtml(desc.substring(0, 300)) + "...";
    }

    // FIXME: getting highlights out is difficult with the existing component, and the es integration.  They will
    // need reworking to do this properly.  For the moment this workaround will deal with it, but it is not
    // great, and will slow down large result sets
    let hits = this.component.edge.result.data.hits.hits;
    for (let hit of hits) {
      if (res.uuid === hit._id) {
        if (
          hit.highlight &&
          hit.highlight[edges.mex.constants.ABSTRACT]
        ) {
          desc = hit.highlight[edges.mex.constants.ABSTRACT][0];
          desc = desc.replace(/<em>/g, "<code>");
          desc = desc.replace(/<\/em>/g, "</code>");
        }
      }
    }

    let start = edges.mex._("Unknown start date");
    start = this._extractMultiDate(edges.mex.constants.START, res, start);

    let end = edges.mex._("Unknown end date");
    end = this._extractMultiDate("custom_fields.mex:end", res, end);

    let previewClass = edges.util.jsClasses(
      this.namespace,
      "preview",
      this.component.id
    );

    let frag = `
            <div class="activity-card card-shadow">
                <div class="title ${title ? "" : "hide"}">
                    <span>
                        ${title}
                    </span>
                </div>

                <div class="subtitle ${alt ? "" : "hide"}">
                    <strong>${alt}</strong>
                </div>

                <div class="description ${desc ? "" : "hide"}">
                    ${desc}
                </div>

                <div class="description ${start || end ? "" : "hide"}">
                    <span class="${start ? "" : "hide"}">
                        ${start}
                    </span>

                    <span class="${start && end ? "" : "hide"}">
                        ${edges.mex._("to")}
                    </span>

                    <span class="${end ? "" : "hide"}">
                        ${end}
                    </span>
                </div>
            </div>
        `;

    return frag;
  }

  _extractMultiDate(path, res, def) {
    let out = def;
    let dates = edges.util.pathValue(path, res, []);
    if (dates.length > 0) {
      out = dates
        .map((d) => {
          return d.date;
        })
        .join(edges.mex._(" or "));
      if (dates.length > 1) {
        out = `(${out})`;
      }
    }
    return out;
  }

  _getLangVal(path, res, def) {
    return edges.mex.getLangVal(path, res, def);
  }

  _rankedByLang(path, res) {
    return edges.mex.rankedByLang(path, res);
  }
};

edges.mex.renderers.BibliographicResourcesResults = class extends (
  edges.Renderer
) {
  constructor(params) {
    super(params);

    //////////////////////////////////////////////
    // parameters that can be passed in

    // what to display when there are no results
    this.noResultsText = edges.util.getParam(
      params,
      "noResultsText",
      edges.mex._("No results to display")
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

    let previewSelector = edges.util.jsClassSelector(
      this.namespace,
      "preview",
      this.component.id
    );
    edges.on(previewSelector, "click", this, "previewBibliographicResource");
  }

  previewBibliographicResource(element) {
    let id = $(element).attr("data-id");
    let previewer = this.component.edge.getComponent({ id: "previewer" });

    // FIXME: poor abstraction, works fine, but feels wrong
    let hits = this.component.edge.result.data.hits.hits;
    for (let hit of hits) {
      if (hit._source.id === id) {
        previewer.showPreview(hit._source);
        break;
      }
    }
  }

  _renderResult(res) {
    let title = edges.util.escapeHtml(
      this._getLangVal(edges.mex.constants.TITLE_CONTAINER, res, "No title")
    );

    let alt = this._getLangVal(edges.mex.constants.ALT_TITLE_CONTAINER, res);
    if (alt) {
      alt = edges.util.escapeHtml(alt);
    } else {
      alt = "";
    }

    let sub = this._getLangVal(edges.mex.constants.SUBTITLE_CONTAINER, res);
    if (sub) {
      sub = edges.util.escapeHtml(alt);
    } else {
      sub = "";
    }

    let desc = this._getLangVal(edges.mex.constants.ABSTRACT_CONTAINER, res, "");
    if (desc.length > 300) {
      desc = edges.util.escapeHtml(desc.substring(0, 300)) + "...";
    }

    // FIXME: getting highlights out is difficult with the existing component, and the es integration.  They will
    // need reworking to do this properly.  For the moment this workaround will deal with it, but it is not
    // great, and will slow down large result sets
    let hits = this.component.edge.result.data.hits.hits;
    for (let hit of hits) {
      if (res.uuid === hit._id) {
        if (
          hit.highlight &&
          hit.highlight[edges.mex.constants.ABSTRACT]
        ) {
          desc = hit.highlight[edges.mex.constants.ABSTRACT][0];
          desc = desc.replace(/<em>/g, "<code>");
          desc = desc.replace(/<\/em>/g, "</code>");
        }
      }
    }

    // FIXME: will need to be a dereferenced field
    let creators = edges.util.pathValue(edges.mex.constants.CREATOR_CONTAINER, res, []);
    creators = creators.map((c) => edges.util.escapeHtml(c)).join(", ");

    let pubYear = edges.util.pathValue(
      "custom_fields.mex:publicationYear.date",
      res,
      ""
    );

    let previewClass = edges.util.jsClasses(
      this.namespace,
      "preview",
      this.component.id
    );

    let frag = `<div class="biblo-resource-card card-shadow">
                <div class="title ${title ? "" : "hide"}">
                     <span>
                        ${title}
                    </span>
                </div>

                <div class="subtitle ${alt ? "" : "hide"}">
                    <strong>${alt}</strong>
                </div>

                <div class="description ${sub ? "" : "hide"}">
                    ${sub}
                </div>

                <div class="tags ${creators || pubYear ? "" : "hide"}">
                    <span class="tag ${creators ? "" : "hide"}">
                        ${creators}
                    </span>

                    <span class="tag ${pubYear ? "" : "hide"}">
                        ${pubYear}
                    </span>
                </div>
            </div>`;
    return frag;
  }

  _getLangVal(path, res, def) {
    return edges.mex.getLangVal(path, res, def);
  }

  _rankedByLang(path, res) {
    return edges.mex.rankedByLang(path, res);
  }
};

edges.mex.renderers.VariablesResults = class extends edges.Renderer {
  constructor(params) {
    super(params);

    //////////////////////////////////////////////
    // parameters that can be passed in

    // what to display when there are no results
    this.noResultsText = edges.util.getParam(
      params,
      "noResultsText",
      edges.mex._("No results to display")
    );

    this.namespace = "mex-variables-results";
  }

  // draw() {
  //   var frag = this.noResultsText;
  //   if (this.component.results === false) {
  //     frag = "";
  //   }

  //   var results = this.component.results;
  //   if (results && results.length > 0) {
  //     // list the css classes we'll require
  //     var recordClasses = edges.util.styleClasses(
  //       this.namespace,
  //       "record",
  //       this.component.id
  //     );

  //     // now call the result renderer on each result to build the records
  //     frag = "";
  //     for (var i = 0; i < results.length; i++) {
  //       var rec = this._renderResult(results[i]);
  //       frag += `${rec}`;
  //     }
  //   }

  //   // finally stick it all together into the table container
  //   var containerClasses = edges.util.styleClasses(
  //     this.namespace,
  //     "container",
  //     this.component.id
  //   );
  //   var container = `<table class="${containerClasses} ui celled table">
  //                       <thead>
  //                           <tr>
  //                               <th>${edges.mex._("Variables")}</th>
  //                               <th>${edges.mex._("Data Source")}</th>
  //                               <th>${edges.mex._("Variable Group")}</th>
  //                               <th>${edges.mex._("Data Type")}</th>
  //                           </tr>
  //                       </thead>
  //                       <tbody>
  //                           ${frag}
  //                       </tbody>
  //                   </table>
  //                   <br/><br/>`;

  //   this.component.context.html(container);

  //   let selectSelector = edges.util.jsClassSelector(
  //     this.namespace,
  //     "select",
  //     this.component.id
  //   );

  //   edges.on(selectSelector, "click", this, "toggleRow");
  // }

  // _renderResult(res) {
  //   // FIXME: this is all a bit raw, in reality some of these values have multiple options
  //   let label = edges.util.escapeHtml(
  //     this._getLangVal("custom_fields.mex:label", res, "No label")
  //   );
  //   let resource = edges.util.escapeHtml(
  //     this._getLangVal("custom_fields.index:enUsedInResource", res)
  //   );
  //   let group = edges.util.escapeHtml(
  //     this._getLangVal("custom_fields.index:belongsToLabel", res)
  //   );
  //   let dataType = edges.util.escapeHtml(
  //     this._getLangVal("custom_fields.mex:dataType", res, "Unknown")
  //   );

  //   let selectClass = edges.util.jsClasses(
  //     this.namespace,
  //     "select",
  //     this.component.id
  //   );

  //   // let frag = `<tr>
  //   //         <td>${label}</td>
  //   //         <td>${resource}</td>
  //   //         <td>${group}</td>
  //   //         <td>${dataType}</td>
  //   //     </tr>`;
  //   // return frag;

  //   // each row will have a "summary row" and a hidden "details row"
  //   let frag = `
  //     <tr class="${selectClass}'>
  //       <span class="variable-summary" >
  //          <td>${label}</td>
  //       <td>${resource}</td>
  //       <td>${group}</td>
  //       <td>${dataType}</td>
  //       </span>
  //       <span class="variable-details">
  //       <td colspan="4">
  //           <div class="details-card">
  //               <h4>${label}</h4>
  //               <p><strong>Data Source:</strong> ${resource}</p>
  //               <p><strong>Variable Group:</strong> ${group}</p>
  //               <p><strong>Data type:</strong> ${dataType}</p>

  //           </div>
  //       </td>
  //   </span>
  //     </tr>
  // `;
  //   return frag;
  // }

  draw() {
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

    let containerClasses = edges.util.allClasses(
      this.namespace,
      "container",
      this.component.id
    );

    let expandAllClass = edges.util.jsClasses(
      this.namespace,
      "expand-all",
      this.component.id
    );

    // Expand/Collapse all button
    var expandAllBtn = `
        <div class="expand-toggle" style="margin-bottom: 1rem; display:flex; gap:0.5rem;">
          <button class="ui small button ${expandAllClass}" data-action="collapse">
            ${edges.mex._("Collapse all")}
          </button>
          <button class="ui small button ${expandAllClass}" data-action="expand">
            ${edges.mex._("Expand all")}
          </button>
        </div>
    `;

    // Main table
    var container = `
        ${expandAllBtn}
        <table class="${containerClasses} ui celled table" style="border: none;">
          <thead>
            <tr>
              <th style="border:none; font-weight:600">${edges.mex._(
                "Variables"
              )}</th>
              <th style="border:none; font-weight:600">${edges.mex._(
                "Data Source"
              )}</th>
              <th style="border:none; font-weight:600">${edges.mex._(
                "Variable Group"
              )}</th>
              <th style="border:none; font-weight:600">${edges.mex._(
                "Data Type"
              )}</th>
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
    let collapsedViewSelector = edges.util.jsClassSelector(
      this.namespace,
      "collapsed-view",
      this.component.id
    );
    edges.on(collapsedViewSelector, "click", this, "showExpanded");

    let expandedViewSelector = edges.util.jsClassSelector(
      this.namespace,
      "expanded-view",
      this.component.id
    );
    edges.on(expandedViewSelector, "click", this, "hideExpanded");

    let expandAllSelector = edges.util.jsClassSelector(
      this.namespace,
      "expand-all",
      this.component.id
    );
    edges.on(expandAllSelector, "click", this, "toggleExpandAll");
  }

  _renderResult(res) {
    // get fields (escaped)
    let label = edges.util.escapeHtml(
      this._getLangVal(edges.mex.constants.LABEL_CONTAINER, res, "No label")
    );

    let langPrefix = edges.mex.state.lang;
        let rpath = langPrefix === "en" ? edges.mex.constants.USED_IN_EN : edges.mex.constants.USED_IN_DE;
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

    let groups = edges.util.pathValue(edges.mex.constants.BELONGS_TO_LABEL, res, []);
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
        edges.mex._("Unknown")
      )
    );

    let desc = edges.util.escapeHtml(
      this._getLangVal(edges.mex.constants.DESCRIPTION_CONTAINER, res, "")
    );

    let codingSystem = edges.util.pathValue(
      edges.mex.constants.CODING_SYSTEM,
      res,
      []
    );
    if (!Array.isArray(codingSystem)) {
      codingSystem = [codingSystem];
    }
    let codingFrag = "";
    if (codingSystem.length > 0) {
      codingFrag =
        `<ul><li>` +
        codingSystem.map((c) => edges.util.escapeHtml(c)).join("</li><li>") +
        "</li></ul>";
    }

    // let selectClass = edges.util.jsClasses(
    //     this.namespace,
    //     "select",
    //     this.component.id
    // );

    let collapsedClass = edges.util.jsClasses(
      this.namespace,
      "collapsed-view",
      this.component.id
    );

    let expandedClass = edges.util.jsClasses(
      this.namespace,
      "expanded-view",
      this.component.id
    );

    let collapsedRowIdClass = edges.util.jsClasses(
      this.namespace,
      "collapsed-row-" + res.id,
      this.component.id
    );

    let expandedRowIdClass = edges.util.jsClasses(
      this.namespace,
      "expanded-row-" + res.id,
      this.component.id
    );

    let collapsedRowClass = edges.util.jsClasses(
      this.namespace,
      "collapsed-row",
      this.component.id
    );

    let expandedRowClass = edges.util.jsClasses(
      this.namespace,
      "expanded-row",
      this.component.id
    );

    let detailFrag = edges.mex._("No additional details");
    if (desc || codingFrag) {
      let descFrag = `<p class="details-desc">${desc}</p>`;
      if (codingFrag) {
        codingFrag = `<div class="coding-system">
                      <div class="coding-title"><strong>${edges.mex._(
                        "Coding System"
                      )}</strong></div>
                      ${codingFrag}
                    </div>`;
      }
      let detailFrag = `
  <div style="border-radius:6px; padding:1rem; margin-top:0.5rem;">
    <h4 style="margin-top:0; font-weight:600;">${label}</h4>
    ${desc ? `<p style="margin:0 0 0.5rem 0;">${desc}</p>` : ""}
    <p><strong>${edges.mex._("Data Source")}:</strong> ${
        resourceFrag || "-"
      }</p>
    <p><strong>${edges.mex._("Variable Group")}:</strong> ${
        groupFrag || "-"
      }</p>
    <p><strong>${edges.mex._("Data type")}:</strong> ${dataType}</p>
    ${
      codingFrag
        ? `<div class="coding-system" style="margin-top:0.5rem;"><strong>${edges.mex._(
            "Coding System"
          )}:</strong> ${codingFrag}</div>`
        : ""
    }
  </div>
`;

      //   detailFrag = `<div class="details-extra">
      //                 ${descFrag}
      //                 ${codingFrag}
      //               </div>`;
    }

    let frag = `
            <tr class="${collapsedRowIdClass} ${collapsedRowClass} variable-row" data-label="${label}" role="row" data-id="${res.id}">
              <td class="${collapsedClass}" style="border-left: 0; border-right: 0">${label}</td>
              <td class="${collapsedClass}" style="border-left: 0; border-right: 0">${resourceFrag}</td>
              <td class="${collapsedClass}" style="border-left: 0; border-right: 0">${groupFrag}</td>
              <td class="${collapsedClass}" style="border-left: 0; border-right: 0">${dataType}</td>
            </tr>

            <tr class="${expandedRowIdClass} ${expandedRowClass} variable-row" data-label="${label}" role="row" data-id="${res.id}" style="display:none; border-bottom: 0;">
                <td class="${expandedClass}" style="border-left: 0; border-right: 0"><strong>${label}</strong></td>
                <td class="${expandedClass}" style="border-left: 0; border-right: 0"><strong>${resourceFrag}</strong></td>
                <td class="${expandedClass}" style="border-left: 0; border-right: 0"><strong>${groupFrag}</strong></td>
                <td class="${expandedClass}" style="border-left: 0; border-right: 0"><strong>${dataType}</strong></td>
            </tr>

            <tr class="${expandedRowIdClass} ${expandedRowClass} variable-row" role="row" style="display:none; border-top: 0">
              <td colspan="4" class="${expandedClass}" style="border-left: 0; border-right: 0; border-top: 0">
                  ${detailFrag}
                </div>
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
    let action = $(element).attr("data-action");
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

    if (action === "expand") {
      $ctx.find(collapsedSelector).hide();
      $ctx.find(expandedSelector).show();
    } else {
      $ctx.find(collapsedSelector).show();
      $ctx.find(expandedSelector).hide();
    }
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
    return edges.mex.getLangVal(path, res, def);
  }

  _rankedByLang(path, res) {
    return edges.mex.rankedByLang(path, res);
  }
};
