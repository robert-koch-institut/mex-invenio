"""JS/CSS Webpack bundles for mex-invenio."""

from invenio_assets.webpack import WebpackThemeBundle

mex_js = "./js/mex_invenio/"
search = mex_js + "search/"
edges_src = mex_js + "edges/src/"
edges_components = edges_src + "components/"

# Define BASE search entries
search_base = [
    "jquery",
    f"{edges_src}datasources/es7x.js",
    f"{edges_src}edges.js",
    f"{edges_components}RefiningANDTermSelector.js",
    f"{edges_components}FullSearchController.js",
    f"{edges_components}ResultsDisplay.js",
    f"{edges_components}DateHistogram.js",
    f"{edges_components}Pager.js",
    f"{edges_components}SelectedFilters.js",
    f"{search}edges.common.js",
]

# SINGLE search bundle with ALL pages (recommended)
search_all = search_base + [
    f"{search}activities.js",
    f"{search}bibliographic-resources.js",
    f"{search}global.js",
    f"{search}resources.js",
    f"{search}variables.js"
]

theme = WebpackThemeBundle(
    __name__,
    "assets",
    default="semantic-ui",
    themes={
        "semantic-ui": dict(
            entry={
                "support-record": "./js/mex_invenio/SupportRecordContainer.js",
                "search": search_all,
            },
        ),
    },
)