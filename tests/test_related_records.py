"""Test lookup of the records linked to and from a given MEx record."""

import pytest
import sqlalchemy as sa
from invenio_db import db
from invenio_rdm_records.records.api import RDMRecord

from mex_invenio.cli import setup_db
from mex_invenio.scripts.utils import get_linked_target_ids, get_related_mex_ids
from tests.data import org_unit_data, resource_data

GIN_INDEX = "idx_rdm_records_custom_fields_gin_std"

PARENT_UNIT_ID = org_unit_data["parentUnit"]
ORG_UNIT_ID = org_unit_data["identifier"]
RESOURCE_ID = resource_data["identifier"]
PARENT_RESOURCE_ID = "dO8iP5KEwJGZPXwCXKnFOZ"  # resource_data["isPartOf"]
UNLINKED_ID = "unlinkedRecordIdentifier01"


def _record(mex_id, record_type):
    """Minimal Invenio-schema record, as passed to get_related_mex_ids on import."""
    return {
        "custom_fields": {"mex:identifier": mex_id},
        "metadata": {"resource_type": {"id": record_type}},
    }


def _uuid(mex_id):
    """Return the UUIDs (as strings) of all records with the given MEx identifier."""
    rows = (
        db.session.query(RDMRecord.model_cls.id)
        .filter(
            RDMRecord.model_cls.json["custom_fields"]["mex:identifier"].as_string()
            == mex_id
        )
        .all()
    )
    return sorted(str(uuid) for (uuid,) in rows)


def _capture_related_query(record):
    """Run get_related_mex_ids and return its result plus the SQL and parameters it ran."""
    captured = []

    def before_cursor_execute(
        conn, cursor, statement, parameters, context, executemany
    ):
        if "rdm_records_metadata.json->'custom_fields'" in statement:
            captured.append((statement, parameters))

    sa.event.listen(db.engine, "before_cursor_execute", before_cursor_execute)
    try:
        result = get_related_mex_ids(record)
    finally:
        sa.event.remove(db.engine, "before_cursor_execute", before_cursor_execute)

    assert len(captured) == 1, f"Expected one related-records query, got {captured}"
    return sorted(result), *captured[0]


def _legacy_related_ids(fields, record_id):
    """The previous lookup: sub-path ? and ->> matches, which the GIN index can't serve."""
    conditions = " OR ".join(
        f"json->'custom_fields'->'mex:{field}' ? :record_id OR "
        f"json->'custom_fields'->>'mex:{field}' = :record_id"
        for field in fields
    )
    rows = db.session.execute(
        sa.text(f"SELECT id FROM rdm_records_metadata WHERE {conditions}"),  # noqa: S608
        {"record_id": record_id},
    ).fetchall()
    return sorted(str(uuid) for (uuid,) in rows)


def _fields(parameters):
    """Recover the referencing fields from get_related_mex_ids' bind parameters."""
    return sorted(
        key.removeprefix("record_id_")
        for key in parameters
        if key.startswith("record_id_") and not key.startswith("record_id_str_")
    )


def _plan(statement, parameters):
    """EXPLAIN a statement with sequential scans disabled where an index can be used.

    Runs on the session's connection, so it sees the indices setup_db created inside
    the test transaction.
    """
    conn = db.session.connection()
    conn.exec_driver_sql("SET LOCAL enable_seqscan = off")
    try:
        rows = conn.exec_driver_sql(f"EXPLAIN {statement}", parameters).fetchall()
    finally:
        conn.exec_driver_sql("SET LOCAL enable_seqscan = on")
    return "\n".join(row[0] for row in rows)


@pytest.fixture
def linked_records(
    db, location, resource_type_v, contributors_role_v, import_file, cli_runner
):
    """Import linked org units and resources.

    - resource.unitInCharge (array) -> org unit
    - org unit.parentUnit (nullable single reference) -> parent unit
    - resource.isPartOf (array, backwards-linked) -> parent resource

    The MEx indices are created first, as in a deployment. An index built after the
    imports' updates in the same transaction isn't usable by that transaction
    (Postgres indcheckxmin), which would hide it from the planner.
    """
    result = cli_runner(setup_db)
    assert result.exit_code == 0, result.output
    indexes = db.session.execute(
        sa.text("SELECT indexname FROM pg_indexes WHERE tablename = :t"),
        {"t": "rdm_records_metadata"},
    ).scalars()
    assert GIN_INDEX in set(indexes), result.output

    import_file(
        "parent-unit",
        {**org_unit_data, "identifier": PARENT_UNIT_ID, "parentUnit": None},
    )
    import_file("org-unit", org_unit_data)
    import_file(
        "parent-resource",
        {**resource_data, "identifier": PARENT_RESOURCE_ID, "isPartOf": []},
    )
    import_file("resource", resource_data)


def test_related_ids_array_field(linked_records):
    """A record referenced from an array field (resource.unitInCharge) is found."""
    related, _, _ = _capture_related_query(_record(ORG_UNIT_ID, "organizationalunit"))

    assert set(_uuid(RESOURCE_ID)) <= set(related)


def test_related_ids_nullable_single_field(linked_records):
    """A record referenced from a nullable single reference (org unit.parentUnit) is found.

    parentUnit is declared as anyOf [$ref, null] in the model and stored as a plain
    string, so this covers both the field discovery and the single-string match.
    """
    related, _, parameters = _capture_related_query(
        _record(PARENT_UNIT_ID, "organizationalunit")
    )

    assert "parentUnit" in _fields(parameters)
    assert related == _uuid(ORG_UNIT_ID)
    assert related == _legacy_related_ids(_fields(parameters), PARENT_UNIT_ID)


def test_related_ids_no_match(linked_records):
    """A record nothing links to has no related records."""
    related, _, _ = _capture_related_query(_record(UNLINKED_ID, "organizationalunit"))

    assert related == []


def test_related_ids_without_identifier_skips_query(linked_records):
    """No query is run for a record without a MEx identifier."""
    assert get_related_mex_ids({"custom_fields": {}, "metadata": {}}) == []


def test_linked_target_ids_backwards_linked_fields(linked_records):
    """Records linked to through backwards-linked fields are returned, others aren't.

    The parent resource lists the resource via isPartOf, so it needs re-indexing; the
    org unit doesn't list resources it is in charge of (unitInCharge isn't
    backwards-linked), so it doesn't.
    """
    targets = get_linked_target_ids(
        {
            "custom_fields": {
                "mex:isPartOf": [PARENT_RESOURCE_ID],
                "mex:unitInCharge": [ORG_UNIT_ID],
            }
        }
    )

    assert sorted(targets) == _uuid(PARENT_RESOURCE_ID)


def test_linked_target_ids_include_previous_links(linked_records):
    """Targets the previous version linked to are returned, so removed links refresh."""
    targets = get_linked_target_ids(
        {"custom_fields": {"mex:isPartOf": []}},
        previous_custom_fields={"mex:isPartOf": [PARENT_RESOURCE_ID]},
    )

    assert sorted(targets) == _uuid(PARENT_RESOURCE_ID)


def test_linked_target_ids_no_links(linked_records):
    """A record without backwards-linked values has no targets."""
    assert get_linked_target_ids({"custom_fields": {"mex:isPartOf": []}}) == []


@pytest.mark.parametrize("mex_id", [ORG_UNIT_ID, UNLINKED_ID])
def test_related_ids_match_legacy_query(linked_records, mex_id):
    """The containment query returns exactly what the previous sub-path query did."""
    related, _, parameters = _capture_related_query(
        _record(mex_id, "organizationalunit")
    )

    assert related == _legacy_related_ids(_fields(parameters), mex_id)


def test_related_ids_uses_gin_index(linked_records):
    """The containment query can use the custom_fields GIN index; the legacy query can't.

    Sequential scans are disabled for the EXPLAIN so the planner picks an index whenever
    one is usable, regardless of how few rows the test table holds.
    """
    _, statement, parameters = _capture_related_query(
        _record(ORG_UNIT_ID, "organizationalunit")
    )
    new_plan = _plan(statement, parameters)

    assert GIN_INDEX in new_plan, new_plan
    assert "Seq Scan" not in new_plan, new_plan

    field = _fields(parameters)[0]
    legacy_plan = _plan(
        f"SELECT id FROM rdm_records_metadata "  # noqa: S608
        f"WHERE json->'custom_fields'->'mex:{field}' ? %(record_id)s "
        f"OR json->'custom_fields'->>'mex:{field}' = %(record_id)s",
        {"record_id": ORG_UNIT_ID},
    )

    assert GIN_INDEX not in legacy_plan, legacy_plan
    assert "Seq Scan" in legacy_plan, legacy_plan
