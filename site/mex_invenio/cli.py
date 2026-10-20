#
# Copyright (C) 2025 Robert Koch Institute.
#
# mex-invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CLI commands for mex-invenio."""

import click
from flask.cli import with_appcontext
from invenio_db import db

from mex_invenio.scripts.dedupe import dedupe_records as run_dedupe


@click.group()
def mex():
    """MEX commands."""


@mex.command("setup-db")
@with_appcontext
def setup_db():
    """Create custom database indices for MEX.

    This command creates performance-optimized indices on custom_fields
    that are not created by the standard Invenio setup process.

    Safe to run multiple times (uses IF NOT EXISTS).

    Note that an alembic migration can be found in:
    site/mex_invenio/alembic/a12c08876802_add_custom_fields_indices.py
    for reference and possible downgrade.
    """
    click.secho("Creating MEX database indices...", fg="yellow")

    # Create GIN index on custom_fields for general JSON queries
    click.echo("  Creating GIN index on custom_fields...")
    db.session.execute(
        db.text("""
            CREATE INDEX IF NOT EXISTS idx_rdm_records_custom_fields_gin_std
            ON rdm_records_metadata
            USING gin ((json->'custom_fields'))
        """)
    )

    # Create B-tree index on mex:identifier for fast identifier lookups
    click.echo("  Creating B-tree index on mex:identifier...")
    db.session.execute(
        db.text("""
            CREATE INDEX IF NOT EXISTS idx_rdm_records_mex_identifier
            ON rdm_records_metadata
            ((json->'custom_fields'->>'mex:identifier'))
        """)
    )

    # Update table statistics
    click.echo("  Analyzing table statistics...")
    db.session.execute(db.text("ANALYZE rdm_records_metadata"))

    db.session.commit()

    click.secho("MEX database indices created successfully!", fg="green")


@mex.command("dedupe-records")
@click.option(
    "--created-after",
    type=click.DateTime(),
    help="Only delete duplicates created at or after this time (UTC).",
)
@click.option(
    "--created-before",
    type=click.DateTime(),
    help="Only delete duplicates created before this time (UTC).",
)
@click.option("--batch-size", default=500, help="Duplicates deleted per transaction.")
@click.option("--output", help="Write the duplicates to delete to this file.")
@click.option(
    "--commit", is_flag=True, help="Delete the duplicates (default: dry run)."
)
@with_appcontext
def dedupe_records(created_after, created_before, batch_size, output, commit):
    """Delete duplicate records: parents created again for an existing MEx identifier.

    The earliest-created parent of each MEx identifier is kept. Dry run unless
    --commit is given.
    """
    if not run_dedupe(
        created_after=created_after,
        created_before=created_before,
        batch_size=batch_size,
        commit=commit,
        output=output,
        echo=click.echo,
    ):
        raise click.exceptions.Exit(1)
