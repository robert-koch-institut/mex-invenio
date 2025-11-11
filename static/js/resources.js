if (!window.hasOwnProperty("edges")) { edges = {}}
if (!edges.hasOwnProperty("instances")) { edges.instances = {}}
if (!edges.hasOwnProperty("active")) { edges.active = {}}

edges.instances.resources = {};
edges.instances.resources.init = function() {
    const openingQuery = edges.mex.resolveOpeningQuery(
        new es.Query({
            size: 50,
            sort: [{field: edges.mex.constants.CREATED, order: "desc"}]
        })
    );

    edges.active["resources"] = edges.mex.makeEdge({
        resourceType: "resources",
        includeVerticalTab: true,
        openingQuery: openingQuery,
        components: [
            edges.mex.fullSearchController({
                fieldOptions: [
                    {field: edges.mex.constants.TITLE, "display": edges.mex._("Title")},
                    {field: edges.mex.constants.ALT_TITLE, "display": edges.mex._("Alternative Title")},
                    {field: edges.mex.constants.CONTRIBUTORS, "display": edges.mex._("Contributor")},
                    {field: edges.mex.constants.DESCRIPTION, "display": edges.mex._("Description")},
                    {field: edges.mex.constants.EXTERNAL_PARTNERS, "display": edges.mex._("External Partner")},
                    {field: edges.mex.constants.ICD10, "display": edges.mex._("ICD-10 Code")},
                ],
                searchPlaceholder: edges.mex._("Search resources..."),
            }),
            edges.mex.selectedFilters(),

            // facets
            edges.mex.accessRestrictionFacet(),
            edges.mex.createdFacet(),
            edges.mex.hasPersonalDataFacet(),
            edges.mex.keywordFacet(),
            edges.mex.resourceCreationMethodFacet(),
            edges.mex.themeFacet(),

            // Stuff above the results
            edges.mex.resultCount(),
            edges.mex.sorter({
                sortOptions: [
                    {field: edges.mex.constants.CREATED, display: edges.mex._("Created (newest first)"), order: "desc"},
                    {field: edges.mex.constants.TITLE_KW, "display": edges.mex._("Title"), order: "desc"}
                ]
            }),
            edges.mex.defaultPager(),

            // The results
            edges.mex.resourceDisplay(),

            // right side resource selector
            edges.mex.resourceSelector(),

            // Stuff below the results
            edges.mex.bottomPager(),
        ]
    })
}

jQuery(document).ready(function($) {
    edges.instances.resources.init();
});
