if (!window.hasOwnProperty("edges")) { edges = {}}
if (!edges.hasOwnProperty("instances")) { edges.instances = {}}
if (!edges.hasOwnProperty("active")) { edges.active = {}}

edges.instances.variables = {};
edges.instances.variables.init = function() {

    // TODO: we will need to load the appropriate resources for pre-selection
    // * They may be in local store.  If this is the case, then we can use them directly
    // * They may be in the URL.  In which case we need to read them, fetch the details of the resources (which
    // can be done easily enough with an ES query with the identifiers provided), and put them into local store.
    //      - In this case, what happens if there is data in the local store and data in the URL?  Do we prefer
    //        the local store or the URL?
    // * There may be no resources anywhere, in which case we start from an empty search

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
                category: "column",
                onSelectToggle: function(params) {
                    let selector = edges.mex.active["variables-resources"].getComponent({id: "selector"});
                    let ids = selector.ids();
                    let mexids = [];
                    for (let id of ids) {
                        let resource = selector.get(id);
                        let mex_id = resource.custom_fields["mex:identifier"];
                        mexids.push(mex_id);
                    }

                    let e = edges.active.variables;
                    let nq = e.cloneQuery();

                    nq.removeMust(new es.TermsFilter({field: "custom_fields.mex:usedIn.keyword"}))
                    nq.addMust(new es.TermsFilter({field: "custom_fields.mex:usedIn.keyword", values: mexids}));

                    e.pushQuery(nq);
                    e.cycle()
                }
            })
        ],
        callbacks: {
            "edges:pre-render": function() {
                // TODO: when there are no selected resources and no search, we should show the search rather
                // than the empty selection

                // sort out the view state of the two exclusive components
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

    edges.active["variables"] = edges.mex.makeEdge({
        selector: "#variables-container",
        template: new edges.mex.templates.SingleColumnTemplate(),
        resourceType: "variables",
        components: [
            // TODO: add text search filter component

            // TODO: I've done a basic variables display as a table, it will need a full work-up instead
            edges.mex.variablesDisplay()

            // TODO: add pager component
        ]
    })
}

jQuery(document).ready(function($) {
    edges.instances.variables.init();
});
