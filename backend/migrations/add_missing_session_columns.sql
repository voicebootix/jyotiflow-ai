-- ================================================================
-- Add Missing Session Columns Migration
-- ================================================================

-- Add missing session columns with idempotent operations
DO $$ 
BEGIN
    -- Verify sessions table exists in public schema
    IF to_regclass('public.sessions') IS NULL THEN
        RAISE EXCEPTION 'sessions table does not exist in public schema. Run base DDL first.';
    END IF;

    -- Add columns using idempotent operations (PostgreSQL 9.6+)
    ALTER TABLE sessions ADD COLUMN IF NOT EXISTS question TEXT;
    RAISE NOTICE '✅ Ensured question column exists in sessions table';

    ALTER TABLE sessions ADD COLUMN IF NOT EXISTS user_email VARCHAR(255);
    RAISE NOTICE '✅ Ensured user_email column exists in sessions table';

    ALTER TABLE sessions ADD COLUMN IF NOT EXISTS service_type VARCHAR(100);
    RAISE NOTICE '✅ Ensured service_type column exists in sessions table';

    ALTER TABLE sessions ADD COLUMN IF NOT EXISTS user_id INTEGER;
    RAISE NOTICE '✅ Ensured user_id column exists in sessions table';

    RAISE NOTICE '🎉 Migration completed successfully - all columns ensured';

END $$;