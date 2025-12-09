"""JS/CSS Webpack bundles for mex-invenio."""

from invenio_assets.webpack import WebpackThemeBundle

mex_js = "./js/mex_invenio/"
search = mex_js + "search/"
edges_src = mex_js + "edges/src/"
edges_components = edges_src + "components/"

# Define BASE search entries
search_base = [
    "jquery",
    "i18next",
    f"{mex_js}i18n.js",
    f"{mex_js}jquery-i18next.init.js",
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
    # f"{search}bibliographic-resources.js",  # Fixed typo
    # f"{search}global.js",
    # f"{search}resources.js",
    # f"{search}variables.js"
]

theme = WebpackThemeBundle(
    __name__,
    "assets",
    default="semantic-ui",
    themes={
        "semantic-ui": dict(
            entry={
                "support-record": "./js/mex_invenio/SupportRecordContainer.js",
                "i18next": "./js/mex_invenio/i18next.js",
                "search": search_all,
            },
        ),
    },
)