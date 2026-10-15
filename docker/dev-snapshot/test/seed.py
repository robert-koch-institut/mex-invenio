"""Seed the scratch MEx DB with synthetic data shaped like staging.

Run via run.sh, which points the app at the throwaway database.
Search, cache and broker are dead/in-memory; indexing is disabled.
"""

import copy
import json
import logging
import sys

import yaml
from flask import current_app
from invenio_access.permissions import system_identity
from invenio_app.factory import create_api
from invenio_db import db
from sqlalchemy import text

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger("seed")

testdata, resource_types = sys.argv[1], sys.argv[2]
app = create_api()

with app.app_context():
    from invenio_accounts.proxies import current_datastore
    from invenio_rdm_records.proxies import current_rdm_records_service as rs
    from invenio_vocabularies.proxies import current_service as vocab

    from mex_invenio.scripts.no_op_indexer import disable_indexing
    from mex_invenio.scripts.utils import mex_to_invenio_schema

    disable_indexing(log)

    from invenio_files_rest.models import Location

    db.session.add(
        Location(name="default-location", uri="s3://mex-staging-files", default=True)
    )
    db.session.commit()

    # Users: the import owner plus two "real" people with login/session traces.
    owner = current_datastore.create_user(
        email="mex-import@rki.de", password="x" * 12, active=True
    )
    alice = current_datastore.create_user(
        email="alice.mueller@rki.de",
        password="y" * 12,
        active=True,
        username="amueller",
        user_profile={"full_name": "Alice Müller", "affiliations": "RKI"},
    )
    bob = current_datastore.create_user(
        email="bob.schmidt@example.org", password="z" * 12, active=True
    )
    db.session.commit()
    owner_id = owner.id

    # Resource type vocabulary.
    vocab.create_type(system_identity, "resourcetypes", "rsrct")
    for entry in yaml.safe_load(open(resource_types)):
        vocab.create(system_identity, {**entry, "type": "resourcetypes"})
    db.session.commit()

    # Records: ~150 of each entity type.
    from invenio_access.permissions import authenticated_user
    from invenio_access.utils import get_identity

    identity = get_identity(owner)
    identity.provides.add(authenticated_user)

    per_type, created = {}, {}
    with open(testdata) as f:
        for line in f:
            item = json.loads(line)
            et = item["entityType"]
            if per_type.get(et, 0) >= 150:
                continue
            # Plant free-text personal data in a few descriptions.
            if et == "MergedResource" and per_type.get(et, 0) < 5:
                item["description"] = [
                    {
                        "language": "de",
                        "value": "Ansprechperson: Dr. Erika Musterfrau (erika.musterfrau@rki.de), Tel. 030 18754 0",
                    }
                ]
            data = mex_to_invenio_schema(current_app.config, copy.deepcopy(item))
            draft = rs.create(identity, data)
            rec = rs.publish(identity, draft.id)
            created.setdefault(et, []).append(rec.id)
            per_type[et] = per_type.get(et, 0) + 1
    print("created:", per_type)

    # Version history: edit + republish 30 persons and 30 contact points twice.
    def bump(recid, n):
        d = rs.edit(identity, recid).to_dict()
        cf = d["custom_fields"]
        if "mex:email" in cf:
            cf["mex:email"] = [f"old{n}.{e}" for e in cf["mex:email"]] or [
                f"history{n}@rki.de"
            ]
        if "mex:fullName" in cf:
            cf["mex:fullName"] = [f"{v} (v{n})" for v in cf["mex:fullName"]]
        rs.update_draft(identity, recid, d)
        rs.publish(identity, recid)

    for et in ("MergedPerson", "MergedContactPoint"):
        for recid in created[et][:30]:
            bump(recid, 1)
            bump(recid, 2)
    # Open drafts with changed personal data (not published).
    for recid in created["MergedPerson"][30:40]:
        d = rs.edit(identity, recid).to_dict()
        d["custom_fields"]["mex:email"] = ["draft.only@rki.de"]
        rs.update_draft(identity, recid, d)
    db.session.commit()

    # Auxiliary tables (sessions, tokens, audit logs, ...) are filled by seed_aux.sql.

    for t in (
        "rdm_records_metadata",
        "rdm_records_metadata_version",
        "rdm_drafts_metadata",
        "transaction",
    ):
        print(t, db.session.execute(text(f'select count(*) from "{t}"')).scalar())
