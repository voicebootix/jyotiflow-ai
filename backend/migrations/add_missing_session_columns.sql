-- ================================================================
-- Add Missing Session Columns Migration
-- ================================================================

-- Add question column to sessions table
DO $$ 
BEGIN
    -- Check if question column exists in sessions table
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'sessions' AND column_name = 'question'
    ) THEN
        ALTER TABLE sessions ADD COLUMN question TEXT;
        RAISE NOTICE '✅ Added question column to sessions table';
    ELSE
        RAISE NOTICE '✅ question column already exists in sessions table';
    END IF;

    -- Check if user_email column exists in sessions table  
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'sessions' AND column_name = 'user_email'
    ) THEN
        ALTER TABLE sessions ADD COLUMN user_email VARCHAR(255);
        RAISE NOTICE '✅ Added user_email column to sessions table';
    ELSE
        RAISE NOTICE '✅ user_email column already exists in sessions table';
    END IF;

    -- Check if service_type column exists (used by many queries)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'sessions' AND column_name = 'service_type'
    ) THEN
        ALTER TABLE sessions ADD COLUMN service_type VARCHAR(100);
        RAISE NOTICE '✅ Added service_type column to sessions table';
    ELSE
        RAISE NOTICE '✅ service_type column already exists in sessions table';
    END IF;

END $$;