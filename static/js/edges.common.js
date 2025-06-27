if (!window.hasOwnProperty("edges")) { edges = {}}
if (!edges.hasOwnProperty("instances")) { edges.instances = {}}
if (!edges.hasOwnProperty("active")) { edges.active = {}}
if (!edges.hasOwnProperty("mex")) { edges.mex = {}}

///////////////////////////////////////////////////
// General Functions

edges.mex.countFormat = edges.util.numFormat({
    thousandsSeparator: ","
});

edges.mex.refiningAndFacet = function(params) {
    return new edges.components.RefiningANDTermSelector({
        id: params.id,
        category: "facet",
        field: params.field,
        renderer: new edges.renderers.bs3.RefiningANDTermSelector({
            title: params.title,
            countFormat: edges.mex.countFormat,
        })
    })
}

edges.mex.fullSearchController = function(params) {
    return new edges.components.FullSearchController({
        id: params.id || "search_controller",
        category: "controller",
        sortOptions: params.sortOptions || [],
        fieldOptions: params.fieldOptions || [],
        renderer: new edges.renderers.bs3.FullSearchController({
            searchButton: true,
            searchPlaceholder: params.searchPlaceholder || "Search...",
            searchButtonText: params.searchButtonText || "Search",
            freetextSubmitDelay: params.freetextSubmitDelay || -1
        })
    });
}

edges.mex.resultsDisplay = function(params) {
    return new edges.components.ResultsDisplay({
        id: params.id || "results",
        category: "results",
        renderer: new edges.renderers.bs3.ResultsFieldsByRow({
            noResultsText: params.noResultsText || "No results found.",
            rowDisplay: params.rowDisplay
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
        template: new edges.templates.bs3.Facetview(),
        searchUrl: search_url,
        components: params.components
    });
}

////////////////////////////////////////////////////
// Specific functions

edges.mex.accessRestrictionFacet = function() {
    return edges.mex.refiningAndFacet({
        id: "access_restriction",
        field: "custom_fields.mex:accessRestriction.keyword",
        title: "Access Restriction"
    });
}

edges.mex.journalFacet = function() {
    return edges.mex.refiningAndFacet({
        id: "journal",
        field: "custom_fields.mex:journal.value.keyword",
        title: "Journal"
    });
}

edges.mex.keywordFacet = function() {
    return edges.mex.refiningAndFacet({
        id: "keyword",
        field: "custom_fields.mex:keyword.value.keyword",
        title: "Keyword"
    });
}

edges.mex.activityTypeFacet = function() {
    return edges.mex.refiningAndFacet({
        id: "activity_type",
        field: "custom_fields.mex:activityType.keyword",
        title: "Activity Type"
    });
}

edges.mex.funderOrCommissionerFacet = function() {
    return edges.mex.refiningAndFacet({
        id: "funder_or_commissioner",
        field: "custom_fields.mex:funderOrCommissioner.keyword",
        title: "Funder or Commissioner"
    });
}

edges.mex.themeFacet = function() {
    return edges.mex.refiningAndFacet({
        id: "theme",
        field: "custom_fields.mex:theme.keyword",
        title: "Theme"
    });
}

edges.mex.hasPersonalDataFacet = function() {
    return edges.mex.refiningAndFacet({
        id: "has_personal_data",
        field: "custom_fields.mex:hasPersonalData.keyword",
        title: "Has Personal Data"
    });
}

edges.mex.resourceCreationMethodFacet = function() {
    return edges.mex.refiningAndFacet({
        id: "resource_creation_method",
        field: "custom_fields.mex:resourceCreationMethod.keyword",
        title: "Resource Creation Method"
    });
}