"""Expand ``modelconf.json`` into the ``UI_SETTINGS`` structure used by the templates.

``modelconf.json`` is the single source of truth for *which* MEx fields a record type
shows and *how they are grouped*: entity type -> categories -> ordered property names.
Everything else the landing pages need -- which column a card sits in, which template
renders it, labels, external-id prefixes, backwards links -- is a rendering decision and
is declared in :class:`RenderingRules` by ``settings.py``.

The rules the build needs -- a category's id, an entity's label -- raise KeyError here
if they drift. The cosmetic ones would only misrender a card, so they are checked by
tests/test_ui_settings.py rather than at import.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from mex_invenio.transform import dromedary_to_snake, ensure_prefix

MEX_PREFIX = "mex:"
ICON_SUFFIX = ".svg"
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
class RenderingRules:
    """Rendering decisions that ``modelconf.json`` deliberately does not carry.

    Attributes:
        entity_labels: Entity type -> msgid for the record-type tag.
        header_category: Id of the category rendered by the page chrome instead of
            as a card.
        sidebar_categories: Ids of the categories rendered in the sidebar column.
        card_templates: Category id -> template file rendering it.
        no_label_categories: Ids of categories whose properties render unlabelled.
        label_overrides: Property name -> msgid, where the derived one does not exist.
        folded_properties: Property names collapsed into one synthetic property by
            their card template, mapped to that property.
        container_components: (entity type, category id) -> its sub-blocks.
        backwards_linked: Entity type -> property names that link backwards, outside
            of container categories.
        ext_id_prefixes: Property name -> URL prefixes stripped for display.
    """

    entity_labels: dict[str, str] = field(default_factory=dict)
    header_category: str = ""
    sidebar_categories: frozenset[str] = frozenset()
    card_templates: dict[str, str] = field(default_factory=dict)
    no_label_categories: frozenset[str] = frozenset()
    label_overrides: dict[str, str] = field(default_factory=dict)
    folded_properties: dict[tuple[str, ...], Property] = field(default_factory=dict)
    container_components: dict[tuple[str, str], list[Component]] = field(
        default_factory=dict
    )
    backwards_linked: dict[str, list[str]] = field(default_factory=dict)
    ext_id_prefixes: dict[str, list[str]] = field(default_factory=dict)

    @property
    def synthetic_properties(self) -> dict[str, Property]:
        """Synthetic field name -> the property replacing a folded group."""
        return {prop["field"]: prop for prop in self.folded_properties.values()}


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


def _property_names(category: dict[str, Any]) -> list[str]:
    """Return the property names of one category, in render order."""
    names: list[str] = category["properties"]
    return names


def _entity_properties(entity: dict[str, Any]) -> list[str]:
    """Return every property name of one entity type, in render order."""
    names: list[str] = []
    for category in entity["categories"]:
        names.extend(name for name in _property_names(category) if name not in names)
    return names


def _fold(names: list[str], rules: RenderingRules) -> list[str]:
    """Collapse folded groups into their synthetic property name."""
    present = set(names)
    consumed: set[str] = set()
    folded: list[str] = []
    for name in names:
        if name in consumed:
            continue
        for group, replacement in rules.folded_properties.items():
            if name in group and set(group) <= present:
                consumed.update(group)
                folded.append(replacement["field"])
                break
        else:
            folded.append(name)
    return folded


def _build_property(
    name: str,
    *,
    entity_type: str,
    labelled: bool,
    rules: RenderingRules,
) -> Property:
    """Build one property entry of a card."""
    synthetic = rules.synthetic_properties.get(name)
    if synthetic is not None:
        return dict(synthetic)
    prop: Property = {"field": ensure_prefix(name, MEX_PREFIX)}
    if labelled:
        prop["label"] = rules.label_overrides.get(name, f"{name}.singular")
    if name in rules.backwards_linked.get(entity_type, []):
        prop["is_backwards_linked"] = True
    if name in rules.ext_id_prefixes:
        prop["prefixes"] = list(rules.ext_id_prefixes[name])
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
    rules: RenderingRules,
) -> Card:
    """Build one card from one category of the model config."""
    category_id = category["id"]
    card: Card = {
        "title": category["title"],
        "icon": f"{category['icon']}{ICON_SUFFIX}",
    }
    if category_id in rules.card_templates:
        card["template"] = rules.card_templates[category_id]

    components = rules.container_components.get((entity_type, category_id))
    if components is not None:
        card["type"] = "container"
        card["components"] = _build_components(components)
        return card

    names = _fold(_property_names(category), rules)
    labelled = len(names) > 1 and category_id not in rules.no_label_categories
    card["properties"] = [
        _build_property(name, entity_type=entity_type, labelled=labelled, rules=rules)
        for name in names
    ]
    return card


def _build_special_fields(entity: dict[str, Any], rules: RenderingRules) -> Entity:
    """Build the alias index templates address single fields by.

    Every field of the entity type gets an alias, so ``special_field("SOME_FIELD")``
    resolves regardless of which category the field is shown in.
    """
    special: Entity = {}
    for name in _entity_properties(entity):
        alias = dromedary_to_snake(name).upper()
        special[alias] = {"field": ensure_prefix(name, MEX_PREFIX)}
        if name in rules.ext_id_prefixes:
            special[alias]["prefixes"] = list(rules.ext_id_prefixes[name])
    return special


def build_ui_settings(
    modelconf: dict[str, Any],
    rules: RenderingRules,
) -> dict[str, Entity]:
    """Expand the model config into the settings the landing-page templates read.

    Args:
        modelconf: Parsed ``modelconf.json``, as returned by :func:`load_modelconf`.
        rules: The rendering decisions to apply.

    Returns:
        Invenio resource type -> ``{label, special_fields, main, side_bar}``.

    Note:
        Rules are not checked here. A rule the build needs raises KeyError; the rest
        are covered by tests/test_ui_settings.py.
    """
    settings: dict[str, Entity] = {}
    for entity_type, entity in modelconf.items():
        built: Entity = {
            "label": rules.entity_labels[entity_type],
            "special_fields": _build_special_fields(entity, rules),
            "main": {},
            "side_bar": {},
        }
        for category in entity["categories"]:
            category_id = category["id"]
            if category_id == rules.header_category:
                continue
            column = "side_bar" if category_id in rules.sidebar_categories else "main"
            built[column][category_id] = _build_card(
                category, entity_type=entity_type, rules=rules
            )
        settings[entity_type.lower()] = built
    return settings


def build_ext_ids(rules: RenderingRules) -> dict[str, dict[str, list[str]]]:
    """Build the external-id lookup used to shorten URLs for display.

    Args:
        rules: The rendering decisions holding the prefixes.

    Returns:
        Custom field name -> ``{"prefixes": [...]}``.
    """
    return {
        ensure_prefix(name, MEX_PREFIX): {"prefixes": list(prefixes)}
        for name, prefixes in rules.ext_id_prefixes.items()
    }


def build_fields_linked_backwards(
    ui_settings: dict[str, Entity],
) -> dict[str, list[str]]:
    """Collect the backwards-linked fields per record type.

    Args:
        ui_settings: The expanded settings, as returned by :func:`build_ui_settings`.

    Returns:
        Invenio resource type -> custom field names, for types that have any.
    """
    linked: dict[str, list[str]] = {}
    for entity_type, entity in ui_settings.items():
        fields: list[str] = []
        for column in ("main", "side_bar"):
            for card in entity[column].values():
                properties = list(card.get("properties", []))
                for component in card.get("components", []):
                    properties.extend(component["properties"])
                fields.extend(
                    prop["field"]
                    for prop in properties
                    if prop.get("is_backwards_linked") and prop["field"] not in fields
                )
        if fields:
            linked[entity_type] = fields
    return linked
