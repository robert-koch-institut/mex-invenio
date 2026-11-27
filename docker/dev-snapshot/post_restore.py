"""Finish a developer snapshot restore inside the local Invenio app.

Run by restore.sh after the database has been restored and the indices recreated:
- reindexes every service and drains the indexer queues here, so no Celery
  worker is needed
- creates empty stats indices so record lookups don't warn about missing aliases
"""

from datetime import datetime

from invenio_access.permissions import system_identity
from invenio_app.factory import create_app
from invenio_records_resources.proxies import current_service_registry
from invenio_search import current_search_client
from invenio_search.utils import prefix_index
from invenio_stats.aggregations import SUPPORTED_INTERVALS
from invenio_stats.proxies import current_stats

app = create_app()
with app.app_context():
    # The stats aliases only exist once the first events are aggregated; until then
    # every record lookup logs "no such index [...-stats-...]". Create the current
    # interval's empty index so the template attaches the alias.
    for agg in current_stats.aggregations.values():
        event = agg.params["event"]
        suffix = SUPPORTED_INTERVALS[agg.params.get("index_interval", "month")]
        index = prefix_index(f"stats-{event}-{datetime.utcnow().strftime(suffix)}")
        if not current_search_client.indices.exists(index=index):
            current_search_client.indices.create(index=index)
            print(f"created {index}")

    # As `invenio rdm rebuild-all-indices` does; the registry has no public listing.
    for name, service in current_service_registry._services.items():  # noqa: SLF001
        if not hasattr(service, "rebuild_index"):
            continue
        try:
            service.rebuild_index(system_identity)
        except NotImplementedError:
            continue
        # Drain with the service's own indexers: the ones in the indexer registry
        # read the same queues but do not resolve these services' record classes.
        for attr in ("indexer", "draft_indexer"):
            indexer = getattr(service, attr, None)
            if indexer is None:
                continue
            # Each call consumes at most `_bulk_index_max_items` (10000) messages,
            # so keep going until the queue is empty.
            indexed = failed = 0
            while True:
                batch_indexed, batch_failed = indexer.process_bulk_queue()
                if not batch_indexed and not batch_failed:
                    break
                indexed += batch_indexed
                failed += batch_failed
            print(f"{name} ({attr}): {indexed} indexed, {failed} failed")
