# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Robert Koch Institute.
#
# mex-invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CLI commands for mex-invenio."""

import click
from invenio_db import db
from flask.cli import with_appcontext


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
