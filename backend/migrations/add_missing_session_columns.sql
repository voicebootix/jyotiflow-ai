-- ================================================================
-- Add Missing Session Columns Migration
-- ================================================================

-- Add missing session columns with idempotent operations
DO $$ 
LANGUAGE plpgsql
BEGIN
    -- Verify sessions table exists in public schema
    IF to_regclass('public.sessions') IS NULL THEN
        RAISE EXCEPTION 'sessions table does not exist in public schema. Run base DDL first.';
    END IF;

    -- Add all columns in a single operation to minimize lock time
    ALTER TABLE public.sessions
        ADD COLUMN IF NOT EXISTS question          TEXT,
        ADD COLUMN IF NOT EXISTS user_email        VARCHAR(255),
        ADD COLUMN IF NOT EXISTS service_type      VARCHAR(100),
        ADD COLUMN IF NOT EXISTS service_type_id   INTEGER,
        ADD COLUMN IF NOT EXISTS user_id           INTEGER;
    
    RAISE NOTICE '✅ Added all missing columns to public.sessions table in single operation';

    RAISE NOTICE '🎉 Migration completed successfully - all columns ensured';

END $$;