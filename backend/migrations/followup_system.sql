-- Follow-up System Database Migration
-- Add follow_up_sent column to sessions table
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS follow_up_sent BOOLEAN DEFAULT FALSE;
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS follow_up_count INTEGER DEFAULT 0;

-- Create follow_up_templates table
CREATE TABLE IF NOT EXISTS follow_up_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    tamil_name VARCHAR(100),
    description TEXT,
    template_type VARCHAR(50) NOT NULL DEFAULT 'session_followup',
    channel VARCHAR(20) NOT NULL DEFAULT 'email',
    subject VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    tamil_content TEXT,
    variables JSONB DEFAULT '[]',
    credits_cost INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create follow_up_schedules table
CREATE TABLE IF NOT EXISTS follow_up_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_email VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) REFERENCES sessions(id),
    template_id UUID REFERENCES follow_up_templates(id),
    channel VARCHAR(20) NOT NULL DEFAULT 'email',
    scheduled_at TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    credits_charged INTEGER DEFAULT 0,
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    read_at TIMESTAMP,
    failure_reason TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create follow_up_analytics table
CREATE TABLE IF NOT EXISTS follow_up_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    template_id UUID REFERENCES follow_up_templates(id),
    channel VARCHAR(20) NOT NULL,
    total_sent INTEGER DEFAULT 0,
    total_delivered INTEGER DEFAULT 0,
    total_read INTEGER DEFAULT 0,
    total_failed INTEGER DEFAULT 0,
    credits_charged INTEGER DEFAULT 0,
    revenue_generated DECIMAL(10,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(date, template_id, channel)
);

-- Create follow_up_settings table
CREATE TABLE IF NOT EXISTS follow_up_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT NOT NULL,
    setting_type VARCHAR(20) DEFAULT 'string',
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Insert default follow-up templates
INSERT INTO follow_up_templates (name, tamil_name, description, template_type, channel, subject, content, tamil_content, variables, credits_cost) VALUES
(
    'Session Follow-up 1',
    'அமர்வு பின்தொடர்தல் 1',
    'First follow-up after spiritual session',
    'session_followup',
    'email',
    'How is your spiritual journey progressing? 🕉️',
    'Dear {{user_name}},

Thank you for your recent spiritual consultation with JyotiFlow.ai. We hope the guidance provided has been helpful in your spiritual journey.

We would love to hear about your progress and any questions you may have:

1. How are you feeling after our session?
2. Have you been able to practice the guidance shared?
3. Do you have any new questions or concerns?

Remember, spiritual growth is a continuous journey. We are here to support you every step of the way.

With divine blessings,
The JyotiFlow.ai Team

P.S. Book your next session to continue your spiritual growth journey.',
    'அன்புள்ள {{user_name}},

ஜோதிப்லோவ்.ஏஐ-உடன் உங்கள் சமீபத்திய ஆன்மீக ஆலோசனைக்கு நன்றி. வழங்கப்பட்ட வழிகாட்டுதல் உங்கள் ஆன்மீக பயணத்தில் உதவியாக இருந்திருக்கும் என்று நம்புகிறோம்.

உங்கள் முன்னேற்றத்தைப் பற்றி கேட்க விரும்புகிறோம்:

1. நமது அமர்வுக்குப் பிறகு எப்படி உணர்கிறீர்கள்?
2. பகிரப்பட்ட வழிகாட்டுதல்களை நடைமுறைப்படுத்த முடிந்ததா?
3. புதிய கேள்விகள் அல்லது கவலைகள் உள்ளதா?

ஆன்மீக வளர்ச்சி என்பது தொடர்ச்சியான பயணம் என்பதை நினைவில் கொள்ளுங்கள். உங்களை ஆதரிக்க நாங்கள் இங்கே இருக்கிறோம்.

தெய்வீக ஆசீர்வாதங்களுடன்,
ஜோதிப்லோவ்.ஏஐ குழு',
    '["user_name", "session_date", "service_type"]',
    5
),
(
    'Session Follow-up 2',
    'அமர்வு பின்தொடர்தல் 2',
    'Second follow-up with additional guidance',
    'session_followup',
    'email',
    'Deepening your spiritual practice 🌟',
    'Dear {{user_name}},

We hope you are continuing to benefit from your spiritual guidance. As you progress on your journey, here are some additional insights:

**Daily Practice Suggestions:**
- Morning meditation (10-15 minutes)
- Evening reflection on your spiritual goals
- Weekly review of your progress

**Upcoming Opportunities:**
- Join our weekly satsang sessions
- Explore our premium consultation services
- Connect with our spiritual community

Would you like to schedule your next consultation to discuss your progress in detail?

With divine blessings,
The JyotiFlow.ai Team',
    'அன்புள்ள {{user_name}},

உங்கள் ஆன்மீக வழிகாட்டுதலில் இருந்து தொடர்ந்து பயனடைவீர்கள் என்று நம்புகிறோம். உங்கள் பயணத்தில் முன்னேறும்போது, இதோ சில கூடுதல் நுண்ணறிவுகள்:

**தினசரி பயிற்சி பரிந்துரைகள்:**
- காலை தியானம் (10-15 நிமிடங்கள்)
- மாலை ஆன்மீக இலக்குகளைப் பற்றிய சிந்தனை
- வாரந்தோறும் உங்கள் முன்னேற்றத்தை மதிப்பாய்வு செய்தல்

**வரவிருக்கும் வாய்ப்புகள்:**
- எங்கள் வாராந்திர சத்சங்க அமர்வுகளில் சேரவும்
- எங்கள் பிரீமியம் ஆலோசனை சேவைகளை ஆராயவும்
- எங்கள் ஆன்மீக சமூகத்துடன் இணைக்கவும்

உங்கள் முன்னேற்றத்தை விரிவாக விவாதிக்க உங்கள் அடுத்த ஆலோசனையை திட்டமிட விரும்புகிறீர்களா?

தெய்வீக ஆசீர்வாதங்களுடன்,
ஜோதிப்லோவ்.ஏஐ குழு',
    '["user_name", "session_date", "service_type"]',
    5
),
(
    'SMS Reminder',
    'எஸ்எம்எஸ் நினைவூட்டல்',
    'SMS reminder for follow-up',
    'reminder',
    'sms',
    '',
    'Namaste {{user_name}}! 🌟 Your spiritual journey continues. How are you feeling after our session? Need guidance? Reply YES for a quick consultation. JyotiFlow.ai',
    'நமஸ்காரம் {{user_name}}! 🌟 உங்கள் ஆன்மீக பயணம் தொடர்கிறது. நமது அமர்வுக்குப் பிறகு எப்படி உணர்கிறீர்கள்? வழிகாட்டுதல் தேவையா? விரைவான ஆலோசனைக்கு YES என்று பதிலளிக்கவும். ஜோதிப்லோவ்.ஏஐ',
    '["user_name"]',
    3
),
(
    'WhatsApp Check-in',
    'வாட்ஸ்அப் சோதனை',
    'WhatsApp check-in message',
    'check_in',
    'whatsapp',
    '',
    '🕉️ Namaste {{user_name}}!

We hope you are well on your spiritual path. 

Quick check-in:
✅ How is your practice going?
✅ Any questions or concerns?
✅ Ready for your next session?

Reply with your thoughts or book your next consultation at JyotiFlow.ai

With divine blessings 🙏',
    '🕉️ நமஸ்காரம் {{user_name}}!

உங்கள் ஆன்மீக பாதையில் நன்றாக இருக்கிறீர்கள் என்று நம்புகிறோம்.

விரைவான சோதனை:
✅ உங்கள் பயிற்சி எப்படி போகிறது?
✅ ஏதேனும் கேள்விகள் அல்லது கவலைகள் உள்ளதா?
✅ உங்கள் அடுத்த அமர்வுக்கு தயாரா?

உங்கள் எண்ணங்களை பதிலளிக்கவும் அல்லது JyotiFlow.ai-ல் உங்கள் அடுத்த ஆலோசனையை பதிவு செய்யவும்

தெய்வீக ஆசீர்வாதங்களுடன் 🙏',
    '["user_name"]',
    2
);

-- Insert default follow-up settings
INSERT INTO follow_up_settings (setting_key, setting_value, setting_type, description) VALUES
('auto_followup_enabled', 'true', 'boolean', 'Enable automatic follow-up system'),
('default_credits_cost', '5', 'integer', 'Default credits cost for follow-ups'),
('max_followups_per_session', '3', 'integer', 'Maximum follow-ups allowed per session'),
('min_interval_hours', '24', 'integer', 'Minimum interval between follow-ups in hours'),
('max_interval_days', '30', 'integer', 'Maximum interval for follow-ups in days'),
('auto_cancel_after_days', '7', 'integer', 'Auto-cancel follow-ups after days'),
('enable_smart_scheduling', 'true', 'boolean', 'Enable smart scheduling based on user behavior'),
('enable_credit_charging', 'true', 'boolean', 'Enable credit charging for follow-ups'),
('enable_analytics', 'true', 'boolean', 'Enable follow-up analytics tracking');

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_follow_up_schedules_user_email ON follow_up_schedules(user_email);
CREATE INDEX IF NOT EXISTS idx_follow_up_schedules_session_id ON follow_up_schedules(session_id);
CREATE INDEX IF NOT EXISTS idx_follow_up_schedules_status ON follow_up_schedules(status);
CREATE INDEX IF NOT EXISTS idx_follow_up_schedules_scheduled_at ON follow_up_schedules(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_follow_up_templates_active ON follow_up_templates(is_active);
CREATE INDEX IF NOT EXISTS idx_follow_up_analytics_date ON follow_up_analytics(date); 