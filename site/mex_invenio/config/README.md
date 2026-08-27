# 🧩 Configuration Documentation Template

This document describes the configuration constants used for defining entity display settings, export options, and related behavior.

## ⚙️ Constants Overview

| Constant                           |	Type	        | Purpose
|------------------------------------|------------------|-------------------------------------------------------------------------------------------------------------------------
|`MODELCONF`                         |	dict            |	Parsed `modelconf.json` — the source of truth for *which* `mex:` fields a record type shows and how they are grouped into categories.
|`ENTITY_LABELS`                     |	dict[str, str]  |	Entity type → msgid for the record-type tag shown on the landing page.
|`CATEGORY_RULES`                    |	dict[str, CategoryRule] |	Category id → how it renders (column, template, container components, backwards links). Only categories that need something other than a plain main-column card are listed.
|`UI_SETTINGS`                       |	dict            |	**Generated** from `MODELCONF` + `ENTITY_LABELS` + `CATEGORY_RULES` by `build_ui_settings()`. This is what the landing-page templates read. Do not edit it directly.
|`CORE_ENTITY_TYPES`                 |	list[str]       |	The record types that get a landing page of their own, derived from `UI_SETTINGS`.
|`EXT_ID_PREFIXES`                   |	dict[str, list[str]] |	Property name → URL prefixes stripped when an external identifier is displayed. Expands into `EXT_IDS`.
|`ACCESS_COLOR_MAP`                  |	dict[str, str]  |	`mex:accessRestriction` vocabulary value → background colour of the access tag on the landing page.
|`APP_RDM_DETAIL_SIDE_BAR_TEMPLATES` |	list[str]       |	Lists custom templates for invenio standard side bar cards. Only the standard Invenio side bar cards are included. Templates are placed in `/templates/semantic-ui/invenio_app_rdm/records/details/side_bar`
|`APP_RDM_RECORD_EXPORTERS`          |	dict[str, dict] |	Configures available data export formats (e.g. JSON, CSV), including serializer, filename pattern, and MIME type.
|`ENTITIES`                          |	list[str]       |	Entity types of the MEx model, derived from `mex.model.ENTITY_JSON_BY_NAME` minus `UNPUBLISHED_ENTITIES`. Note `concept` / `concept-scheme` are vocabulary descriptors, not entity types, and are absent by construction.
|`TITLE_FIELDS`                      |	list[str]       |	Ordered list of field names used to derive a display title for a record (checked in sequence).
|`DISCLAIMER`                        |	str             |	Generic disclaimer text displayed below metadata, stating that information is provided as-is.


## 🧱 UI_SETTINGS

`UI_SETTINGS` defines the configuration for the core landing pages — including layout (the main section and the side bar), field mapping, icons, labels, and templates.
Each core record's landing page (i.e. "resource", "activity", "bibliographicresource") has its own configuration object.

> ⚠️ **`UI_SETTINGS` is generated, not written.** `build_ui_settings()` in `ui_settings.py`
> expands it from two inputs. The sections below document the *output* shape, which is what
> the templates read; to change what a landing page shows, edit one of the inputs instead:
>
> | To change… | Edit |
> |---|---|
> | which fields a record type shows, their order, which category they sit in, a category's title or icon | `modelconf.json` |
> | a category's column, its card template, its container sub-blocks, or which of its properties link backwards | `CATEGORY_RULES` in `settings.py` |
> | the record-type tag | `ENTITY_LABELS` in `settings.py` |
> | a property's label | nothing here — labels are derived as `"<property>.singular"` and resolved from the translation catalogs. A missing label means a missing msgid; add it to `translations/{de,en}/LC_MESSAGES/ui.po`. |
>
> A card with exactly one property renders it without a label, since the card title already
> says what the value is. `tests/test_ui_settings.py` checks every rule against
> `modelconf.json`.

### 🧩 Structure Overview

```
UI_SETTINGS = {
    "<core_record_type>": {
        "label": "<Display label>",
        "special_fields": { ... },
        "main": { ... },
        "side_bar": { ... },
    },
    ...
}
```

### 🧭 Entity Configuration Structure

Each entity configuration (e.g. `UI_SETTINGS["resource"]`) includes the following keys:

Key             |  Required  |  Type             |  Description
----------------|------------|-------------------|------------------------
label           |  ✓         |  str              |  User-facing label for this type of records (e.g "Publication")
special_fields  |  ✓         |  dict[str, dict]  |  fields used in the template outside of the cards, these are not automatically added to the template but require custom implementation
main            |  ✓         |  dict[str, dict]  |  Cards in the main section of the landing page
right           |  ✓         |  dict[str, dict]  |  Cards displayed in the side bar (right column) of the record details page - only custom cards are listed here; standard Invenio cards are listed in the `APP_RDM_DETAIL_SIDE_BAR_TEMPLATES` (see: Constants Overview)

### 🧩 special_fields

These fields appear in the template outside of the cards. They are **not** added automatically and must be implemented manually.

```
"special_fields": {
    "TITLE": {"field": "mex:title"},
    "DESCRIPTION": {"field": "mex:description"},
    "ACCESS_RESTRICTION": {"field": "mex:accessRestriction"},
    ...
}
```

Key                  |  Required  |  Type       |  Description
---------------------|------------|-------------|----------------
_key_                   |  ✓         |  str        |  Internal identifier for a special field (e.g. "TITLE", "LANGUAGE")
field                |  ✓         |  str        |  Metadata field (e.g. "mex:title")

Every property of the entity type gets an alias, derived from its name in `modelconf.json`
(`alternativeTitle` → `ALTERNATIVE_TITLE`), so `special_field("SOME_FIELD")` resolves
regardless of which category the field is shown in.

#### ✨ ACCESS RESTRICTION COLOUR MAP

The background colour of the access tag comes from the top-level `ACCESS_COLOR_MAP`, keyed by
the `mex:accessRestriction` vocabulary value the record carries — not from `special_fields`.

### 🧩 Cards

Cards are listed per columns: main section and the side bar. Only custom cards are listed in the side bar (standard Invenio cards are listed in the `APP_RDM_DETAIL_SIDE_BAR_TEMPLATES`; see: Constants Overview)

```
"<card_id>": {
    "title": "<Card title>",
    "icon": "<icon file name>",
    "template": "<optional Jinja template>",
    "type": "container" | "component",  # optional; determines grouping
    "properties": [ ... ],
    "components": [ ... ],
}

```

Key                  |  Required  |  Type                        |  Description
---------------------|------------|------------------------------|----------------
<card_id>            |  ✓         |  str                         |  Identifier of the section (e.g. "creators", "theme")
title                |  ✓         |  str                         |  Section title shown in UI
icon                 |  ✓         |  str                         |  Icon filename (e.g. "creators.svg")
template             |  -         |  str                         |  Custom HTML template to render this section, relative templates should be placed in `/templates/semantic-ui/invenio_app_rdm/records/details/components/cards/`
type                 |  -         |  "container" or "component"  |  Used for nested structures. "container" groups multiple cards; "component" defines a sub-block inside a container. For "regular" cards omit this property
properties           |  ✓         |  list[dict]                  |  List of metadata fields rendered in this card (see below).
components           |  ✓ (**only** for cards of `type="container"`)         |  list[dict]                  |  list of nested cards, each with its own title and properties (icons are not supported in component cards)

## 🧩 properties

Each entry in a properties list defines one metadata field and its display options.

```
"properties": [
    {"field": "mex:creator", "label": "Author"},
    {"field": "mex:license", "label": "License"},
]
```

Key                             |  required  |  Type                  |  Description
--------------------------------|------------|------------------------|----------
field                           |  ✓         |  str                   |  Metadata field (e.g. `mex:creator`)
label                           |  -         |  str                   |  Custom UI label to display; if no label is provided, the values will be displayed without a label
is_backwards_linked             |  -         |  bool                  |  Marks that the field represents a reverse relationship (e.g. record listed as `partOf` another record). Set from a category's `backwards`, or from a container component's `reverse`.

### 🧾 Example of the generated structure

Below is a minimal entity block as `build_ui_settings()` would emit it, illustrating all supported keys and options:

```
UI_SETTINGS = {
    "example_entity": {
        "label": "Example Entity",
        "special_fields": {
            "TITLE": {"field": "mex:title"},
            "DESCRIPTION": {"field": "mex:description"},
        },
        "main": {
            "basic_info": {
                "title": "Basic Information",
                "icon": "info.svg",
                "properties": [
                    {"field": "mex:title", "label": "Title"},
                    {"field": "mex:description", "label": "Description"},
                ],
            },
            "relations": {
                "type": "container",
                "title": "Relations",
                "icon": "relations.svg",
                "components": [
                    {
                        "type": "component",
                        "title": "Part Of",
                        "properties": [{"field": "mex:isPartOf"}],
                    },
                    {
                        "type": "component",
                        "title": "Includes",
                        "properties": [{"field": "mex:includes", "is_backwards_linked": True}],
                    },
                ],
            },
        },
        "right": {
            "contact": {
                "title": "Contact",
                "template": "contact.html",
                "icon": "contact.svg",
                "properties": [{"field": "mex:contact"}],
            },
        },
    },
}
```
