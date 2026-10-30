-- Verify a sanitised MEx snapshot database. Run after sanitise.sql:
--   psql -v ON_ERROR_STOP=1 -f verify.sql
--
-- Scans EVERY text/json column in the public schema, not only the ones sanitise.sql
-- knows about, and fails (non-zero exit, nothing gets dumped) on:
--   * an email address that is not pseudonymised
--   * any canary value (real emails/names sampled before sanitising)
--   * leftover account, session or token data
-- On success it drops snapshot_tmp (salt, helpers, canary) so it is not in the dump.

\set ON_ERROR_STOP on
SET client_min_messages = notice;
BEGIN;

CREATE TEMP TABLE findings (check_name text, location text, detail text);

DO $$
DECLARE
    c record;
    email_re text := (SELECT email_re FROM snapshot_tmp.settings);
    canary_re text := (
        -- Whole-word match, so a canary name doesn't fire inside a longer word.
        SELECT '\m(' || string_agg(regexp_replace(v, '([.\\+*?\[^\]$(){}=!<>|:\-#])', '\\\1', 'g'), '|') || ')\M'
        FROM snapshot_tmp.canary WHERE v <> '');
    n bigint;
    sample text;
BEGIN
    FOR c IN
        SELECT table_name, column_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND data_type IN ('json', 'jsonb', 'text', 'character varying')
        ORDER BY table_name, column_name
    LOOP
        -- Unexpected email addresses.
        EXECUTE format(
            'SELECT count(*), min(m) FROM (
                 SELECT lower(x[1]) AS m
                 FROM %I, LATERAL regexp_matches(%I::text, %L, ''g'') AS x
             ) s
             WHERE m NOT LIKE ''%%@example.invalid''',
            c.table_name, c.column_name, email_re)
        INTO n, sample;
        IF n > 0 THEN
            INSERT INTO findings VALUES ('email', c.table_name || '.' || c.column_name,
                                         n || ' occurrence(s), e.g. ' || left(sample, 3) || '***');
        END IF;

        -- Phone numbers after a keyword, or in +CC form.
        EXECUTE format(
            'SELECT count(*) FROM %I WHERE %I::text ~* %L OR %I::text ~ %L',
            c.table_name, c.column_name,
            '\m(tel|telefon|phone|fon|fax|mobil|mobile|handy)\.?:?\s*(\+|00)?\(?[0-9][0-9 ()/.\-]{5,}[0-9]',
            c.column_name, (SELECT phone_intl_re FROM snapshot_tmp.settings))
        INTO n;
        IF n > 0 THEN
            INSERT INTO findings VALUES ('phone', c.table_name || '.' || c.column_name, n || ' row(s)');
        END IF;

        -- Canary values (case-insensitive, anywhere in the value).
        IF canary_re IS NOT NULL THEN
            EXECUTE format('SELECT count(*) FROM %I WHERE %I::text ~* %L',
                           c.table_name, c.column_name, canary_re)
            INTO n;
            IF n > 0 THEN
                INSERT INTO findings VALUES ('canary', c.table_name || '.' || c.column_name, n || ' row(s)');
            END IF;
        END IF;
    END LOOP;
END $$;

-- Tables that must be empty.
INSERT INTO findings
SELECT 'not empty', t, NULL
FROM unnest(ARRAY[
    'accounts_user_session_activity', 'accounts_user_login_information', 'accounts_useridentity',
    'oauthclient_remotetoken', 'oauthclient_remoteaccount', 'oauth2server_token', 'oauth2server_client',
    'rdm_records_access_request_tokens', 'rdm_records_secret_links', 'audit_logs_metadata',
    'jobs_run', 'webhooks_events']) AS t
WHERE (xpath('/row/n/text()', query_to_xml(format('SELECT count(*) AS n FROM %I', t), false, true, '')))[1]::text::int > 0;

INSERT INTO findings
SELECT 'account', 'accounts_user', count(*) || ' user(s) with password/username/real email'
FROM accounts_user
WHERE password IS NOT NULL OR username IS NOT NULL OR email NOT LIKE '%@example.invalid'
HAVING count(*) > 0;

INSERT INTO findings
SELECT 'ip', 'transaction.remote_addr', count(*) || ' row(s)'
FROM transaction WHERE remote_addr IS NOT NULL HAVING count(*) > 0;

DO $$
DECLARE
    f record;
    total int := (SELECT count(*) FROM findings);
BEGIN
    FOR f IN SELECT * FROM findings ORDER BY 1, 2 LOOP
        RAISE NOTICE 'FAIL [%] % %', f.check_name, f.location, coalesce(f.detail, '');
    END LOOP;
    IF total > 0 THEN
        RAISE EXCEPTION 'snapshot verification failed with % finding(s); not dumping', total;
    END IF;
    RAISE NOTICE 'snapshot verification passed';
END $$;

-- Remove salt, helper functions, pgcrypto and canary samples before dumping.
SET client_min_messages = warning;
DROP SCHEMA snapshot_tmp CASCADE;

COMMIT;
