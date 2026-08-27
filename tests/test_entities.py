"""Tests for the entity lists derived from the mex-model package."""

from pathlib import Path

import yaml
from mex.model import ENTITY_JSON_BY_NAME

from mex_invenio.entities import (
    CORE_ENTITY_TYPES,
    ENTITIES,
    FACET_EXCLUDED_RESOURCE_TYPES,
    PUBLISHED_ENTITIES,
    RESOURCE_TYPE_TO_ENTITY,
    RESOURCE_TYPES,
    SEARCHABLE_ENTITY_TYPES,
    UNPUBLISHED_ENTITIES,
)
from mex_invenio.views import URL_RESOURCE_TYPE_MAP

VOCABULARY = Path(__file__).parent.parent / "app_data/vocabularies/resource_types.yaml"


def test_unpublished_entities_exist_in_the_model():
    """A typo in UNPUBLISHED_ENTITIES would silently exclude nothing."""
    assert set(ENTITY_JSON_BY_NAME) >= UNPUBLISHED_ENTITIES


def test_vocabulary_descriptors_are_not_entities():
    """Concept and concept_scheme describe vocabularies; they are not entity types."""
    assert "concept" not in ENTITY_JSON_BY_NAME
    assert "concept_scheme" not in ENTITY_JSON_BY_NAME


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
    assert len(ENTITIES) == len(RESOURCE_TYPES) == len(PUBLISHED_ENTITIES)
    assert set(RESOURCE_TYPE_TO_ENTITY) == set(RESOURCE_TYPES)
    assert set(RESOURCE_TYPE_TO_ENTITY.values()) == set(ENTITIES)


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
