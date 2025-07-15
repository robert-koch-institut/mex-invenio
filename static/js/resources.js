if (!window.hasOwnProperty("edges")) { edges = {}}
if (!edges.hasOwnProperty("instances")) { edges.instances = {}}
if (!edges.hasOwnProperty("active")) { edges.active = {}}

edges.instances.resources = {};
edges.instances.resources.init = function() {
    edges.active["resources"] = edges.mex.makeEdge({
        resourceType: "resources",
        components: [
            edges.mex.fullSearchController({
                sortOptions: [
                    {field: "created", "display": edges.mex._("Created Date")},
                    {field: "metadata.title.keyword", "display": edges.mex._("Title")}
                ],
                searchPlaceholder: edges.mex._("Search resources..."),
            }),
            edges.mex.accessRestrictionFacet(),
            edges.mex.createdFacet(),
            edges.mex.hasPersonalDataFacet(),
            edges.mex.keywordFacet(),
            edges.mex.resourceCreationMethodFacet(),
            edges.mex.themeFacet(),
            edges.mex.defaultPager(),
            edges.mex.resourceDisplay(),
            edges.mex.resourcePreview(),
            edges.mex.resourceSelector()
        ]
    })
}

jQuery(document).ready(function($) {
    edges.instances.resources.init();
});
