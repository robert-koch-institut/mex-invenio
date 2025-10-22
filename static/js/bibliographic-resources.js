if (!window.hasOwnProperty("edges")) {
  edges = {};
}
if (!edges.hasOwnProperty("instances")) {
  edges.instances = {};
}
if (!edges.hasOwnProperty("active")) {
  edges.active = {};
}

edges.instances.bibliographicResources = {};
edges.instances.bibliographicResources.init = function () {
  edges.active["bibliographic-resources"] = edges.mex.makeEdge({
    resourceType: "bibliographic-resources",
    openingQuery: new es.Query({
      size: 50,
      sort: [{ field: edges.mex.constants.CREATED, order: "desc" }]
    }),
    components: [
      edges.mex.fullSearchController({
        fieldOptions: [
            {field: edges.mex.constants.TITLE, "display": edges.mex._("Title")},
            {field: edges.mex.constants.ALT_TITLE, "display": edges.mex._("Alternative Title")},
            {field: edges.mex.constants.SUBTITLE, "display": edges.mex._("Involved Person")},
            {field: edges.mex.constants.ABSTRACT, "display": edges.mex._("Abstract")},
            {field: edges.mex.constants.CREATOR, "display": edges.mex._("Short Name")},
            {field: edges.mex.constants.KEYWORD, "display": edges.mex._("External Associate")}
        ],
        searchPlaceholder: edges.mex._("Search bibliographic resources..."),
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
              {field: edges.mex.constants.CREATED, display: edges.mex._("Created (newest first)"), order: "desc"},
              {
                field: edges.mex.constants.PUBLICATION_YEAR,
                display: edges.mex._("Publication Year (newest first)"),
                order: "desc"
              },
              {field: edges.mex.constants.TITLE_KW, "display": edges.mex._("Title"), order: "desc"}
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
