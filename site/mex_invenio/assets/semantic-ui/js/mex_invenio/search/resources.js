/* global $ */

import i18n from "./../i18n"
import { edges, es, mex } from "../search/edges.common";

edges.instances = edges.instances || {};
edges.instances.resources = edges.instances.resources || {};
edges.active = edges.active || {};

edges.instances.resources.init = function() {
    const openingQuery = mex.resolveOpeningQuery(
        new es.Query({
            size: 50,
            sort: [{field: mex.constants.CREATED, order: "desc"}]
        })
    );

    edges.active["resources"] = mex.makeEdge({
        resourceType: "resources",
        includeVerticalTab: true,
        openingQuery: openingQuery,
        components: [
            mex.fullSearchController({
                fieldOptions: [
                    {field: mex.constants.TITLE, "display": i18n.t("Title")},
                    {field: mex.constants.ALT_TITLE, "display": i18n.t("Alternative Title")},
                    {field: mex.constants.CONTRIBUTORS, "display": i18n.t("Contributor")},
                    {field: mex.constants.DESCRIPTION, "display": i18n.t("Description")},
                    {field: mex.constants.EXTERNAL_PARTNERS, "display": i18n.t("External Partner")},
                    {field: mex.constants.ICD10, "display": i18n.t("ICD-10 Code")},
                ],
                searchPlaceholder: i18n.t("Search resources..."),
                label: "Search",
                inlineLabel: true
            }),
            mex.selectedFilters(),

            // facets
            mex.accessRestrictionFacet(),
            mex.createdFacet(),
            mex.hasPersonalDataFacet(),
            mex.keywordFacet(),
            mex.resourceCreationMethodFacet(),
            mex.themeFacet(),

            // Stuff above the results
            mex.resultCount(),
            mex.sorter({
                sortOptions: [
                    {field: mex.constants.CREATED, display: i18n.t("Created (newest first)"), order: "desc"},
                    {field: mex.constants.TITLE_KW, "display": i18n.t("Title"), order: "desc"}
                ]
            }),
            mex.defaultPager(),

            // The results
            mex.resourceDisplay(),

            // right side resource selector
            mex.resourceSelector({
                onSelectToggle: edges.instances.resources.propagateSelection
            }),

            // Stuff below the results
            mex.bottomPager(),

            // vertical tab
            mex.verticalTabButton(),
        ]
    })
}

edges.instances.resources.propagateSelection = function(params) {
    let renderer = params.parent;
    let vt = renderer.component.edge.getComponent({id: "vertical-tab"});
    vt.draw();
}

$(document).ready(function($) {
    edges.instances.resources.init();
});
