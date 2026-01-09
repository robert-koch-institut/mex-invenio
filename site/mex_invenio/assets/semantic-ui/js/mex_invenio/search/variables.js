/* global $ */

import i18n from "./../i18n"
import { edges, es, mex } from "../search/edges.common";

edges.instances = edges.instances || {};
edges.instances.variables = edges.instances.variables || {};
edges.active = edges.active || {};

edges.instances.variables.init = function () {

    // There are three main ways that the page needs to load for the variables search
    // * There may be selected resources in the local store.  If this is the case, then we can use them directly
    // * There may be no resources selected, in which case we start from an empty search
    // * They may be mexIds in the URL.  In which case we need to read them, fetch the details of the resources (which
    // can be done easily enough with an ES query with the identifiers provided), and put them into local store.
    //      - This data replaces the existing local store data

    // see if we have any resources in the URL
    const params = new URLSearchParams(window.location.search);
    const resourceId = params.get("resource") ?? "";
    let preSeed = [];
    if (resourceId !== "") {
        preSeed.push(resourceId);
        const url = new URL(window.location.href);
        url.search = "";
        window.history.replaceState("", "", url.toString());
    }

    edges.active["variables-resources"] = mex.makeEdge({
        selector: "#resources-container",
        openingQuery: new es.Query({size: 10}),
        template: new mex.templates.SingleColumnTemplate({
            preamble: `<a class="link-button" href="/search/resources">${i18n.t("Back to Data Sources &amp; Datasets Search")}</a>`,
        }),
        resourceType: "resources",
        secondaryQueries: {
            "selected-filter": function(edge) {
                let selectedMexIds = edges.instances.variables.getSelectedMexIds();

                let sq = edge.cloneQuery();
                sq.addMust(
                    new es.TermsFilter({
                        field: mex.constants.MEX_ID_KW,
                        values: selectedMexIds["resources"],
                    })
                );
                return sq;
            }
        },
        components: [
            mex.recordSelectorCompact({
                category: "column",
                title : "All Data Sources & Datasets",
                preSeed: preSeed,
                preSeedLoadedCallback: edges.instances.variables.selectionLoaded,
                resourceComponentIds: ["all-resources"], //, "selected-filtered"
                onSelectToggle: function (params) {
                    edges.instances.variables.propagateSelection();
                }
            }),

            mex.staticHeading ({
                id:"all-resources-heading",
                category: "column",
                staticTitle : "All Data Sources & Datasets",
                fontStyle : "small"
            }),

            mex.fullSearchController({
                category: "column",
                searchPlaceholder: i18n.t("Find resources..."),
                label: "Search Data Sources & Datasets by Title",
                inlineLabel: false,
                searchTitle: i18n.t(" "),
                defaultField: "custom_fields.mex:title.value",
                clearButton: false,
                searchButton : true,
                compactDesign : true,
            }),

            mex.resourceDisplayCompact({
                id: "all-resources",
                category: "column",
                title: i18n.t(" "),
                onSelectToggle: function (params) {
                    edges.instances.variables.propagateSelection();
                }
            }),

            mex.pagerSelector({
                category: "column",
                id: "resource-pager",
                showPageNavigation: true,
            }),
        ]
    });

    if (preSeed.length === 0) {
        // no pre-seed, so we can load directly
        edges.instances.variables.selectionLoaded();
    }
};

edges.instances.variables.selectionLoaded = function() {
    // to prepare the initial variables search, we need to see if anything has been
    // selected already, and set the opening query
    let selectedMexIds = edges.instances.variables.getSelectedMexIds();

    // get any query constraints from the URL
    let openingQuery = mex.resolveOpeningQuery(
        new es.Query({
            size: 50,
            sort: [{field: mex.constants.CREATED, order: "desc"}]
        })
    );

    // update the query with the resources constraints
    openingQuery = edges.instances.variables.buildVariablesQuery(openingQuery, selectedMexIds);

    edges.active["variables"] = mex.makeEdge({
        selector: "#variables-container",
        template: new mex.templates.SingleColumnTemplate(),
        resourceType: "variables",
        openingQuery: openingQuery,
        components: [
            mex.resultCount({
                category: "left-middle-top",
            }),

            mex.fullSearchController({
                category: "right-middle-top",
                searchPlaceholder: i18n.t("Find variables..."),
                searchTitle: "Search Variable By Name",
            }),
            mex.variablesDisplay(),
            mex.pagerSelector({
                category: "column",
                showPageNavigation: true,
            }),
        ],
    });
};

edges.instances.variables.propagateSelection = function () {
    let selectedMexIds = edges.instances.variables.getSelectedMexIds();

    let e = edges.active.variables;
    let nq = e.cloneQuery();

    nq.removeMust(
        new es.TermsFilter({field: mex.constants.USED_IN_ID_KW})
    );
    nq.removeMust(
        new es.TermsFilter({field: mex.constants.BELONGS_TO_ID_KW})
    );
    nq = edges.instances.variables.buildVariablesQuery(nq, selectedMexIds);

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
                field: mex.constants.USED_IN_ID_KW,
                values: selectedMexIds["resources"],
            })
        );

        // only add the variable group constraints if there are selected resources
        if (selectedMexIds["variable_groups"].length > 0) {
            query.addMust(
                new es.TermsFilter({
                    field: mex.constants.BELONGS_TO_ID_KW,
                    values: selectedMexIds["variable_groups"],
                })
            );
        }
    }
    return query;
}

$(document).ready(function ($) {
    edges.instances.variables.init();
});
