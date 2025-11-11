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
    const openingQuery = edges.mex.resolveOpeningQuery(
        new es.Query({
            size: 50,
            sort: [{field: edges.mex.constants.CREATED, order: "desc"}]
        })
    );

    edges.active["activities"] = edges.mex.makeEdge({
        resourceType: "activities",
        openingQuery: openingQuery,
        components: [
            edges.mex.fullSearchController({
                fieldOptions: [
                    {field: edges.mex.constants.TITLE, "display": edges.mex._("Title")},
                    {field: edges.mex.constants.ALT_TITLE, "display": edges.mex._("Alternative Title")},
                    {field: edges.mex.constants.SHORT_NAME, "display": edges.mex._("Short Name")},
                    {field: edges.mex.constants.ABSTRACT, "display": edges.mex._("Abstract")},
                    {field: edges.mex.constants.EXTERNAL_ASSOCIATE, "display": edges.mex._("External Associate")},
                    {field: edges.mex.constants.INVOLVED_PERSON, "display": edges.mex._("Involved Person")},
                ],
                searchPlaceholder: edges.mex._("Search activities..."),
            }),
            edges.mex.selectedFilters(),

            // facets
            edges.mex.activityTypeFacet(),
            edges.mex.startFacet(),
            edges.mex.endFacet(),
            edges.mex.funderOrCommissionerFacet(),
            edges.mex.themeFacet(),

            // Stuff above the results
            edges.mex.resultCount(),
            edges.mex.sorter({
                sortOptions: [
                    {field: edges.mex.constants.CREATED, display: edges.mex._("Created (newest first)"), order: "desc"},
                    {
                        field: edges.mex.constants.END,
                        display: edges.mex._("End Date (latest first)"),
                        order: "desc"
                    },
                    {
                        field: edges.mex.constants.START,
                        display: edges.mex._("Start Date (latest first)"),
                        order: "desc"
                    },
                    {field: edges.mex.constants.TITLE_KW, "display": edges.mex._("Title"), order: "desc"}
                ]
            }),
            edges.mex.defaultPager(),

            //  The results
            edges.mex.activitiesDisplay(),

            // Stuff below the results
            edges.mex.bottomPager(),
        ],
    });
};

jQuery(document).ready(function ($) {
    edges.instances.activities.init();
});
