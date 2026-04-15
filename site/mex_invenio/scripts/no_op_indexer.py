from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_records_resources.services.uow import RecordCommitOp, RecordDeleteOp


# No-op indexer class to disable indexing during import
class NoOpIndexer:
    """A no-operation indexer that does nothing."""

    def index(self, *args, **kwargs):
        pass

    def delete(self, *args, **kwargs):
        pass

    def delete_by_id(self, *args, **kwargs):
        pass

    def exists(self, *args, **kwargs):
        return False

    def bulk_index(self, *args, **kwargs):
        pass

    def bulk_delete(self, *args, **kwargs):
        pass

    def refresh(self, *args, **kwargs):
        pass


original_record_commit_op = None
original_record_delete_op = None
original_indexer_property = None


def disable_indexing(logger):
    global original_record_commit_op, original_record_delete_op, original_indexer_property  # noqa: PLW0603

    # Store original on_commit methods
    original_record_commit_op = RecordCommitOp.on_commit
    original_record_delete_op = RecordDeleteOp.on_commit

    # Disable on_commit methods for performance
    RecordCommitOp.on_commit = lambda self, uow: None
    RecordDeleteOp.on_commit = lambda self, uow: None

    # Temporarily disable indexing for performance
    # IMPORTANT: indexer is a property that creates new instances, so we need to
    # monkey-patch the property getter itself, not just set an attribute
    # current_rdm_records_service is a LocalProxy, so we need to get the actual class
    service_class = current_rdm_records_service.__class__
    original_indexer_property = service_class.indexer
    noop_indexer = NoOpIndexer()
    service_class.indexer = property(lambda self: noop_indexer)
    logger.info(
        "Disabled indexing and commit operations during import for better performance"
    )


def re_enable_indexing(logger):
    service_class = current_rdm_records_service.__class__
    # Restore original indexer property
    service_class.indexer = original_indexer_property

    # Restore original on_commit methods
    RecordCommitOp.on_commit = original_record_commit_op
    RecordDeleteOp.on_commit = original_record_delete_op

    logger.info("Restored indexing and commit operations")
