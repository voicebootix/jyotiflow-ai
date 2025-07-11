-- Migration: Add all feature tables for complete functionality
-- This ensures all features have their required tables

-- 1. Avatar Generation Tables
CREATE TABLE IF NOT EXISTS avatar_templates (
    id SERIAL PRIMARY KEY,
    template_name VARCHAR(100) UNIQUE NOT NULL,
    avatar_style VARCHAR(50) NOT NULL,
    voice_tone VARCHAR(50) NOT NULL,
    background_style VARCHAR(50) NOT NULL,
    clothing_style VARCHAR(50) NOT NULL,
    description TEXT,
    preview_image_url VARCHAR(500),
    is_premium BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS avatar_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    template_id INTEGER NOT NULL,
    avatar_prompt TEXT NOT NULL,
    generated_avatar_url VARCHAR(500),
    status VARCHAR(50) DEFAULT 'pending',
    generation_time_seconds DECIMAL(10,2),
    quality_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE,
    FOREIGN KEY (template_id) REFERENCES avatar_templates(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS avatar_generation_queue (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    template_id INTEGER NOT NULL,
    prompt TEXT NOT NULL,
    priority INTEGER DEFAULT 5,
    status VARCHAR(50) DEFAULT 'queued',
    attempts INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE,
    FOREIGN KEY (template_id) REFERENCES avatar_templates(id) ON DELETE CASCADE
);

-- 2. Agora Live Chat Tables
CREATE TABLE IF NOT EXISTS live_chat_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    channel_name VARCHAR(255) NOT NULL,
    agora_app_id VARCHAR(255) NOT NULL,
    agora_token VARCHAR(500) NOT NULL,
    user_role VARCHAR(50) DEFAULT 'audience',
    session_type VARCHAR(100) DEFAULT 'spiritual_guidance',
    mode VARCHAR(20) DEFAULT 'video',
    status VARCHAR(50) DEFAULT 'active',
    credits_used INTEGER DEFAULT 0,
    duration_minutes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    expires_at TIMESTAMP,
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS session_participants (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    agora_uid INTEGER NOT NULL,
    role VARCHAR(50) DEFAULT 'audience',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    left_at TIMESTAMP,
    duration_minutes INTEGER,
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS agora_usage_logs (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB DEFAULT '{}',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
);

-- 3. AI Marketing Director Tables
CREATE TABLE IF NOT EXISTS marketing_campaigns (
    id SERIAL PRIMARY KEY,
    campaign_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    campaign_type VARCHAR(50) NOT NULL,
    target_audience JSONB,
    budget DECIMAL(10,2),
    status VARCHAR(50) DEFAULT 'draft',
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    performance_metrics JSONB DEFAULT '{}',
    ai_recommendations JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS marketing_insights (
    id SERIAL PRIMARY KEY,
    insight_id VARCHAR(100) UNIQUE NOT NULL,
    insight_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    data_points JSONB,
    confidence_score DECIMAL(3,2),
    actionable_recommendations TEXT[],
    impact_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS performance_analytics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,2) NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    time_period VARCHAR(50) NOT NULL,
    dimensions JSONB DEFAULT '{}',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date DATE DEFAULT CURRENT_DATE
);

-- 4. Enhanced Spiritual Guidance Tables
CREATE TABLE IF NOT EXISTS rag_knowledge_base (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100),
    tags TEXT[],
    embedding_vector FLOAT[],
    metadata JSONB DEFAULT '{}',
    source_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

CREATE TABLE IF NOT EXISTS birth_chart_cache (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    birth_details_hash VARCHAR(64) UNIQUE NOT NULL,
    birth_details JSONB NOT NULL,
    chart_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    access_count INTEGER DEFAULT 1,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS service_usage_logs (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    service_type VARCHAR(100) NOT NULL,
    session_reference VARCHAR(255),
    credits_used INTEGER NOT NULL,
    duration_minutes INTEGER,
    cost_breakdown JSONB DEFAULT '{}',
    usage_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    billing_status VARCHAR(50) DEFAULT 'completed',
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
);

-- 5. User Management Tables
CREATE TABLE IF NOT EXISTS user_purchases (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    service_type VARCHAR(100) NOT NULL,
    credits_purchased INTEGER NOT NULL,
    amount_paid DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    payment_method VARCHAR(50),
    transaction_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'completed',
    purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    session_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT,
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
);

-- 6. Admin and Analytics Tables
CREATE TABLE IF NOT EXISTS admin_analytics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,2) NOT NULL,
    metric_category VARCHAR(50) NOT NULL,
    time_period VARCHAR(50) NOT NULL,
    metadata JSONB DEFAULT '{}',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date DATE DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS system_logs (
    id SERIAL PRIMARY KEY,
    log_level VARCHAR(20) NOT NULL,
    component VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    details JSONB DEFAULT '{}',
    user_email VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS admin_notifications (
    id SERIAL PRIMARY KEY,
    notification_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(50) DEFAULT 'unread',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_analytics (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB DEFAULT '{}',
    session_id VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS revenue_analytics (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    revenue_amount DECIMAL(15,2) NOT NULL,
    transaction_count INTEGER DEFAULT 0,
    user_count INTEGER DEFAULT 0,
    average_transaction_value DECIMAL(10,2),
    dimensions JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Monetization Tables
CREATE TABLE IF NOT EXISTS monetization_insights (
    id SERIAL PRIMARY KEY,
    recommendation_id VARCHAR(100) UNIQUE NOT NULL,
    recommendation_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    projected_revenue_increase_percent DECIMAL(5,2),
    projected_user_impact VARCHAR(255),
    confidence_score DECIMAL(3,2) NOT NULL,
    implementation_effort VARCHAR(20) NOT NULL,
    timeframe_days INTEGER,
    risk_level VARCHAR(20) NOT NULL,
    data_points JSONB,
    status VARCHAR(50) DEFAULT 'pending',
    admin_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS api_usage_metrics (
    id SERIAL PRIMARY KEY,
    api_name VARCHAR(100) NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    user_email VARCHAR(255),
    request_count INTEGER DEFAULT 1,
    response_time_ms INTEGER,
    status_code INTEGER,
    error_message TEXT,
    request_size_bytes INTEGER,
    response_size_bytes INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date DATE DEFAULT CURRENT_DATE,
    UNIQUE(api_name, endpoint, user_email, date)
);

-- 8. Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_avatar_sessions_user ON avatar_sessions(user_email);
CREATE INDEX IF NOT EXISTS idx_live_chat_sessions_user ON live_chat_sessions(user_email);
CREATE INDEX IF NOT EXISTS idx_marketing_campaigns_status ON marketing_campaigns(status);
CREATE INDEX IF NOT EXISTS idx_rag_knowledge_category ON rag_knowledge_base(category);
CREATE INDEX IF NOT EXISTS idx_birth_chart_cache_hash ON birth_chart_cache(birth_details_hash);
CREATE INDEX IF NOT EXISTS idx_user_analytics_date ON user_analytics(date);
CREATE INDEX IF NOT EXISTS idx_revenue_analytics_date ON revenue_analytics(date);