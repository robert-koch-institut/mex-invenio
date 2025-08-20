if (!window.hasOwnProperty("edges")) { edges = {}}
if (!edges.hasOwnProperty("instances")) { edges.instances = {}}
if (!edges.hasOwnProperty("active")) { edges.active = {}}

edges.instances.variables = {};
edges.instances.variables.init = function() {
    edges.active["variables-resources"] = edges.mex.makeEdge({
        selector: "#resources-container",
        template: new edges.mex.templates.SingleColumnTemplate(),
        resourceType: "resources",
        components: [
            edges.mex.fullSearchController({
                category: "column",
                searchPlaceholder: edges.mex._("Find resources..."),
            }),
            edges.mex.recordSelector({
                category: "column",
            }),
            edges.mex.resourceDisplay({
                category: "column"
            })
        ],
        callbacks: {
            "edges:pre-render": function() {
                let sc = edges.active["variables-resources"].getComponent({id: "search_controller"});
                if (sc.searchString) {
                    // if a search string is set, show the search results and hide the selector
                    $("#selector").hide();
                    $("#results").show();
                } else {
                    // if no search string is set, show the selector and hide the results
                    $("#selector").show();
                    $("#results").hide();
                }
            }
        }
    })
}

jQuery(document).ready(function($) {
    edges.instances.variables.init();
});
