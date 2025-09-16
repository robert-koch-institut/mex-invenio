if (!window.hasOwnProperty("edges")) {
  edges = {};
}
if (!edges.hasOwnProperty("instances")) {
  edges.instances = {};
}
if (!edges.hasOwnProperty("active")) {
  edges.active = {};
}

edges.instances.variables = {};
edges.instances.variables.init = function () {

  // There are two main ways that the page needs to load for the variables search
  // * There may be selected resources in the local store.  If this is the case, then we can use them directly
  // * There may be no resources selected, in which case we start from an empty search

  // A case which has not been addressed, and which is not clear if a need exists is:
  // * They may be mexIds in in the URL.  In which case we need to read them, fetch the details of the resources (which
  // can be done easily enough with an ES query with the identifiers provided), and put them into local store.
  //      - In this case, what happens if there is data in the local store and data in the URL?  Do we prefer
  //        the local store or the URL?

  edges.active["variables-resources"] = edges.mex.makeEdge({
    selector: "#resources-container",
    template: new edges.mex.templates.SingleColumnTemplate({
      preamble: `<a href="/search/resources">${edges.mex._("Back to Data Sources &amp; Datasets Search")}</a>`,
    }),
    resourceType: "resources",
    components: [
      edges.mex.fullSearchController({
        category: "column",
        searchPlaceholder: edges.mex._("Find resources..."),
        searchTitle: edges.mex._("Search Resources By Title"),
      }),
      edges.mex.recordSelectorCompact({
        category: "column",
      }),
      edges.mex.resourceDisplayCompact({
        category: "column",
        onSelectToggle: function (params) {
          let selector = edges.active["variables-resources"].getComponent({
            id: "selector",
          });
          let ids = selector.ids();
          let mexids = [];
          for (let id of ids) {
            let resource = selector.get(id);
            let mex_id = resource.custom_fields["mex:identifier"];
            mexids.push(mex_id);
          }

          let e = edges.active.variables;
          let nq = e.cloneQuery();

          nq.removeMust(
            new es.TermsFilter({ field: "custom_fields.mex:usedIn.keyword" })
          );

          if (mexids.length > 0) {
            nq.addMust(
                new es.TermsFilter({
                  field: "custom_fields.mex:usedIn.keyword",
                  values: mexids,
                })
            );
          }

          e.pushQuery(nq);
          e.cycle();
        },
      }),

      // TODO: add pager component
      edges.mex.pagerSelector({
        category: "column",
        id:"resource-pager",
        showPageNavigation: true,
      }),
    ],
    callbacks: {
      "edges:pre-render": function () {
        // TODO: when there are no selected resources and no search, we should show the search rather
        // than the empty selection

        // sort out the view state of the two exclusive components
        let sc = edges.active["variables-resources"].getComponent({
          id: "search_controller",
        });
        if (sc.searchString) {
          // if a search string is set, show the search results and hide the selector
          $("#selector").hide();
          $("#results").show();
          $("#resource-pager").show();
        } else {
          // if no search string is set, show the selector and hide the results
          $("#selector").show();
          $("#results").hide();
          $("#resource-pager").hide();
        }
      },
    },
  });

  // to prepare the initial variables search, we need to see if anything has been
  // selected already, and set the opening query
  let selectedMexIds = edges.instances.variables.getSelectedMexIds();
  let openingQuery = null;
  if (selectedMexIds.length > 0) {
      openingQuery = new es.Query();
      openingQuery.addMust(
          new es.TermsFilter({
            field: "custom_fields.mex:usedIn.keyword",
            values: selectedMexIds,
          })
      );
  }

  edges.active["variables"] = edges.mex.makeEdge({
    selector: "#variables-container",
    template: new edges.mex.templates.SingleColumnTemplate(),
    resourceType: "variables",
    openingQuery: openingQuery,
    components: [
      edges.mex.pager({
        category: "left",
        showPageNavigation: false,
      }),

      edges.mex.fullSearchController({
        category: "middle",
        searchPlaceholder: edges.mex._("Find variables..."),
        searchTitle: "Search Variable By Name",
      }),
      edges.mex.variablesDisplay(),
      edges.mex.pagerSelector({
        category: "column",
        showPageNavigation: true,
      }),
    ],
  });
};

edges.instances.variables.getSelectedMexIds = function() {
  let selector = edges.active["variables-resources"].getComponent({
    id: "selector",
  });
  let ids = selector.ids();
  let mexids = [];
  for (let id of ids) {
    let resource = selector.get(id);
    let mex_id = resource.custom_fields["mex:identifier"];
    mexids.push(mex_id);
  }
  return mexids;
}

jQuery(document).ready(function ($) {
  edges.instances.variables.init();
});
