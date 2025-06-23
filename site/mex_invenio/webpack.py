"""JS/CSS Webpack bundles for mex-invenio."""

from invenio_assets.webpack import WebpackThemeBundle

theme = WebpackThemeBundle(
    __name__,
    "assets",
    default="semantic-ui",
    themes={
        "semantic-ui": dict(
            entry={
                # "edges_jq": "./js/mex_invenio/edges/vendor/jquery-3.6.0/jquery-3.6.0.min.js",
                # "edges_core": "./js/mex_invenio/edges/src/edges.js",
                #
                # "edges_components_refining-and-term-selector": "./js/mex_invenio/edges/src/components/RefiningANDTermSelector.js",
                # #"edges_components_date-histogram": "./js/mex_invenio/edges/src/components/DateHistogram.js",    # TODO: doesn't exist yet
                # "edges_components_full-search-controller": "./js/mex_invenio/edges/src/components/FullSearchController.js",
                # "edges_components_results-display": "./js/mex_invenio/edges/src/components/ResultsDisplay.js",
                #
                # "edges_renderers_refining-and-term-selector": "./js/mex_invenio/edges/src/renderers/bs3/RefiningANDTermSelector.js",
                # #"edges_renderers_date-histogram": "./js/mex_invenio/edges/src/renderers/bs3/DateHistogram.js",  # TODO: doesn't exist yet
                # "edges_renderers_full-search-controller": "./js/mex_invenio/edges/src/renderers/bs3/FullSearchController.js",
                # "edges_renderers_results-fields-by-row": "./js/mex_invenio/edges/src/renderers/bs3/ResultsFieldsByRow.js",
            },
        ),
    },
)
