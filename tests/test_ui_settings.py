import json
from pathlib import Path

import pytest

import mex_invenio
from mex_invenio.config import (
    EXT_IDS,
    FIELD_TYPES,
    FIELDS_LINKED_BACKWARDS,
    UI_SETTINGS,
)
from mex_invenio.config.settings import MODELCONF, RENDERING_RULES
from mex_invenio.config.ui_settings import (
    Component,
    RenderingRules,
    build_ext_ids,
    build_fields_linked_backwards,
    build_ui_settings,
    validate,
)
from mex_invenio.custom_fields.custom_fields import RDM_CUSTOM_FIELDS


@pytest.fixture
def modelconf():
    return {
        "someEntity": {
            "categories": [
                {
                    "id": "general",
                    "title": "General",
                    "icon": "some",
                    "properties": ["title"],
                },
                {
                    "id": "cards",
                    "title": "Cards",
                    "icon": "card",
                    "properties": ["one", "two"],
                },
                {
                    "id": "aside",
                    "title": "Aside",
                    "icon": "aside",
                    "properties": ["three"],
                },
            ]
        }
    }


@pytest.fixture
def rules():
    return RenderingRules(
        entity_labels={"someEntity": "Some Entity"},
        header_category="general",
        sidebar_categories=frozenset({"aside"}),
    )


def test_builds_expected_shape(modelconf, rules):
    built = build_ui_settings(modelconf, rules)

    assert list(built) == ["someentity"]
    assert built["someentity"]["label"] == "Some Entity"
    assert list(built["someentity"]["main"]) == ["cards"]
    assert list(built["someentity"]["side_bar"]) == ["aside"]


def test_header_category_is_not_a_card(modelconf, rules):
    built = build_ui_settings(modelconf, rules)["someentity"]

    titles = [card["title"] for card in {**built["main"], **built["side_bar"]}.values()]
    assert "General" not in titles


def test_special_fields_index_every_property(modelconf, rules):
    special = build_ui_settings(modelconf, rules)["someentity"]["special_fields"]

    assert special == {
        "TITLE": {"field": "mex:title"},
        "ONE": {"field": "mex:one"},
        "TWO": {"field": "mex:two"},
        "THREE": {"field": "mex:three"},
    }


def test_labels_are_derived_and_suppressed(modelconf, rules):
    built = build_ui_settings(modelconf, rules)["someentity"]

    assert built["main"]["cards"]["properties"] == [
        {"field": "mex:one", "label": "one.singular"},
        {"field": "mex:two", "label": "two.singular"},
    ]
    # a card with a single property renders it without a label
    assert built["side_bar"]["aside"]["properties"] == [{"field": "mex:three"}]


def test_folded_properties_replace_their_group(modelconf, rules):
    modelconf["someEntity"]["categories"][1]["properties"] = ["one", "two", "three"]
    folded = RenderingRules(
        **{
            **rules.__dict__,
            "folded_properties": {("one", "two"): {"field": "fn", "label": "Folded"}},
        }
    )

    props = build_ui_settings(modelconf, folded)["someentity"]["main"]["cards"]
    assert props["properties"] == [
        {"field": "fn", "label": "Folded"},
        {"field": "mex:three", "label": "three.singular"},
    ]


def test_container_components(modelconf, rules):
    container = RenderingRules(
        **{
            **rules.__dict__,
            "container_components": {
                ("someEntity", "cards"): [
                    Component(name="one", title="First"),
                    Component(name="two", reverse=True),
                ]
            },
        }
    )

    card = build_ui_settings(modelconf, container)["someentity"]["main"]["cards"]
    assert card["type"] == "container"
    assert "properties" not in card
    assert card["components"] == [
        {"type": "component", "title": "First", "properties": [{"field": "mex:one"}]},
        {
            "type": "component",
            "properties": [{"field": "mex:two", "is_backwards_linked": True}],
        },
    ]


def test_build_ext_ids_prefixes_the_field_names():
    rules = RenderingRules(ext_id_prefixes={"doi": ["https://doi.org/"]})

    assert build_ext_ids(rules) == {"mex:doi": {"prefixes": ["https://doi.org/"]}}


def test_build_fields_linked_backwards_collects_both_shapes():
    ui_settings = {
        "someentity": {
            "main": {
                "container": {
                    "components": [
                        {
                            "properties": [
                                {"field": "mex:one", "is_backwards_linked": True}
                            ]
                        }
                    ]
                }
            },
            "side_bar": {
                "plain": {
                    "properties": [{"field": "mex:two", "is_backwards_linked": True}]
                },
                "forward": {"properties": [{"field": "mex:three"}]},
            },
        }
    }

    assert build_fields_linked_backwards(ui_settings) == {
        "someentity": ["mex:one", "mex:two"]
    }


@pytest.mark.parametrize(
    ("attribute", "value", "message"),
    [
        ("entity_labels", {}, "entity_labels is missing"),
        ("header_category", "nope", "header_category names unknown"),
        ("sidebar_categories", frozenset({"nope"}), "sidebar_categories names unknown"),
        ("card_templates", {"nope": "x.html"}, "card_templates names unknown"),
        (
            "no_label_categories",
            frozenset({"nope"}),
            "no_label_categories names unknown",
        ),
        ("label_overrides", {"nope": "Nope"}, "unknown properties"),
    ],
)
def test_validate_rejects_drift(modelconf, rules, attribute, value, message):
    broken = RenderingRules(**{**rules.__dict__, attribute: value})

    with pytest.raises(ValueError, match=message):
        validate(modelconf, broken)


def test_validate_rejects_partial_container(modelconf, rules):
    broken = RenderingRules(
        **{
            **rules.__dict__,
            "container_components": {
                ("someEntity", "cards"): [Component(name="one")],
            },
        }
    )

    with pytest.raises(ValueError, match="but the model config lists"):
        validate(modelconf, broken)


def test_instance_config_matches_modelconf():
    """The shipped settings expand the shipped model config without drift."""
    validate(MODELCONF, RENDERING_RULES)

    assert set(UI_SETTINGS) == {name.lower() for name in MODELCONF}
    for entity_type, entity in MODELCONF.items():
        built = UI_SETTINGS[entity_type.lower()]
        cards = {**built["main"], **built["side_bar"]}
        expected = {
            category["id"]
            for category in entity["categories"]
            if category["id"] != RENDERING_RULES.header_category
        }
        assert set(cards) == expected


def test_instance_special_fields_resolve_template_aliases():
    """Aliases the landing-page templates address must exist."""
    assert UI_SETTINGS["resource"]["special_fields"]["ACCESS_RESTRICTION"] == {
        "field": "mex:accessRestriction"
    }
    for entity_type in ("resource", "activity", "bibliographicresource"):
        assert "TITLE" in UI_SETTINGS[entity_type]["special_fields"]
        assert "ALTERNATIVE_TITLE" in UI_SETTINGS[entity_type]["special_fields"]


def test_instance_derived_config():
    assert EXT_IDS["mex:doi"]["prefixes"][0].startswith("https://")
    assert FIELDS_LINKED_BACKWARDS["resource"] == ["mex:isPartOf", "mex:usedIn"]


def test_every_rendered_property_has_a_custom_field():
    """A property in modelconf.json renders nothing without a custom field behind it."""
    custom_fields = {cf.name for cf in RDM_CUSTOM_FIELDS}
    rendered = {
        f"mex:{name}"
        for entity in MODELCONF.values()
        for category in entity["categories"]
        for name in category["properties"]
    }

    assert rendered - custom_fields == set()


def test_identifier_properties_are_in_the_linked_records_mapping():
    """The record mapping is ``dynamic: strict``, inherited by ``linked_records``.

    MexDumper emits ``display_data.linked_records["mex:<field>"]`` for every
    identifier-typed field, so a missing mapping entry makes OpenSearch reject the
    whole document instead of dropping the field.
    """
    mapping_path = (
        Path(mex_invenio.__file__).parent
        / "records/mappings/os-v2/mexrecords/records/record-v8.0.0.json"
    )
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    linked_records = mapping["mappings"]["properties"]["display_data"]["properties"][
        "linked_records"
    ]
    mapped = set(linked_records["properties"])

    identifiers = {
        f"mex:{name}"
        for entity_type, entity in MODELCONF.items()
        for category in entity["categories"]
        for name in category["properties"]
        if FIELD_TYPES.get(entity_type.lower(), {}).get(f"mex:{name}") == "identifier"
    }

    assert identifiers
    assert identifiers - mapped == set()
