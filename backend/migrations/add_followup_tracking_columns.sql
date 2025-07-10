-- Add specific follow-up tracking columns to sessions table
-- Migration: Add follow-up channel tracking columns

-- Add follow-up email tracking
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS follow_up_email_sent BOOLEAN DEFAULT FALSE;

-- Add follow-up SMS tracking  
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS follow_up_sms_sent BOOLEAN DEFAULT FALSE;

-- Add follow-up WhatsApp tracking
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS follow_up_whatsapp_sent BOOLEAN DEFAULT FALSE;

-- Create indexes for better performance on follow-up queries
CREATE INDEX IF NOT EXISTS idx_sessions_follow_up_email_sent ON sessions(follow_up_email_sent);
CREATE INDEX IF NOT EXISTS idx_sessions_follow_up_sms_sent ON sessions(follow_up_sms_sent);
CREATE INDEX IF NOT EXISTS idx_sessions_follow_up_whatsapp_sent ON sessions(follow_up_whatsapp_sent);

-- Update existing sessions to have default values
UPDATE sessions SET 
    follow_up_email_sent = COALESCE(follow_up_email_sent, FALSE),
    follow_up_sms_sent = COALESCE(follow_up_sms_sent, FALSE),
    follow_up_whatsapp_sent = COALESCE(follow_up_whatsapp_sent, FALSE)
WHERE follow_up_email_sent IS NULL 
   OR follow_up_sms_sent IS NULL 
   OR follow_up_whatsapp_sent IS NULL;

-- Add comments for documentation
COMMENT ON COLUMN sessions.follow_up_email_sent IS 'Track if email follow-up was sent for this session';
COMMENT ON COLUMN sessions.follow_up_sms_sent IS 'Track if SMS follow-up was sent for this session';
COMMENT ON COLUMN sessions.follow_up_whatsapp_sent IS 'Track if WhatsApp follow-up was sent for this session'; 