if (!window.hasOwnProperty("edges")) {
    edges = {};
}
if (!edges.hasOwnProperty("instances")) {
    edges.instances = {};
}
if (!edges.hasOwnProperty("active")) {
    edges.active = {};
}

edges.instances.variables = {};
edges.instances.variables.init = function () {

    // There are two main ways that the page needs to load for the variables search
    // * There may be selected resources in the local store.  If this is the case, then we can use them directly
    // * There may be no resources selected, in which case we start from an empty search

    // A case which has not been addressed, and which is not clear if a need exists is:
    // * They may be mexIds in in the URL.  In which case we need to read them, fetch the details of the resources (which
    // can be done easily enough with an ES query with the identifiers provided), and put them into local store.
    //      - In this case, what happens if there is data in the local store and data in the URL?  Do we prefer
    //        the local store or the URL?

    edges.active["variables-resources"] = edges.mex.makeEdge({
        selector: "#resources-container",
        openingQuery: new es.Query({size: 10}),
        template: new edges.mex.templates.SingleColumnTemplate({
            preamble: `<a class="link-button" href="/search/resources">${edges.mex._("Back to Data Sources &amp; Datasets Search")}</a>`,
            // hideComponentsInitially: ["selector", "selected-filtered", "results"],
        }),
        resourceType: "resources",
        secondaryQueries: {
            "selected-filter": function(edge) {
                let selectedMexIds = edges.instances.variables.getSelectedMexIds();

                let sq = edge.cloneQuery();
                sq.addMust(
                    new es.TermsFilter({
                        field: "custom_fields.mex:identifier.keyword",
                        values: selectedMexIds["resources"],
                    })
                );
                return sq;
            }
        },
        components: [
            edges.mex.recordSelectorCompact({
                category: "column",
                title : "All Data Sources & Datasets",
                resourceComponentIds: ["all-resources", "selected-filtered"],
                onSelectToggle: function (params) {
                    edges.instances.variables.propagateSelection();
                }
            }),

            edges.mex.staticHeading ({
                id:"all-resources-heading",
                category: "column",
                staticTitle : "All Data Sources & Datasets",
                fontStyle : "tiny"
            }),

            edges.mex.staticHeading ({
                id:"all-resources-search-heading",
                category: "column",
                staticTitle : "Search Data Sources & Datasets by Title",
                fontStyle : "small"
            }),

            edges.mex.fullSearchController({
                category: "column",
                searchPlaceholder: edges.mex._("Find resources..."),
                searchTitle: edges.mex._(" "),
                defaultField: "custom_fields.mex:title.value",
                clearButton: false,
                searchButton : true,
                compactDesign : true,
            }),

            edges.mex.resourceDisplayCompact({
                id: "selected-filtered",
                category: "column",
                secondaryResults: "selected-filter",
                title: edges.mex._(" "),
                hideIfNoResults: true,
                onSelectToggle: function (params) {
                    edges.instances.variables.propagateSelection();
                }
            }),
            edges.mex.resourceDisplayCompact({
                id: "all-resources",
                category: "column",
                title: edges.mex._(" "),
                onSelectToggle: function (params) {
                    edges.instances.variables.propagateSelection();
                }
            }),

            edges.mex.pagerSelector({
                category: "column",
                id: "resource-pager",
                showPageNavigation: true,
            }),
        ],
        callbacks: {
            "edges:pre-render": function () {
                // TODO: when there are no selected resources and no search, we should show the search rather
                // than the empty selection

                // sort out the view state of the two exclusive components
                let sc = edges.active["variables-resources"].getComponent({
                    id: "search_controller",
                });
                if (sc.searchString) {
                    // if a search string is set, show the search results and hide the selector
                    $("#selector").hide();
                    $("#selected-filtered").show();
                    $("#all-resources").show();
                    $("#resource-pager").show();
                } else {
                    // if no search string is set, show the selector and hide the results
                    $("#selected-filtered").hide();
                    $("#all-resources").show();
                    $("#resource-pager").show();
                    $("#selector").show();
                }
            },
        },
    });

    // to prepare the initial variables search, we need to see if anything has been
    // selected already, and set the opening query
    let selectedMexIds = edges.instances.variables.getSelectedMexIds();
    let openingQuery = edges.instances.variables.buildVariablesQuery(null, selectedMexIds);
    // if (selectedMexIds.length > 0) {
    //     openingQuery = new es.Query();
    //
    //     // add the resource constraints
    //     if (selectedMexIds["resources"].length > 0) {
    //         openingQuery.addMust(
    //             new es.TermsFilter({
    //                 field: "custom_fields.mex:usedIn.keyword",
    //                 values: selectedMexIds["resources"],
    //             })
    //         );
    //
    //         // only add the variable group constraints if there are selected resources
    //         if (selectedMexIds["variable_groups"].length > 0) {
    //             openingQuery.addMust(
    //                 new es.TermsFilter({
    //                     field: "custom_fields.mex:belongsTo.keyword",
    //                     values: selectedMexIds["variable_groups"],
    //                 })
    //             );
    //         }
    //     }
    // }

    edges.active["variables"] = edges.mex.makeEdge({
        selector: "#variables-container",
        template: new edges.mex.templates.SingleColumnTemplate(),
        resourceType: "variables",
        openingQuery: openingQuery,
        components: [
            edges.mex.resultCount({
                category: "left-middle-top",
            }),

            edges.mex.fullSearchController({
                category: "right-middle-top",
                searchPlaceholder: edges.mex._("Find variables..."),
                searchTitle: "Search Variable By Name",
            }),
            edges.mex.variablesDisplay(),
            edges.mex.pagerSelector({
                category: "column",
                showPageNavigation: true,
            }),
        ],
    });
};

edges.instances.variables.propagateSelection = function () {
    let selectedMexIds = edges.instances.variables.getSelectedMexIds();

    // let selector = edges.active["variables-resources"].getComponent({
    //   id: "selector",
    // });
    // let ids = selector.ids();
    // let resource_mexids = [];
    // for (let id of ids) {
    //   let resource = selector.get(id);
    //   let mex_id = resource.custom_fields["mex:identifier"];
    //   resource_mexids.push(mex_id);
    // }

    let e = edges.active.variables;
    let nq = e.cloneQuery();

    nq.removeMust(
        new es.TermsFilter({field: "custom_fields.mex:usedIn.keyword"})
    );
    nq.removeMust(
        new es.TermsFilter({field: "custom_fields.mex:belongsTo.keyword"})
    );

    nq = edges.instances.variables.buildVariablesQuery(nq, selectedMexIds);

    // if (resource_mexids.length > 0) {
    //     nq.addMust(
    //         new es.TermsFilter({
    //             field: "custom_fields.mex:usedIn.keyword",
    //             values: resource_mexids,
    //         })
    //     );
    // }

    e.pushQuery(nq);
    e.cycle();
}

edges.instances.variables.getSelectedMexIds = function () {
    let selector = edges.active["variables-resources"].getComponent({
        id: "selector",
    });

    // We can get the resource ids, just by asking the selector ids() function for them
    let ids = selector.ids();
    let resource_mexids = [];
    for (let id of ids) {
        let resource = selector.get(id);
        let mex_id = resource.custom_fields["mex:identifier"];
        resource_mexids.push(mex_id);
    }

    // we also need to see if any variable groups are pre-selected
    let vg_mexids = selector.selectedVariableGroups();

    return {"resources": resource_mexids, "variable_groups": vg_mexids};
}

edges.instances.variables.buildVariablesQuery = function (query, selectedMexIds) {
    if (query == null) {
        query = new es.Query();
    }

    // add the resource constraints
    if (selectedMexIds["resources"].length > 0) {
        query.addMust(
            new es.TermsFilter({
                field: "custom_fields.mex:usedIn.keyword",
                values: selectedMexIds["resources"],
            })
        );

        // only add the variable group constraints if there are selected resources
        if (selectedMexIds["variable_groups"].length > 0) {
            query.addMust(
                new es.TermsFilter({
                    field: "custom_fields.mex:belongsTo.keyword",
                    values: selectedMexIds["variable_groups"],
                })
            );
        }
    }
    return query;
}

jQuery(document).ready(function ($) {
    edges.instances.variables.init();
});
