"""Finish a developer snapshot restore inside the local Invenio app.

Run by restore.sh after the database has been restored and the indices recreated:
- reindexes every service and drains the indexer queues here, so no Celery
  worker is needed
"""

from invenio_access.permissions import system_identity
from invenio_app.factory import create_app
from invenio_records_resources.proxies import current_service_registry

app = create_app()
with app.app_context():
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
            if indexer is not None:
                indexed, failed = indexer.process_bulk_queue()
                print(f"{name} ({attr}): {indexed} indexed, {failed} failed")
