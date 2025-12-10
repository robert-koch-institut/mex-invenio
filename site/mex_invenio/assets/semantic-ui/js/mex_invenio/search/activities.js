/* global $ */

import i18n from "./../i18n"
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
                    {field: mex.constants.TITLE, "display": i18n.t("Title")},
                    {field: mex.constants.ALT_TITLE, "display": i18n.t("Alternative Title")},
                    {field: mex.constants.SHORT_NAME, "display": i18n.t("Short Name")},
                    {field: mex.constants.ABSTRACT, "display": i18n.t("Abstract")},
                    {field: mex.constants.EXTERNAL_ASSOCIATE, "display": i18n.t("External Associate")},
                    {field: mex.constants.INVOLVED_PERSON, "display": i18n.t("Involved Person")},
                ],
                searchPlaceholder: i18n.t("Search activities..."),
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
                    {field: mex.constants.CREATED, display: i18n.t("Created (newest first)"), order: "desc"},
                    {
                        field: mex.constants.END,
                        display: i18n.t("End Date (latest first)"),
                        order: "desc"
                    },
                    {
                        field: mex.constants.START,
                        display: i18n.t("Start Date (latest first)"),
                        order: "desc"
                    },
                    {field: mex.constants.TITLE_KW, "display": i18n.t("Title"), order: "desc"}
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
