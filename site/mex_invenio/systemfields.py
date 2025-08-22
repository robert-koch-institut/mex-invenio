# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 MEX.
#
# MEX-Invenio is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Custom system fields for MEX Records."""

from invenio_records.systemfields import SystemField


class IndexField(SystemField):
    """Field for storing searchable index data."""

    #
    # Data descriptor methods (i.e. attribute access)
    #
    def __get__(self, record, owner=None):
        """Get the index data."""
        print('Hello from IndexField __get__')
        print(record)
        if record is None:
            # returns the field itself.
            return self
        print("IndexField __get__ called")

        return record.get("index_data", {"index_data": {"belongsToLabel": ["Got nothing"]}})

    def __set__(self, record, value):
        """Set the index data."""
        pass
        #record["index"] = value or {}

    def pre_commit(self, record, **kwargs):
        """Called before record is committed."""
        # Ensure index field exists
        #if "index" not in record:
        #    record["index"] = {}
        record.pop("index_data", None)

    def pre_dump(self, record, data, **kwargs):
        """Called before record is dumped to search engine."""
        # Make sure index data is included in search dump
        #if "index" in record:
        #    data["index"] = record["index"]
        pass