if (!window.hasOwnProperty("edges")) { edges = {}}
if (!edges.hasOwnProperty("instances")) { edges.instances = {}}
if (!edges.hasOwnProperty("active")) { edges.active = {}}

edges.instances.activities = {};
edges.instances.activities.init = function() {
    edges.active["activities"] = edges.mex.makeEdge({
        resourceType: "activities",
        components: [
            edges.mex.activityTypeFacet(),
            edges.mex.funderOrCommissionerFacet(),
            edges.mex.themeFacet(),
            edges.mex.fullSearchController({
                sortOptions: [
                    {field: "custom_fields.mex:end.date", "display": "End Date"},
                    {field: "custom_fields.mex:start.date", "display": "Start Date"},
                    {field: "metadata.title.keyword", "display": "Title"}
                ],
                searchPlaceholder: "Search activities...",
            }),
            edges.mex.resultsDisplay({
                noResultsText: "No activities found.",
                rowDisplay: [
                    [{field: "metadata.title"}],
                    [{field: "custom_fields.mex:alternativeTitle.value"}],
                    [{field: "custom_fields.mex:abstract.value"}],
                    [{field: "custom_fields.mex:start.date"}],
                    [{field: "custom_fields.mex:end.date"}]
                ]
            })
        ]
    })
}

jQuery(document).ready(function($) {
    edges.instances.activities.init();
});
