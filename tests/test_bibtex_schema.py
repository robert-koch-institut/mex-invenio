import re
from unittest.mock import patch

import pytest

from mex_invenio.services.schema import MExCustomBibTeXSchema as BibSchema
from tests.data import PREF_LABELS_mock as pref_labels
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
    schema = BibSchema()
    creator = schema.get_creator(pub)
    assert creator == "Elias Morgenstern and Bruce Willis"

    with patch("mex_invenio.services.schema.get_locale", return_value="en"):
        title = schema.get_title(pub)
        assert title == "Moonlight Contamination in Amateur Telescope Snack Selection"

    # check with language not provided
    with patch("mex_invenio.services.schema.get_locale", return_value="de"):
        title = schema.get_title(pub)
        assert title == "Moonlight Contamination in Amateur Telescope Snack Selection"

    publication_year = schema.get_publication_year(pub)
    assert publication_year == "2002"

    with patch("mex_invenio.services.schema.get_locale", return_value="en"):
        journal = schema.get_journal(pub)
        assert journal == "The Observer-Independent Astrophysical Review"

    # when requested language exists
    with patch("mex_invenio.services.schema.get_locale", return_value="de"):
        journal = schema.get_journal(pub)
        assert journal == "Die beobachterunabhängige astrophysikalische Übersicht"

    issue = schema.get_issue(pub)
    assert issue == "Q3"

    pages = schema.get_pages(pub)
    assert pages == "10-12"

    doi = schema.get_doi(pub)
    assert doi == "10.1016/j.anaerobe.2016.04.006"

    with patch("mex_invenio.services.schema.get_locale", return_value="en"):
        abstract = schema.get_abstract(pub)
        assert (
            abstract
            == "While the influence of lunar illumination on astronomical observations has been extensively documented, its effect on observer behaviour remains understudied. This paper examines snack-selection patterns among amateur astronomers during 48 community observing sessions conducted under varying lunar phases. Results suggest a statistically significant increase in the consumption of pale-colored biscuits, vanilla confectionery, and lightly salted crackers during periods of high lunar brightness. Dark chocolate and heavily seasoned snacks were preferred during new-moon observations. Several competing explanations are considered, including visual availability, cultural associations, and unconscious attempts to maintain thematic consistency with the night sky. Although no causal mechanism is proposed, the persistence of the effect across multiple observing groups warrants further investigation and possibly a dedicated catering guideline for public star parties."
        )

    # all keywords should be returned regardles the user's language
    with patch("mex_invenio.services.schema.get_locale", return_value="en"):
        keywords = schema.get_keywords(pub)
        assert (
            keywords
            == "amateur astronomy, lunar illumination, observer behaviour, public observing sessions, food choice, Nachthimmel-Kultur, astronomische Öffentlichkeitsarbeit, Verhaltensastrophysik"
        )


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
    app.config["PREF_LABELS"] = pref_labels

    schema = BibSchema()
    pub = {"custom_fields": {"mex:bibliographicResourceType": [resource_type_url]}}
    result = schema.resolve_bibtex_type(pub)
    assert result == expected_type


def test_to_bibtex(app):
    app.config["PREF_LABELS"] = pref_labels

    schema = BibSchema()
    with patch("mex_invenio.services.schema.get_locale", return_value="en"):
        result = schema.to_bibtex(pub)

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
            "abstract = {While the influence of lunar illumination on astronomical observations has been extensively documented, its effect on observer behaviour remains understudied. This paper examines snack-selection patterns among amateur astronomers during 48 community observing sessions conducted under varying lunar phases. Results suggest a statistically significant increase in the consumption of pale-colored biscuits, vanilla confectionery, and lightly salted crackers during periods of high lunar brightness. Dark chocolate and heavily seasoned snacks were preferred during new-moon observations. Several competing explanations are considered, including visual availability, cultural associations, and unconscious attempts to maintain thematic consistency with the night sky. Although no causal mechanism is proposed, the persistence of the effect across multiple observing groups warrants further investigation and possibly a dedicated catering guideline for public star parties.},"
            in result
        )
        assert (
            "keywords = {amateur astronomy, lunar illumination, observer behaviour, public observing sessions, food choice, Nachthimmel-Kultur, astronomische Öffentlichkeitsarbeit, Verhaltensastrophysik}"
            in result
        )

        # Every field should use "name = {value}" format
        field_pattern = re.compile(r"^\s*\w+\s*=\s*\{.*\},?$")

        lines = result.splitlines()[1:-1]  # skip @book{... and final }
        for line in lines:
            assert field_pattern.match(line), f"Invalid field format: {line}"
