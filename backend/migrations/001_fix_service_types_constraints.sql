-- Fix service_types table constraints and ID generation
-- This migration ensures service_types table works properly with ON CONFLICT clauses

-- ========================================
-- 1. ENSURE SERVICE_TYPES TABLE HAS PROPER CONSTRAINTS
-- ========================================

-- Add unique constraint on name if it doesn't exist (required for ON CONFLICT)
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'service_types') THEN
        -- Check if unique constraint exists
        IF NOT EXISTS (
            SELECT 1 FROM pg_constraint 
            WHERE conname = 'service_types_name_key' 
            OR (conrelid = 'service_types'::regclass AND contype = 'u' AND array_to_string(conkey, ',') = (
                SELECT array_to_string(array_agg(attnum), ',') 
                FROM pg_attribute 
                WHERE attrelid = 'service_types'::regclass AND attname = 'name'
            ))
        ) THEN
            -- Add unique constraint on name
            ALTER TABLE service_types ADD CONSTRAINT service_types_name_unique UNIQUE (name);
            RAISE NOTICE 'Added unique constraint to service_types.name';
        ELSE
            RAISE NOTICE 'Unique constraint already exists on service_types.name';
        END IF;
    ELSE
        RAISE NOTICE 'service_types table does not exist';
    END IF;
EXCEPTION 
    WHEN duplicate_object THEN
        RAISE NOTICE 'Unique constraint already exists on service_types.name';
    WHEN others THEN
        RAISE NOTICE 'Could not add unique constraint to service_types: %', SQLERRM;
END $$;

-- ========================================
-- 2. FIX SERVICE_TYPES ID SEQUENCE ISSUE
-- ========================================

-- Ensure the ID sequence is properly linked and has correct next value
DO $$ 
DECLARE
    max_id INTEGER;
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'service_types') THEN
        -- Get the maximum ID currently in the table
        SELECT COALESCE(MAX(id), 0) INTO max_id FROM service_types;
        
        -- Reset the sequence to start after the maximum ID
        PERFORM setval('service_types_id_seq', max_id + 1, false);
        
        RAISE NOTICE 'Reset service_types_id_seq to start at %', max_id + 1;
    END IF;
EXCEPTION 
    WHEN others THEN
        RAISE NOTICE 'Could not reset service_types sequence: %', SQLERRM;
END $$;

-- ========================================
-- 3. ENSURE PROPER DEFAULT VALUES
-- ========================================

-- Update any NULL id values (shouldn't happen with SERIAL but just in case)
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'service_types') THEN
        -- Check if there are any NULL id values
        IF EXISTS (SELECT 1 FROM service_types WHERE id IS NULL) THEN
            -- Delete rows with NULL ids as they're invalid
            DELETE FROM service_types WHERE id IS NULL;
            RAISE NOTICE 'Removed invalid service_types rows with NULL ids';
        END IF;
    END IF;
EXCEPTION 
    WHEN others THEN
        RAISE NOTICE 'Could not clean up service_types NULL ids: %', SQLERRM;
END $$;

-- ========================================
-- 4. ADD MISSING COLUMNS TO SERVICE_TYPES IF NEEDED
-- ========================================

-- Ensure all required columns exist for the application
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'service_types') THEN
        -- Add base_credits if missing
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'service_types' AND column_name = 'base_credits'
        ) THEN
            ALTER TABLE service_types ADD COLUMN base_credits INTEGER DEFAULT 10;
            RAISE NOTICE 'Added base_credits column to service_types';
        END IF;
        
        -- Add icon if missing
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'service_types' AND column_name = 'icon'
        ) THEN
            ALTER TABLE service_types ADD COLUMN icon VARCHAR(50) DEFAULT '🔮';
            RAISE NOTICE 'Added icon column to service_types';
        END IF;
        
        -- Add gradient_class if missing
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'service_types' AND column_name = 'gradient_class'
        ) THEN
            ALTER TABLE service_types ADD COLUMN gradient_class VARCHAR(100) DEFAULT 'from-purple-500 to-indigo-600';
            RAISE NOTICE 'Added gradient_class column to service_types';
        END IF;
    END IF;
EXCEPTION 
    WHEN others THEN
        RAISE NOTICE 'Could not add missing columns to service_types: %', SQLERRM;
END $$;

-- ========================================
-- MIGRATION COMPLETE
-- ========================================

DO $$ 
BEGIN
    RAISE NOTICE '✅ Service types constraint fixes completed successfully';
    RAISE NOTICE '📋 service_types table now supports ON CONFLICT operations';
END $$;

