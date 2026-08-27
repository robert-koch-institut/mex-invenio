"""The MEx entity types, as this instance sees them.

The same entity is spelled three ways depending on where it appears:

===================  ==========================  ===================================
form                 example                     used by
===================  ==========================  ===================================
snake_case           ``bibliographic_resource``  ``mex.model.ENTITY_JSON_BY_NAME``
squashed             ``bibliographicresource``   Invenio ``resource_type.id``
kebab-case           ``bibliographic-resource``  ``ENTITIES`` config, mex-model URLs
===================  ==========================  ===================================

This module is the single place those forms and this instance's own entity
policy are derived, so that they cannot drift from each other or from the
mex-model package.
"""

from mex.model import ENTITY_JSON_BY_NAME

# Entity types that are never published to Invenio, so they are skipped
# wherever config is derived from the mex-model package.
UNPUBLISHED_ENTITIES = frozenset({"consent", "primary_source"})

# The mex-model entity names this instance publishes. Note that "concept" and
# "concept_scheme" are vocabulary descriptors rather than entity types, so they
# are absent from ENTITY_JSON_BY_NAME by construction and cannot creep back in.
PUBLISHED_ENTITIES = frozenset(ENTITY_JSON_BY_NAME) - UNPUBLISHED_ENTITIES

# Kebab-case, as used by the ENTITIES config value.
ENTITIES = sorted(name.replace("_", "-") for name in PUBLISHED_ENTITIES)

# Squashed, as used by Invenio's metadata.resource_type.id. Equal to the ids in
# app_data/vocabularies/resource_types.yaml -- asserted by
# tests/test_entities.py, since several config values below rely on it.
RESOURCE_TYPES = sorted(name.replace("_", "") for name in PUBLISHED_ENTITIES)

# resource_type.id -> kebab-case entity name, for looking a record's type back
# up in the mex-model schema.
RESOURCE_TYPE_TO_ENTITY = {
    name.replace("_", ""): name.replace("_", "-") for name in PUBLISHED_ENTITIES
}

# The record types that get a landing page of their own. Hand-kept: which types
# are worth a page is an editorial decision, not something the model states.
CORE_ENTITY_TYPES = ["activity", "resource", "bibliographicresource"]

# The record types that get a search page of their own under /search. Everything
# with a landing page, plus variable, which is searchable but renders as JSON.
SEARCHABLE_ENTITY_TYPES = [*CORE_ENTITY_TYPES, "variable"]

# Resource-type facet values to hide: everything that has no search page to
# send the user to. A vocabulary id that is not a published entity type is left
# visible rather than silently hidden.
FACET_EXCLUDED_RESOURCE_TYPES = sorted(
    set(RESOURCE_TYPES) - set(SEARCHABLE_ENTITY_TYPES)
)
