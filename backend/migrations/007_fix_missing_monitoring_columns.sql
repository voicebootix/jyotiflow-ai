-- Migration: Fix missing columns in monitoring tables
-- Purpose: Add missing auto_fixable and error_message columns
-- Author: JyotiFlow Team  
-- Date: 2024-12-29
-- Follows: .cursor rules - fix database schema issues without duplication

-- Add auto_fixable column to business_logic_issues table if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'business_logic_issues' 
        AND column_name = 'auto_fixable'
        AND table_schema = 'public'
    ) THEN
        ALTER TABLE business_logic_issues 
        ADD COLUMN auto_fixable BOOLEAN DEFAULT FALSE;
        
        RAISE NOTICE 'Added auto_fixable column to business_logic_issues table';
    ELSE
        RAISE NOTICE 'auto_fixable column already exists in business_logic_issues table';
    END IF;
END $$;

-- Add error_message column to integration_validations table if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'integration_validations' 
        AND column_name = 'error_message'
        AND table_schema = 'public'
    ) THEN
        ALTER TABLE integration_validations 
        ADD COLUMN error_message TEXT;
        
        RAISE NOTICE 'Added error_message column to integration_validations table';
    ELSE
        RAISE NOTICE 'error_message column already exists in integration_validations table';
    END IF;
END $$;

-- Add comments for documentation
COMMENT ON COLUMN business_logic_issues.auto_fixable IS 'Indicates if the issue can be automatically fixed by the system';
COMMENT ON COLUMN integration_validations.error_message IS 'Detailed error message when validation fails';

-- Verify the columns were added successfully
DO $$
DECLARE
    auto_fixable_exists BOOLEAN;
    error_message_exists BOOLEAN;
BEGIN
    -- Check auto_fixable column
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'business_logic_issues' 
        AND column_name = 'auto_fixable'
        AND table_schema = 'public'
    ) INTO auto_fixable_exists;
    
    -- Check error_message column
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'integration_validations' 
        AND column_name = 'error_message'
        AND table_schema = 'public'
    ) INTO error_message_exists;
    
    IF auto_fixable_exists AND error_message_exists THEN
        RAISE NOTICE '✅ Migration completed successfully - all required columns exist';
    ELSE
        RAISE WARNING '⚠️ Migration may have issues - please check column existence manually';
    END IF;
END $$;