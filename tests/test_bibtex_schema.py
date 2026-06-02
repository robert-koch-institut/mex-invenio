import re

import pytest

from mex_invenio.custom_fields.pref_labels import get_pref_labels
from mex_invenio.services.schema import MExCustomBibTeXSchema as BibSchema
from tests.data import bibliographic_resource_record_minimal as pub


@pytest.mark.parametrize(
    ("input_value", "expected"),
    [
        ("https://doi.org/10.1000/xyz123", "10.1000/xyz123"),
        ("10.1000/abc456", "10.1000/abc456"),
        ("random-string-without-doi", "random-string-without-doi"),
    ],
)
def test_normalize_doi(input_value, expected):
    assert BibSchema._normalize_doi(input_value) == expected


def test_normalize_doi_empty_and_none():
    assert BibSchema._normalize_doi("") is None
    assert BibSchema._normalize_doi(None) is None


def test_bibtex_fields(db, location, resource_type_v, contributors_role_v, import_file):
    schema = BibSchema("de")
    creator = schema.get_creator(pub)
    assert creator == "Elias Morgenstern and Bruce Willis"

    title = schema.get_title(pub)
    assert title == "Moonlight Contamination in Amateur Telescope Snack Selection"

    publication_year = schema.get_publication_year(pub)
    assert publication_year == "2002"

    journal = schema.get_journal(pub)
    assert journal == "Die beobachterunabhängige astrophysikalische Übersicht"

    issue = schema.get_issue(pub)
    assert issue == "Q3"

    pages = schema.get_pages(pub)
    assert pages == "10-12"

    doi = schema.get_doi(pub)
    assert doi == "10.1016/j.anaerobe.2016.04.006"

    schema = BibSchema("en")

    title = schema.get_title(pub)
    assert title == "Moonlight Contamination in Amateur Telescope Snack Selection"

    abstract = schema.get_abstract(pub)
    assert (
        abstract
        == "The influence of lunar illumination on astronomical observations has been extensively documented..."
    )

    journal = schema.get_journal(pub)
    assert journal == "The Observer-Independent Astrophysical Review"

    keywords = schema.get_keywords(pub)
    assert keywords == "amateur astronomy, Nachthimmel-Kultur"


@pytest.mark.parametrize(
    ("resource_type_url", "expected_type"),
    [
        (
            "https://mex.rki.de/item/bibliographic-resource-type-1",
            "book",
        ),
        (
            "https://mex.rki.de/item/bibliographic-resource-type-2",
            "inbook",
        ),
        (
            "https://mex.rki.de/item/bibliographic-resource-type-3",
            "inproceedings",
        ),
        (
            "https://mex.rki.de/item/bibliographic-resource-type-4",
            "phdthesis",
        ),
        (
            "https://mex.rki.de/item/bibliographic-resource-type-5",
            "phdthesis",
        ),
        (
            "https://mex.rki.de/item/bibliographic-resource-type-6",
            "misc",
        ),
        (
            "https://mex.rki.de/item/bibliographic-resource-type-7",
            "article",
        ),
        (
            "https://mex.rki.de/item/bibliographic-resource-type-8",
            "misc",
        ),
        (
            "https://mex.rki.de/item/bibliographic-resource-type-9",
            "misc",
        ),
        (
            "https://mex.rki.de/item/bibliographic-resource-type-10",
            "unpublished",
        ),
        (
            "https://mex.rki.de/item/bibliographic-resource-type-11",
            "misc",
        ),
        (
            "https://mex.rki.de/item/bibliographic-resource-type-12",
            "techreport",
        ),
        (
            "https://mex.rki.de/item/bibliographic-resource-type-13",
            "unpublished",
        ),
        (
            "https://mex.rki.de/item/bibliographic-resource-type-14",
            "mastersthesis",
        ),
    ],
)
def test_resolve_bibtex_type(app, resource_type_url, expected_type):
    schema = BibSchema()
    pub = {"custom_fields": {"mex:bibliographicResourceType": [resource_type_url]}}
    pref_labels = get_pref_labels()
    result = schema.resolve_bibtex_type(pub, pref_labels)
    assert result == expected_type


def test_to_bibtex(app):
    schema = BibSchema()
    pref_labels = get_pref_labels()
    result = schema.to_bibtex(pub, pref_labels)

    # Starts with correct entry type and citation key
    assert result.startswith("@book{gLXGQRPXcmvCRHLjA2f73y,")

    # Ends with closing brace
    assert result.endswith("}")

    # Required fields are present
    assert "creator = {Elias Morgenstern and Bruce Willis}" in result
    assert (
        "title = {Moonlight Contamination in Amateur Telescope Snack Selection}"
        in result
    )
    assert "publication_year = {2002}" in result
    assert "issue = {Q3}" in result
    assert "pages = {10-12}" in result
    assert "doi = {10.1016/j.anaerobe.2016.04.006}" in result
    assert (
        "abstract = {The influence of lunar illumination on astronomical observations has been extensively documented...},"
        in result
    )
    assert "keywords = {amateur astronomy, Nachthimmel-Kultur}" in result

    # Every field should use "name = {value}" format
    field_pattern = re.compile(r"^\s*\w+\s*=\s*\{.*\},?$")

    lines = result.splitlines()[1:-1]  # skip @book{... and final }
    for line in lines:
        assert field_pattern.match(line), f"Invalid field format: {line}"
