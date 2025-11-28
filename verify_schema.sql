-- ============================================================================
-- DATABASE SCHEMA VERIFICATION SCRIPT
-- Checks if database schema matches code at commit 3fb0a16
-- ============================================================================
-- Run this in Supabase SQL Editor
-- ============================================================================

-- STEP 1: Check if all required tables exist
SELECT
    CASE
        WHEN COUNT(*) = 10 THEN '✅ ALL REQUIRED TABLES PRESENT'
        ELSE '❌ MISSING TABLES - Database needs migration'
    END as status,
    COUNT(*) as present_count,
    10 as required_count
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
    'system_settings',
    'settings_audit_log',
    'email_templates',
    'email_queue',
    'email_recipients',
    'email_send_log',
    'webhooks',
    'webhook_deliveries',
    'api_keys',
    'api_key_usage'
);

-- STEP 2: Detailed status for each required table
SELECT
    required_tables.table_name,
    required_tables.migration,
    CASE
        WHEN actual_tables.table_name IS NOT NULL THEN '✅ Present'
        ELSE '❌ Missing'
    END as status
FROM (
    VALUES
        ('system_settings', 'Migration 008'),
        ('settings_audit_log', 'Migration 008'),
        ('email_templates', 'Migration 009'),
        ('email_queue', 'Migration 009'),
        ('email_recipients', 'Migration 009'),
        ('email_send_log', 'Migration 009'),
        ('webhooks', 'Migration 010'),
        ('webhook_deliveries', 'Migration 010'),
        ('api_keys', 'Migration 011'),
        ('api_key_usage', 'Migration 011')
) AS required_tables(table_name, migration)
LEFT JOIN information_schema.tables actual_tables
    ON required_tables.table_name = actual_tables.table_name
    AND actual_tables.table_schema = 'public'
ORDER BY required_tables.migration, required_tables.table_name;

-- STEP 3: Show ONLY missing tables (if any)
SELECT
    required_tables.table_name as missing_table,
    required_tables.migration,
    required_tables.migration_file
FROM (
    VALUES
        ('system_settings', 'Migration 008', 'backend/migrations/008_system_settings.sql'),
        ('settings_audit_log', 'Migration 008', 'backend/migrations/008_system_settings.sql'),
        ('email_templates', 'Migration 009', 'backend/migrations/009_smtp_email.sql'),
        ('email_queue', 'Migration 009', 'backend/migrations/009_smtp_email.sql'),
        ('email_recipients', 'Migration 009', 'backend/migrations/009_smtp_email.sql'),
        ('email_send_log', 'Migration 009', 'backend/migrations/009_smtp_email.sql'),
        ('webhooks', 'Migration 010', 'backend/migrations/010_webhooks.sql'),
        ('webhook_deliveries', 'Migration 010', 'backend/migrations/010_webhooks.sql'),
        ('api_keys', 'Migration 011', 'backend/migrations/011_api_keys.sql'),
        ('api_key_usage', 'Migration 011', 'backend/migrations/011_api_keys.sql')
) AS required_tables(table_name, migration, migration_file)
WHERE NOT EXISTS (
    SELECT 1
    FROM information_schema.tables actual_tables
    WHERE actual_tables.table_name = required_tables.table_name
    AND actual_tables.table_schema = 'public'
);

-- STEP 4: Verify webhooks table structure (if exists)
SELECT
    'webhooks' as table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'webhooks'
AND table_schema = 'public'
ORDER BY ordinal_position;

-- STEP 5: Verify api_keys table structure (if exists)
SELECT
    'api_keys' as table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'api_keys'
AND table_schema = 'public'
ORDER BY ordinal_position;
