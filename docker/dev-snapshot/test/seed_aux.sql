-- Traces of real users in auxiliary tables (synthetic values; user 2 = alice).
\set ON_ERROR_STOP on
BEGIN;
INSERT INTO accounts_user_login_information (user_id, last_login_ip, current_login_ip, login_count, last_login_at, current_login_at)
SELECT id, '192.0.2.20', '192.0.2.21', 3, now(), now() FROM accounts_user;
INSERT INTO accounts_user_session_activity (created, updated, sid_s, user_id, ip, country, browser, os, device)
VALUES (now(), now(), 'sid-123', 2, '198.51.100.7', 'DE', 'Firefox', 'Linux', 'Other');
INSERT INTO accounts_useridentity (id, method, id_user, created, updated)
VALUES ('alice-keycloak-sub', 'keycloak', 2, now(), now());
INSERT INTO oauthclient_remoteaccount (id, user_id, client_id, extra_data, created, updated)
VALUES (1, 2, 'keycloak', '{"email": "alice.mueller@rki.de"}', now(), now());
INSERT INTO oauthclient_remotetoken (id_remote_account, token_type, access_token, secret, created, updated)
VALUES (1, '', 'secret-access-token', '', now(), now());
UPDATE transaction SET remote_addr = '203.0.113.5' WHERE id % 3 = 0;
INSERT INTO rdm_records_access_request_tokens (id, token, created, expires_at, email, full_name, message, record_pid, consent_to_share_personal_data)
SELECT gen_random_uuid(), 'tok', now(), now() + interval '30 days', 'requester@uni-berlin.de', 'Max Requester', 'Bitte Zugang, Max',
       (SELECT json->>'id' FROM rdm_records_metadata LIMIT 1), 'true';
INSERT INTO audit_logs_metadata (id, created, updated, action, resource_type, user_id, json, version_id)
VALUES (gen_random_uuid(), now(), now(), 'record.publish', 'record', '2',
        '{"user": {"email": "alice.mueller@rki.de", "name": "Alice Müller"}, "metadata": {"ip_address": "198.51.100.7"}}', 1);
INSERT INTO jobs_job (id, created, updated, active, title, description, task, default_queue, schedule)
VALUES (gen_random_uuid(), now(), now(), true, 'Notify', 'Mail alice.mueller@rki.de on failures', 'noop', 'celery', NULL);
INSERT INTO jobs_run (id, created, updated, job_id, started_by_id, status, message, title, args, queue)
SELECT gen_random_uuid(), now(), now(), id, 2, 'S', 'sent to bob.schmidt@example.org', 'run', '{"email": "alice.mueller@rki.de"}', 'celery' FROM jobs_job;
COMMIT;
