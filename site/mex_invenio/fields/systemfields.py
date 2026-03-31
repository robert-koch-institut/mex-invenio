#
# Copyright (C) 2024 MEX.
#
# MEX-Invenio is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Custom system fields for MEX Records."""

from invenio_records.systemfields import SystemField
from invenio_search.proxies import current_search_client
from invenio_search.utils import build_alias_name


class DisplayField(SystemField):
    """Field for storing display data."""

    def __init__(self, dump=True, **kwargs) -> None:
        """Initialize the field with dump configuration."""
        super().__init__(**kwargs)
        self._dump = dump

    #
    # Data descriptor methods (i.e. attribute access)
    #
    def __get__(self, record, owner=None):
        """Get the display data."""
        # print(
        #    f"DisplayField.__get__ called for record: {record.get('id', 'unknown') if record else 'None'}"
        # )

        if record is None:
            # returns the field itself.
            return self

        # Check if already in record
        display_data = record.get("display_data", None)
        if display_data:
            # print(f"display_data already exists with keys: {list(display_data.keys())}")
            return display_data

        # # Try to get from search index first
        try:
            # print("Trying to get display_data from search index...")
            res = current_search_client.get(
                index=build_alias_name(record.index._name),
                id=record.id,
                params={"_source_includes": "display_data"},
            )
            return res["_source"]["display_data"]
            # print(
            #    f"Retrieved display_data from search index with keys: {list(display_data.keys())}"
            # )
        except Exception:
            return {}
            # print(f"Failed to get from search index: {e}")
            # Fallback to generating using MexDumper
            # print("Fallback: generating display_data using MexDumper...")

        # from mex_invenio.services.search import MexDumper

        # dumper = MexDumper()
        # temp_data = {"display_data": {}}
        # dumper.dump(record, temp_data)
        # display_data = temp_data["display_data"]
        # print(f"Generated display_data with keys: {list(display_data.keys())}")

        # Store it in the record for subsequent access
        # record["display_data"] = display_data
        # return display_data

    def pre_commit(self, record, **kwargs):
        """Called before record is committed."""
        # Remove display_data to keep it transient
        record.pop("display_data", None)

    def pre_dump(self, record, data, **kwargs):
        """Called before record is dumped."""
        # print(f"DisplayField.pre_dump called for record {record.get('id', 'unknown')}")
        # print(f"Record has display_data: {'display_data' in record}")
        # print(f"Dump enabled: {self._dump}")

        # Include display_data in dumps if enabled
        if self._dump and "display_data" in record:
            # print(f"Adding display_data to dump: {record['display_data']}")
            data["display_data"] = record["display_data"]
        # else:
        #    print("display_data not added to dump")


class IndexField(SystemField):
    """Field for storing searchable index data."""

    def __init__(self, dump=True, **kwargs) -> None:
        """Initialize the field with dump configuration."""
        super().__init__(**kwargs)
        self._dump = dump

    #
    # Data descriptor methods (i.e. attribute access)
    #
    def __get__(self, record, owner=None):
        """Get the index data."""
        # print(
        #    f"IndexField.__get__ called for record: {record.get('id', 'unknown') if record else 'None'}"
        # )

        if record is None:
            # returns the field itself.
            return self

        # Check if already in record
        index_data = record.get("index_data", None)
        if index_data:
            # print(f"index_data already exists with keys: {list(index_data.keys())}")
            return index_data

        # Try to get from search index first (like EndorsementsField does)
        try:
            # print("Trying to get index_data from search index...")
            res = current_search_client.get(
                index=build_alias_name(record.index._name),
                id=record.id,
                params={"_source_includes": "index_data"},
            )
            index_data = res["_source"]["index_data"]
            # print(
            #     f"Retrieved index_data from search index with keys: {list(index_data.keys())}"
            # )
        except Exception:
            return {}
            # print(f"Failed to get from search index: {e}")
            # Fallback to generating using MexDumper
            # print("Fallback: generating index_data using MexDumper...")
            # from mex_invenio.services.search import MexDumper

            # dumper = MexDumper()
            # temp_data = {"index_data": {}}
            # dumper.dump(record, temp_data)
            # index_data = temp_data["index_data"]
            # print(f"Generated index_data with keys: {list(index_data.keys())}")

        # Store it in the record for subsequent access
        record["index_data"] = index_data
        return index_data

    def pre_commit(self, record, **kwargs):
        """Called before record is committed."""
        # Remove index_data to keep it transient (like endorsements)
        record.pop("index_data", None)

    def pre_dump(self, record, data, **kwargs):
        """Called before record is dumped."""
        # print(f"IndexField.pre_dump called for record {record.get('id', 'unknown')}")
        # print(f"Record has index_data: {'index_data' in record}")
        # print(f"Dump enabled: {self._dump}")

        # Include index_data in dumps if enabled
        if self._dump and "index_data" in record:
            # print(f"Adding index_data to dump: {record['index_data']}")
            data["index_data"] = record["index_data"]
        # else:
        #    print("index_data not added to dump")
