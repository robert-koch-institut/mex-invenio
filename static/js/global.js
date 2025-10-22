if (!window.hasOwnProperty("edges")) {
    edges = {};
}
if (!edges.hasOwnProperty("instances")) {
    edges.instances = {};
}
if (!edges.hasOwnProperty("active")) {
    edges.active = {};
}

edges.instances.activities = {};
edges.instances.activities.init = function () {
    edges.active["global"] = edges.mex.makeEdge({
        resourceType: "global",
        openingQuery: new es.Query({
            size: 50,
            sort: [{field: edges.mex.constants.CREATED, order: "desc"}]
        }),
        components: [
            edges.mex.fullSearchController({
                searchPlaceholder: edges.mex._("Search across all resource types..."),
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
    edges.instances.activities.init();
});
