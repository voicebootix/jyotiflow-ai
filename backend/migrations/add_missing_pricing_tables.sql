-- Add missing tables for universal pricing engine
-- Migration: Add missing pricing and session tables
-- FIXED: PostgreSQL syntax (SERIAL instead of AUTOINCREMENT, TIMESTAMP instead of DATETIME)
-- FIXED: Ensure sessions table compatibility with existing structure

-- Sessions table for demand tracking (only if not exists or add missing columns)
-- First, try to add columns to existing sessions table if it exists
DO $$
BEGIN
    -- Check if sessions table exists
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'sessions') THEN
        -- Add missing columns if they don't exist
        IF NOT EXISTS (SELECT FROM information_schema.columns 
                      WHERE table_name = 'sessions' AND column_name = 'duration_minutes') THEN
            ALTER TABLE sessions ADD COLUMN duration_minutes INTEGER DEFAULT 0;
        END IF;
        
        IF NOT EXISTS (SELECT FROM information_schema.columns 
                      WHERE table_name = 'sessions' AND column_name = 'session_data') THEN
            ALTER TABLE sessions ADD COLUMN session_data TEXT;
        END IF;
    ELSE
        -- Create sessions table if it doesn't exist
        CREATE TABLE sessions (
            id SERIAL PRIMARY KEY,
            user_id TEXT,
            service_type TEXT NOT NULL,
            duration_minutes INTEGER DEFAULT 0,
            credits_used INTEGER DEFAULT 0,
            session_data TEXT, -- JSON data
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active'
        );
    END IF;
END $$;

-- AI pricing recommendations table
CREATE TABLE IF NOT EXISTS ai_pricing_recommendations (
    id SERIAL PRIMARY KEY,
    service_type TEXT NOT NULL,
    recommendation_data TEXT NOT NULL, -- JSON data
    confidence_score REAL DEFAULT 0.5,
    status TEXT DEFAULT 'pending', -- pending, approved, rejected
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    admin_notes TEXT,
    applied_at TIMESTAMP
);

-- Service usage logs for cost tracking
CREATE TABLE IF NOT EXISTS service_usage_logs (
    id SERIAL PRIMARY KEY,
    service_type TEXT NOT NULL,
    api_name TEXT NOT NULL, -- elevenlabs, d_id, agora, openai
    usage_type TEXT NOT NULL, -- minutes, tokens, calls
    usage_amount REAL NOT NULL,
    cost_usd REAL NOT NULL,
    cost_credits REAL NOT NULL,
    session_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add foreign key constraint separately to handle existing sessions table
DO $$
BEGIN
    -- Only add foreign key if sessions table exists and has id column
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'sessions') AND
       EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'sessions' AND column_name = 'id') THEN
        
        -- Check if foreign key constraint doesn't already exist
        IF NOT EXISTS (SELECT FROM information_schema.table_constraints 
                      WHERE table_name = 'service_usage_logs' 
                      AND constraint_name = 'service_usage_logs_session_id_fkey') THEN
            ALTER TABLE service_usage_logs 
            ADD CONSTRAINT service_usage_logs_session_id_fkey 
            FOREIGN KEY (session_id) REFERENCES sessions(id);
        END IF;
    END IF;
END $$;

-- API usage metrics for real-time monitoring
CREATE TABLE IF NOT EXISTS api_usage_metrics (
    id SERIAL PRIMARY KEY,
    api_name TEXT NOT NULL,
    endpoint TEXT,
    calls_count INTEGER DEFAULT 0,
    total_cost_usd REAL DEFAULT 0,
    total_cost_credits REAL DEFAULT 0,
    average_response_time REAL DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    date DATE DEFAULT CURRENT_DATE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(api_name, endpoint, date)
);

-- Satsang events table (enhanced)
CREATE TABLE IF NOT EXISTS satsang_events (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    scheduled_at TIMESTAMP NOT NULL,
    duration_minutes INTEGER DEFAULT 60,
    max_participants INTEGER DEFAULT 1000,
    current_participants INTEGER DEFAULT 0,
    theme TEXT,
    host_name TEXT DEFAULT 'Swamiji',
    event_type TEXT DEFAULT 'community', -- community, premium, interactive
    has_donations BOOLEAN DEFAULT TRUE,
    interactive_level TEXT DEFAULT 'basic', -- basic, advanced, premium
    voice_enabled BOOLEAN DEFAULT TRUE,
    video_enabled BOOLEAN DEFAULT TRUE,
    base_credits INTEGER DEFAULT 5,
    dynamic_pricing_enabled BOOLEAN DEFAULT TRUE,
    created_by TEXT DEFAULT 'system',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'scheduled' -- scheduled, live, completed, cancelled
);

-- Satsang donations/superchats table
CREATE TABLE IF NOT EXISTS satsang_donations (
    id SERIAL PRIMARY KEY,
    satsang_event_id INTEGER NOT NULL,
    user_id TEXT,
    amount_credits INTEGER NOT NULL,
    amount_usd REAL,
    message TEXT,
    is_superchat BOOLEAN DEFAULT FALSE,
    highlight_duration INTEGER DEFAULT 0, -- seconds to highlight
    donation_type TEXT DEFAULT 'general', -- general, superchat, dedication
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (satsang_event_id) REFERENCES satsang_events(id)
);

-- Satsang attendees table
CREATE TABLE IF NOT EXISTS satsang_attendees (
    id SERIAL PRIMARY KEY,
    satsang_event_id INTEGER NOT NULL,
    user_id TEXT NOT NULL,
    join_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    leave_time TIMESTAMP,
    interaction_count INTEGER DEFAULT 0,
    donation_total REAL DEFAULT 0,
    attendance_duration INTEGER DEFAULT 0, -- minutes
    FOREIGN KEY (satsang_event_id) REFERENCES satsang_events(id),
    UNIQUE(satsang_event_id, user_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_sessions_service_type ON sessions(service_type);
CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_ai_recommendations_service ON ai_pricing_recommendations(service_type, status);
CREATE INDEX IF NOT EXISTS idx_usage_logs_service_api ON service_usage_logs(service_type, api_name);
CREATE INDEX IF NOT EXISTS idx_usage_logs_created_at ON service_usage_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_api_metrics_date ON api_usage_metrics(date, api_name);
CREATE INDEX IF NOT EXISTS idx_satsang_events_scheduled ON satsang_events(scheduled_at, status);
CREATE INDEX IF NOT EXISTS idx_satsang_donations_event ON satsang_donations(satsang_event_id);
CREATE INDEX IF NOT EXISTS idx_satsang_attendees_event ON satsang_attendees(satsang_event_id);

-- Sample data for testing (PostgreSQL syntax)
INSERT INTO sessions (service_type, duration_minutes, credits_used, created_at) VALUES
('comprehensive_life_reading_30min', 30, 15, CURRENT_TIMESTAMP - INTERVAL '1 day'),
('comprehensive_life_reading_30min', 30, 15, CURRENT_TIMESTAMP - INTERVAL '2 hours'),
('horoscope_reading_quick', 10, 8, CURRENT_TIMESTAMP - INTERVAL '3 hours'),
('satsang_community', 60, 5, CURRENT_TIMESTAMP - INTERVAL '1 day')
ON CONFLICT DO NOTHING;

INSERT INTO ai_pricing_recommendations (service_type, recommendation_data, confidence_score, status) VALUES
('comprehensive_life_reading_30min', '{"suggested_price": 16.5, "reasoning": "High demand and increased API costs"}', 0.78, 'pending'),
('horoscope_reading_quick', '{"suggested_price": 9.0, "reasoning": "Stable demand, optimized costs"}', 0.65, 'pending')
ON CONFLICT DO NOTHING;

-- Sample satsang event
INSERT INTO satsang_events (
    title, description, scheduled_at, duration_minutes, theme, event_type, 
    has_donations, interactive_level, voice_enabled, video_enabled, base_credits
) VALUES (
    'Monthly Community Satsang',
    'Join our global spiritual family for guided meditation, spiritual discourse, and community connection',
    CURRENT_TIMESTAMP + INTERVAL '7 days' + INTERVAL '10 hours', -- Next week at 10 AM
    90,
    'Inner Peace and Divine Connection',
    'community',
    TRUE,
    'basic',
    TRUE,
    TRUE,
    5
) ON CONFLICT DO NOTHING;

-- Triggers for updated_at timestamps (PostgreSQL syntax)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_sessions_timestamp 
    BEFORE UPDATE ON sessions 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_satsang_events_timestamp 
    BEFORE UPDATE ON satsang_events 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_api_metrics_timestamp 
    BEFORE UPDATE ON api_usage_metrics 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

