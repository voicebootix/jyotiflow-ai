-- Create follow_up_templates table and insert default templates
-- PostgreSQL Migration Script

-- Create follow_up_templates table
CREATE TABLE IF NOT EXISTS follow_up_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    tamil_name VARCHAR(100),
    description TEXT,
    template_type VARCHAR(50) NOT NULL DEFAULT 'session_followup',
    channel VARCHAR(20) NOT NULL DEFAULT 'email',
    subject VARCHAR(200),
    content TEXT NOT NULL,
    tamil_content TEXT,
    variables JSONB DEFAULT '[]',
    credits_cost INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
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
    TRUE
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
    TRUE
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
    TRUE
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