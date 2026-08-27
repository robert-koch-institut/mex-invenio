"""Expand ``modelconf.json`` into the ``UI_SETTINGS`` structure used by the templates.

``modelconf.json`` is the single source of truth for *which* MEx fields a record type
shows and *how they are grouped*: entity type -> categories -> ordered property names.
Everything else the landing pages need -- which column a card sits in, which template
renders it, which of its properties link backwards -- is a rendering decision, declared
per category as a :class:`CategoryRule` in ``settings.py``. Categories without a rule
render as a plain card in the main column, which is most of them.

An entity label or a rule naming a column that does not exist raises here, because the
build cannot go on without them. Everything else would only misrender a card, so it is
checked by tests/test_ui_settings.py rather than at import.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from mex_invenio.transform import dromedary_to_snake, ensure_prefix

MEX_PREFIX = "mex:"
ICON_SUFFIX = ".svg"
HEADER_COLUMN = "header"
COLUMNS = ("main", "side_bar")
MODELCONF_PATH = Path(__file__).parent / "modelconf.json"

Property = dict[str, Any]
Card = dict[str, Any]
Entity = dict[str, Any]


@dataclass(frozen=True)
class Component:
    """One titled sub-block of a container card.

    Attributes:
        name: Property name, as written in ``modelconf.json``.
        title: Sub-heading shown above the value, or None to render it untitled.
        reverse: Whether the property links backwards, i.e. names records that point
            at this one instead of the other way around.
    """

    name: str
    title: str | None = None
    reverse: bool = False


@dataclass(frozen=True)
class CategoryRule:
    """How one category of ``modelconf.json`` renders.

    Attributes:
        column: ``"main"``, ``"side_bar"``, or ``"header"`` for the category the page
            chrome renders itself instead of as a card.
        template: Template rendering the card, when the generic ``card.html`` will not
            do.
        components: Entity type -> the sub-blocks of a container card. A category with
            components for an entity type renders as a container for that type.
        backwards: Names of properties in this category that link backwards, i.e. that
            name records pointing at this one.
    """

    column: str = "main"
    template: str | None = None
    components: dict[str, list[Component]] = field(default_factory=dict)
    backwards: frozenset[str] = frozenset()


DEFAULT_RULE = CategoryRule()


def load_modelconf(path: Path = MODELCONF_PATH) -> dict[str, Any]:
    """Read the model config.

    Args:
        path: Location of the JSON file, defaulting to the one next to this module.

    Returns:
        Entity type -> ``{"categories": [...]}``, in declaration order.
    """
    with path.open(encoding="utf-8") as handle:
        modelconf: dict[str, Any] = json.load(handle)
    return modelconf


def _build_property(name: str, *, labelled: bool, backwards: bool) -> Property:
    """Build one property entry of a card."""
    prop: Property = {"field": ensure_prefix(name, MEX_PREFIX)}
    if labelled:
        prop["label"] = f"{name}.singular"
    if backwards:
        prop["is_backwards_linked"] = True
    return prop


def _build_components(components: list[Component]) -> list[dict[str, Any]]:
    """Build the sub-blocks of a container card."""
    built: list[dict[str, Any]] = []
    for component in components:
        prop: Property = {"field": ensure_prefix(component.name, MEX_PREFIX)}
        if component.reverse:
            prop["is_backwards_linked"] = True
        block: dict[str, Any] = {"type": "component"}
        if component.title is not None:
            block["title"] = component.title
        block["properties"] = [prop]
        built.append(block)
    return built


def _build_card(
    category: dict[str, Any],
    *,
    entity_type: str,
    rule: CategoryRule,
) -> Card:
    """Build one card from one category of the model config."""
    card: Card = {
        "title": category["title"],
        "icon": f"{category['icon']}{ICON_SUFFIX}",
    }
    if rule.template is not None:
        card["template"] = rule.template

    if components := rule.components.get(entity_type):
        card["type"] = "container"
        card["components"] = _build_components(components)
        return card

    names: list[str] = category["properties"]
    # A card with a single property needs no label -- its title already says what the
    # value is.
    labelled = len(names) > 1
    card["properties"] = [
        _build_property(name, labelled=labelled, backwards=name in rule.backwards)
        for name in names
    ]
    return card


def _build_special_fields(entity: dict[str, Any]) -> Entity:
    """Build the alias index templates address single fields by.

    Every field of the entity type gets an alias, so ``special_field("SOME_FIELD")``
    resolves regardless of which category the field is shown in.
    """
    return {
        dromedary_to_snake(name).upper(): {"field": ensure_prefix(name, MEX_PREFIX)}
        for category in entity["categories"]
        for name in category["properties"]
    }


def build_ui_settings(
    modelconf: dict[str, Any],
    *,
    entity_labels: dict[str, str],
    categories: dict[str, CategoryRule],
) -> dict[str, Entity]:
    """Expand the model config into the settings the landing-page templates read.

    Args:
        modelconf: Parsed ``modelconf.json``, as returned by :func:`load_modelconf`.
        entity_labels: Entity type -> msgid for the record-type tag.
        categories: Category id -> how it renders. Ids without an entry render as a
            plain card in the main column.

    Returns:
        Invenio resource type -> ``{label, special_fields, main, side_bar}``.
    """
    settings: dict[str, Entity] = {}
    for entity_type, entity in modelconf.items():
        built: Entity = {
            "label": entity_labels[entity_type],
            "special_fields": _build_special_fields(entity),
            "main": {},
            "side_bar": {},
        }
        for category in entity["categories"]:
            rule = categories.get(category["id"], DEFAULT_RULE)
            if rule.column == HEADER_COLUMN:
                continue
            built[rule.column][category["id"]] = _build_card(
                category, entity_type=entity_type, rule=rule
            )
        settings[entity_type.lower()] = built
    return settings


def build_ext_ids(prefixes: dict[str, list[str]]) -> dict[str, dict[str, list[str]]]:
    """Build the external-id lookup used to shorten URLs for display.

    Args:
        prefixes: Property name -> URL prefixes stripped when the value is displayed.

    Returns:
        Custom field name -> ``{"prefixes": [...]}``.
    """
    return {
        ensure_prefix(name, MEX_PREFIX): {"prefixes": list(values)}
        for name, values in prefixes.items()
    }


def build_fields_linked_backwards(
    modelconf: dict[str, Any],
    categories: dict[str, CategoryRule],
) -> dict[str, list[str]]:
    """Collect the backwards-linked fields per record type.

    Args:
        modelconf: Parsed ``modelconf.json``, as returned by :func:`load_modelconf`.
        categories: Category id -> how it renders.

    Returns:
        Invenio resource type -> custom field names, for types that have any.
    """
    linked: dict[str, list[str]] = {}
    for entity_type, entity in modelconf.items():
        fields: list[str] = []
        for category in entity["categories"]:
            rule = categories.get(category["id"], DEFAULT_RULE)
            names = [
                component.name
                for component in rule.components.get(entity_type, [])
                if component.reverse
            ]
            names += [name for name in category["properties"] if name in rule.backwards]
            fields += [
                prefixed
                for name in names
                if (prefixed := ensure_prefix(name, MEX_PREFIX)) not in fields
            ]
        if fields:
            linked[entity_type.lower()] = fields
    return linked
