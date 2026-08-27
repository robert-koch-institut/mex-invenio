import pytest

from mex_invenio.transform import (
    dromedary_to_kebab,
    dromedary_to_snake,
    ensure_prefix,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("title", "title"),
        ("alternativeTitle", "alternative_title"),
        ("bibliographicResource", "bibliographic_resource"),
        ("meshId", "mesh_id"),
        ("repositoryURL", "repository_url"),
        ("numberOfUniqueIndividuals", "number_of_unique_individuals"),
        ("icd10code", "icd_10_code"),
    ],
)
def test_dromedary_to_snake(value, expected):
    assert dromedary_to_snake(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("resource", "resource"),
        ("bibliographicResource", "bibliographic-resource"),
        ("accessPlatform", "access-platform"),
        ("organizationalUnit", "organizational-unit"),
    ],
)
def test_dromedary_to_kebab(value, expected):
    assert dromedary_to_kebab(value) == expected


def test_ensure_prefix():
    assert ensure_prefix("title", "mex:") == "mex:title"
    assert ensure_prefix("mex:title", "mex:") == "mex:title"
    assert ensure_prefix(42, "mex:") == "mex:42"
