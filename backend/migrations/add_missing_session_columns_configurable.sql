-- ================================================================
-- Add Missing Session Columns Migration - Enhanced Version
-- ================================================================
-- Supports configurable schema for multi-schema environments
-- Usage: 
--   SET target_schema = 'public';
--   \i add_missing_session_columns_configurable.sql
-- Or via command line:
--   psql "$DATABASE_URL" -c "SET target_schema = 'production';" -f add_missing_session_columns_configurable.sql

-- Add missing columns to sessions table with schema-aware checks
DO $$ 
LANGUAGE plpgsql
DECLARE
    target_schema_name TEXT;
BEGIN
    -- Expect the caller to run: SET target_schema = 'your_schema';
    target_schema_name := current_setting('target_schema', true);
    IF target_schema_name IS NULL THEN
        RAISE EXCEPTION 'Please SET target_schema before executing this migration';
    END IF;
    
    RAISE NOTICE 'Running migration for schema: %', target_schema_name;

    -- Bail out early if the sessions table itself is missing
    IF to_regclass(format('%I.sessions', target_schema_name)) IS NULL THEN
        RAISE EXCEPTION 'sessions table does not exist in schema %.  Run base DDL first.', target_schema_name;
    END IF;

    -- Add all columns in a single operation to minimize lock time
    EXECUTE format('
        ALTER TABLE %I.sessions
            ADD COLUMN IF NOT EXISTS question          TEXT,
            ADD COLUMN IF NOT EXISTS user_email        VARCHAR(255),
            ADD COLUMN IF NOT EXISTS service_type      VARCHAR(100),
            ADD COLUMN IF NOT EXISTS service_type_id   INTEGER,
            ADD COLUMN IF NOT EXISTS user_id           INTEGER
    ', target_schema_name);
    
    RAISE NOTICE '✅ Added all missing columns to %.sessions table in single operation', target_schema_name;

    RAISE NOTICE '🎉 Migration completed for schema: %', target_schema_name;

END $$;