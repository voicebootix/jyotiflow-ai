-- 🚨 CRITICAL DATABASE SCHEMA FIX
-- Problem: platform_settings table has wrong structure
-- Solution: Drop and recreate with correct schema

-- ========================================
-- 1. BACKUP EXISTING DATA (if any)
-- ========================================

-- Create backup table if platform_settings exists with old structure
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'platform_settings' 
        AND column_name = 'platform_name'
    ) THEN
        -- Old structure detected, create backup
        CREATE TABLE platform_settings_backup AS 
        SELECT * FROM platform_settings;
        
        RAISE NOTICE '📦 Backup created: platform_settings_backup';
    END IF;
END $$;

-- ========================================
-- 2. DROP WRONG TABLE STRUCTURE
-- ========================================

DROP TABLE IF EXISTS platform_settings CASCADE;

-- ========================================
-- 3. CREATE CORRECT TABLE STRUCTURE
-- ========================================

CREATE TABLE platform_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- 4. INSERT INITIAL PLATFORM CREDENTIALS
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
-- 5. CREATE INDEXES FOR PERFORMANCE
-- ========================================

CREATE INDEX IF NOT EXISTS idx_platform_settings_key ON platform_settings(key);
CREATE INDEX IF NOT EXISTS idx_platform_settings_created_at ON platform_settings(created_at);

-- ========================================
-- 6. VERIFICATION QUERIES
-- ========================================

-- Verify table structure
\d platform_settings

-- Verify data
SELECT key, 
       CASE 
           WHEN value ? 'status' THEN value->>'status'
           ELSE 'configured'
       END as status,
       created_at
FROM platform_settings
ORDER BY key;

-- ========================================
-- SUCCESS MESSAGE
-- ========================================

DO $$ 
BEGIN
    RAISE NOTICE '✅ platform_settings table fixed successfully!';
    RAISE NOTICE '✅ Social media configuration save should now work!';
    RAISE NOTICE '🎯 Test: Go to Admin Dashboard → Social Media → Platform Configuration';
END $$; 