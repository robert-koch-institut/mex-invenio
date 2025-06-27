if (!window.hasOwnProperty("edges")) { edges = {}}
if (!edges.hasOwnProperty("instances")) { edges.instances = {}}
if (!edges.hasOwnProperty("active")) { edges.active = {}}

edges.instances.variables = {};
edges.instances.variables.init = function() {
    edges.active["variables"] = edges.mex.makeEdge({
        resourceType: "variables",
        components: [
            edges.mex.fullSearchController({
                sortOptions: [
                    {field: "custom_fields.mex:label.value", "display": "Label"},
                    {field: "custom_fields.mex:usedIn.keyword", "display": "Used In"},
                    {field: "custom_fields.mex:belongsTo.keyword", "display": "Belongs To"},
                ],
                searchPlaceholder: "Search variables...",
            }),
            edges.mex.resultsDisplay({
                noResultsText: "No variables found.",
                rowDisplay: [
                    [{field: "custom_fields.mex:label.value"}],
                    [{field: "custom_fields.mex:usedIn"}],
                    [{field: "custom_fields.mex:belongsTo"}],
                    [{field: "custom_fields.mex:description.value"}],
                    [{field: "custom_fields.mex:dataType"}],
                    [{field: "custom_fields.mex:codingSystem"}],
                    [{field: "custom_fields.mex:valueSet"}]
                ]
            })
        ]
    })
}

jQuery(document).ready(function($) {
    edges.instances.variables.init();
});
