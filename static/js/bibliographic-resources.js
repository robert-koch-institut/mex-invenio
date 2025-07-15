if (!window.hasOwnProperty("edges")) { edges = {}}
if (!edges.hasOwnProperty("instances")) { edges.instances = {}}
if (!edges.hasOwnProperty("active")) { edges.active = {}}

edges.instances.bibliographicResources = {};
edges.instances.bibliographicResources.init = function() {
    edges.active["bibliographic-resources"] = edges.mex.makeEdge({
        resourceType: "bibliographic-resources",
        components: [
            edges.mex.fullSearchController({
                sortOptions: [
                    {field: "custom_fields.mex:publicationYear.date", "display": edges.mex._("Publication Year")},
                    {field: "metadata.title.keyword", "display": edges.mex._("Title")}
                ],
                searchPlaceholder: edges.mex._("Search bibliographic resources..."),
            }),
            edges.mex.accessRestrictionFacet(),
            edges.mex.journalFacet(),
            edges.mex.keywordFacet(),
            edges.mex.publicationYearFacet(),
            edges.mex.defaultPager(),
            edges.mex.bibliographicResourcesDisplay(),
            edges.mex.bibliographicResourcesPreview(),
        ]
    })
}

jQuery(document).ready(function($) {
    edges.instances.bibliographicResources.init();
});
