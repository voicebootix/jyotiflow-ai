-- Update social_content table for better RAG content storage
-- Migration: 025_update_social_content_for_rag.sql

BEGIN;

-- Columns already exist, but ensure they're properly configured
-- Update hashtags column to handle longer hashtag strings if needed
ALTER TABLE social_content 
ALTER COLUMN hashtags TYPE TEXT;

-- Update any existing records to have default values
UPDATE social_content 
SET hashtags = '#jyotiflow,#spirituality' 
WHERE hashtags IS NULL OR hashtags = '';

-- Add index for better query performance on RAG content
CREATE INDEX IF NOT EXISTS idx_social_content_scheduled_at ON social_content(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_social_content_platform_status ON social_content(platform_name, status);
CREATE INDEX IF NOT EXISTS idx_social_content_content_type ON social_content(content_type);

-- Add a comment to track RAG-generated content
COMMENT ON TABLE social_content IS 'Stores social media content including RAG-generated spiritual content';

COMMIT;
