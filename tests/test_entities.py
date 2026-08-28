"""Tests for the entity lists derived from the mex-model package."""

import json
from pathlib import Path

import yaml
from mex.model import EXTRACTED_MODEL_JSON_BY_NAME, MERGED_MODEL_JSON_BY_NAME

from mex_invenio.custom_fields.custom_fields import RDM_CUSTOM_FIELDS
from mex_invenio.custom_fields.field_types import get_field_types
from mex_invenio.entities import (
    CORE_ENTITY_TYPES,
    FACET_EXCLUDED_RESOURCE_TYPES,
    PUBLISHED_ENTITIES,
    RESOURCE_TYPE_TO_ENTITY,
    RESOURCE_TYPES,
    SEARCHABLE_ENTITY_TYPES,
    UNPUBLISHED_ENTITIES,
)
from mex_invenio.views import URL_RESOURCE_TYPE_MAP

REPO_ROOT = Path(__file__).parent.parent
VOCABULARY = REPO_ROOT / "app_data/vocabularies/resource_types.yaml"
MAPPING = (
    REPO_ROOT
    / "site/mex_invenio/records/mappings/os-v2/mexrecords/records/record-v8.0.0.json"
)


def test_unpublished_entities_exist_in_the_model():
    """A typo in UNPUBLISHED_ENTITIES would silently exclude nothing."""
    assert set(MERGED_MODEL_JSON_BY_NAME) >= UNPUBLISHED_ENTITIES


def test_vocabulary_descriptors_are_not_entities():
    """Concept and concept_scheme describe vocabularies; they are not entity types."""
    assert "concept" not in MERGED_MODEL_JSON_BY_NAME
    assert "concept_scheme" not in MERGED_MODEL_JSON_BY_NAME


def test_resource_types_match_the_vocabulary():
    """The resource_types vocabulary must list exactly the published entity types.

    FACET_EXCLUDED_RESOURCE_TYPES is derived from RESOURCE_TYPES but applied to
    vocabulary ids, so the two sets drifting apart would either hide a type that
    should be facetable or leak one that should not be.
    """
    vocabulary_ids = {entry["id"] for entry in yaml.safe_load(VOCABULARY.read_text())}

    assert vocabulary_ids == set(RESOURCE_TYPES)


def test_name_forms_agree():
    """The snake, squashed and kebab spellings must describe the same set."""
    assert len(RESOURCE_TYPES) == len(PUBLISHED_ENTITIES)
    assert set(RESOURCE_TYPE_TO_ENTITY) == set(RESOURCE_TYPES)
    assert set(RESOURCE_TYPE_TO_ENTITY.values()) == {
        name.replace("_", "-") for name in PUBLISHED_ENTITIES
    }


def test_core_types_are_searchable_and_published():
    """Every type with a landing page must also be searchable and in the model."""
    assert set(CORE_ENTITY_TYPES) <= set(SEARCHABLE_ENTITY_TYPES)
    assert set(SEARCHABLE_ENTITY_TYPES) <= set(RESOURCE_TYPES)


def test_facet_hides_exactly_the_unsearchable_types():
    """A facet value the user can click must lead to a search page."""
    assert set(FACET_EXCLUDED_RESOURCE_TYPES).isdisjoint(SEARCHABLE_ENTITY_TYPES)
    assert set(FACET_EXCLUDED_RESOURCE_TYPES) | set(SEARCHABLE_ENTITY_TYPES) == set(
        RESOURCE_TYPES
    )


def test_query_api_serves_every_searchable_type():
    """/query/api/<resource_type> must cover the types the facet leaves visible."""
    single = {v for v in URL_RESOURCE_TYPE_MAP.values() if isinstance(v, str)}

    assert single == set(SEARCHABLE_ENTITY_TYPES)
    assert URL_RESOURCE_TYPE_MAP["global"] == SEARCHABLE_ENTITY_TYPES


def test_field_types_ignore_extracted_only_fields():
    """Invenio only ingests merged items, so extracted-only fields must not leak.

    hadPrimarySource, identifierInPrimarySource and stableTargetId exist only on
    extracted items. Deriving from mex.model.ENTITY_JSON_BY_NAME -- a deprecated
    alias for the extracted model -- would add all three to every entity.
    """
    extracted_only = set()
    for name, merged in MERGED_MODEL_JSON_BY_NAME.items():
        extracted = EXTRACTED_MODEL_JSON_BY_NAME[name]
        extracted_only |= set(extracted.get("properties", {})) - set(
            merged.get("properties", {})
        )

    assert extracted_only == {
        "hadPrimarySource",
        "identifierInPrimarySource",
        "stableTargetId",
    }

    field_types = get_field_types()
    for resource_type, properties in field_types.items():
        leaked = {f"mex:{name}" for name in extracted_only} & set(properties)

        assert not leaked, f"{resource_type} carries extracted-only {leaked}"


def test_field_types_cover_every_custom_field():
    """Every declared custom field needs a type, or it cannot be rendered."""
    typed = set().union(*(set(props) for props in get_field_types().values()))
    declared = {cf.name for cf in RDM_CUSTOM_FIELDS}

    assert declared - typed == set()


def test_mapping_covers_every_linked_record_field():
    """The dumper writes one linked_records key per identifier field.

    display_data.linked_records inherits ``dynamic: strict`` from the mapping
    root, so a field typed "identifier" that the mapping does not declare makes
    indexing fail outright -- and a declared field that is no longer an
    identifier is dead weight nothing can ever write.
    """
    mapping = json.loads(MAPPING.read_text())
    linked_records = mapping["mappings"]["properties"]["display_data"]["properties"][
        "linked_records"
    ]["properties"]

    identifiers = set()
    for properties in get_field_types().values():
        identifiers |= {f for f, t in properties.items() if t == "identifier"}

    # backwards_linked is added by the dumper itself, not derived from a field
    assert set(linked_records) - {"backwards_linked"} == identifiers
