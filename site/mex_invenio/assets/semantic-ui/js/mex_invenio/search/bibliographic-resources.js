import { edges } from "../search/edges.common"
import { es } from "../search/edges.common"

if (!edges.hasOwnProperty("instances")) {
    edges.instances = {};
}
if (!edges.hasOwnProperty("active")) {
    edges.active = {};
}

edges.instances.bibliographicResources = {};
edges.instances.bibliographicResources.init = function () {
    const openingQuery = edges.mex.resolveOpeningQuery(
        new es.Query({
            size: 50,
            sort: [{field: edges.mex.constants.CREATED, order: "desc"}]
        })
    );

    edges.active["bibliographic-resources"] = edges.mex.makeEdge({
        resourceType: "bibliographic-resources",
        openingQuery: openingQuery,
        components: [
            edges.mex.fullSearchController({
                fieldOptions: [
                    {field: edges.mex.constants.TITLE, "display": edges.$.t("Title")},
                    {field: edges.mex.constants.ALT_TITLE, "display": edges.$.t("Alternative Title")},
                    {field: edges.mex.constants.SUBTITLE, "display": edges.$.t("Involved Person")},
                    {field: edges.mex.constants.ABSTRACT, "display": edges.$.t("Abstract")},
                    {field: edges.mex.constants.CREATOR, "display": edges.$.t("Short Name")},
                    {field: edges.mex.constants.KEYWORD, "display": edges.$.t("External Associate")}
                ],
                searchPlaceholder: edges.$.t("Search bibliographic resources..."),
            }),
            edges.mex.selectedFilters(),

            // facets
            edges.mex.accessRestrictionFacet(),
            edges.mex.journalFacet(),
            edges.mex.keywordFacet(),
            edges.mex.publicationYearFacet(),

            // Stuff above the results
            edges.mex.resultCount(),
            edges.mex.sorter({
                sortOptions: [
                    {field: edges.mex.constants.CREATED, display: edges.$.t("Created (newest first)"), order: "desc"},
                    {
                        field: edges.mex.constants.PUBLICATION_YEAR,
                        display: edges.$.t("Publication Year (newest first)"),
                        order: "desc"
                    },
                    {field: edges.mex.constants.TITLE_KW, "display": edges.$.t("Title"), order: "desc"}
                ]
            }),
            edges.mex.defaultPager(),

            //  The results
            edges.mex.bibliographicResourcesDisplay(),

            // Stuff below the results
            edges.mex.bottomPager(),
        ],
    });
};

jQuery(document).ready(function ($) {
    edges.instances.bibliographicResources.init();
});
