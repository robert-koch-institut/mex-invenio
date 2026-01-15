# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Robert Koch Institute.
#
# mex-invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""MEX Invenio extension."""

from .cli import mex as mex_cmd


class MexInvenio:
    """MEX Invenio extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize application."""
        app.cli.add_command(mex_cmd)
        app.extensions["mex-invenio"] = self
