if (!window.hasOwnProperty("edges")) { edges = {}}
if (!edges.hasOwnProperty("instances")) { edges.instances = {}}
if (!edges.hasOwnProperty("active")) { edges.active = {}}

edges.instances.bibliographicResources = {};
edges.instances.bibliographicResources.init = function(params) {
    if (!params) { params = {} }

    let current_domain = document.location.host;
    let current_scheme = window.location.protocol;
    let selector = params.selector || "#bibliographic-resources";
    let search_url = current_scheme + "//" + current_domain + "/search/api/bibliographic-resources";

    let countFormat = edges.util.numFormat({
        thousandsSeparator: ","
    });

    edges.active[selector] = new edges.Edge({
        selector: selector,
        template: new edges.templates.bs3.Facetview(),
        searchUrl: search_url,
        components: [
            new edges.components.RefiningANDTermSelector({
                id: "access_restriction",
                category: "facet",
                field: "custom_fields.mex:accessRestriction.keyword",
                renderer: new edges.renderers.bs3.RefiningANDTermSelector({
                    title: "Access Restriction",
                    countFormat: countFormat
                })
            }),
            new edges.components.RefiningANDTermSelector({
                id: "journal",
                category: "facet",
                field: "custom_fields.mex:journal.value.keyword",
                renderer: new edges.renderers.bs3.RefiningANDTermSelector({
                    title: "Journal",
                    countFormat: countFormat
                })
            }),
            new edges.components.RefiningANDTermSelector({
                id: "keyword",
                category: "facet",
                field: "custom_fields.mex:keyword.value.keyword",
                renderer: new edges.renderers.bs3.RefiningANDTermSelector({
                    title: "Keyword",
                    countFormat: countFormat
                })
            }),
            new edges.components.FullSearchController({
                id: "search_controller",
                category: "controller",
                sortOptions: [
                    {field: "custom_fields.mex:publicationYear.date", "display": "Publication Year"},
                    {field: "metadata.title.keyword", "display": "Title"}
                ],
                fieldOptions: [],
                renderer: new edges.renderers.bs3.FullSearchController({
                    searchButton: true,
                    searchPlaceholder: "Search bibliographic resources...",
                    searchButtonText: "Search",
                    freetextSubmitDelay: -1
                })
            }),
            new edges.components.ResultsDisplay({
                id: "results",
                category: "results",
                renderer: new edges.renderers.bs3.ResultsFieldsByRow({
                    noResultsText: "No bibliographic resources found.",
                    rowDisplay: [
                        [{field: "metadata.title"}],
                        [{field: "custom_fields.mex:subtitle.value"}],
                        [{field: "custom_fields.mex:alternativeTitle.value"}],
                        [{field: "custom_fields.mex:abstract.value"}],
                        [{field: "metadata.creators.person_or_org.name"}],
                        [{field: "custom_fields.mex:publicationYear.date"}]
                    ]
                })
            })
        ]
    })
}

jQuery(document).ready(function($) {
    edges.instances.bibliographicResources.init();
});
