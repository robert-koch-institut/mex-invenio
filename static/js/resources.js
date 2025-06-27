if (!window.hasOwnProperty("edges")) { edges = {}}
if (!edges.hasOwnProperty("instances")) { edges.instances = {}}
if (!edges.hasOwnProperty("active")) { edges.active = {}}

edges.instances.resources = {};
edges.instances.resources.init = function() {
    edges.active["resources"] = edges.mex.makeEdge({
        resourceType: "resources",
        components: [
            edges.mex.accessRestrictionFacet(),
            edges.mex.keywordFacet(),
            edges.mex.themeFacet(),
            edges.mex.hasPersonalDataFacet(),
            edges.mex.resourceCreationMethodFacet(),
            edges.mex.fullSearchController({
                sortOptions: [
                    {field: "created", "display": "Created Date"},
                    {field: "metadata.title.keyword", "display": "Title"}
                ],
                searchPlaceholder: "Search resources...",
            }),
            edges.mex.resultsDisplay({
                noResultsText: "No resources found.",
                rowDisplay: [
                    [{field: "metadata.title"}],
                    [{field: "custom_fields.mex:alternativeTitle.value"}],
                    [{field: "custom_fields.mex:description.value"}],
                    [{field: "custom_fields.mex:keyword.value"}]
                ]
            })
        ]
    })
}

jQuery(document).ready(function($) {
    edges.instances.resources.init();
});
