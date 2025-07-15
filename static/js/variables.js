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
                    {field: "custom_fields.mex:label.value.keyword", "display": "Label"},
                    {field: "custom_fields.mex:usedIn.keyword", "display": "Used In"},
                    {field: "custom_fields.index:belongsToLabel.keyword", "display": "Belongs To"},
                ],
                searchPlaceholder: "Search variables...",
            }),
            edges.mex.resultsDisplay({
                noResultsText: "No variables found.",
                rowDisplay: [
                    [{
                        pre: "label: ", valueFunction: function (labels, result) {
                            let values = [];
                            if (result.custom_fields["mex:label"]) {
                                for (let l of result.custom_fields["mex:label"]) {
                                    if (l.value) {
                                        values.push(l.value);
                                    }
                                }
                            }
                            return values.join(", ");
                        }
                    }],
                    [{pre: "<strong>used in</strong>: ", field: "custom_fields.mex:usedIn"}],
                    [{pre: "<strong>belongs to</strong>: ", field: "custom_fields.index:belongsToLabel"}],
                    [{
                        pre: "<strong>description</strong>: ", valueFunction: function (labels, result) {
                            let values = [];
                            if (result.custom_fields["mex:description"]) {
                                for (let l of result.custom_fields["mex:description"]) {
                                    if (l.value) {
                                        values.push(l.value);
                                    }
                                }
                            }
                            return values.join(", ");
                        }
                    }],
                    [{pre: "<strong>datatype</strong>: ", field: "custom_fields.mex:dataType"}],
                    [{pre: "<strong>coding system</strong>: ", field: "custom_fields.mex:codingSystem"}],
                    [{pre: "<strong>value set</strong>: ", field: "custom_fields.mex:valueSet"}],
                    [{valueFunction: function(value, result) {return "<br>"}}]
                ]
            })
        ]
    })
}

jQuery(document).ready(function($) {
    edges.instances.variables.init();
});
