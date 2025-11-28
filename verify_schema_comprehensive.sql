-- ============================================================================
-- COMPREHENSIVE DATABASE SCHEMA VERIFICATION
-- Validates database matches migrations 008-011 at commit 3fb0a16
-- ============================================================================

-- ============================================================================
-- 1. TABLE EXISTENCE CHECK
-- ============================================================================

SELECT
    'TABLE_EXISTENCE' as check_type,
    CASE
        WHEN COUNT(*) = 10 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as result,
    COUNT(*) || '/10 tables present' as details
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
    'system_settings', 'settings_audit_log',
    'email_templates', 'email_queue', 'email_recipients', 'email_send_log',
    'webhooks', 'webhook_deliveries',
    'api_keys', 'api_key_usage'
);

-- ============================================================================
-- 2. MISSING TABLES (if any)
-- ============================================================================

SELECT
    'MISSING_TABLES' as check_type,
    '❌ MISSING' as result,
    table_name as details,
    migration_file
FROM (
    VALUES
        ('system_settings', 'backend/migrations/008_system_settings.sql'),
        ('settings_audit_log', 'backend/migrations/008_system_settings.sql'),
        ('email_templates', 'backend/migrations/009_smtp_email.sql'),
        ('email_queue', 'backend/migrations/009_smtp_email.sql'),
        ('email_recipients', 'backend/migrations/009_smtp_email.sql'),
        ('email_send_log', 'backend/migrations/009_smtp_email.sql'),
        ('webhooks', 'backend/migrations/010_webhooks.sql'),
        ('webhook_deliveries', 'backend/migrations/010_webhooks.sql'),
        ('api_keys', 'backend/migrations/011_api_keys.sql'),
        ('api_key_usage', 'backend/migrations/011_api_keys.sql')
) AS required_tables(table_name, migration_file)
WHERE NOT EXISTS (
    SELECT 1 FROM information_schema.tables t
    WHERE t.table_name = required_tables.table_name
    AND t.table_schema = 'public'
);

-- ============================================================================
-- 3. PRIMARY KEY CONSTRAINTS
-- ============================================================================

SELECT
    'PRIMARY_KEYS' as check_type,
    CASE
        WHEN COUNT(*) = 10 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as result,
    COUNT(*) || '/10 primary keys present' as details
FROM information_schema.table_constraints
WHERE table_schema = 'public'
AND constraint_type = 'PRIMARY KEY'
AND table_name IN (
    'system_settings', 'settings_audit_log',
    'email_templates', 'email_queue', 'email_recipients', 'email_send_log',
    'webhooks', 'webhook_deliveries',
    'api_keys', 'api_key_usage'
);

-- ============================================================================
-- 4. FOREIGN KEY CONSTRAINTS
-- ============================================================================

SELECT
    'FOREIGN_KEYS' as check_type,
    CASE
        WHEN COUNT(*) >= 12 THEN '✅ PASS'
        ELSE '⚠️ WARNING'
    END as result,
    COUNT(*) || ' foreign keys found (expected ~12-15)' as details
FROM information_schema.table_constraints
WHERE table_schema = 'public'
AND constraint_type = 'FOREIGN KEY'
AND table_name IN (
    'system_settings', 'settings_audit_log',
    'email_templates', 'email_queue', 'email_recipients', 'email_send_log',
    'webhooks', 'webhook_deliveries',
    'api_keys', 'api_key_usage'
);

-- ============================================================================
-- 5. UNIQUE CONSTRAINTS
-- ============================================================================

SELECT
    'UNIQUE_CONSTRAINTS' as check_type,
    table_name,
    constraint_name
FROM information_schema.table_constraints
WHERE table_schema = 'public'
AND constraint_type = 'UNIQUE'
AND table_name IN (
    'system_settings', 'settings_audit_log',
    'email_templates', 'email_queue', 'email_recipients', 'email_send_log',
    'webhooks', 'webhook_deliveries',
    'api_keys', 'api_key_usage'
)
ORDER BY table_name;

-- Expected unique constraints:
-- system_settings: setting_key
-- email_templates: template_key
-- email_recipients: notification_type
-- api_keys: key_hash

-- ============================================================================
-- 6. INDEXES VERIFICATION
-- ============================================================================

SELECT
    'INDEXES' as check_type,
    CASE
        WHEN COUNT(*) >= 20 THEN '✅ PASS'
        ELSE '⚠️ WARNING'
    END as result,
    COUNT(*) || ' indexes found (expected ~25-30)' as details
FROM pg_indexes
WHERE schemaname = 'public'
AND tablename IN (
    'system_settings', 'settings_audit_log',
    'email_templates', 'email_queue', 'email_recipients', 'email_send_log',
    'webhooks', 'webhook_deliveries',
    'api_keys', 'api_key_usage'
);

-- ============================================================================
-- 7. DETAILED INDEX LIST
-- ============================================================================

SELECT
    'INDEX_DETAILS' as check_type,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
AND tablename IN (
    'system_settings', 'settings_audit_log',
    'email_templates', 'email_queue', 'email_recipients', 'email_send_log',
    'webhooks', 'webhook_deliveries',
    'api_keys', 'api_key_usage'
)
ORDER BY tablename, indexname;

-- ============================================================================
-- 8. TRIGGERS VERIFICATION
-- ============================================================================

SELECT
    'TRIGGERS' as check_type,
    event_object_table as table_name,
    trigger_name,
    action_statement
FROM information_schema.triggers
WHERE event_object_schema = 'public'
AND event_object_table IN (
    'system_settings', 'settings_audit_log',
    'email_templates', 'email_queue', 'email_recipients', 'email_send_log',
    'webhooks', 'webhook_deliveries',
    'api_keys', 'api_key_usage'
)
ORDER BY event_object_table, trigger_name;

-- Expected triggers (updated_at):
-- system_settings, email_templates, email_queue, email_recipients, webhooks, webhook_deliveries

-- ============================================================================
-- 9. CRITICAL COLUMNS VALIDATION - WEBHOOKS
-- ============================================================================

SELECT
    'WEBHOOKS_SCHEMA' as check_type,
    column_name,
    data_type,
    character_maximum_length,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name = 'webhooks'
ORDER BY ordinal_position;

-- ============================================================================
-- 10. CRITICAL COLUMNS VALIDATION - API_KEYS
-- ============================================================================

SELECT
    'API_KEYS_SCHEMA' as check_type,
    column_name,
    data_type,
    character_maximum_length,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name = 'api_keys'
ORDER BY ordinal_position;

-- ============================================================================
-- 11. CRITICAL COLUMNS VALIDATION - SYSTEM_SETTINGS
-- ============================================================================

SELECT
    'SYSTEM_SETTINGS_SCHEMA' as check_type,
    column_name,
    data_type,
    character_maximum_length,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name = 'system_settings'
ORDER BY ordinal_position;

-- ============================================================================
-- 12. CHECK CONSTRAINTS
-- ============================================================================

SELECT
    'CHECK_CONSTRAINTS' as check_type,
    tc.table_name,
    tc.constraint_name,
    cc.check_clause
FROM information_schema.table_constraints tc
JOIN information_schema.check_constraints cc
    ON tc.constraint_name = cc.constraint_name
WHERE tc.table_schema = 'public'
AND tc.constraint_type = 'CHECK'
AND tc.table_name IN (
    'system_settings', 'settings_audit_log',
    'email_templates', 'email_queue', 'email_recipients', 'email_send_log',
    'webhooks', 'webhook_deliveries',
    'api_keys', 'api_key_usage'
)
ORDER BY tc.table_name, tc.constraint_name;

-- Expected CHECK constraints:
-- system_settings: data_type IN (...)
-- email_queue: status IN (...), priority BETWEEN 1 AND 10
-- webhooks: timeout_seconds BETWEEN 5 AND 120, retry_attempts BETWEEN 0 AND 10, retry_delay_seconds BETWEEN 10 AND 3600
-- webhook_deliveries: status IN (...)

-- ============================================================================
-- 13. SUMMARY
-- ============================================================================

SELECT
    '========== VERIFICATION SUMMARY ==========' as summary,
    (SELECT COUNT(*) FROM information_schema.tables
     WHERE table_schema = 'public'
     AND table_name IN (
         'system_settings', 'settings_audit_log',
         'email_templates', 'email_queue', 'email_recipients', 'email_send_log',
         'webhooks', 'webhook_deliveries',
         'api_keys', 'api_key_usage'
     )) || '/10 tables' as tables,
    (SELECT COUNT(*) FROM information_schema.table_constraints
     WHERE table_schema = 'public'
     AND constraint_type = 'PRIMARY KEY'
     AND table_name IN (
         'system_settings', 'settings_audit_log',
         'email_templates', 'email_queue', 'email_recipients', 'email_send_log',
         'webhooks', 'webhook_deliveries',
         'api_keys', 'api_key_usage'
     )) || '/10 primary keys' as primary_keys,
    (SELECT COUNT(*) FROM information_schema.table_constraints
     WHERE table_schema = 'public'
     AND constraint_type = 'FOREIGN KEY'
     AND table_name IN (
         'system_settings', 'settings_audit_log',
         'email_templates', 'email_queue', 'email_recipients', 'email_send_log',
         'webhooks', 'webhook_deliveries',
         'api_keys', 'api_key_usage'
     )) || ' foreign keys' as foreign_keys,
    (SELECT COUNT(*) FROM pg_indexes
     WHERE schemaname = 'public'
     AND tablename IN (
         'system_settings', 'settings_audit_log',
         'email_templates', 'email_queue', 'email_recipients', 'email_send_log',
         'webhooks', 'webhook_deliveries',
         'api_keys', 'api_key_usage'
     )) || ' indexes' as indexes,
    (SELECT COUNT(*) FROM information_schema.triggers
     WHERE event_object_schema = 'public'
     AND event_object_table IN (
         'system_settings', 'settings_audit_log',
         'email_templates', 'email_queue', 'email_recipients', 'email_send_log',
         'webhooks', 'webhook_deliveries',
         'api_keys', 'api_key_usage'
     )) || ' triggers' as triggers;
