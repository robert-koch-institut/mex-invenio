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
                searchPlaceholder: i18n.t("Search across all records..."),
            }),

            mex.typeSpecificJumpOff({
                preamble: i18n.t("Search only in"),
                targets: {
                    "/search/resources": {"label": i18n.t("Data Sources & Datasets"), "icon": "resource"},
                    "/search/variables": {"label": i18n.t("Variables"), "icon": "variable"},
                    "/search/activities": {"label": i18n.t("Activities"), "icon": "activity"},
                    "/search/bibliographic-resources": {"label": i18n.t("Publications"), "icon": "bibliographicresource"}
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
            mex.pager({showRecordCount: false}),

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
