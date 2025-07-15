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

    -- Check if question column exists in sessions table
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'sessions' 
        AND column_name = 'question' 
        AND table_schema = target_schema_name
    ) THEN
        EXECUTE format('ALTER TABLE %I.sessions ADD COLUMN question TEXT', target_schema_name);
        RAISE NOTICE '✅ Added question column to %.sessions table', target_schema_name;
    ELSE
        RAISE NOTICE '✅ question column already exists in %.sessions table', target_schema_name;
    END IF;

    -- Check if user_email column exists in sessions table  
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'sessions' 
        AND column_name = 'user_email' 
        AND table_schema = target_schema_name
    ) THEN
        EXECUTE format('ALTER TABLE %I.sessions ADD COLUMN user_email VARCHAR(255)', target_schema_name);
        RAISE NOTICE '✅ Added user_email column to %.sessions table', target_schema_name;
    ELSE
        RAISE NOTICE '✅ user_email column already exists in %.sessions table', target_schema_name;
    END IF;

    -- Check if service_type column exists (used by many queries)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'sessions' 
        AND column_name = 'service_type' 
        AND table_schema = target_schema_name
    ) THEN
        EXECUTE format('ALTER TABLE %I.sessions ADD COLUMN service_type VARCHAR(100)', target_schema_name);
        RAISE NOTICE '✅ Added service_type column to %.sessions table', target_schema_name;
    ELSE
        RAISE NOTICE '✅ service_type column already exists in %.sessions table', target_schema_name;
    END IF;

    -- Check if user_id column exists (used in WHERE clauses)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'sessions' 
        AND column_name = 'user_id' 
        AND table_schema = target_schema_name
    ) THEN
        EXECUTE format('ALTER TABLE %I.sessions ADD COLUMN user_id INTEGER', target_schema_name);
        RAISE NOTICE '✅ Added user_id column to %.sessions table', target_schema_name;
    ELSE
        RAISE NOTICE '✅ user_id column already exists in %.sessions table', target_schema_name;
    END IF;

    RAISE NOTICE '🎉 Migration completed for schema: %', target_schema_name;

END $$;