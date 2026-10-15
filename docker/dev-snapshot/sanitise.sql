-- Pseudonymise a restored copy of the MEx staging database for developer snapshots.
--
-- Run against the SCRATCH copy only, never the staging database itself:
--   psql -v ON_ERROR_STOP=1 -v salt="$SNAPSHOT_SALT" -f sanitise.sql
-- then run verify.sql, which checks the result and drops the snapshot_tmp schema
-- (salt, helper functions and canary samples) so none of it ends up in the dump.
--
-- Replacements are deterministic (HMAC of the original value with the secret salt),
-- so a person keeps the same pseudonym across record versions, drafts and snapshots.

\set ON_ERROR_STOP on
SET client_min_messages = warning;

BEGIN;

CREATE SCHEMA snapshot_tmp;
CREATE EXTENSION pgcrypto SCHEMA snapshot_tmp;

CREATE TABLE snapshot_tmp.settings AS
SELECT
    :'salt'::text AS salt,
    -- Close to RFC 5322 for the addresses that occur in practice.
    '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'::text AS email_re,
    -- Phone numbers only after a phone keyword or in +CC form; bare digit runs would
    -- hit dates, ISNIs and other identifiers in the JSON.
    '\+[1-9][0-9]{0,2}[ ()/.\-]*[0-9][0-9 ()/.\-]{5,}[0-9]'::text AS phone_intl_re;

DO $$
BEGIN
    IF length((SELECT salt FROM snapshot_tmp.settings)) < 32 THEN
        RAISE EXCEPTION 'salt must be at least 32 characters';
    END IF;
END $$;

-- Short keyed hash of a value.
CREATE FUNCTION snapshot_tmp.h(v text, n int DEFAULT 10) RETURNS text
LANGUAGE sql STABLE AS $$
    SELECT substr(encode(snapshot_tmp.hmac(v, (SELECT salt FROM snapshot_tmp.settings), 'sha256'), 'hex'), 1, n)
$$;

CREATE FUNCTION snapshot_tmp.fake_email(v text) RETURNS text
LANGUAGE sql STABLE AS $$
    SELECT 'user-' || snapshot_tmp.h(lower(v)) || '@example.invalid'
$$;

CREATE FUNCTION snapshot_tmp.fake_full_name(v text) RETURNS text
LANGUAGE sql STABLE AS $$
    SELECT 'Person ' || snapshot_tmp.h(lower(v), 8)
$$;

CREATE FUNCTION snapshot_tmp.re_escape(v text) RETURNS text
LANGUAGE sql IMMUTABLE AS $$
    SELECT regexp_replace(v, '([.\\+*?\[^\]$(){}=!<>|:\-#])', '\\\1', 'g')
$$;

-- ORCID-shaped fake (16 digits from the hash), keeping the https://orcid.org/ form.
CREATE FUNCTION snapshot_tmp.fake_orcid(v text) RETURNS text
LANGUAGE sql STABLE AS $$
    SELECT 'https://orcid.org/' || regexp_replace(
        lpad(((('x' || snapshot_tmp.h(v, 13))::bit(52)::bigint) % 10000000000000000)::text, 16, '0'),
        '(\d{4})(\d{4})(\d{4})(\d{4})', '\1-\2-\3-\4')
$$;

-- ---------------------------------------------------------------------------
-- 1. Collect real personal values from every record row (current, history, drafts)
-- ---------------------------------------------------------------------------
CREATE TABLE snapshot_tmp.docs AS
    SELECT json FROM rdm_records_metadata WHERE json IS NOT NULL
    UNION ALL SELECT json FROM rdm_records_metadata_version WHERE json IS NOT NULL
    UNION ALL SELECT json FROM rdm_drafts_metadata WHERE json IS NOT NULL;

CREATE TABLE snapshot_tmp.name_map (orig text PRIMARY KEY, fake text NOT NULL, kind text NOT NULL);

INSERT INTO snapshot_tmp.name_map (orig, fake, kind)
SELECT DISTINCT ON (v) v,
       -- Fakes derive from the lower-cased value so every spelling maps the same way.
       CASE k WHEN 'mex:fullName' THEN snapshot_tmp.fake_full_name(v)
              WHEN 'mex:givenName' THEN 'Given ' || snapshot_tmp.h(lower(v), 8)
              ELSE 'Family ' || snapshot_tmp.h(lower(v), 8) END,
       k
FROM snapshot_tmp.docs d,
     LATERAL unnest(ARRAY['mex:fullName', 'mex:givenName', 'mex:familyName']) AS k,
     LATERAL jsonb_array_elements_text(
         CASE WHEN jsonb_typeof(d.json -> 'custom_fields' -> k) = 'array'
              THEN d.json -> 'custom_fields' -> k ELSE '[]'::jsonb END) AS v
WHERE d.json -> 'metadata' -> 'resource_type' ->> 'id' = 'person' AND v <> ''
ORDER BY v, k;

-- Full names (with a space, >= 5 chars) are also replaced inside free text.
-- One regex alternation, longest first so "Anna Maria Schmidt" wins over "Anna Maria".
CREATE TABLE snapshot_tmp.name_re AS
SELECT string_agg(snapshot_tmp.re_escape(orig), '|' ORDER BY length(orig) DESC) AS re
FROM snapshot_tmp.name_map
WHERE kind = 'mex:fullName' AND length(orig) >= 5 AND orig LIKE '% %';

-- Canary samples for verify.sql: real values that must not survive anywhere.
CREATE TABLE snapshot_tmp.canary AS
(SELECT DISTINCT lower(e) AS v
   FROM snapshot_tmp.docs d,
        LATERAL jsonb_array_elements_text(
            CASE WHEN jsonb_typeof(d.json -> 'custom_fields' -> 'mex:email') = 'array'
                 THEN d.json -> 'custom_fields' -> 'mex:email' ELSE '[]'::jsonb END) AS e
  ORDER BY 1 LIMIT 200)
UNION ALL
(SELECT orig FROM snapshot_tmp.name_map
  WHERE kind = 'mex:fullName' AND length(orig) >= 5 AND orig LIKE '% %'
  ORDER BY snapshot_tmp.h(orig) LIMIT 200)
UNION ALL
(SELECT lower(email) FROM accounts_user WHERE email IS NOT NULL);

DROP TABLE snapshot_tmp.docs;

-- ---------------------------------------------------------------------------
-- 2. Text-level scrubbing: every email address, plus known full names
-- ---------------------------------------------------------------------------
CREATE FUNCTION snapshot_tmp.scrub_text(t text) RETURNS text
LANGUAGE plpgsql STABLE AS $$
DECLARE
    m text;
    name_re text := (SELECT re FROM snapshot_tmp.name_re);
BEGIN
    IF t IS NULL THEN
        RETURN NULL;
    END IF;
    -- Longest first, so "bob@x.de" can't clobber part of "jimbob@x.de".
    FOR m IN SELECT v FROM (SELECT DISTINCT x[1] AS v
                            FROM regexp_matches(t, (SELECT email_re FROM snapshot_tmp.settings), 'g') AS x) s
             ORDER BY length(v) DESC
    LOOP
        IF m NOT LIKE '%@example.invalid' THEN
            t := replace(t, m, snapshot_tmp.fake_email(m));
        END IF;
    END LOOP;
    t := regexp_replace(t, '\m(tel|telefon|phone|fon|fax|mobil|mobile|handy)(\.?:?\s*)(\+|00)?\(?[0-9][0-9 ()/.\-]{5,}[0-9]',
                        '\1\2[phone removed]', 'gi');
    t := regexp_replace(t, (SELECT phone_intl_re FROM snapshot_tmp.settings), '[phone removed]', 'g');
    IF name_re IS NOT NULL THEN
        -- Case-insensitive, whole words, longest first.
        FOR m IN SELECT v FROM (SELECT DISTINCT x[1] AS v
                                FROM regexp_matches(t, '\m(' || name_re || ')\M', 'gi') AS x) s
                 ORDER BY length(v) DESC
        LOOP
            t := regexp_replace(t, '\m' || snapshot_tmp.re_escape(m) || '\M',
                                snapshot_tmp.fake_full_name(m), 'g');
        END LOOP;
    END IF;
    RETURN t;
END $$;

-- ---------------------------------------------------------------------------
-- 3. Record documents: structured person fields, titles, then text scrub
-- ---------------------------------------------------------------------------
CREATE FUNCTION snapshot_tmp.map_names(arr jsonb) RETURNS jsonb
LANGUAGE sql STABLE AS $$
    SELECT coalesce(jsonb_agg(coalesce((SELECT fake FROM snapshot_tmp.name_map WHERE orig = v),
                                       'Name ' || snapshot_tmp.h(v, 8)) ORDER BY ord), '[]'::jsonb)
    FROM jsonb_array_elements_text(arr) WITH ORDINALITY AS t(v, ord)
$$;

CREATE FUNCTION snapshot_tmp.map_ids(arr jsonb) RETURNS jsonb
LANGUAGE sql STABLE AS $$
    SELECT coalesce(jsonb_agg(snapshot_tmp.fake_orcid(v) ORDER BY ord), '[]'::jsonb)
    FROM jsonb_array_elements_text(arr) WITH ORDINALITY AS t(v, ord)
$$;

-- First usable value (> 2 chars, as get_title() requires) of a string array.
CREATE FUNCTION snapshot_tmp.first_value(arr jsonb) RETURNS text
LANGUAGE sql IMMUTABLE AS $$
    SELECT v FROM jsonb_array_elements_text(
        CASE WHEN jsonb_typeof(arr) = 'array' THEN arr ELSE '[]'::jsonb END) WITH ORDINALITY AS t(v, ord)
    WHERE length(v) > 2 ORDER BY ord LIMIT 1
$$;

CREATE FUNCTION snapshot_tmp.sanitise_record(j jsonb) RETURNS jsonb
LANGUAGE plpgsql STABLE AS $$
DECLARE
    cf jsonb;
    k text;
    rtype text;
    new_title text;
BEGIN
    IF j IS NULL OR j = '{}'::jsonb THEN
        RETURN j;
    END IF;
    cf := j -> 'custom_fields';
    rtype := j -> 'metadata' -> 'resource_type' ->> 'id';

    IF cf IS NOT NULL AND jsonb_typeof(cf) = 'object' THEN
        FOREACH k IN ARRAY ARRAY['mex:fullName', 'mex:givenName', 'mex:familyName'] LOOP
            IF jsonb_typeof(cf -> k) = 'array' THEN
                cf := jsonb_set(cf, ARRAY[k], snapshot_tmp.map_names(cf -> k));
            END IF;
        END LOOP;
        IF jsonb_typeof(cf -> 'mex:orcidId') = 'array' THEN
            cf := jsonb_set(cf, '{mex:orcidId}', snapshot_tmp.map_ids(cf -> 'mex:orcidId'));
        END IF;
        -- ISNI identifies a person only on Person records; organisations keep theirs.
        IF rtype = 'person' AND jsonb_typeof(cf -> 'mex:isniId') = 'array' THEN
            cf := jsonb_set(cf, '{mex:isniId}', snapshot_tmp.map_ids(cf -> 'mex:isniId'));
        END IF;
        j := jsonb_set(j, '{custom_fields}', cf);
    END IF;

    -- Titles of people and contact points are copies of name/email fields
    -- (RECORD_METADATA_TITLE_PROPERTIES), so recompute them from the pseudonyms.
    IF rtype IN ('person', 'contactpoint') AND j -> 'metadata' ? 'title' THEN
        new_title := coalesce(
            snapshot_tmp.first_value(cf -> 'mex:fullName'),
            snapshot_tmp.first_value(cf -> 'mex:email'),   -- scrubbed below
            snapshot_tmp.first_value(cf -> 'mex:familyName'),
            '[Untitled]');
        j := jsonb_set(j, '{metadata,title}', to_jsonb(new_title));
    END IF;

    RETURN snapshot_tmp.scrub_text(j::text)::jsonb;
END $$;

UPDATE rdm_records_metadata SET json = snapshot_tmp.sanitise_record(json) WHERE json IS NOT NULL;
UPDATE rdm_records_metadata_version SET json = snapshot_tmp.sanitise_record(json) WHERE json IS NOT NULL;
UPDATE rdm_drafts_metadata SET json = snapshot_tmp.sanitise_record(json) WHERE json IS NOT NULL;

-- Other JSON that can quote record content or people (requests, communities, generic records).
UPDATE rdm_parents_metadata SET json = snapshot_tmp.scrub_text(json::text)::jsonb WHERE json IS NOT NULL;
UPDATE records_metadata SET json = snapshot_tmp.scrub_text(json::text)::jsonb WHERE json IS NOT NULL;
UPDATE records_metadata_version SET json = snapshot_tmp.scrub_text(json::text)::jsonb WHERE json IS NOT NULL;
UPDATE request_metadata SET json = snapshot_tmp.scrub_text(json::text)::jsonb WHERE json IS NOT NULL;
UPDATE request_events SET json = snapshot_tmp.scrub_text(json::text)::jsonb WHERE json IS NOT NULL;
UPDATE communities_metadata SET json = snapshot_tmp.scrub_text(json::text)::jsonb WHERE json IS NOT NULL;
UPDATE communities_members SET json = snapshot_tmp.scrub_text(json::text)::jsonb WHERE json IS NOT NULL;
UPDATE communities_archivedinvitations SET json = snapshot_tmp.scrub_text(json::text)::jsonb WHERE json IS NOT NULL;
UPDATE jobs_job SET description = snapshot_tmp.scrub_text(description), title = snapshot_tmp.scrub_text(title);

-- ---------------------------------------------------------------------------
-- 4. Accounts and activity traces
-- ---------------------------------------------------------------------------
-- Keep user rows (records and requests reference them) but strip identity.
UPDATE accounts_user SET
    email = 'user' || id || '@example.invalid',
    username = NULL,
    displayname = NULL,
    password = NULL,
    domain = NULL,
    profile = '{}'::jsonb,
    preferences = '{}'::jsonb;

TRUNCATE
    accounts_user_session_activity,
    accounts_user_login_information,
    accounts_useridentity,
    oauthclient_remotetoken,
    oauthclient_remoteaccount,
    oauth2server_token,
    oauth2server_client,
    rdm_records_access_request_tokens,
    rdm_records_secret_links,
    audit_logs_metadata,
    jobs_run,
    webhooks_events
CASCADE;

-- SQLAlchemy-Continuum records the client IP of every change.
UPDATE transaction SET remote_addr = NULL WHERE remote_addr IS NOT NULL;

-- Point storage at a local path instead of the staging bucket.
UPDATE files_location SET uri = 'file:///opt/invenio/var/instance/data';

COMMIT;
