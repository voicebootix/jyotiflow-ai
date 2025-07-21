-- 🚨 CRITICAL MIGRATION: Fix platform_settings table schema
-- Migration: 002_fix_platform_settings_schema
-- Date: 2025-01-21
-- Problem: platform_settings table has wrong structure (platform_name vs key/value)
-- Solution: Recreate with correct key/value JSONB structure

-- ========================================
-- 1. CHECK CURRENT STRUCTURE
-- ========================================

DO $$ 
DECLARE
    has_platform_name BOOLEAN;
    has_key_column BOOLEAN;
BEGIN
    -- Check if current table has wrong structure
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'platform_settings' 
        AND column_name = 'platform_name'
    ) INTO has_platform_name;
    
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'platform_settings' 
        AND column_name = 'key'
    ) INTO has_key_column;
    
    IF has_platform_name AND NOT has_key_column THEN
        RAISE NOTICE '❌ WRONG SCHEMA DETECTED: platform_settings has platform_name column';
        RAISE NOTICE '🔧 APPLYING FIX: Will recreate with key/value structure';
        
        -- Backup existing data if any
        IF EXISTS (SELECT 1 FROM platform_settings LIMIT 1) THEN
            DROP TABLE IF EXISTS platform_settings_backup_migration;
            CREATE TABLE platform_settings_backup_migration AS 
            SELECT * FROM platform_settings;
            RAISE NOTICE '📦 Backup created: platform_settings_backup_migration';
        END IF;
        
        -- Drop wrong table structure
        DROP TABLE IF EXISTS platform_settings CASCADE;
        RAISE NOTICE '🗑️ Dropped wrong table structure';
        
    ELSIF has_key_column THEN
        RAISE NOTICE '✅ CORRECT SCHEMA: platform_settings already has key/value structure';
        RAISE NOTICE '⏭️ SKIPPING: No migration needed';
        RETURN;
    ELSE
        RAISE NOTICE '🆕 NEW INSTALLATION: Creating platform_settings table';
    END IF;
END $$;

-- ========================================
-- 2. CREATE CORRECT TABLE STRUCTURE
-- ========================================

CREATE TABLE IF NOT EXISTS platform_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- 3. INSERT INITIAL DATA
-- ========================================

INSERT INTO platform_settings (key, value) VALUES
    ('facebook_credentials', '{"status": "not_connected"}'),
    ('instagram_credentials', '{"status": "not_connected"}'),
    ('youtube_credentials', '{"status": "not_connected"}'),
    ('twitter_credentials', '{"status": "not_connected"}'),
    ('tiktok_credentials', '{"status": "not_connected"}'),
    ('social_automation_config', '{
        "auto_posting_enabled": true,
        "auto_comment_response": true,
        "daily_content_generation": true,
        "posting_schedule": {
            "facebook": ["09:00", "15:00", "20:00"],
            "instagram": ["10:00", "16:00", "21:00"],
            "youtube": ["12:00", "18:00"],
            "twitter": ["08:00", "14:00", "19:00", "22:00"],
            "tiktok": ["11:00", "17:00", "20:30"]
        }
    }')
ON CONFLICT (key) DO NOTHING;

-- ========================================
-- 4. CREATE INDEXES
-- ========================================

CREATE INDEX IF NOT EXISTS idx_platform_settings_key ON platform_settings(key);
CREATE INDEX IF NOT EXISTS idx_platform_settings_created_at ON platform_settings(created_at);

-- ========================================
-- 5. VERIFICATION
-- ========================================

DO $$ 
DECLARE
    rec RECORD;
    count_platforms INTEGER;
BEGIN
    -- Count platforms
    SELECT COUNT(*) FROM platform_settings INTO count_platforms;
    RAISE NOTICE '📊 Platform configurations: %', count_platforms;
    
    -- List all platforms
    FOR rec IN 
        SELECT key, value->>'status' as status 
        FROM platform_settings 
        WHERE key LIKE '%_credentials'
        ORDER BY key
    LOOP
        RAISE NOTICE '  ✅ %: %', rec.key, rec.status;
    END LOOP;
    
    -- Test the exact query used by backend
    PERFORM value FROM platform_settings WHERE key = 'youtube_credentials';
    RAISE NOTICE '✅ Backend query test: SUCCESS';
    
    RAISE NOTICE '🎉 MIGRATION COMPLETED SUCCESSFULLY!';
    RAISE NOTICE '🎯 Social media configuration save should now work!';
END $$; 