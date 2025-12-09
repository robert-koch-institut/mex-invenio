import $ from 'jquery';
import { edges, es, mex } from "../search/edges.common";

edges.instances = edges.instances || {};

edges.instances.activities = {};
edges.instances.activities.init = function () {
    const openingQuery = mex.resolveOpeningQuery(
        new es.Query({
            size: 50,
            sort: [{field: mex.constants.CREATED, order: "desc"}]
        })
    );

    edges.active["activities"] = mex.makeEdge({
        resourceType: "activities",
        openingQuery: openingQuery,
        components: [
            mex.fullSearchController({
                fieldOptions: [
                    {field: mex.constants.TITLE, "display": $.t("Title")},
                    {field: mex.constants.ALT_TITLE, "display": $.t("Alternative Title")},
                    {field: mex.constants.SHORT_NAME, "display": $.t("Short Name")},
                    {field: mex.constants.ABSTRACT, "display": $.t("Abstract")},
                    {field: mex.constants.EXTERNAL_ASSOCIATE, "display": $.t("External Associate")},
                    {field: mex.constants.INVOLVED_PERSON, "display": $.t("Involved Person")},
                ],
                searchPlaceholder: $.t("Search activities..."),
            }),
            mex.selectedFilters(),

            // facets
            mex.activityTypeFacet(),
            mex.startFacet(),
            mex.endFacet(),
            mex.funderOrCommissionerFacet(),
            mex.themeFacet(),

            // Stuff above the results
            mex.resultCount(),
            mex.sorter({
                sortOptions: [
                    {field: mex.constants.CREATED, display: $.t("Created (newest first)"), order: "desc"},
                    {
                        field: mex.constants.END,
                        display: $.t("End Date (latest first)"),
                        order: "desc"
                    },
                    {
                        field: mex.constants.START,
                        display: $.t("Start Date (latest first)"),
                        order: "desc"
                    },
                    {field: mex.constants.TITLE_KW, "display": $.t("Title"), order: "desc"}
                ]
            }),
            mex.defaultPager(),

            //  The results
            mex.activitiesDisplay(),

            // Stuff below the results
            mex.bottomPager(),
        ],
    });
};

$(document).ready(function ($) {
    edges.instances.activities.init();
});
