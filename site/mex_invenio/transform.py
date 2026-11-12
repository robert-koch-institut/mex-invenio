"""String transformations shared between the MEx model and this instance.

Adapted from ``mex/common/transform.py`` in `mex-common
<https://github.com/robert-koch-institut/mex-common>`_, which is not a dependency of
this instance. Only the converters needed to derive Invenio names from MEx model
names are vendored here; keep them behaviour-compatible with the originals.
"""

import re

SNAKE_CASE_SPLITTER = re.compile(r"([A-Z]+(?![a-z])|[A-Z][a-z]*|[0-9]+|^[a-z]+)")


def dromedary_to_snake(value: str) -> str:
    """Convert dromedaryCase to snake_case, e.g. ``alternativeTitle``."""
    return "_".join(
        word.lower() for word in SNAKE_CASE_SPLITTER.split(value) if word.strip("_")
    )


def dromedary_to_kebab(value: str) -> str:
    """Convert dromedaryCase to kebab-case, e.g. ``bibliographicResource``."""
    return "-".join(
        word.lower() for word in SNAKE_CASE_SPLITTER.split(value) if word.strip("-")
    )


def ensure_prefix(value: object, prefix: object) -> str:
    """Return a string with the given prefix, adding it only when missing."""
    string = str(value)
    prefix = str(prefix)
    return string if string.startswith(prefix) else f"{prefix}{string}"
