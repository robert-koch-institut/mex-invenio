# 🧩 Configuration Documentation Template

This document describes the configuration constants used for defining entity display settings, export options, and related behavior.

## ⚙️ Constants Overview

| Constant                           |	Type	        | Purpose                                                                                                                 
|------------------------------------|------------------|-------------------------------------------------------------------------------------------------------------------------
|`UI_SETTINGS`                       |	dict            |	Defines the configuration for the core landing pages (i.e. `resource`, `activity`, `bibliographicresource`) are displayed in the user interface — including labels, fields, icons, cards, and templates.
|`APP_RDM_DETAIL_SIDE_BAR_TEMPLATES` |	list[str]       |	Lists custom templates for invenio standard side bar cards. Only the standard Invenio side bar cards are included. Templates are placed in `/templates/semantic-ui/invenio_app_rdm/records/details/side_bar`
|`APP_RDM_RECORD_EXPORTERS`          |	dict[str, dict] |	Configures available data export formats (e.g. JSON, CSV), including serializer, filename pattern, and MIME type.
|`ENTITIES`                          |	list[str]       |	Lists all entity types recognized by the MEX data model. Used for validation and filtering.
|`TITLE_FIELDS`                      |	list[str]       |	Ordered list of field names used to derive a display title for a record (checked in sequence).
|`DISCLAIMER`                        |	str             |	Generic disclaimer text displayed below metadata, stating that information is provided as-is.


## 🧱 UI_SETTINGS

`UI_SETTINGS` defines the configuration for core the landing pages — including layout (the main section and the side bar), field mapping, icons, labels, and templates.
Each core record's landing page (i.e. "resource", "activity", "bibliographicresource") has its own configuration object.

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
prefixes             |  -         |  list[str]  |  List of recognised URI prefixes for external link values (used to extract the display value (e.g. `D000026`), from the link (e.g. `http://id.nlm.nih.gov/mesh/D000026`) )

#### ✨ ACCESS RESTRICTION COLOUR MAP

The special `ACCESS_RESTRICTION` field includes an additional property, `color_map`, which maps the values of the mex:accessRestriction field to colors used as the background for the access tag.

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
is_backwards_linked             |  -         |  bool                  |  Marks that the field represents a reverse relationship (e.g. record listed as `partOf` another record)
prefixes                        |  -         |  list[str] (optional)  |  List of recognised URI prefixes for external link values                               

### 🧾 Example Configuration Snippet

Below is a minimal valid entity configuration block, illustrating all supported keys and options:

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