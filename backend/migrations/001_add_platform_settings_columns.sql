-- Migration: Add missing columns to platform_settings table
-- Date: 2025-07-10
-- Description: Add created_at and updated_at columns to platform_settings table for proper audit trail

-- Add created_at column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'platform_settings' 
        AND column_name = 'created_at'
    ) THEN
        ALTER TABLE platform_settings ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
        
        -- Update existing records with current timestamp
        UPDATE platform_settings SET created_at = NOW() WHERE created_at IS NULL;
        
        -- Make the column NOT NULL after setting default values
        ALTER TABLE platform_settings ALTER COLUMN created_at SET NOT NULL;
    END IF;
END $$;

-- Add updated_at column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'platform_settings' 
        AND column_name = 'updated_at'
    ) THEN
        ALTER TABLE platform_settings ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
        
        -- Update existing records with current timestamp
        UPDATE platform_settings SET updated_at = NOW() WHERE updated_at IS NULL;
        
        -- Make the column NOT NULL after setting default values
        ALTER TABLE platform_settings ALTER COLUMN updated_at SET NOT NULL;
    END IF;
END $$;

-- Create or replace the trigger function for updated_at
CREATE OR REPLACE FUNCTION update_platform_settings_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop existing trigger if it exists and create new one
DROP TRIGGER IF EXISTS update_platform_settings_updated_at_trigger ON platform_settings;
CREATE TRIGGER update_platform_settings_updated_at_trigger
    BEFORE UPDATE ON platform_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_platform_settings_updated_at();

-- Add index for better performance on timestamp queries
CREATE INDEX IF NOT EXISTS idx_platform_settings_created_at ON platform_settings(created_at);
CREATE INDEX IF NOT EXISTS idx_platform_settings_updated_at ON platform_settings(updated_at);

-- Verify the migration
DO $$
BEGIN
    -- Check if columns exist
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'platform_settings' 
        AND column_name IN ('created_at', 'updated_at')
    ) THEN
        RAISE NOTICE 'Migration completed successfully: platform_settings table now has created_at and updated_at columns';
    ELSE
        RAISE EXCEPTION 'Migration failed: columns were not added properly';
    END IF;
END $$;

