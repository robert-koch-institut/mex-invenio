"""JS/CSS Webpack bundles for mex-invenio."""

from invenio_assets.webpack import WebpackThemeBundle

theme = WebpackThemeBundle(
    __name__,
    "assets",
    default="semantic-ui",
    themes={
        "semantic-ui": dict(
            entry={
                "i18next": "./js/mex_invenio/i18next.js",
            },
        ),
    },
)
