"""Add indices on custom_fields for performance optimization.

Revision ID: 20251218_214700
Revises:
Create Date: 2025-12-18 21:47:00.000000

ATTENTION !!!
This migration should create database indices on rdm_records_metadata.json->'custom_fields'
to dramatically improve query performance for MexDumper operations.

However, invenio-db create, which sets up the tables, only stamps/marks migrations, but does
not actually run them. This migration file is therefore provided for reference, but the actual
index creation must be done in a separate step after the database is live by running
invenio mex setup-db.

"""

from alembic import op

# Revision identifiers, used by Alembic.
revision = "a12c08876802"
down_revision = None  # This is the first migration for mex_invenio
branch_labels = ("mex_invenio",)  # Branch label for this module
depends_on = None


def upgrade():
    """Create indices on rdm_records_metadata.json->custom_fields.

    Creates two indices:
    1. GIN index on entire custom_fields (for general queries)
    2. B-tree index on mex:identifier (for specific identifier lookups)

    Note: CONCURRENTLY is not used because this runs during deployment when the
    service is not live. For adding indices to an existing production database,
    use the manual SQL statements with CONCURRENTLY option.
    """
    # Create GIN index on custom_fields for general JSON queries
    # This supports queries with @> operator: json->'custom_fields' @> '{"mex:isPartOf": "value"}'
    # Standard GIN (not jsonb_path_ops) supports ?, @>, and other JSONB operators
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_rdm_records_custom_fields_gin_std
        ON rdm_records_metadata
        USING gin ((json->'custom_fields'))
    """)

    # Create B-tree index on mex:identifier for fast identifier lookups
    # This supports queries like: json->'custom_fields'->>'mex:identifier' = 'some-id'
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_rdm_records_mex_identifier
        ON rdm_records_metadata
        ((json->'custom_fields'->>'mex:identifier'))
    """)

    # Update table statistics so query planner knows about new indices
    op.execute("ANALYZE rdm_records_metadata")


def downgrade():
    """Drop the custom_fields indices.

    Removes both indices created in upgrade().
    """
    # Drop indices
    op.execute("""
        DROP INDEX IF EXISTS idx_rdm_records_mex_identifier
    """)

    op.execute("""
        DROP INDEX IF EXISTS idx_rdm_records_custom_fields_gin_std
    """)
