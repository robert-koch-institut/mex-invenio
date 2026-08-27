import json
from pathlib import Path

import pytest

import mex_invenio
from mex_invenio.config import (
    ENTITIES,
    EXT_IDS,
    FIELD_TYPES,
    FIELDS_LINKED_BACKWARDS,
    UI_SETTINGS,
)
from mex_invenio.config.settings import (
    CATEGORY_RULES,
    ENTITY_LABELS,
    EXT_ID_PREFIXES,
    MODELCONF,
)
from mex_invenio.config.ui_settings import (
    CategoryRule,
    Component,
    build_ext_ids,
    build_fields_linked_backwards,
    build_ui_settings,
)
from mex_invenio.custom_fields.custom_fields import RDM_CUSTOM_FIELDS

COLUMNS = ("main", "side_bar")


def validate(modelconf, categories, entity_labels):
    """Check that every rendering rule still matches the model config.

    This lives here rather than in the package because nothing at runtime calls it:
    build_ui_settings raises on its own for the rules it cannot do without, and the
    rest would only ever misrender a card, which is a thing for CI to catch, not a
    reason to stop the instance from booting.
    """
    ids = {
        category["id"]
        for entity in modelconf.values()
        for category in entity["categories"]
    }
    if missing := sorted(set(modelconf) - set(entity_labels)):
        message = f"entity_labels is missing: {', '.join(missing)}"
        raise ValueError(message)
    if unknown := sorted(set(categories) - ids):
        message = f"category rules name unknown categories: {', '.join(unknown)}"
        raise ValueError(message)

    for category_id, rule in categories.items():
        if rule.column not in (*COLUMNS, "header"):
            message = f"{category_id} names unknown column: {rule.column}"
            raise ValueError(message)
        _validate_properties(modelconf, category_id, rule)


def _validate_properties(modelconf, category_id, rule):
    """Raise if a rule names properties its category does not have."""
    for entity_type, entity in modelconf.items():
        categories = [
            category
            for category in entity["categories"]
            if category["id"] == category_id
        ]
        components = rule.components.get(entity_type)
        if not categories:
            # Not every entity type has every category; only components pinned to
            # this entity type make that a mistake.
            if components is not None:
                message = (
                    f"components names a category {entity_type} does not have: "
                    f"{category_id}"
                )
                raise ValueError(message)
            continue

        declared = set(categories[0]["properties"])
        if unknown := sorted(rule.backwards - declared):
            message = (
                f"{entity_type}.{category_id} declares backwards {unknown}, "
                f"which the model config does not list"
            )
            raise ValueError(message)

        if components is None:
            continue
        covered = {component.name for component in components}
        if covered != declared:
            message = (
                f"container {entity_type}.{category_id} covers {sorted(covered)}, "
                f"but the model config lists {sorted(declared)}"
            )
            raise ValueError(message)


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
def labels():
    return {"someEntity": "Some Entity"}


@pytest.fixture
def rules():
    return {
        "general": CategoryRule(column="header"),
        "aside": CategoryRule(column="side_bar"),
    }


def build(modelconf, rules, labels):
    return build_ui_settings(modelconf, entity_labels=labels, categories=rules)


def test_builds_expected_shape(modelconf, rules, labels):
    built = build(modelconf, rules, labels)

    assert list(built) == ["someentity"]
    assert built["someentity"]["label"] == "Some Entity"
    assert list(built["someentity"]["main"]) == ["cards"]
    assert list(built["someentity"]["side_bar"]) == ["aside"]


def test_header_category_is_not_a_card(modelconf, rules, labels):
    built = build(modelconf, rules, labels)["someentity"]

    titles = [card["title"] for card in {**built["main"], **built["side_bar"]}.values()]
    assert "General" not in titles


def test_categories_without_a_rule_are_plain_main_cards(modelconf, labels):
    built = build(modelconf, {}, labels)["someentity"]

    assert list(built["main"]) == ["general", "cards", "aside"]
    assert built["side_bar"] == {}
    assert "template" not in built["main"]["cards"]


def test_card_carries_title_icon_and_template(modelconf, rules, labels):
    rules["cards"] = CategoryRule(template="custom.html")

    card = build(modelconf, rules, labels)["someentity"]["main"]["cards"]

    assert card["title"] == "Cards"
    assert card["icon"] == "card.svg"
    assert card["template"] == "custom.html"


def test_special_fields_index_every_property(modelconf, rules, labels):
    special = build(modelconf, rules, labels)["someentity"]["special_fields"]

    assert special == {
        "TITLE": {"field": "mex:title"},
        "ONE": {"field": "mex:one"},
        "TWO": {"field": "mex:two"},
        "THREE": {"field": "mex:three"},
    }


def test_labels_are_derived_and_suppressed(modelconf, rules, labels):
    built = build(modelconf, rules, labels)["someentity"]

    assert built["main"]["cards"]["properties"] == [
        {"field": "mex:one", "label": "one.singular"},
        {"field": "mex:two", "label": "two.singular"},
    ]
    # a card with a single property renders it without a label
    assert built["side_bar"]["aside"]["properties"] == [{"field": "mex:three"}]


def test_backwards_marks_the_named_properties(modelconf, rules, labels):
    rules["cards"] = CategoryRule(backwards=frozenset({"two"}))

    assert build(modelconf, rules, labels)["someentity"]["main"]["cards"][
        "properties"
    ] == [
        {"field": "mex:one", "label": "one.singular"},
        {"field": "mex:two", "label": "two.singular", "is_backwards_linked": True},
    ]


def test_container_components(modelconf, rules, labels):
    rules["cards"] = CategoryRule(
        components={
            "someEntity": [
                Component(name="one", title="First"),
                Component(name="two", reverse=True),
            ]
        }
    )

    card = build(modelconf, rules, labels)["someentity"]["main"]["cards"]
    assert card["type"] == "container"
    assert "properties" not in card
    assert card["components"] == [
        {"type": "component", "title": "First", "properties": [{"field": "mex:one"}]},
        {
            "type": "component",
            "properties": [{"field": "mex:two", "is_backwards_linked": True}],
        },
    ]


def test_components_only_apply_to_their_entity_type(modelconf, rules, labels):
    rules["cards"] = CategoryRule(components={"otherEntity": [Component(name="one")]})

    card = build(modelconf, rules, labels)["someentity"]["main"]["cards"]
    assert "components" not in card
    assert [prop["field"] for prop in card["properties"]] == ["mex:one", "mex:two"]


def test_build_ext_ids_prefixes_the_field_names():
    assert build_ext_ids({"doi": ["https://doi.org/"]}) == {
        "mex:doi": {"prefixes": ["https://doi.org/"]}
    }


def test_build_fields_linked_backwards_collects_both_shapes(modelconf):
    rules = {
        "cards": CategoryRule(
            components={
                "someEntity": [
                    Component(name="one", reverse=True),
                    Component(name="two"),
                ]
            }
        ),
        "aside": CategoryRule(backwards=frozenset({"three"})),
    }

    assert build_fields_linked_backwards(modelconf, rules) == {
        "someentity": ["mex:one", "mex:three"]
    }


def test_build_fields_linked_backwards_skips_types_without_any(modelconf):
    assert build_fields_linked_backwards(modelconf, {}) == {}


@pytest.mark.parametrize(
    ("labels_override", "rules_override", "message"),
    [
        ({}, {}, "entity_labels is missing"),
        (None, {"nope": CategoryRule()}, "unknown categories"),
        (None, {"cards": CategoryRule(column="middle")}, "unknown column"),
        (
            None,
            {"cards": CategoryRule(backwards=frozenset({"nope"}))},
            "which the model config does not list",
        ),
        (
            None,
            {"cards": CategoryRule(components={"someEntity": [Component("one")]})},
            "but the model config lists",
        ),
    ],
)
def test_validate_rejects_drift(
    modelconf, rules, labels, labels_override, rules_override, message
):
    with pytest.raises(ValueError, match=message):
        validate(
            modelconf,
            {**rules, **rules_override},
            labels if labels_override is None else labels_override,
        )


def test_instance_config_matches_modelconf():
    """The shipped settings expand the shipped model config without drift."""
    validate(MODELCONF, CATEGORY_RULES, ENTITY_LABELS)

    assert set(UI_SETTINGS) == {name.lower() for name in MODELCONF}
    for entity_type, entity in MODELCONF.items():
        built = UI_SETTINGS[entity_type.lower()]
        cards = {**built["main"], **built["side_bar"]}
        expected = {
            category["id"]
            for category in entity["categories"]
            if CATEGORY_RULES.get(category["id"], CategoryRule()).column != "header"
        }
        assert set(cards) == expected


def test_no_property_appears_in_two_categories():
    """special_fields aliases every property once, so a repeat would be ambiguous."""
    for entity_type, entity in MODELCONF.items():
        names = [
            name for category in entity["categories"] for name in category["properties"]
        ]
        assert len(names) == len(set(names)), f"{entity_type} repeats a property"


def test_instance_special_fields_resolve_template_aliases():
    """Aliases the landing-page templates address must exist."""
    assert UI_SETTINGS["resource"]["special_fields"]["ACCESS_RESTRICTION"] == {
        "field": "mex:accessRestriction"
    }
    for entity_type in ("resource", "activity", "bibliographicresource"):
        assert "TITLE" in UI_SETTINGS[entity_type]["special_fields"]
        assert "ALTERNATIVE_TITLE" in UI_SETTINGS[entity_type]["special_fields"]


def test_instance_derived_config():
    assert build_ext_ids(EXT_ID_PREFIXES) == EXT_IDS
    assert EXT_IDS["mex:doi"]["prefixes"][0].startswith("https://")
    assert FIELDS_LINKED_BACKWARDS["resource"] == ["mex:isPartOf", "mex:usedIn"]


def test_entities_excludes_non_entity_types():
    """The vocabulary descriptors are not entity types and must not be listed."""
    assert "concept" not in ENTITIES
    assert "concept-scheme" not in ENTITIES
    assert "consent" not in ENTITIES
    assert "primary-source" not in ENTITIES
    assert {"resource", "activity", "bibliographic-resource"} <= set(ENTITIES)


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
