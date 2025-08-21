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
  edges.active["activities"] = edges.mex.makeEdge({
    resourceType: "activities",
    components: [
      edges.mex.fullSearchController({
        sortOptions: [
          {
            field: "custom_fields.mex:end.date",
            display: edges.mex._("End Date"),
          },
          {
            field: "custom_fields.mex:start.date",
            display: edges.mex._("Start Date"),
          },
          { field: "metadata.title.keyword", display: edges.mex._("Title") },
        ],
        searchPlaceholder: edges.mex._("Search activities..."),
      }),
      edges.mex.activityTypeFacet(),
      edges.mex.startFacet(),
      edges.mex.endFacet(),
      edges.mex.funderOrCommissionerFacet(),
      edges.mex.themeFacet(),
      edges.mex.defaultPager(),
      edges.mex.activitiesDisplay(),
      //   edges.mex.activityPreview(),
      edges.mex.bottomPager(),
    ],
  });
};

jQuery(document).ready(function ($) {
  edges.instances.activities.init();
});
