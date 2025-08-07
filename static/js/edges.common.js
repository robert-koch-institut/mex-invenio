if (!window.hasOwnProperty("edges")) { edges = {}}
if (!edges.hasOwnProperty("instances")) { edges.instances = {}}
if (!edges.hasOwnProperty("active")) { edges.active = {}}
if (!edges.hasOwnProperty("mex")) { edges.mex = {}}
if (!edges.mex.hasOwnProperty("state")) { edges.mex.state = {}}
if (!edges.mex.hasOwnProperty("babel")) { edges.mex.babel = {}}

///////////////////////////////////////////////////
// State management
edges.mex.state.lang = "en";

///////////////////////////////////////////////////
// General Functions

edges.mex.countFormat = edges.util.numFormat({
    thousandsSeparator: ","
});

edges.mex.fullDateFormatter = function(datestr) {
    let date = new Date(datestr);
    return date.toLocaleString('default', {day: 'numeric', month: 'long', year: 'numeric', timeZone: "UTC"});
}

edges.mex.yearFormatter = function(val) {
    let date = new Date(parseInt(val));
    return date.toLocaleString('default', { year: 'numeric', timeZone: "UTC" });
}

edges.mex.monthFormatter = function(val) {
    let date = new Date(parseInt(val));
    return date.toLocaleString('default', { month: 'long', year: 'numeric', timeZone: "UTC" });
}

edges.mex._register = [];
edges.mex._keymode = true;
edges.mex._ = function(key) {
    if (!edges.mex._register.includes(key)) {
        edges.mex._register.push(key);
    }
    if (edges.mex._keymode === false) {
        if (key in edges.mex.babel) {
            return edges.mex.babel[key];
        }
        return key
    } else {
        let val = key;
        if (key in edges.mex.babel) {
            val = `*${val}*`;
        } else {
            val = `~~${val}~~`;
        }
        return val;
    }
}
edges.mex._jinja_babel = function() {
    let temp = "";
    for (let r in edges.mex._register) {
        temp += `"${edges.mex._register[r]}": "{{ _("${edges.mex._register[r]}") }}",\n`;
    }
}

edges.mex.getLangVal = function(path, res, def) {
    let preferred = ""
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
}

edges.mex.getAllLangVals = function(path, res) {
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
}

edges.mex.rankedByLang = function(path, res) {
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
}

edges.mex.refiningAndFacet = function(params) {
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
            open : true,
            controls : false,
            togglable : false,
            hideIfEmpty : true,
            title: params.title,
            countFormat: edges.mex.countFormat,
        })
    })
}

edges.mex.dateHistogram = function(params) {
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
        sortFunction : function(values) {
            values.reverse();
            return values;
        },
        renderer: new edges.mex.renderers.DateHistogramSelector({
            title: params.title || edges.mex._("Date Histogram"),
            open : true,
            togglable : false,
            countFormat: edges.mex.countFormat,
        })
    })
}

edges.mex.fullSearchController = function(params) {
    return new edges.components.FullSearchController({
        id: params.id || "search_controller",
        category: params.category || "full",
        sortOptions: params.sortOptions || [],
        fieldOptions: params.fieldOptions || [],
        renderer: new edges.mex.renderers.SidebarSearchController({
            searchButton: true,
            clearButton : false,
            searchPlaceholder: params.searchPlaceholder || edges.mex._("Search..."),
            searchButtonText: params.searchButtonText || edges.mex._("Search"),
            freetextSubmitDelay: params.freetextSubmitDelay || -1
        })
    });
}

edges.mex.pager = function(params) {
    return new edges.components.Pager({
        id: params.id || "pager",
        category: params.category || "middle",
        renderer: new edges.mex.renderers.Pager({
            showSizeSelector : false
        })
    })
}

edges.mex.pagerSelector = function(params) {
    return new edges.components.Pager({
        id: params.id || "pager-selector",
        category: params.category || "middle",
        renderer: new edges.mex.renderers.Pager({
            showSizeSelector : true,
            sizePrefix : "Show",
            sizeSuffix : "results per page",
            showPageNavigation : false,
            showRecordCount : false,
            customClassForSizeSelector : "page-size-selector"
        })
    })
}

edges.mex.previewer = function(params) {
    return new edges.mex.components.Previewer({
        id: params.id || "previewer",
        category: params.category || "right",
        renderer: new edges.mex.renderers.RecordPreview({

        })
    })
}

edges.mex.recordSelector = function(params) {
    return new edges.mex.components.Selector({
        id: params.id || "selector",
        category: params.category || "right",
        renderer: new edges.mex.renderers.SelectedRecords({
            title : "Variables Query Filters"
        })
    })
}

edges.mex.makeEdge = function (params) {
    let current_domain = document.location.host;
    let current_scheme = window.location.protocol;
    let selector = params.selector || "#edge-container";
    let search_url = current_scheme + "//" + current_domain + "/query/api/" + params.resourceType;

    return new edges.Edge({
        selector: selector,
        openingQuery : new es.Query({size: 50}),
        template: new edges.mex.templates.MainSearchTemplate(),
        searchUrl: search_url,
        components: params.components
    });
}

////////////////////////////////////////////////////
// Specific functions for generating field-specific widgets

// Resources
edges.mex.resourceDisplay = function(params) {
    if (!params) {
        params = {};
    }
    return new edges.components.ResultsDisplay({
        id: params.id || "results",
        category: params.category || "middle",
        renderer: new edges.mex.renderers.ResourcesResults({
            noResultsText: params.noResultsText || edges.mex._("No resources found.")
        })
    })
}

edges.mex.resourcePreview = function() {
    return edges.mex.previewer({});
}

edges.mex.resourceSelector = function() {
    return edges.mex.recordSelector({});
}
/////////////

// Activities
edges.mex.activitiesDisplay = function(params) {
    if (!params) {
        params = {};
    }
    return new edges.components.ResultsDisplay({
        id: params.id || "results",
        category: params.category || "middle",
        renderer: new edges.mex.renderers.ActivitiesResults({
            noResultsText: params.noResultsText || edges.mex._("No activities found.")
        })
    })
}

edges.mex.activityPreview = function() {
    return edges.mex.previewer({});
}

///////////

// Bibliographic Resources
edges.mex.bibliographicResourcesDisplay = function(params) {
    if (!params) {
        params = {};
    }
    return new edges.components.ResultsDisplay({
        id: params.id || "results",
        category: params.category || "middle",
        renderer: new edges.mex.renderers.BibliographicResourcesResults({
            noResultsText: params.noResultsText || edges.mex._("No bibliographic resources found.")
        })
    })
}

edges.mex.bibliographicResourcesPreview = function() {
    return edges.mex.previewer({});
}

///////////


edges.mex.accessRestrictionFacet = function() {
    return edges.mex.refiningAndFacet({
        id: "access_restriction",
        field: "custom_fields.mex:accessRestriction.keyword",
        title: edges.mex._("Access Restriction"),
        valueFunction: edges.mex.vocabularyLookup,
        category: "left"
    });
}

edges.mex.createdFacet = function() {
    return edges.mex.dateHistogram({
        id: "created",
        field: "created",
        title: edges.mex._("Created"),
        category: "left",
        interval: "month",
    })
}

edges.mex.endFacet = function() {
    return edges.mex.dateHistogram({
        id: "end",
        field: "custom_fields.mex:end.date_range",
        title: edges.mex._("Activity End"),
        category: "left",
        interval: "year",
    })
}

edges.mex.startFacet = function() {
    return edges.mex.dateHistogram({
        id: "start",
        field: "custom_fields.mex:start.date_range",
        title: edges.mex._("Activity Start"),
        category: "left",
        interval: "year",
    })
}

edges.mex.publicationYearFacet = function() {
    return edges.mex.dateHistogram({
        id: "publication_year",
        field: "custom_fields.mex:publicationYear.date_range",
        title: edges.mex._("Publication Year"),
        category: "left",
        interval: "year",
    })
}


edges.mex.journalFacet = function() {
    return edges.mex.refiningAndFacet({
        id: "journal",
        field: "custom_fields.mex:journal.value.keyword",
        title: edges.mex._("Journal"),
        category: "left"
    });
}

edges.mex.keywordFacet = function() {
    return edges.mex.refiningAndFacet({
        id: "keyword",
        field: "custom_fields.mex:keyword.value.keyword",
        title: edges.mex._("Keyword"),
        size: 5,
        category: "left"
    });
}

edges.mex.activityTypeFacet = function() {
    return edges.mex.refiningAndFacet({
        id: "activity_type",
        field: "custom_fields.mex:activityType.keyword",
        title: edges.mex._("Activity Type"),
        category: "left",
        valueFunction: edges.mex.vocabularyLookup,
    });
}

edges.mex.funderOrCommissionerFacet = function() {
    let field = "custom_fields.index:deFunderOrCommissioners.keyword";
    if (edges.mex.state.lang === "en") {
        field = "custom_fields.index:enFunderOrCommissioners.keyword";
    }
    return edges.mex.refiningAndFacet({
        id: "funder_or_commissioner",
        field: field,
        title: edges.mex._("Funder or Commissioner"),
        category: "left"
    });
}

edges.mex.themeFacet = function() {
    return edges.mex.refiningAndFacet({
        id: "theme",
        field: "custom_fields.mex:theme.keyword",
        title: edges.mex._("Theme"),
        category: "left",
        valueFunction: edges.mex.vocabularyLookup,
    });
}

edges.mex.hasPersonalDataFacet = function() {
    return edges.mex.refiningAndFacet({
        id: "has_personal_data",
        field: "custom_fields.mex:hasPersonalData.keyword",
        title: edges.mex._("Has Personal Data"),
        category: "left",
        valueFunction: edges.mex.vocabularyLookup,
    });
}

edges.mex.resourceCreationMethodFacet = function() {
    return edges.mex.refiningAndFacet({
        id: "resource_creation_method",
        field: "custom_fields.mex:resourceCreationMethod.keyword",
        title: edges.mex._("Resource Creation Method"),
        category: "left",
        valueFunction: edges.mex.vocabularyLookup,
    });
}

edges.mex.defaultPager = function() {
    return edges.mex.pager({})
}

edges.mex.bottomPager = function() {
    return edges.mex.pagerSelector({})
}

/////////////////////////////////////////
// Vocabulary lookup

edges.mex.VOCABULARY = {}

edges.mex.vocabularyLookup = function(value) {
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
}

/////////////////////////////////////////
// Template(s)

if (!edges.mex.hasOwnProperty("templates")) { edges.mex.templates = {}}

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
        let rightContainerStyle = "display:none;"
        let rightClass = edges.util.styleClasses(this.namespace, "right");
        let rightContainers = "";
        if (right.length > 0) {
            for (let i = 0; i < right.length; i++) {
                if(right[i].length > 0) {
                    rightContainerStyle = 'display:""'
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


        let verticalTabClass = edges.util.jsClasses(this.namespace, "verticalTab", "");

        let frag = `
            <div class="ui grid container">
                <div class="sixteen wide column">
                    ${fullContainers}
                </div>
                <div class="three wide column">
                    ${facetContainers}
                </div>
                <div class="wide column" style="flex: 1;">
                    ${middleContainers}
                </div>
                <div id="right-col" class="five wide column" style=${rightContainerStyle}>
                    ${rightContainers}
                </div>
                 <div id="vertical-tab" class="vertical-tab ${verticalTabClass}">
                </div>
            </div>
        `;

        edge.context.html(frag);

        let verticalTabSelector = edges.util.jsClassSelector(this.namespace, "verticalTab", "");
        edges.on(verticalTabSelector, "click", this, "showTabContent");
    }

    showTabContent(){
        let doc = document.getElementById("right-col")
        if(doc) {
            doc.style.display = ""
        }
    }
}

//////////////////////////////////////////////
// Components
if (!edges.mex.hasOwnProperty("components")) { edges.mex.components = {}}

edges.mex.components.Previewer = class extends edges.Component {
    constructor(params) {
        super(params);

        this.currentPreview = null;

        this.fields = [
            { field: "mex:title", name: edges.mex._("Title"), lang: true, valueFunction: null },
            { field: "mex:abstract", name: edges.mex._("Abstract"), lang: true, valueFunction: null },
            { field: "mex:accessPlatform", name: edges.mex._("Access Platform"), lang: false, valueFunction: null },
            { field: "mex:accessRestriction", name: edges.mex._("Access Restriction"), lang: false, valueFunction: null },
            { field: "mex:accessService", name: edges.mex._("Access Service"), lang: false, valueFunction: null },
            { field: "mex:accessURL.url", name: edges.mex._("Access URL"), lang: false, valueFunction: null },
            { field: "mex:accrualPeriodicity", name: edges.mex._("Accrual Periodicity"), lang: false, valueFunction: null },
            { field: "mex:affiliation", name: edges.mex._("Affiliation"), lang: false, valueFunction: null },
            { field: "mex:alternateIdentifier", name: edges.mex._("Alternate Identifier"), lang: false, valueFunction: null },
            { field: "mex:alternativeTitle", name: edges.mex._("Alternative Title"), lang: true, valueFunction: null },
            { field: "mex:anonymizationPseudonymization", name: edges.mex._("Anonymization/Pseudonymization"), lang: false, valueFunction: null },
            { field: "mex:belongsTo", name: edges.mex._("Belongs To"), lang: false, valueFunction: null },
            { field: "mex:bibliographicResourceType", name: edges.mex._("Bibliographic Resource Type"), lang: false, valueFunction: null },
            { field: "mex:codingSystem", name: edges.mex._("Coding System"), lang: false, valueFunction: null },
            { field: "mex:conformsTo", name: edges.mex._("Conforms To"), lang: false, valueFunction: null },
            { field: "mex:contact", name: edges.mex._("Contact"), lang: false, valueFunction: null },
            { field: "mex:containedBy", name: edges.mex._("Contained By"), lang: false, valueFunction: null },
            { field: "mex:contributingUnit", name: edges.mex._("Contributing Unit"), lang: false, valueFunction: null },
            { field: "mex:contributor", name: edges.mex._("Contributor"), lang: false, valueFunction: null },
            { field: "mex:created", name: edges.mex._("Created"), lang: false, valueFunction: null },
            { field: "mex:creator", name: edges.mex._("Creator"), lang: false, valueFunction: null },
            { field: "mex:dataType", name: edges.mex._("Data Type"), lang: false, valueFunction: null },
            { field: "mex:description", name: edges.mex._("Description"), lang: true, valueFunction: null },
            { field: "mex:distribution", name: edges.mex._("Distribution"), lang: false, valueFunction: null },
            { field: "mex:documentation.url", name: edges.mex._("URL"), lang: false, valueFunction: null },
            { field: "mex:doi", name: edges.mex._("DOI"), lang: false, valueFunction: null },
            { field: "mex:downloadURL", name: edges.mex._("Download URL"), lang: false, valueFunction: null },
            { field: "mex:edition", name: edges.mex._("Edition"), lang: false, valueFunction: null },
            { field: "mex:editor", name: edges.mex._("Editor"), lang: false, valueFunction: null },
            { field: "mex:editorOfSeries", name: edges.mex._("Editor of Series"), lang: false, valueFunction: null },
            { field: "mex:email", name: edges.mex._("Email"), lang: false, valueFunction: null },
            { field: "mex:end.date", name: edges.mex._("End"), lang: false, valueFunction: null },
            { field: "mex:endpointDescription", name: edges.mex._("Endpoint Description"), lang: false, valueFunction: null },
            { field: "mex:endpointType", name: edges.mex._("Endpoint Type"), lang: false, valueFunction: null },
            { field: "mex:endpointURL", name: edges.mex._("Endpoint URL"), lang: false, valueFunction: null },
            { field: "mex:externalAssociate", name: edges.mex._("External Associate"), lang: false, valueFunction: null },
            { field: "mex:externalPartner", name: edges.mex._("External Partner"), lang: false, valueFunction: null },
            { field: "mex:familyName", name: edges.mex._("Family Name"), lang: false, valueFunction: null },
            { field: "mex:fullName", name: edges.mex._("Full Name"), lang: false, valueFunction: null },
            { field: "mex:funderOrCommissioner", name: edges.mex._("Funder or Commissioner"), lang: false, valueFunction: null },
            { field: "mex:fundingProgram", name: edges.mex._("Funding Program"), lang: false, valueFunction: null },
            { field: "mex:geprisId", name: edges.mex._("Gepris ID"), lang: false, valueFunction: null },
            { field: "mex:givenName", name: edges.mex._("Given Name"), lang: false, valueFunction: null },
            { field: "mex:gndId", name: edges.mex._("GND ID"), lang: false, valueFunction: null },
            { field: "mex:hasLegalBasis", name: edges.mex._("Has Legal Basis"), lang: true, valueFunction: null },
            { field: "mex:hasPersonalData", name: edges.mex._("Has Personal Data"), lang: false, valueFunction: null },
            { field: "mex:icd10code", name: edges.mex._("ICD10 Code"), lang: false, valueFunction: null },
            { field: "mex:identifier", name: edges.mex._("MEX Identifier"), lang: false, valueFunction: null },
            { field: "mex:instrumentToolOrApparatus", name: edges.mex._("Instrument/Tool/Aparatus"), lang: true, valueFunction: null },
            { field: "mex:involvedPerson", name: edges.mex._("Involved Person"), lang: false, valueFunction: null },
            { field: "mex:involvedUnit", name: edges.mex._("Involved Unit"), lang: false, valueFunction: null },
            { field: "mex:isPartOf", name: edges.mex._("Is Part Of"), lang: false, valueFunction: null },
            { field: "mex:isPartOfActivity", name: edges.mex._("Is Part Of Activity"), lang: false, valueFunction: null },
            { field: "mex:isbnIssn", name: edges.mex._("ISBN/ISSN"), lang: false, valueFunction: null },
            { field: "mex:isniId", name: edges.mex._("ISNI"), lang: false, valueFunction: null },
            { field: "mex:issue", name: edges.mex._("Issue"), lang: false, valueFunction: null },
            { field: "mex:issued", name: edges.mex._("Issued"), lang: false, valueFunction: null },
            { field: "mex:journal", name: edges.mex._("Journal"), lang: true, valueFunction: null },
            { field: "mex:keyword", name: edges.mex._("Keyword"), lang: true, valueFunction: null },
            { field: "mex:label", name: edges.mex._("Label"), lang: true, valueFunction: null },
        ]
    }

    setPreviewRecord(previewRecord) {
        this.currentPreview = previewRecord;
    }

    showPreview(previewRecord) {
        this.setPreviewRecord(previewRecord);
        this.draw();
    }
}

edges.mex.components.Selector = class extends edges.Component {
    constructor(params) {
        super(params);

        this._selection = {};

        let ids = window.localStorage.getItem("selection")
        ids = JSON.parse(ids);
        if (ids) {
            for (let id of ids) {
                let object = window.localStorage.getItem(id);
                if (object) {
                    object = JSON.parse(object);
                    this._selection[id] = object;
                }
            }
        }
    }

    ////////////////////////////////////////
    // pure data access functions

    get length() {
        return this.ids().length;
    }

    get(id) {
        return this._selection[id];
    }

    set(id, data) {
        this._selection[id] = data;
        window.localStorage.setItem(id, JSON.stringify(data))
        window.localStorage.setItem("selection", JSON.stringify(this.ids()));
    }

    delete(id) {
        delete this._selection[id];
        window.localStorage.removeItem(id);
        window.localStorage.setItem("selection", JSON.stringify(this.ids()));
    }

    clearAll() {
        for (let id in this._selection) {
            window.localStorage.removeItem(id)
        }
        this._selection = {}
        window.localStorage.removeItem("selection")
    }

    ids() {
        return Object.keys(this._selection);
    }

    isSelected(id) {
        return this._selection.hasOwnProperty(id);
    }

    //////////////////////////////////////
    // component behavioural functions

    selectRecord(id) {
        for (let hit of this.edge.result.data.hits.hits) {
            if (id === hit._source.id) {
                this.set(id, hit._source);
                break;
            }
        }
        this.draw();
    }

    unselectRecord(id) {
        this.delete(id);
        this.draw();
    }
}

//////////////////////////////////////////////
// Renderers

if (!edges.mex.hasOwnProperty("renderers")) { edges.mex.renderers = {}}

edges.mex.renderers.SelectedRecords = class extends edges.Renderer {
    constructor(params) {
        super(params);
        this.title = edges.util.getParam(params, "title", "Selected Resources");
        this.showIfEmpty = edges.util.getParam(params, "showIfEmpty", false);
        this.namespace = "select-records"

        this.resourceComponent = null;
    }

    init(component) {
        super.init(component);
        this.resourceComponent = this.component.edge.getComponent({id: "results"})
    }

    draw() {
        if (this.component.length === 0 && this.showIfEmpty) {
            this.component.context.html(`<h2>${edges.mex._(this.title)}</h2><p>${edges.mex._("No records selected.")}</p>`);
            return;
        }

        let recordsFrag = ``;
        let selectClass = edges.util.jsClasses(this.namespace, "select", this.component.id);
        let hideClass = edges.util.jsClasses(this.namespace, "hide", this.component.id);

        for (let id of this.component.ids()) {
            let record = this.component.get(id);

            let title = edges.mex.getLangVal("custom_fields.mex:title", record, edges.mex._("No title"));
            recordsFrag += `
                <div class="selected-list">
                    <img
                        data-id="${id}"
                        class="${selectClass} controls" src="/static/images/close.svg" alt="Slide right" width="24px" height="32px"/>
                    <div>
                        <div class="selected-list-item">
                            ${title}
                        </div>
                        <!-- TODO: Create and entry point -->
                        <a class="selected-list-sub-item">
                            26 Variables
                        </a>
                    </div>
                </div>`
        }



        let frag = ""
        if(recordsFrag) {
            frag = `
                <div class="card card-shadow">

                    <div id="control-section">
                        <img class="${hideClass} controls" src="/static/images/slide-right.svg" alt="Slide right" width="16px" height="17px"/>
                    </div>

                    <div class="divider">
                    </div>

                    <h4 class="title" style="margin:0px">${edges.mex._(this.title)}</h4>
                    <div>
                        ${recordsFrag}
                    </div>
                    <a class="search-variable" href="/search/variables">
                        ${edges.mex._("See in Variables Search")}
                    </a>
                </div>
                `;

        }

        let verticalBar = document.getElementById("vertical-tab")
        if(verticalBar) {
            const length = this.component.length
            verticalBar.innerHTML = `<span> Variables Query Filters ${length > 0 ? `(${length})` : ""} </span>`;
        }

        this.component.context.html(frag);

        let selectSelector = edges.util.jsClassSelector(this.namespace, "select", this.component.id);
        let hideSelector = edges.util.jsClassSelector(this.namespace, "hide", this.component.id);
        edges.on(selectSelector, "click", this, "selectResource");
        edges.on(hideSelector, "click", this, "hideSelectedRecords");
    }

    hideSelectedRecords(){
        let doc = document.getElementById("right-col")
        if(doc) {
            doc.style.display = "none"
        }
    }


    selectResource(element) {
        let el = $(element);
        let id = el.attr("data-id");

        // Syncing this with resource result component.
        let doc = document.getElementById(`resource-list-${id}`)

        if(doc && this.resourceComponent && this.resourceComponent.renderer) {
            this.resourceComponent.renderer.selectResource(doc)
        }
    }
}

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
                let vals = edges.util.pathValue(field, this.component.currentPreview, []);
                if (vals !== "" && vals !== null && !Array.isArray(vals)) {
                    vals = [vals];
                }
            }

            if (vals.length === 0) {
                continue; // skip this field if no value
            }

            if (displayFunction) {
                vals = vals.map(val => displayFunction(val, this));
            }

            let val = vals.join(", ");

            // render the field
            fieldsFrag += `<dt>${display}</dt><dd>${val}</dd>`
        }

        let frag = `<dl>${fieldsFrag}</dl>`;
        this.component.context.html(frag);
    }
}

edges.mex.renderers.SidebarSearchController = class extends edges.Renderer {
    constructor (params) {
        super(params)

        // enable the search button
        this.searchButton = edges.util.getParam(params, "searchButton", false);

        // text to include on the search button.  If not provided, will just be the magnifying glass
        this.searchButtonText = edges.util.getParam(params, "searchButtonText", false);

        // should the clear button be rendered
        this.clearButton = edges.util.getParam(params, "clearButton", true);

        // enable sorting options
        this.enableSorting = edges.util.getParam(params, "clearButton", false)

        // set the placeholder text for the search box
        this.searchPlaceholder = edges.util.getParam(params, "searchPlaceholder", edges.mex._("Search"));

        // amount of time between finishing typing and when a query is executed from the search box
        this.freetextSubmitDelay = edges.util.getParam(params, "freetextSubmitDelay", 500);

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
            let directionClass = edges.util.allClasses(this.namespace, "direction", this);
            let sortFieldClass = edges.util.allClasses(this.namespace, "sortby", this);

            let sortOptions = "";
            for (let i = 0; i < comp.sortOptions.length; i++) {
                let field = comp.sortOptions[i].field;
                let display = comp.sortOptions[i].display;
                sortOptions += `<option value="${field}">${edges.util.escapeHtml(display)}</option>`;
            }

            // sortFrag = `<div class="ui form">
            //     <div class="fields">
            //         <!-- Commenting as of now
            //         <div class="field">
            //             <button type="button" class="ui button ${directionClass}" title="" href="#"></button>
            //         </div>
            //         -->
            //         <div class="field">
            //             <select class="ui fluid dropdown ${sortFieldClass}">
            //                 <option value="_score">${edges.mex._("Relevance")}</option>
            //                 ${sortOptions}
            //             </select>
            //         </div>
            //     </div>`;
            sortFrag = `<div class="ui form">
                <div class="field">
                    <select class="ui fluid dropdown ${sortFieldClass}">
                        <option value="_score">${edges.mex._("Relevance")}</option>
                        ${sortOptions}
                    </select>
                </div>
            </div>`;
        }

        // select box for fields to search on
        let field_select = "";
        if (comp.fieldOptions && comp.fieldOptions.length > 0) {
            // classes that we'll use
            let searchFieldClass = edges.util.allClasses(this.namespace, "field", this);

            let fieldOptions = "";
            for (let i = 0; i < comp.fieldOptions.length; i++) {
                let obj = comp.fieldOptions[i];
                fieldOptions += `<option value="${obj['field']}">${edges.util.escapeHtml(obj['display'])}</option>`;
            }

            field_select += `<select class="${searchFieldClass}">
                                <option value="">${edges.mex._("search all")}</option>
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
                <button type="button" class="ui button ${resetClass}" title="${edges.mex._("Clear all search and sort parameters and start again")}">
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
            searchFrag = `<div class="field"><button type="button" class="button ${searchClass} search-button">${text}</button></div>`;
        }

        let searchBox = `
            <div class="ui form" style="display: flex;">
                ${clearFrag}

                <div class="field">
                    ${field_select}
                </div>

                <div class="field" style="flex-grow: 1;">
                    <input type="text" id="${textId}" class="ui input ${textClass}" name="q" placeholder="${this.searchPlaceholder}" style="width: 100%;" />
                </div>
            </div>`;

        // assemble the final fragment and render it into the component's context
        let containerClass = edges.util.styleClasses(this.namespace, "container", this);
        // let frag = `
        //     <div class="${containerClass}">
        //         <div class="row">
        //             <div>${searchBox}</div>
        //             <div>${sortFrag}</div>
        //             <div>${searchFrag}</div>
        //         </div>
        //     </div>`;

        // Upgrading the search UI as per sematic ui
        let frag = `
    <div class="ui grid ${containerClass}">
        <div class="row middle aligned">
            <div class="search-label">
                <label><h3>Search</h3></label>
            </div>
            <div class="eleven wide column">
                ${searchBox}
            </div>
            <div class="three wide column">
                ${sortFrag}
            </div>
            <div class="one wide column">
                ${searchFrag}
            </div>
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
            let directionSelector = edges.util.jsClassSelector(this.namespace, "direction", this);
            let sortSelector = edges.util.jsClassSelector(this.namespace, "sortby", this);
            edges.on(directionSelector, "click", this, "changeSortDir");
            edges.on(sortSelector, "change", this, "changeSortBy");
        }
        if (comp.fieldOptions && comp.fieldOptions.length > 0) {
            let fieldSelector = edges.util.jsClassSelector(this.namespace, "field", this);
            edges.on(fieldSelector, "change", this, "changeSearchField");
        }
        let textSelector = edges.util.jsClassSelector(this.namespace, "text", this);
        if (this.freetextSubmitDelay > -1) {
            edges.on(textSelector, "keyup", this, "setSearchText", this.freetextSubmitDelay);
        } else {
            function onlyEnter(event) {
                let code = (event.keyCode ? event.keyCode : event.which);
                return code === 13;
            }

            edges.on(textSelector, "keyup", this, "setSearchText", false, onlyEnter);
        }

        let resetSelector = edges.util.jsClassSelector(this.namespace, "reset", this);
        edges.on(resetSelector, "click", this, "clearSearch");

        let searchSelector = edges.util.jsClassSelector(this.namespace, "search", this);
        edges.on(searchSelector, "click", this, "doSearch");

        if (this.shareLink) {
            let shareSelector = edges.util.jsClassSelector(this.namespace, "toggle-share", this);
            edges.on(shareSelector, "click", this, "toggleShare");

            let closeShareSelector = edges.util.jsClassSelector(this.namespace, "close-share", this);
            edges.on(closeShareSelector, "click", this, "toggleShare");

            if (this.component.urlShortener) {
                let shortenSelector = edges.util.jsClassSelector(this.namespace, "shorten", this);
                edges.on(shortenSelector, "click", this, "toggleShorten");
            }
        }
    }

    ///////////////////////////////////////a///////////////
    // functions for setting UI values

    setUISortDir() {
        // get the selector we need
        let directionSelector = edges.util.jsClassSelector(this.namespace, "direction", this);
        let el = this.component.jq(directionSelector);
        if (this.component.sortDir === 'asc') {
            el.html(`<i class="icon sort up"></i> ${edges.mex._("sort by")}`);
            el.attr('title', edges.mex._('Current order ascending. Click to change to descending'));
        } else {
            el.html(`<i class="icon sort down"></i> ${edges.mex._("sort by")}`);
            el.attr('title', edges.mex._('Current order descending. Click to change to ascending'));
        }
    }

    setUISortField() {
        if (!this.component.sortBy) {
            return;
        }
        // get the selector we need
        let sortSelector = edges.util.jsClassSelector(this.namespace, "sortby", this);
        let el = this.component.jq(sortSelector);
        el.val(this.component.sortBy);
    }

    setUISearchField() {
        if (!this.component.searchField) {
            return;
        }
        // get the selector we need
        let fieldSelector = edges.util.jsClassSelector(this.namespace, "field", this);
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
    }

    changeSortBy = function (element) {
        let val = this.component.jq(element).val();
        this.component.setSortBy(val);
    }

    changeSearchField = function (element) {
        let val = this.component.jq(element).val();
        this.component.setSearchField(val);
    }

    setSearchText = function (element) {
        let val = this.component.jq(element).val();
        this.component.setSearchText(val);
    }

    clearSearch = function (element) {
        this.component.clearSearch();
    }

    doSearch = function (element) {
        let textId = edges.util.idSelector(this.namespace, "text", this);
        let text = this.component.jq(textId).val();
        this.component.setSearchText(text);
    }
}


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
        this.sortCycle = edges.util.getParam(params, "sortCycle", ["count desc", "count asc", "term desc", "term asc"]);

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

        let valClass = edges.util.allClasses(this.namespace, "value", this.component.id);
        let filterRemoveClass = edges.util.allClasses(this.namespace, "filter-remove", this.component.id);

        let resultsListClass = edges.util.styleClasses(this.namespace, "results-list", this.component.id);
        let resultClass = edges.util.styleClasses(this.namespace, "result", this.component.id);
        let controlClass = edges.util.styleClasses(this.namespace, "controls", this.component.id);
        let facetClass = edges.util.styleClasses(this.namespace, "facet", this.component.id);
        let headerClass = edges.util.styleClasses(this.namespace, "header", this.component.id);
        let selectedClass = edges.util.styleClasses(this.namespace, "selected", this.component.id);

        let controlId = edges.util.htmlID(this.namespace, "controls", this.component.id);
        let sizeId = edges.util.htmlID(this.namespace, "size", this.component.id);
        let orderId = edges.util.htmlID(this.namespace, "order", this.component.id);
        let toggleId = edges.util.htmlID(this.namespace, "toggle", this.component.id);
        let resultsId = edges.util.htmlID(this.namespace, "results", this.component.id);

        let showFacet = ts.values && ts.values.length > 0;
        if (!showFacet && this.hideIfEmpty) {
            ts.context.html("");
            return;
        }

        let results = showFacet ? "" : edges.mex._("No data available");
        let filterTerms = ts.filters.map(f => f.term.toString());

        if (showFacet) {
            // Optional checkbox "Select All / Deselect All" buttons
            if (this.useCheckboxes) {
                results += `
                    <div class="ui mini buttons" style="margin-bottom: 10px;">
                        <button class="ui button" id="select-all-${ts.id}">Select All</button>
                        <button class="ui button" id="deselect-all-${ts.id}">Deselect All</button>
                    </div>`;
            }

            for (let val of ts.values) {
                if (filterTerms.includes(val.term.toString())) continue;

                let count = this.countFormat ? this.countFormat(val.count) : val.count;
                let escapedTerm = edges.util.escapeHtml(val.term);
                let escapedDisplay = edges.util.escapeHtml(val.display);

                if (this.useCheckboxes) {
                    results += `
                        <div class="${resultClass}">
                            <div class="ui checkbox">
                                <input type="checkbox" class="${valClass}" data-key="${escapedTerm}" />
                                <label>${escapedDisplay} (${count})</label>
                            </div>
                        </div>`;
                } else {
                    results += `
                        <div class="${resultClass}">
                            <a href="#" class="${valClass}" data-key="${escapedTerm}">${escapedDisplay}</a> (${count})
                        </div>`;
                }
            }
        }

        // Tooltip
        let tooltipFrag = "";
        if (this.tooltipText) {
            let tooltipClass = edges.util.styleClasses(this.namespace, "tooltip", this.component.id);
            let tooltipId = edges.util.htmlID(this.namespace, "tooltip", this.component.id);
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
                            <a href="#" class="${filterRemoveClass}" data-key="${edges.util.escapeHtml(filt.term)}">
                                <i class="delete icon"></i>
                            </a>
                        </strong>
                    </div>`;
            }
        }

        // Header toggle
        let tog = `<h4> ${this.title} </h4>`;
        if (this.togglable) {
            tog = `<a href="#" id="${toggleId}"><i class="plus icon"></i>&nbsp;${this.title}</a>`;
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
        let valueSelector = edges.util.jsClassSelector(this.namespace, "value", this.component.id);
        let filterRemoveSelector = edges.util.jsClassSelector(this.namespace, "filter-remove", this);
        let toggleSelector = edges.util.idSelector(this.namespace, "toggle", this);
        let sizeSelector = edges.util.idSelector(this.namespace, "size", this.component.id);
        let orderSelector = edges.util.idSelector(this.namespace, "order", this.component.id);
        let tooltipSelector = edges.util.idSelector(this.namespace, "tooltip-toggle", this.component.id);

        edges.on(valueSelector, "click", this, "termSelected");
        edges.on(toggleSelector, "click", this, "toggleOpen");
        edges.on(filterRemoveSelector, "click", this, "removeFilter");
        edges.on(sizeSelector, "click", this, "changeSize");
        edges.on(orderSelector, "click", this, "changeSort");
        edges.on(tooltipSelector, "click", this, "toggleTooltip");

        // Checkbox controls
        if (this.useCheckboxes) {
            const selector = `#${resultsId} .${valClass.replace(/\s+/g, '.')} input[type=checkbox]`;
            $(`#select-all-${ts.id}`).on("click", () => {
                $(selector).prop("checked", true);
            });
            $(`#deselect-all-${ts.id}`).on("click", () => {
                $(selector).prop("checked", false);
            });
        }
    }

    // draw() {
    //     // for convenient short references ...
    //     let ts = this.component;

    //     if (!ts.active && this.hideInactive) {
    //         ts.context.html("");
    //         return;
    //     }

    //     // classes where we need both styles and js
    //     let valClass = edges.util.allClasses(this.namespace, "value", this.component.id);
    //     let filterRemoveClass = edges.util.allClasses(this.namespace, "filter-remove", this.component.id);

    //     // sort out all the classes that we're going to be using
    //     let resultsListClass = edges.util.styleClasses(this.namespace, "results-list", this.component.id);
    //     let resultClass = edges.util.styleClasses(this.namespace, "result", this.component.id);
    //     let controlClass = edges.util.styleClasses(this.namespace, "controls", this.component.id);
    //     let facetClass = edges.util.styleClasses(this.namespace, "facet", this.component.id);
    //     let headerClass = edges.util.styleClasses(this.namespace, "header", this.component.id);
    //     let selectedClass = edges.util.styleClasses(this.namespace, "selected", this.component.id);

    //     let controlId = edges.util.htmlID(this.namespace, "controls", this.component.id);
    //     let sizeId = edges.util.htmlID(this.namespace, "size", this.component.id);
    //     let orderId = edges.util.htmlID(this.namespace, "order", this.component.id);
    //     let toggleId = edges.util.htmlID(this.namespace, "toggle", this.component.id);
    //     let resultsId = edges.util.htmlID(this.namespace, "results", this.component.id);

    //     // this is what's displayed in the body if there are no results
    //     let results = edges.mex._("Loading...");
    //     if (ts.values !== false) {
    //         results = edges.mex._("No data available");
    //     }

    //     // render a list of the values
    //     if (ts.values && ts.values.length > 0) {
    //         results = "";

    //         // get the terms of the filters that have already been set
    //         let filterTerms = [];
    //         for (let i = 0; i < ts.filters.length; i++) {
    //             filterTerms.push(ts.filters[i].term.toString());
    //         }

    //         // render each value, if it is not also a filter that has been set
    //         for (let i = 0; i < ts.values.length; i++) {
    //             let val = ts.values[i];
    //             if ($.inArray(val.term.toString(), filterTerms) === -1) {   // the toString() helps us normalise other values, such as integers
    //                 let count = val.count;
    //                 if (this.countFormat) {
    //                     count = this.countFormat(count)
    //                 }
    //                 results += `<div class="${resultClass}"><a href="#" class="${valClass}" data-key="${edges.util.escapeHtml(val.term)}">
    //                     ${edges.util.escapeHtml(val.display)}</a> (${count})</div>`;
    //             }
    //         }
    //     }

    //     // if there is a tooltip, make the frag
    //     let tooltipFrag = "";
    //     if (this.tooltipText) {
    //         let tt = this._shortTooltip();
    //         let tooltipClass = edges.util.styleClasses(this.namespace, "tooltip", this.component.id);
    //         let tooltipId = edges.util.htmlID(this.namespace, "tooltip", this.component.id);
    //         tooltipFrag = `<div id="${tooltipId}" class="${tooltipClass}" style="display:none">
    //             <div class="ui grid">
    //                 <div class="sixteen wide column">${tt}</div>
    //             </div>
    //         </div>`;
    //     }

    //     // if we want to display the controls, render them
    //     let controlFrag = "";
    //     if (this.controls) {
    //         let ordering = `<a href="#" title=""><i class="sort up icon"></i></a>`;
    //         controlFrag = `<div class="${controlClass}" style="display:none" id="${controlId}"><div class="ui grid">
    //                     <div class="sixteen wide column">
    //                         <div class="ui buttons">
    //                             <button type="button" class="ui button mini" id="${sizeId}" title="List Size" href="#">0</button>
    //                             <button type="button" class="ui button mini" id="${orderId}" title="List Order" href="#"></button>
    //                         </div>
    //                     </div>
    //                 </div></div>`;
    //     }

    //     // if we want the active filters, render them
    //     let filterFrag = "";
    //     if (ts.filters.length > 0 && this.showSelected) {
    //         for (let i = 0; i < ts.filters.length; i++) {
    //             let filt = ts.filters[i];
    //             filterFrag += `<div class="${resultClass}"><strong>${edges.util.escapeHtml(filt.display)}&nbsp;`;
    //             filterFrag += `<a href="#" class="${filterRemoveClass}" data-key="${edges.util.escapeHtml(filt.term)}">`;
    //             filterFrag += `<i class="delete icon"></i></a>`;
    //             filterFrag += `</strong></a></div>`;
    //         }
    //     }

    //     // render the toggle capability
    //     let tog = this.title;
    //     if (this.togglable) {
    //         tog = `<a href="#" id="${toggleId}"><i class="plus icon"></i>&nbsp;${this.title}</a>`;
    //     }

    //     // render the overall facet
    //     let frag = `
    //         <div class="ui segment ${facetClass}">
    //             <div class="${headerClass}"><div class="ui grid">
    //                 <div class="sixteen wide column">
    //                     ${tog}
    //                 </div>
    //             </div></div>
    //             ${tooltipFrag}
    //             ${controlFrag}
    //             <div class="ui grid" style="display:none" id="${resultsId}">
    //                 <div class="sixteen wide column">
    //                     <div class="${selectedClass}">${filterFrag}</div>
    //                     <div class="${resultsListClass}">${results}</div>
    //                 </div>
    //             </div>
    //         </div>`;

    //     // now render it into the page
    //     ts.context.html(frag);

    //     // trigger all the post-render set-up functions
    //     this.setUISize();
    //     this.setUISort();
    //     this.setUIOpen();

    //     // sort out the selectors we're going to be needing
    //     let valueSelector = edges.util.jsClassSelector(this.namespace, "value", this.component.id);
    //     let filterRemoveSelector = edges.util.jsClassSelector(this.namespace, "filter-remove", this);
    //     let toggleSelector = edges.util.idSelector(this.namespace, "toggle", this);
    //     let sizeSelector = edges.util.idSelector(this.namespace, "size", this.component.id);
    //     let orderSelector = edges.util.idSelector(this.namespace, "order", this.component.id);
    //     let tooltipSelector = edges.util.idSelector(this.namespace, "tooltip-toggle", this.component.id);

    //     // for when a value in the facet is selected
    //     edges.on(valueSelector, "click", this, "termSelected");
    //     // for when the open button is clicked
    //     edges.on(toggleSelector, "click", this, "toggleOpen");
    //     // for when a filter remove button is clicked
    //     edges.on(filterRemoveSelector, "click", this, "removeFilter");
    //     // for when a size change request is made
    //     edges.on(sizeSelector, "click", this, "changeSize");
    //     // when a sort order request is made
    //     edges.on(orderSelector, "click", this, "changeSort");
    //     // toggle the full tooltip
    //     edges.on(tooltipSelector, "click", this, "toggleTooltip");
    // };

    /////////////////////////////////////////////////////
    // UI behaviour functions

    setUIOpen() {
        // the selectors that we're going to use
        let resultsSelector = edges.util.idSelector(this.namespace, "results", this.component.id);
        let controlsSelector = edges.util.idSelector(this.namespace, "controls", this.component.id);
        let tooltipSelector = edges.util.idSelector(this.namespace, "tooltip", this.component.id);
        let toggleSelector = edges.util.idSelector(this.namespace, "toggle", this.component.id);

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
    };

    setUISize() {
        let sizeSelector = edges.util.idSelector(this.namespace, "size", this.component.id);
        this.component.jq(sizeSelector).html(this.component.size);
    };

    setUISort() {
        let orderSelector = edges.util.idSelector(this.namespace, "order", this.component.id);
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
    };

    /////////////////////////////////////////////////////
    // event handlers

    termSelected(element) {
        let term = this.component.jq(element).attr("data-key");
        this.component.selectTerm(term);
    };

    removeFilter(element) {
        let term = this.component.jq(element).attr("data-key");
        this.component.removeFilter(term);
    };

    toggleOpen(element) {
        this.open = !this.open;
        this.setUIOpen();
    };

    changeSize(element) {
        let newSize = prompt(`${edges.mex._("Currently displaying")} ${this.component.size} ${edges.mex._("results per page. How many would you like instead?")}`);
        if (newSize) {
            this.component.changeSize(parseInt(newSize));
        }
    };

    changeSort(element) {
        let current = this.component.orderBy + " " + this.component.orderDir;
        let idx = $.inArray(current, this.sortCycle);
        let next = this.sortCycle[(idx + 1) % 4];
        let bits = next.split(" ");
        this.component.changeSort(bits[0], bits[1]);
    };

    toggleTooltip(element) {
        let tooltipSpanSelector = edges.util.idSelector(this.namespace, "tooltip-span", this.component.id);
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
        let tooltipSelector = edges.util.idSelector(this.namespace, "tooltip-toggle", this.component.id);
        // refresh the event binding
        edges.on(tooltipSelector, "click", this, "toggleTooltip");
    };

    //////////////////////////////////////////////////////////
    // some useful reusable components

    _shortTooltip() {
        let tt = this.tooltipText;
        let tooltipLinkId = edges.util.htmlID(this.namespace, "tooltip-toggle", this.component.id);
        let tooltipSpan = edges.util.htmlID(this.namespace, "tooltip-span", this.component.id);
        if (this.tooltip) {
            let tooltipLinkClass = edges.util.styleClasses(this.namespace, "tooltip-link", this.component.id);
            tt = `<span id="${tooltipSpan}"><a id="${tooltipLinkId}" class="${tooltipLinkClass}" href="#">${tt}</a></span>`;
        }
        return tt;
    };

    _longTooltip = function() {
        let tt = this.tooltip;
        let tooltipLinkId = edges.util.htmlID(this.namespace, "tooltip-toggle", this.component.id);
        let tooltipLinkClass = edges.util.styleClasses(this.namespace, "tooltip-link", this.component.id);
        let tooltipSpan = edges.util.htmlID(this.namespace, "tooltip-span", this.component.id);
        tt = `<span id="${tooltipSpan}">${this.tooltip} <a id="${tooltipLinkId}" class="${tooltipLinkClass}" href="#">${edges.mex._("less")}</a></span>`;
        return tt;
    };
}


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

        this.title = edges.util.getParam(params, "title", edges.mex._("Select Date Range"));

        // a short tooltip and a fuller explanation
        this.tooltipText = edges.util.getParam(params, "tooltipText", false);
        this.tooltip = edges.util.getParam(params, "tooltip", false);

        this.tooltipState = "closed";

        // whether to suppress display of date range with no values
        this.hideEmptyDateBin = edges.util.getParam(params, "hideEmptyDateBin", true);Date

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

        let resultsListClass = edges.util.allClasses(namespace, "results-list", this);
        let resultClass = edges.util.allClasses(namespace, "result", this);
        let valClass = edges.util.allClasses(namespace, "value", this);
        let filterRemoveClass = edges.util.allClasses(namespace, "filter-remove", this);
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

            let filterTerms = ts.filters.map(f => f.display);
            let longClass = edges.util.allClasses(namespace, "long", this);
            let short = true;

            for (let i = 0; i < ts.values.length; i++) {
                let val = ts.values[i];
                let checked = filterTerms.includes(val.display) ? "checked" : "";
                let myLongClass = "";
                let styles = "";

                if (this.shortDisplay && this.shortDisplay <= i) {
                    myLongClass = longClass;
                    styles = 'style="display:none"';
                    short = false;
                }

                let count = this.countFormat ? this.countFormat(val.count) : val.count;
                let ltData = val.lt ? ` data-lt="${edges.util.escapeHtml(val.lt)}"` : "";

                results += `
                    <div class="${resultClass} ${myLongClass}" ${styles}>
                        <label style="display: flex; align-items: center; gap: 4px; cursor: pointer;">
                            <input type="checkbox" class="${valClass}" data-gte="${edges.util.escapeHtml(val.gte)}" ${ltData} ${checked}>
                            ${edges.util.escapeHtml(val.display)} (${count})
                        </label>
                    </div>`;
            }

            if (!short) {
                let showClass = edges.util.allClasses(namespace, "show-link", this);
                let showId = edges.util.htmlID(namespace, "show-link", this);
                let slToggleId = edges.util.htmlID(namespace, "sl-toggle", this);
                results += `<div class="${showClass}" id="${showId}">
                    <a href="#" id="${slToggleId}">
                        <span class="all">show all</span>
                        <span class="less" style="display:none">${edges.mex._("show less")}</span>
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
                let ltData = filt.lt ? ` data-lt="${edges.util.escapeHtml(filt.lt)}"` : "";
                filterFrag += `<div class="${resultClass}">
                    <strong>${edges.util.escapeHtml(filt.display)}&nbsp;
                        <a href="#" class="${filterRemoveClass}" data-gte="${edges.util.escapeHtml(filt.gte)}" ${ltData}>
                            <i class="icon delete"></i>
                        </a>
                    </strong>
                </div>`;
            }
        }

        let tog = `<h4> ${this.title} </h4>`;
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
        let filterRemoveSelector = edges.util.jsClassSelector(namespace, "filter-remove", this);
        let toggleSelector = edges.util.idSelector(namespace, "toggle", this);
        let tooltipSelector = edges.util.idSelector(namespace, "tooltip-toggle", this);
        let shortLongToggleSelector = edges.util.idSelector(namespace, "sl-toggle", this);

        edges.on(valueSelector, "change", this, "checkboxSelected");
        edges.on(filterRemoveSelector, "click", this, "removeFilter");
        edges.on(toggleSelector, "click", this, "toggleOpen");
        edges.on(tooltipSelector, "click", this, "toggleTooltip");
        edges.on(shortLongToggleSelector, "click", this, "toggleShortLong");
    }

    checkboxSelected(element) {
        let gte = $(element).data("gte");
        let lt = $(element).data("lt");
        let display = $(element).parent().text().trim();
        this.component.toggleFilter({
            gte: gte,
            lt: lt,
            display: display
        });
    }


    // draw() {
    //     // for convenient short references ...
    //     let ts = this.component;
    //     let namespace = this.namespace;

    //     if (!ts.active && this.hideInactive) {
    //         ts.context.html("");
    //         return;
    //     }

    //     // sort out all the classes that we're going to be using
    //     let resultsListClass = edges.util.allClasses(namespace, "results-list", this);
    //     let resultClass = edges.util.allClasses(namespace, "result", this);
    //     let valClass = edges.util.allClasses(namespace, "value", this);
    //     let filterRemoveClass = edges.util.allClasses(namespace, "filter-remove", this);
    //     let facetClass = edges.util.allClasses(namespace, "facet", this);
    //     let headerClass = edges.util.allClasses(namespace, "header", this);
    //     let selectedClass = edges.util.allClasses(namespace, "selected", this);

    //     let toggleId = edges.util.htmlID(namespace, "toggle", this);
    //     let resultsId = edges.util.htmlID(namespace, "results", this);

    //     // this is what's displayed in the body if there are no results
    //     let results = edges.mex._("Loading...");
    //     if (ts.values !== false) {
    //         results = edges.mex._("No data available");
    //     }

    //     // render a list of the values
    //     if (ts.values && ts.values.length > 0) {
    //         results = "";

    //         // get the terms of the filters that have already been set
    //         let filterTerms = [];
    //         for (let i = 0; i < ts.filters.length; i++) {
    //             filterTerms.push(ts.filters[i].display);
    //         }

    //         // render each value, if it is not also a filter that has been set
    //         let longClass = edges.util.allClasses(namespace, "long", this);
    //         let short = true;
    //         for (let i = 0; i < ts.values.length; i++) {
    //             let val = ts.values[i];
    //             if ($.inArray(val.display, filterTerms) === -1) {
    //                 let myLongClass = "";
    //                 let styles = "";
    //                 if (this.shortDisplay && this.shortDisplay <= i) {
    //                     myLongClass = longClass;
    //                     styles = 'style="display:none"';
    //                     short = false;
    //                 }

    //                 let count = val.count;
    //                 if (this.countFormat) {
    //                     count = this.countFormat(count)
    //                 }
    //                 let ltData = "";
    //                 if (val.lt) {
    //                     ltData = ' data-lt="' + edges.util.escapeHtml(val.lt) + '" ';
    //                 }
    //                 results += `<div class="${resultClass} ${myLongClass}" ${styles}><a href="#" class="${valClass}" data-gte="${edges.util.escapeHtml(val.gte)}" ${ltData}>
    //                                 ${edges.util.escapeHtml(val.display)}</a> (${count})
    //                             </div>`;

    //             }
    //         }
    //         if (!short) {
    //             let showClass = edges.util.allClasses(namespace, "show-link", this);
    //             let showId = edges.util.htmlID(namespace, "show-link", this);
    //             let slToggleId = edges.util.htmlID(namespace, "sl-toggle", this);
    //             results += `<div class="${showClass}" id="${showId}">
    //                 <a href="#" id="${slToggleId}"><span class="all">show all</span><span class="less" style="display:none">${edges.mex._("show less")}</span></a>
    //             </div>`;
    //         }

    //     }

    //     // if there is a tooltip, make the frag
    //     let tooltipFrag = "";
    //     if (this.tooltipText) {
    //         let tt = this._shortTooltip();
    //         let tooltipClass = edges.util.allClasses(namespace, "tooltip", this);
    //         let tooltipId = edges.util.htmlID(namespace, "tooltip", this);
    //         tooltipFrag = `<div id="${tooltipId}" class="${tooltipClass}" style="display:none"><div class="row"><div class="col-md-12">${tt}</div></div></div>`;
    //     }

    //     // if we want the active filters, render them
    //     let filterFrag = "";
    //     if (ts.filters.length > 0 && this.showSelected) {
    //         for (let i = 0; i < ts.filters.length; i++) {
    //             let filt = ts.filters[i];
    //             let ltData = "";
    //             if (filt.lt) {
    //                 ltData = ` data-lt="${edges.util.escapeHtml(filt.lt)}" `;
    //             }
    //             filterFrag += `<div class="${resultClass}">
    //                         <strong>${edges.util.escapeHtml(filt.display)}&nbsp;
    //                             <a href="#" class="${filterRemoveClass}" data-gte="${edges.util.escapeHtml(filt.gte)}" ${ltData}>
    //                             <i class="icon delete"></i></a>
    //                         </strong></a></div>`;
    //         }
    //     }

    //     // render the toggle capability
    //     let tog = this.title;
    //     if (this.togglable) {
    //         tog = `<a href="#" id="${toggleId}"><i class="icon plus"></i>&nbsp;${tog}</a>`;
    //     }

    //     // render the overall facet

    //     let frag = `
    //         <div class="ui segment ${facetClass}">
    //             <div class="${headerClass}"><div class="row">
    //                 <div class="col-md-12">
    //                     ${tog}
    //                 </div>
    //             </div></div>
    //             ${tooltipFrag}
    //             <div class="row" style="display:none" id="${resultsId}">
    //                 <div class="col-md-12">
    //                     <div class="${selectedClass}">${filterFrag}</div>
    //                     <div class="${resultsListClass}">${results}</div>
    //                 </div>
    //             </div>
    //         </div>`;

    //     // now render it into the page
    //     ts.context.html(frag);

    //     // trigger all the post-render set-up functions
    //     this.setUIOpen();

    //     // sort out the selectors we're going to be needing
    //     let valueSelector = edges.util.jsClassSelector(namespace, "value", this);
    //     let filterRemoveSelector = edges.util.jsClassSelector(namespace, "filter-remove", this);
    //     let toggleSelector = edges.util.idSelector(namespace, "toggle", this);
    //     let tooltipSelector = edges.util.idSelector(namespace, "tooltip-toggle", this);
    //     let shortLongToggleSelector = edges.util.idSelector(namespace, "sl-toggle", this);

    //     // for when a value in the facet is selected
    //     edges.on(valueSelector, "click", this, "termSelected");
    //     // for when the open button is clicked
    //     edges.on(toggleSelector, "click", this, "toggleOpen");
    //     // for when a filter remove button is clicked
    //     edges.on(filterRemoveSelector, "click", this, "removeFilter");
    //     // toggle the full tooltip
    //     edges.on(tooltipSelector, "click", this, "toggleTooltip");
    //     // toggle show/hide full list
    //     edges.on(shortLongToggleSelector, "click", this, "toggleShortLong");
    // }

    /////////////////////////////////////////////////////
    // UI behaviour functions

    setUIOpen() {
        // the selectors that we're going to use
        let resultsSelector = edges.util.idSelector(this.namespace, "results", this.component.id);
        let tooltipSelector = edges.util.idSelector(this.namespace, "tooltip", this);
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
        let tooltipSpanSelector = edges.util.idSelector(this.namespace, "tooltip-span", this);
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
        let tooltipSelector = edges.util.idSelector(this.namespace, "tooltip-toggle", this);
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
        let tooltipLinkId = edges.util.htmlID(this.namespace, "tooltip-toggle", this);
        let tooltipSpan = edges.util.htmlID(this.namespace, "tooltip-span", this);
        if (this.tooltip) {
            let tooltipLinkClass = edges.util.allClasses(this.namespace, "tooltip-link", this);
            tt = '<span id="' + tooltipSpan + '"><a id="' + tooltipLinkId + '" class="' + tooltipLinkClass + '" href="#">' + tt + '</a></span>'
        }
        return tt;
    }

    _longTooltip() {
        let tt = this.tooltip;
        let tooltipLinkId = edges.util.htmlID(this.namespace, "tooltip-toggle", this);
        let tooltipLinkClass = edges.util.allClasses(this.namespace, "tooltip-link", this);
        let tooltipSpan = edges.util.htmlID(this.namespace, "tooltip-span", this);
        tt = '<span id="' + tooltipSpan + '">' + this.tooltip + ' <a id="' + tooltipLinkId + '" class="' + tooltipLinkClass + '" href="#">less</a></span>';
        return tt;
    }
}


edges.mex.renderers.Pager = class extends edges.Renderer {
    constructor (params) {
        super(params);

        this.scroll = edges.util.getParam(params, "scroll", true);

        this.scrollSelector = edges.util.getParam(params, "scrollSelector", "body");

        this.showSizeSelector = edges.util.getParam(params, "showSizeSelector", true);

        this.sizeOptions = edges.util.getParam(params, "sizeOptions", [10, 25, 50, 100]);

        this.sizePrefix = edges.util.getParam(params, "sizePrefix", "");

        this.sizeSuffix = edges.util.getParam(params, "sizeSuffix", edges.mex._(" per page"));

        this.showRecordCount = edges.util.getParam(params, "showRecordCount", true);

        this.showPageNavigation = edges.util.getParam(params, "showPageNavigation", true);

        this.numberFormat = edges.util.getParam(params, "numberFormat", false);

        this.customClassForSizeSelector = edges.util.getParam(params, "customClassForSizeSelector", "");

        this.namespace = "mex-pager";
    }

    draw() {
        if (this.component.total === false || this.component.total === 0) {
            this.component.context.html("");
            return;
        }

        // classes we'll need
        let containerClass = edges.util.allClasses(this.namespace, "container", this);
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
            `
        }

        // the number of records per page
        let sizer = "";
        if (this.showSizeSelector) {
            let sizeopts = "";
            let optarr = this.sizeOptions.slice(0);
            if ($.inArray(this.component.pageSize, optarr) === -1) {
                optarr.push(this.component.pageSize)
            }
            optarr.sort(function (a, b) {
                return a - b
            });  // sort numerically
            for (let i = 0; i < optarr.length; i++) {
                let so = optarr[i];
                let selected = "";
                if (so === this.component.pageSize) {
                    selected = "selected='selected'";
                }
                sizeopts += `<option name="${so}" ${selected}>${so}</option>`;
            }

            let selectName = edges.util.htmlID(this.namespace, "page-size", this.component.id);
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
            </div>`
        }

        let nav = "";
        if (this.showPageNavigation) {
            let first = `<a href="#" class="${firstClass} cursor-pointer">${edges.mex._("First")}</a>`;
            let prev = `<a href="#" class="${prevClass} cursor-pointer">${edges.mex._("Prev")}</a>`;
            if (this.component.page === 1) {
                first = `<span class="${firstClass} disabled cursor-not-allowed">${edges.mex._("First")}</span>`;
                prev = `<span class="${prevClass} disabled cursor-not-allowed">${edges.mex._("Prev")}</span>`;
            }

            let next = `<a href="#" class="${nextClass} cursor-pointer">${edges.mex._("Next")}</a>`;
            let last = `<a href="#" class="${lastClass} cursor-pointer">${edges.mex._("Last")}</a>`;

            if (this.component.page === this.component.totalPages) {
                next = `<span class="${nextClass} disabled cursor-not-allowed">${edges.mex._("Next")}</a>`;
                last = `<span class="${lastClass} disabled cursor-not-allowed">${edges.mex._("Last")}</a>`;
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
                            <span class="${pageClass}">Page ${pageNum} ${edges.mex._("of")} ${totalPages}</span>
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

        frag += `<div class="sixteen wide column">${sizer}</div>`

        if(this.showPageNavigation) {
            frag += `<div class="sixteen wide column">${nav}</div>`
        }

        frag += `</div>`

        this.component.context.html(frag);

        // now create the selectors for the functions
        if (this.showPageNavigation) {
            let firstSelector = edges.util.jsClassSelector(this.namespace, "first", this);
            let prevSelector = edges.util.jsClassSelector(this.namespace, "prev", this);
            let nextSelector = edges.util.jsClassSelector(this.namespace, "next", this);
            let lastSelector = edges.util.jsClassSelector(this.namespace, "last" , this)

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
            let sizeSelector = edges.util.jsClassSelector(this.namespace, "size", this);
            edges.on(sizeSelector, "change", this, "changeSize");
        }
    }

    doScroll() {
        $("html, body").animate({
            scrollTop: $(this.scrollSelector).offset().top
        }, 1);
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

        if(from) {
            this.component.setFrom(from);
        }
    }

    changeSize(element) {
        let size = $(element).val();
        this.component.setSize(size);
    }
}

edges.mex.renderers.ResourcesResults = class extends edges.Renderer {
    constructor(params) {
        super(params);

        //////////////////////////////////////////////
        // parameters that can be passed in

        // what to display when there are no results
        this.noResultsText = edges.util.getParam(params, "noResultsText", edges.mex._("No results to display"));


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
            var recordClasses = edges.util.styleClasses(this.namespace, "record", this.component.id);

            // now call the result renderer on each result to build the records
            frag = "";
            for (var i = 0; i < results.length; i++) {
                var rec = this._renderResult(results[i]);
                frag += `<div class="${recordClasses}">${rec}</div>`;
            }
        }

        // finally stick it all together into the container
        var containerClasses = edges.util.styleClasses(this.namespace, "container", this.component.id);
        var container = `<div class="${containerClasses}">${frag}</div>`;
        this.component.context.html(container);

        let previewSelector = edges.util.jsClassSelector(this.namespace, "preview", this.component.id);
        edges.on(previewSelector, "click", this, "previewResource");

        let selectSelector = edges.util.jsClassSelector(this.namespace, "select", this.component.id);
        edges.on(selectSelector, "click", this, "selectResource");
    }

    previewResource(element) {
        let id = $(element).attr("data-id");
        let previewer = this.component.edge.getComponent({id: "previewer"});

        // FIXME: poor abstraction, works fine, but feels wrong
        let hits = this.component.edge.result.data.hits.hits;
        for (let hit of hits) {
            if (hit._source.id === id) {
                previewer.showPreview(hit._source)
                break;
            }
        }
    }

    selectResource(element) {
        let el = $(element);
        let id = el.attr("data-id");
        let state = el.attr("data-state");

        if (state === "unselected") {
            this.selector.selectRecord(id)
            el.attr("data-state", "selected");
            el.attr("src" , "/static/images/selected.svg")
        } else {
            this.selector.unselectRecord(id);
            el.attr("data-state", "unselected");
            el.attr("src" , "/static/images/unselected.svg")
        }

        // PATCH: to hide the right section on resources, since edges don't have template sync function
        let doc = document.getElementById("right-col")
        if(doc) {
            if(this.selector && this.selector.length > 0) {
                doc.style.display = ""
            } else {
                doc.style.display = "none"
            }
        }
    }

    _renderResult(res) {
        let title = edges.util.escapeHtml(this._getLangVal("custom_fields.mex:title", res, edges.mex._("No title")));

        let alt = this._getLangVal("custom_fields.mex:alternativeTitle", res);
        if (alt) {
            alt = edges.util.escapeHtml(alt);
        } else {
            alt = "";
        }

        let desc = this._getLangVal("custom_fields.mex:description", res, "");
        if (desc.length > 300) {
            desc = edges.util.escapeHtml(desc.substring(0, 300)) + "...";
        }

        // FIXME: getting highlights out is difficult with the existing component, and the es integration.  They will
        // need reworking to do this properly.  For the moment this workaround will deal with it, but it is not
        // great, and will slow down large result sets
        let hits = this.component.edge.result.data.hits.hits;
        for (let hit of hits) {
            if (res.uuid === hit._id) {
                if (hit.highlight && hit.highlight["custom_fields.mex:description.value"]) {
                    desc = hit.highlight["custom_fields.mex:description.value"][0];
                    desc = desc.replace(/<em>/g, "<code>");
                    desc = desc.replace(/<\/em>/g, "</code>");
                }
            }
        }

        let created = edges.util.escapeHtml(edges.util.pathValue("created", res, ""));
        // let createdDate = new Date(created);
        created = edges.mex.fullDateFormatter(created)

        let keywords = this._rankedByLang("custom_fields.mex:keyword", res);
        if (keywords.length > 5) {
            keywords = keywords.slice(0, 5);
        }
        keywords = keywords.map(k => edges.util.escapeHtml(k)).join(", ");
        if (keywords !== "") {
            keywords = `<span class="tag">${keywords}</span>`;
        }

        let selectState = "unselected";
        let currentImage = '/static/images/unselected.svg'

        if (this.selector && this.selector.isSelected(res.id)) {
            selectState = "selected";
            currentImage = "/static/images/selected.svg"
            // selectText = edges.mex._("Remove");
        }

        let previewClass = edges.util.jsClasses(this.namespace, "preview", this.component.id);
        let selectClass = edges.util.jsClasses(this.namespace, "select", this.component.id);

        let frag = `
            <div class="resource-card card-shadow">
                <div class="card-header ${created ? '' :  'hide'}">
                    <span class="date">${created}</span>
                    <!--
                    <span  class="${previewClass} preview" data-id="${res.id}">
                        👁️ ${edges.mex._("Preview")}
                    </span>
                    -->
                </div>

                <div class="title ${title ? '' :  'hide'}">
                    <img
                        class="${selectClass} bookmark icon"
                        id="resource-list-${res.id}"
                        data-id="${res.id}"
                        data-state="${selectState}"
                        src="${currentImage}"
                        alt="${selectState} Icon" width="22" height="24"
                    />
                    <span>
                        ${title}
                    </span>
                </div>

                <div class="subtitle ${alt ? '' :  'hide'}">
                    <strong>${alt}</strong>
                </div>

                <div class="description ${desc ? '' :  'hide'}">
                    ${desc}
                </div>

                <div class="tags ${keywords ? '' :  'hide'}">
                    ${keywords}
                </div>
            </div>
        `
        return frag;
    }

    _getLangVal(path, res, def) {
        return edges.mex.getLangVal(path, res, def);
    }

    _rankedByLang(path, res) {
        return edges.mex.rankedByLang(path, res);
    }
}

edges.mex.renderers.ActivitiesResults = class extends edges.Renderer {
    constructor(params) {
        super(params);

        //////////////////////////////////////////////
        // parameters that can be passed in

        // what to display when there are no results
        this.noResultsText = edges.util.getParam(params, "noResultsText", edges.mex._("No results to display"));

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
            var recordClasses = edges.util.styleClasses(this.namespace, "record", this.component.id);

            // now call the result renderer on each result to build the records
            frag = "";
            for (var i = 0; i < results.length; i++) {
                var rec = this._renderResult(results[i]);
                frag += `<div class="${recordClasses}">${rec}</div>`;
            }
        }

        // finally stick it all together into the container
        var containerClasses = edges.util.styleClasses(this.namespace, "container", this.component.id);
        var container = `<div class="${containerClasses}">${frag}</div>`;
        this.component.context.html(container);

        let previewSelector = edges.util.jsClassSelector(this.namespace, "preview", this.component.id);
        edges.on(previewSelector, "click", this, "previewActivity");
    }

    previewActivity(element) {
        let id = $(element).attr("data-id");
        let previewer = this.component.edge.getComponent({id: "previewer"});

        // FIXME: poor abstraction, works fine, but feels wrong
        let hits = this.component.edge.result.data.hits.hits;
        for (let hit of hits) {
            if (hit._source.id === id) {
                previewer.showPreview(hit._source)
                break;
            }
        }
    }

    _renderResult(res) {
        let title = edges.util.escapeHtml(this._getLangVal("custom_fields.mex:title", res, "No title"));

        let alt = this._getLangVal("custom_fields.mex:alternativeTitle", res);
        if (alt) {
            alt = edges.util.escapeHtml(alt);
        } else {
            alt = "";
        }

        let desc = this._getLangVal("custom_fields.mex:abstract", res, "");
        if (desc.length > 300) {
            desc = edges.util.escapeHtml(desc.substring(0, 300)) + "...";
        }

        // FIXME: getting highlights out is difficult with the existing component, and the es integration.  They will
        // need reworking to do this properly.  For the moment this workaround will deal with it, but it is not
        // great, and will slow down large result sets
        let hits = this.component.edge.result.data.hits.hits;
        for (let hit of hits) {
            if (res.uuid === hit._id) {
                if (hit.highlight && hit.highlight["custom_fields.mex:abstract.value"]) {
                    desc = hit.highlight["custom_fields.mex:abstract.value"][0];
                    desc = desc.replace(/<em>/g, "<code>");
                    desc = desc.replace(/<\/em>/g, "</code>");
                }
            }
        }

        let start = edges.mex._("Unknown start date");
        start = this._extractMultiDate("custom_fields.mex:start", res, start);

        let end = edges.mex._("Unknown end date");
        end = this._extractMultiDate("custom_fields.mex:end", res, end);

        let previewClass = edges.util.jsClasses(this.namespace, "preview", this.component.id);

        let frag = `<div class="ui grid segment">
                <div class="twelve wide column">
                    <strong>${title}</strong><br>
                    <em>${alt}</em><br><br>
                    <p>${desc}</p>
                    ${start} ${edges.mex._("to")} ${end}
                </div>
                <div class="four wide column">
                    <a class="ui button ${previewClass}" data-id="${res.id}">${edges.mex._("Preview")}</a>
                </div>
            </div>`;
        return frag;
    }

    _extractMultiDate(path, res, def) {
        let out = def;
        let dates = edges.util.pathValue(path, res, []);
        if (dates.length > 0) {
            out = dates.map(d => { return d.date }).join(edges.mex._(" or "))
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
}

edges.mex.renderers.BibliographicResourcesResults = class extends edges.Renderer {
    constructor(params) {
        super(params);

        //////////////////////////////////////////////
        // parameters that can be passed in

        // what to display when there are no results
        this.noResultsText = edges.util.getParam(params, "noResultsText", edges.mex._("No results to display"));

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
            var recordClasses = edges.util.styleClasses(this.namespace, "record", this.component.id);

            // now call the result renderer on each result to build the records
            frag = "";
            for (var i = 0; i < results.length; i++) {
                var rec = this._renderResult(results[i]);
                frag += `<div class="${recordClasses}">${rec}</div>`;
            }
        }

        // finally stick it all together into the container
        var containerClasses = edges.util.styleClasses(this.namespace, "container", this.component.id);
        var container = `<div class="${containerClasses}">${frag}</div>`;
        this.component.context.html(container);

        let previewSelector = edges.util.jsClassSelector(this.namespace, "preview", this.component.id);
        edges.on(previewSelector, "click", this, "previewBibliographicResource");
    }

    previewBibliographicResource(element) {
        let id = $(element).attr("data-id");
        let previewer = this.component.edge.getComponent({id: "previewer"});

        // FIXME: poor abstraction, works fine, but feels wrong
        let hits = this.component.edge.result.data.hits.hits;
        for (let hit of hits) {
            if (hit._source.id === id) {
                previewer.showPreview(hit._source)
                break;
            }
        }
    }

    _renderResult(res) {
        let title = edges.util.escapeHtml(this._getLangVal("custom_fields.mex:title", res, "No title"));

        let alt = this._getLangVal("custom_fields.mex:alternativeTitle", res);
        if (alt) {
            alt = edges.util.escapeHtml(alt);
        } else {
            alt = "";
        }

        let sub = this._getLangVal("custom_fields.mex:subtitle", res);
        if (sub) {
            sub = edges.util.escapeHtml(alt);
        } else {
            sub = "";
        }

        let desc = this._getLangVal("custom_fields.mex:abstract", res, "");
        if (desc.length > 300) {
            desc = edges.util.escapeHtml(desc.substring(0, 300)) + "...";
        }

        // FIXME: getting highlights out is difficult with the existing component, and the es integration.  They will
        // need reworking to do this properly.  For the moment this workaround will deal with it, but it is not
        // great, and will slow down large result sets
        let hits = this.component.edge.result.data.hits.hits;
        for (let hit of hits) {
            if (res.uuid === hit._id) {
                if (hit.highlight && hit.highlight["custom_fields.mex:abstract.value"]) {
                    desc = hit.highlight["custom_fields.mex:abstract.value"][0];
                    desc = desc.replace(/<em>/g, "<code>");
                    desc = desc.replace(/<\/em>/g, "</code>");
                }
            }
        }

        // FIXME: will need to be a dereferenced field
        let creators = edges.util.pathValue("custom_fields.mex:creator", res, []);
        creators = creators.map(c => edges.util.escapeHtml(c)).join(", ");

        let pubYear = edges.util.pathValue("custom_fields.mex:publicationYear.date", res, "");

        let previewClass = edges.util.jsClasses(this.namespace, "preview", this.component.id);

        let frag = `<div class="ui grid segment">
                <div class="twelve wide column">
                    <strong>${title}</strong><br>
                    <em>${alt}</em><br>
                    <em>${sub}</em><br><br>
                    <p>${desc}</p>
                    ${creators}, ${pubYear}
                </div>
                <div class="four wide column">
                    <a class="ui button ${previewClass}" data-id="${res.id}">${edges.mex._("Preview")}</a>
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
}
