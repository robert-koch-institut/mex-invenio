import { edges } from "../search/edges.common"
import { es } from "../search/edges.common"

if (!edges.hasOwnProperty("instances")) {
    edges.instances = {};
}
if (!edges.hasOwnProperty("active")) {
    edges.active = {};
}

edges.instances.global = {};
edges.instances.global.init = function () {
    const openingQuery = edges.mex.resolveOpeningQuery(
        new es.Query({
            size: 50,
            sort: [{field: edges.mex.constants.CREATED, order: "desc"}]
        })
    );

    edges.active["global"] = edges.mex.makeEdge({
        resourceType: "global",
        openingQuery: openingQuery,
        components: [
            edges.mex.fullSearchController({
                searchPlaceholder: edges.i18next.t("Search across all resource types..."),
            }),

            edges.mex.typeSpecificJumpOff({
                preamble: edges.i18next.t("Search on specific resource type: "),
                targets: {
                    "/search/resources": edges.i18next.t("Data Sources & Datasets"),
                    "/search/variables": edges.i18next.t("Variables"),
                    "/search/activities": edges.i18next.t("Activities"),
                    "/search/bibliographic-resources": edges.i18next.t("Publications")
                }
            }),

            // Stuff above the results
            edges.mex.resultCount(),
            edges.mex.sorter({
                sortOptions: [
                    {field: edges.mex.constants.CREATED, display: edges.i18next.t("Created (newest first)"), order: "desc"},
                    {field: edges.mex.constants.TITLE_KW, "display": edges.i18next.t("Title"), order: "desc"}
                ]
            }),
            edges.mex.defaultPager(),

            //  The results
            edges.mex.globalDisplay(),

            // Stuff below the results
            edges.mex.bottomPager(),
        ],
    });
};

jQuery(document).ready(function ($) {
    edges.instances.global.init();
});
