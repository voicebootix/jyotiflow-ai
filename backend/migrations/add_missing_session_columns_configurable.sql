-- ================================================================
-- Add Missing Session Columns Migration - Enhanced Version
-- ================================================================
-- Supports configurable schema for multi-schema environments
-- Usage: 
--   For public schema: \set target_schema 'public'
--   For custom schema: \set target_schema 'your_schema_name'
--   Then include this file: \i add_missing_session_columns_configurable.sql

-- Set default schema if not provided
\set target_schema 'public'

-- Display which schema we're targeting
\echo 'Targeting schema:' :target_schema

-- Add missing columns to sessions table with schema-aware checks
DO $$ 
DECLARE
    target_schema_name TEXT := :'target_schema';
BEGIN
    RAISE NOTICE 'Running migration for schema: %', target_schema_name;

    -- Bail out early if the sessions table itself is missing
    IF to_regclass(format('%I.sessions', target_schema_name)) IS NULL THEN
        RAISE EXCEPTION 'sessions table does not exist in schema %.  Run base DDL first.', target_schema_name;
    END IF;

    -- Add question column (idempotent)
    EXECUTE format('ALTER TABLE %I.sessions ADD COLUMN IF NOT EXISTS question TEXT', target_schema_name);
    RAISE NOTICE '✅ Ensured question column exists in %.sessions table', target_schema_name;

    -- Add user_email column (idempotent)
    EXECUTE format('ALTER TABLE %I.sessions ADD COLUMN IF NOT EXISTS user_email VARCHAR(255)', target_schema_name);
    RAISE NOTICE '✅ Ensured user_email column exists in %.sessions table', target_schema_name;

    -- Add service_type column (idempotent)
    EXECUTE format('ALTER TABLE %I.sessions ADD COLUMN IF NOT EXISTS service_type VARCHAR(100)', target_schema_name);
    RAISE NOTICE '✅ Ensured service_type column exists in %.sessions table', target_schema_name;

    -- Add user_id column (idempotent)
    EXECUTE format('ALTER TABLE %I.sessions ADD COLUMN IF NOT EXISTS user_id INTEGER', target_schema_name);
    RAISE NOTICE '✅ Ensured user_id column exists in %.sessions table', target_schema_name;

    RAISE NOTICE '🎉 Migration completed for schema: %', target_schema_name;

END $$;