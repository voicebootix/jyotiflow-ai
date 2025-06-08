-- 🙏🏼 JyotiFlow.ai PostgreSQL Database Schema
-- Swami Jyotirananthan's Digital Ashram Database Structure
-- தமிழ் - ஆன்மீக வழிகாட்டுதல் தளத்திற்கான database schema

-- தமிழ் - Users table - பயனர்களின் தகவல்கள்
CREATE TABLE IF NOT EXISTS users (
    email TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    birth_date TEXT,  -- தமிழ் - பிறந்த தேதி (YYYY-MM-DD format)
    birth_time TEXT,  -- தமிழ் - பிறந்த நேரம் (HH:MM format)
    birth_location TEXT,  -- தமிழ் - பிறந்த இடம்
    credits INTEGER DEFAULT 0,  -- தமிழ் - ஆன்மீக வழிகாட்டுதல் credits
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- தமிழ் - Sessions table - ஆன்மீக வழிகாட்டுதல் sessions
CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    user_email TEXT REFERENCES users(email) ON DELETE CASCADE,
    session_type TEXT NOT NULL,  -- தமிழ் - clarity, love, premium, elite
    credits_used INTEGER NOT NULL,
    result_summary TEXT,  -- தமிழ் - Swami Jyotirananthan's guidance
    session_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'completed',  -- தமிழ் - started, completed, failed
    zoom_session_id TEXT,  -- தமிழ் - SalesCloser Zoom session ID
    birth_chart_data JSONB,  -- தமிழ் - Prokerala birth chart data
    question TEXT,  -- தமிழ் - User's spiritual question
    duration_minutes INTEGER,  -- தமிழ் - Session duration
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- தமிழ் - User insights table - பயனர்களின் ஆன்மீக insights
CREATE TABLE IF NOT EXISTS user_insights (
    id SERIAL PRIMARY KEY,
    user_email TEXT REFERENCES users(email) ON DELETE CASCADE,
    type TEXT NOT NULL,  -- தமிழ் - daily, weekly, monthly insights
    content TEXT NOT NULL,  -- தமிழ் - Spiritual insight content
    session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sku_type TEXT,  -- தமிழ் - Which service generated this insight
    astrological_data JSONB,  -- தமிழ் - Related astrological information
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- தமிழ் - Admin logs table - நிர்வாக செயல்பாடுகளின் பதிவு
CREATE TABLE IF NOT EXISTS admin_logs (
    id SERIAL PRIMARY KEY,
    admin_email TEXT NOT NULL,
    action TEXT NOT NULL,  -- தமிழ் - credit_adjustment, session_review, etc.
    target_user TEXT,  -- தமிழ் - Affected user email
    details TEXT,  -- தமிழ் - Action details
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address TEXT,  -- தமிழ் - Admin IP for security
    metadata JSONB  -- தமிழ் - Additional action metadata
);

-- தமிழ் - Feedback table - பயனர்களின் கருத்துக்கள்
CREATE TABLE IF NOT EXISTS feedback (
    id SERIAL PRIMARY KEY,
    user_email TEXT,  -- தமிழ் - Optional, can be anonymous
    session_id INTEGER REFERENCES sessions(id),
    message TEXT NOT NULL,
    sentiment TEXT,  -- தமிழ் - positive, neutral, negative
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    category TEXT,  -- தமிழ் - guidance_quality, platform_experience, etc.
    is_anonymous BOOLEAN DEFAULT FALSE
);

-- தமிழ் - Payment transactions table - பணம் செலுத்துதல் பதிவுகள்
CREATE TABLE IF NOT EXISTS payment_transactions (
    id SERIAL PRIMARY KEY,
    user_email TEXT REFERENCES users(email) ON DELETE CASCADE,
    stripe_session_id TEXT UNIQUE,
    stripe_payment_intent_id TEXT,
    amount_cents INTEGER NOT NULL,  -- தமிழ் - Amount in cents
    currency TEXT DEFAULT 'usd',
    credits_purchased INTEGER NOT NULL,
    package_type TEXT NOT NULL,  -- தமிழ் - starter, popular, premium, seeker
    status TEXT DEFAULT 'pending',  -- தமிழ் - pending, completed, failed, refunded
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    metadata JSONB  -- தமிழ் - Additional payment metadata
);

-- தமிழ் - API usage logs table - API பயன்பாட்டு பதிவுகள்
CREATE TABLE IF NOT EXISTS api_usage_logs (
    id SERIAL PRIMARY KEY,
    user_email TEXT,
    api_service TEXT NOT NULL,  -- தமிழ் - openai, prokerala, salescloser
    endpoint TEXT,
    request_data JSONB,
    response_data JSONB,
    status_code INTEGER,
    response_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id INTEGER REFERENCES sessions(id),
    error_message TEXT
);

-- தமிழ் - Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
CREATE INDEX IF NOT EXISTS idx_sessions_user_email ON sessions(user_email);
CREATE INDEX IF NOT EXISTS idx_sessions_session_time ON sessions(session_time);
CREATE INDEX IF NOT EXISTS idx_sessions_session_type ON sessions(session_type);
CREATE INDEX IF NOT EXISTS idx_admin_logs_timestamp ON admin_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_admin_logs_admin_email ON admin_logs(admin_email);
CREATE INDEX IF NOT EXISTS idx_feedback_created_at ON feedback(created_at);
CREATE INDEX IF NOT EXISTS idx_payment_transactions_user_email ON payment_transactions(user_email);
CREATE INDEX IF NOT EXISTS idx_payment_transactions_created_at ON payment_transactions(created_at);
CREATE INDEX IF NOT EXISTS idx_api_usage_logs_created_at ON api_usage_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_api_usage_logs_api_service ON api_usage_logs(api_service);

-- தமிழ் - Create admin user with hashed password
-- Note: In production, run this separately with proper password hashing
-- INSERT INTO users (email, password_hash, first_name, last_name, credits) 
-- VALUES ('admin@jyotiflow.ai', '$2b$12$...', 'Admin', 'User', 1000);

-- தமிழ் - Sample data for testing (remove in production)
-- INSERT INTO users (email, password_hash, first_name, last_name, credits, birth_date, birth_time, birth_location)
-- VALUES 
--     ('test@jyotiflow.ai', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.Gm.F5e', 'Test', 'User', 10, '1990-01-01', '10:30', 'Chennai, India'),
--     ('seeker@jyotiflow.ai', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.Gm.F5e', 'Spiritual', 'Seeker', 5, '1985-06-15', '14:45', 'Mumbai, India');

-- தமிழ் - Functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- தமிழ் - Trigger for users table updated_at
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- தமிழ் - View for session analytics
CREATE OR REPLACE VIEW session_analytics AS
SELECT 
    session_type,
    COUNT(*) as total_sessions,
    SUM(credits_used) as total_credits_used,
    AVG(credits_used) as avg_credits_per_session,
    COUNT(DISTINCT user_email) as unique_users,
    DATE_TRUNC('day', session_time) as session_date
FROM sessions 
WHERE status = 'completed'
GROUP BY session_type, DATE_TRUNC('day', session_time)
ORDER BY session_date DESC;

-- தமிழ் - View for user statistics
CREATE OR REPLACE VIEW user_statistics AS
SELECT 
    u.email,
    u.first_name,
    u.last_name,
    u.credits,
    u.created_at as registration_date,
    u.last_login,
    COUNT(s.id) as total_sessions,
    SUM(s.credits_used) as total_credits_spent,
    MAX(s.session_time) as last_session_date
FROM users u
LEFT JOIN sessions s ON u.email = s.user_email
GROUP BY u.email, u.first_name, u.last_name, u.credits, u.created_at, u.last_login
ORDER BY u.created_at DESC;

-- தமிழ் - Function to clean old logs (run monthly)
CREATE OR REPLACE FUNCTION cleanup_old_logs()
RETURNS void AS $$
BEGIN
    -- தமிழ் - Delete API logs older than 3 months
    DELETE FROM api_usage_logs 
    WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '3 months';
    
    -- தமிழ் - Delete admin logs older than 1 year
    DELETE FROM admin_logs 
    WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '1 year';
    
    -- தமிழ் - Archive old sessions (move to archive table if needed)
    -- This is a placeholder for archival logic
    
END;
$$ LANGUAGE plpgsql;

-- தமிழ் - Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO jyotiflow_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO jyotiflow_user;

-- தமிழ் - Database setup complete
-- 🙏🏼 May Swami Jyotirananthan's digital ashram serve seekers with wisdom and compassion

