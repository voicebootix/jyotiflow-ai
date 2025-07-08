-- ============================================================================
-- 🚀 SOCIAL MEDIA AUTOMATION DATABASE MIGRATION SCRIPT
-- Run this script in your PostgreSQL database to fix the social media automation
-- ============================================================================

-- Create platform_settings table for storing API credentials and configuration
CREATE TABLE IF NOT EXISTS platform_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create social media campaigns table
CREATE TABLE IF NOT EXISTS social_campaigns (
    id SERIAL PRIMARY KEY,
    campaign_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    campaign_type VARCHAR(50) NOT NULL,
    budget DECIMAL(10,2),
    target_audience JSONB,
    duration_days INTEGER,
    status VARCHAR(50) DEFAULT 'active',
    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create social media posts tracking table
CREATE TABLE IF NOT EXISTS social_posts (
    id SERIAL PRIMARY KEY,
    post_id VARCHAR(100) UNIQUE NOT NULL,
    platform VARCHAR(50) NOT NULL,
    platform_post_id VARCHAR(255),
    title VARCHAR(500),
    content TEXT NOT NULL,
    hashtags TEXT,
    media_url VARCHAR(500),
    scheduled_time TIMESTAMP,
    posted_time TIMESTAMP,
    status VARCHAR(50) DEFAULT 'scheduled',
    engagement_metrics JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial platform settings with empty credentials placeholders
INSERT INTO platform_settings (key, value) VALUES 
('facebook_credentials', '{}') 
ON CONFLICT (key) DO NOTHING;

INSERT INTO platform_settings (key, value) VALUES 
('instagram_credentials', '{}') 
ON CONFLICT (key) DO NOTHING;

INSERT INTO platform_settings (key, value) VALUES 
('youtube_credentials', '{}') 
ON CONFLICT (key) DO NOTHING;

INSERT INTO platform_settings (key, value) VALUES 
('twitter_credentials', '{}') 
ON CONFLICT (key) DO NOTHING;

INSERT INTO platform_settings (key, value) VALUES 
('tiktok_credentials', '{}') 
ON CONFLICT (key) DO NOTHING;

INSERT INTO platform_settings (key, value) VALUES 
('ai_model_config', '{}') 
ON CONFLICT (key) DO NOTHING;

INSERT INTO platform_settings (key, value) VALUES 
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

-- Show current platform settings
SELECT 'Platform Settings Created:' AS status;
SELECT key, value FROM platform_settings ORDER BY key;

-- ============================================================================
-- 🎯 NEXT STEP: Add your Facebook credentials
-- Run this query with your actual Facebook credentials:
-- ============================================================================

-- UPDATE platform_settings 
-- SET value = '{
--     "app_id": "YOUR_FACEBOOK_APP_ID",
--     "app_secret": "YOUR_FACEBOOK_APP_SECRET", 
--     "page_id": "YOUR_FACEBOOK_PAGE_ID",
--     "page_access_token": "YOUR_FACEBOOK_PAGE_ACCESS_TOKEN",
--     "configured_at": "' || NOW() || '",
--     "status": "configured"
-- }', updated_at = CURRENT_TIMESTAMP
-- WHERE key = 'facebook_credentials';

SELECT '✅ Migration completed! Platform settings table created and initialized.' AS completion_status;