"""JS/CSS Webpack bundles for mex-invenio."""

from invenio_assets.webpack import WebpackThemeBundle

theme = WebpackThemeBundle(
    __name__,
    "assets",
    default="semantic-ui",
    themes={
        "semantic-ui": dict(
            entry={
                "my-js": "./js/mex_invenio/myjs.js",
                # Add your webpack entrypoints
            },
        ),
    },
)
