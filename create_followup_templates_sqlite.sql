-- Create follow_up_templates table and insert default templates
-- SQLite Migration Script

-- Create follow_up_templates table
CREATE TABLE IF NOT EXISTS follow_up_templates (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    name TEXT NOT NULL,
    tamil_name TEXT,
    description TEXT,
    template_type TEXT NOT NULL DEFAULT 'session_followup',
    channel TEXT NOT NULL DEFAULT 'email',
    subject TEXT,
    content TEXT NOT NULL,
    tamil_content TEXT,
    variables TEXT DEFAULT '[]',
    credits_cost INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_follow_up_templates_active ON follow_up_templates(is_active);
CREATE INDEX IF NOT EXISTS idx_follow_up_templates_channel ON follow_up_templates(channel);
CREATE INDEX IF NOT EXISTS idx_follow_up_templates_type ON follow_up_templates(template_type);

-- Insert default templates with user-specified content
INSERT INTO follow_up_templates (
    name, 
    tamil_name, 
    description, 
    template_type, 
    channel, 
    subject, 
    content, 
    tamil_content, 
    variables, 
    credits_cost, 
    is_active
) VALUES
(
    'Default Email Template',
    'இயல்பான மின்னஞ்சல் வார்ப்புரு',
    'Default email follow-up template for sessions',
    'session_followup',
    'email',
    'Session Insights - Your Spiritual Journey',
    'நமஸ்காரம்! Your session insights...',
    'நமஸ்காரம்! Your session insights...',
    '["user_name", "session_date", "session_type"]',
    0,
    1
),
(
    'Default SMS Template',
    'இயல்பான SMS வார்ப்புரு',
    'Default SMS follow-up template for sessions',
    'session_followup',
    'sms',
    NULL,
    'Swami''s daily guidance for you...',
    'Swami''s daily guidance for you...',
    '["user_name", "session_date"]',
    1,
    1
),
(
    'Default WhatsApp Template',
    'இயல்பான வாட்ஸ்அப் வார்ப்புரு',
    'Default WhatsApp follow-up template for sessions',
    'session_followup',
    'whatsapp',
    NULL,
    '🕉️ Special message from Swami...',
    '🕉️ Special message from Swami...',
    '["user_name", "session_date"]',
    2,
    1
);

-- Verify the templates were created
SELECT 
    name, 
    tamil_name, 
    channel, 
    credits_cost, 
    is_active 
FROM follow_up_templates 
ORDER BY created_at; 