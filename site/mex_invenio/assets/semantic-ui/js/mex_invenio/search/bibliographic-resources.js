/* global $ */

import i18n from "./../i18n"
import { edges, es, mex } from "../search/edges.common";

edges.instances = edges.instances || {};
edges.instances.bibliographicResources = edges.instances.bibliographicResources || {};
edges.active = edges.active || {};

edges.instances.bibliographicResources.init = function () {
    const openingQuery = mex.resolveOpeningQuery(
        new es.Query({
            size: 50,
            sort: [{field: mex.constants.CREATED, order: "desc"}]
        })
    );

    edges.active["bibliographic-resources"] = mex.makeEdge({
        resourceType: "bibliographic-resources",
        openingQuery: openingQuery,
        components: [
            mex.fullSearchController({
                fieldOptions: [
                    {field: mex.constants.TITLE, "display": i18n.t("Title")},
                    {field: mex.constants.ALT_TITLE, "display": i18n.t("Alternative Title")},
                    {field: mex.constants.SUBTITLE, "display": i18n.t("Involved Person")},
                    {field: mex.constants.ABSTRACT, "display": i18n.t("Abstract")},
                    {field: mex.constants.CREATOR, "display": i18n.t("Short Name")},
                    {field: mex.constants.KEYWORD, "display": i18n.t("External Partner")}
                ],
                searchPlaceholder: i18n.t("Search publications..."),
            }),
            mex.selectedFilters(),

            // facets
            mex.accessRestrictionFacet(),
            mex.journalFacet(),
            mex.keywordFacet(),
            mex.publicationYearFacet(),

            // Stuff above the results
            mex.resultCount(),
            mex.sorter({
                sortOptions: [
                    {field: mex.constants.CREATED, display: i18n.t("Created (newest first)"), order: "desc"},
                    {
                        field: mex.constants.PUBLICATION_YEAR,
                        display: i18n.t("Publication Year (newest first)"),
                        order: "desc"
                    },
                    {field: mex.constants.TITLE_SORT, "display": i18n.t("Title"), order: "asc"}
                ]
            }),
            mex.pager({showRecordCount: false}),

            //  The results
            mex.bibliographicResourcesDisplay(),

            // Stuff below the results
            mex.bottomPager(),
        ],
    });
};

$(document).ready(function ($) {
    edges.instances.bibliographicResources.init();
});
