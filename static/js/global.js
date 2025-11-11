if (!window.hasOwnProperty("edges")) {
    edges = {};
}
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
                searchPlaceholder: edges.mex._("Search across all resource types..."),
            }),

            edges.mex.typeSpecificJumpOff({
                preamble: edges.mex._("Search on specific resource type: "),
                targets: {
                    "/search/resources": edges.mex._("Data Sources & Datasets"),
                    "/search/variables": edges.mex._("Variables"),
                    "/search/activities": edges.mex._("Activities"),
                    "/search/bibliographic-resources": edges.mex._("Publications")
                }
            }),

            // Stuff above the results
            edges.mex.resultCount(),
            edges.mex.sorter({
                sortOptions: [
                    {field: edges.mex.constants.CREATED, display: edges.mex._("Created (newest first)"), order: "desc"},
                    {field: edges.mex.constants.TITLE_KW, "display": edges.mex._("Title"), order: "desc"}
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
