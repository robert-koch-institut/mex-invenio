if (!window.hasOwnProperty("edges")) { edges = {}}
if (!edges.hasOwnProperty("instances")) { edges.instances = {}}
if (!edges.hasOwnProperty("active")) { edges.active = {}}

edges.instances.bibliographicResources = {};
edges.instances.bibliographicResources.init = function() {
    edges.active["bibliographic-resources"] = edges.mex.makeEdge({
        resourceType: "bibliographic-resources",
        components: [
            edges.mex.accessRestrictionFacet(),
            edges.mex.journalFacet(),
            edges.mex.keywordFacet(),
            edges.mex.fullSearchController({
                sortOptions: [
                    {field: "custom_fields.mex:publicationYear.date", "display": "Publication Year"},
                    {field: "metadata.title.keyword", "display": "Title"}
                ],
                searchPlaceholder: "Search bibliographic resources...",
            }),
            edges.mex.resultsDisplay({
                noResultsText: "No bibliographic resources found.",
                rowDisplay: [
                    [{field: "metadata.title"}],
                    [{field: "custom_fields.mex:subtitle.value"}],
                    [{field: "custom_fields.mex:alternativeTitle.value"}],
                    [{field: "custom_fields.mex:abstract.value"}],
                    [{field: "custom_fields.mex:creator"}],
                    [{field: "custom_fields.mex:publicationYear.date"}]
                ]
            })
        ]
    })
}

jQuery(document).ready(function($) {
    edges.instances.bibliographicResources.init();
});
