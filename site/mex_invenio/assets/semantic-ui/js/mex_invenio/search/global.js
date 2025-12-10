/* global $ */

import i18n from "./../i18n"
import { edges, es, mex } from "../search/edges.common";

edges.instances = edges.instances || {};
edges.instances.global = edges.instances.global || {};
edges.active = edges.active || {};

edges.instances.global.init = function () {
    const openingQuery = mex.resolveOpeningQuery(
        new es.Query({
            size: 50,
            sort: [{field: mex.constants.CREATED, order: "desc"}]
        })
    );

    edges.active["global"] = mex.makeEdge({
        resourceType: "global",
        openingQuery: openingQuery,
        components: [
            mex.fullSearchController({
                searchPlaceholder: i18n.t("Search across all resource types..."),
            }),

            mex.typeSpecificJumpOff({
                preamble: i18n.t("Search on specific resource type: "),
                targets: {
                    "/search/resources": i18n.t("Data Sources & Datasets"),
                    "/search/variables": i18n.t("Variables"),
                    "/search/activities": i18n.t("Activities"),
                    "/search/bibliographic-resources": i18n.t("Publications")
                }
            }),

            // Stuff above the results
            mex.resultCount(),
            mex.sorter({
                sortOptions: [
                    {field: mex.constants.CREATED, display: i18n.t("Created (newest first)"), order: "desc"},
                    {field: mex.constants.TITLE_KW, "display": i18n.t("Title"), order: "desc"}
                ]
            }),
            mex.defaultPager(),

            //  The results
            mex.globalDisplay(),

            // Stuff below the results
            mex.bottomPager(),
        ],
    });
};

$(document).ready(function ($) {
    edges.instances.global.init();
});
