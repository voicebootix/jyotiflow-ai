-- JyotiFlow.ai Comprehensive Database Fix Script
-- This script creates all missing tables and fixes column/constraint issues
-- Run this script against your Supabase database to enable full platform functionality

-- Start transaction for atomic execution
BEGIN;

-- =====================================================
-- PART 1: Fix existing table issues
-- =====================================================

-- Fix users table column naming
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='users' AND column_name='last_login'
    ) AND NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='users' AND column_name='last_login_at'
    ) THEN
        ALTER TABLE users RENAME COLUMN last_login TO last_login_at;
    END IF;
END $$;

-- Fix service_types display_name constraint
ALTER TABLE service_types ALTER COLUMN display_name DROP NOT NULL;

-- Add missing columns to existing tables
DO $$
BEGIN
    -- Add missing columns to service_types
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='service_types' AND column_name='is_premium') THEN
        ALTER TABLE service_types ADD COLUMN is_premium BOOLEAN DEFAULT false;
    END IF;
    
    -- Add missing columns to api_usage_metrics
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='api_usage_metrics' AND column_name='api_name') THEN
        -- Column already exists in the schema, this is just a safety check
        NULL;
    END IF;
END $$;

-- =====================================================
-- PART 2: Create missing core tables
-- =====================================================

-- 1. Service Configuration Cache (Critical - mentioned in logs)
CREATE TABLE IF NOT EXISTS service_configuration_cache (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(255) NOT NULL,
    config_key VARCHAR(255),
    config_value TEXT,
    configuration JSONB DEFAULT '{}',
    persona_config JSONB DEFAULT '{}',
    knowledge_domains JSONB DEFAULT '[]',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '24 hours'),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(service_name, config_key)
);

-- 2. Credit Transactions
CREATE TABLE IF NOT EXISTS credit_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    user_email VARCHAR(255) NOT NULL,
    package_id INTEGER,
    credits_purchased INTEGER NOT NULL,
    bonus_credits INTEGER DEFAULT 0,
    total_credits INTEGER NOT NULL,
    amount_usd DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    payment_method VARCHAR(50),
    transaction_id VARCHAR(255) UNIQUE,
    stripe_payment_intent_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
);

-- 3. Donation Transactions
CREATE TABLE IF NOT EXISTS donation_transactions (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    donation_id INTEGER,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    payment_method VARCHAR(50),
    transaction_id VARCHAR(255) UNIQUE,
    status VARCHAR(50) DEFAULT 'completed',
    temple_name VARCHAR(255),
    deity_name VARCHAR(255),
    purpose TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
);

-- 4. Session Donations
CREATE TABLE IF NOT EXISTS session_donations (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    donation_transaction_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (donation_transaction_id) REFERENCES donation_transactions(id) ON DELETE CASCADE
);

-- 5. Follow-up Interactions
CREATE TABLE IF NOT EXISTS followup_interactions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    question_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    answer_timestamp TIMESTAMP,
    ai_confidence_score DECIMAL(3,2),
    tokens_used INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
);

-- =====================================================
-- PART 3: Communication and Notification Tables
-- =====================================================

-- 6. Email Logs
CREATE TABLE IF NOT EXISTS email_logs (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255),
    recipient_email VARCHAR(255) NOT NULL,
    subject VARCHAR(500) NOT NULL,
    template_id VARCHAR(100),
    status VARCHAR(50) DEFAULT 'pending',
    provider VARCHAR(50) DEFAULT 'sendgrid',
    provider_message_id VARCHAR(255),
    opened_at TIMESTAMP,
    clicked_at TIMESTAMP,
    bounced_at TIMESTAMP,
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP
);

-- 7. SMS Logs
CREATE TABLE IF NOT EXISTS sms_logs (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255),
    recipient_phone VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    template_id VARCHAR(100),
    status VARCHAR(50) DEFAULT 'pending',
    provider VARCHAR(50) DEFAULT 'twilio',
    provider_message_id VARCHAR(255),
    delivered_at TIMESTAMP,
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP
);

-- 8. Webhook Logs
CREATE TABLE IF NOT EXISTS webhook_logs (
    id SERIAL PRIMARY KEY,
    webhook_type VARCHAR(100) NOT NULL,
    endpoint_url VARCHAR(500) NOT NULL,
    payload JSONB NOT NULL,
    response_status INTEGER,
    response_body TEXT,
    attempts INTEGER DEFAULT 1,
    success BOOLEAN DEFAULT false,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_attempt_at TIMESTAMP
);

-- 9. Notification Templates
CREATE TABLE IF NOT EXISTS notification_templates (
    id SERIAL PRIMARY KEY,
    template_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'email', 'sms', 'push'
    subject VARCHAR(500),
    content TEXT NOT NULL,
    variables JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. Notification Queue
CREATE TABLE IF NOT EXISTS notification_queue (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    template_id VARCHAR(100),
    data JSONB DEFAULT '{}',
    priority INTEGER DEFAULT 5,
    status VARCHAR(50) DEFAULT 'queued',
    scheduled_for TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    sent_at TIMESTAMP,
    failed_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- PART 4: Subscription and Payment Tables
-- =====================================================

-- 11. Subscription Plans
CREATE TABLE IF NOT EXISTS subscription_plans (
    id SERIAL PRIMARY KEY,
    plan_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price_usd DECIMAL(10,2) NOT NULL,
    billing_period VARCHAR(50) NOT NULL, -- 'monthly', 'yearly'
    credits_per_period INTEGER NOT NULL,
    features JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT true,
    stripe_product_id VARCHAR(255),
    stripe_price_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 12. Subscription History
CREATE TABLE IF NOT EXISTS subscription_history (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    plan_id VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL, -- 'subscribed', 'upgraded', 'downgraded', 'cancelled', 'expired'
    previous_plan_id VARCHAR(100),
    reason TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
);

-- 13. Refunds
CREATE TABLE IF NOT EXISTS refunds (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    original_transaction_id VARCHAR(255) NOT NULL,
    refund_amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    reason TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    stripe_refund_id VARCHAR(255),
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
);

-- 14. Coupons
CREATE TABLE IF NOT EXISTS coupons (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    discount_type VARCHAR(50) NOT NULL, -- 'percentage', 'fixed'
    discount_value DECIMAL(10,2) NOT NULL,
    max_uses INTEGER,
    used_count INTEGER DEFAULT 0,
    valid_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_until TIMESTAMP,
    minimum_purchase DECIMAL(10,2),
    applicable_services JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 15. User Coupons
CREATE TABLE IF NOT EXISTS user_coupons (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    coupon_code VARCHAR(50) NOT NULL,
    used_at TIMESTAMP,
    transaction_id VARCHAR(255),
    discount_applied DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE,
    FOREIGN KEY (coupon_code) REFERENCES coupons(code) ON DELETE CASCADE
);

-- =====================================================
-- PART 5: Chat and Expert Management Tables
-- =====================================================

-- 16. Chat Messages
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    message_type VARCHAR(50) NOT NULL, -- 'user', 'ai', 'system', 'expert'
    content TEXT NOT NULL,
    attachments JSONB DEFAULT '[]',
    is_edited BOOLEAN DEFAULT false,
    edited_at TIMESTAMP,
    deleted_at TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
);

-- 17. Spiritual Practitioners / Astrologer Profiles
CREATE TABLE IF NOT EXISTS spiritual_practitioners (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    bio TEXT,
    experience_years INTEGER,
    specializations JSONB DEFAULT '[]',
    languages JSONB DEFAULT '[]',
    certifications JSONB DEFAULT '[]',
    profile_image_url VARCHAR(500),
    rating DECIMAL(3,2) DEFAULT 0,
    total_sessions INTEGER DEFAULT 0,
    is_verified BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    hourly_rate DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 18. Practitioner Availability
CREATE TABLE IF NOT EXISTS practitioner_availability (
    id SERIAL PRIMARY KEY,
    practitioner_email VARCHAR(255) NOT NULL,
    day_of_week INTEGER NOT NULL, -- 0-6 (Sunday-Saturday)
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    timezone VARCHAR(50) DEFAULT 'UTC',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (practitioner_email) REFERENCES spiritual_practitioners(email) ON DELETE CASCADE
);

-- 19. Appointments
CREATE TABLE IF NOT EXISTS appointments (
    id SERIAL PRIMARY KEY,
    appointment_id VARCHAR(255) UNIQUE NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    practitioner_email VARCHAR(255) NOT NULL,
    service_type VARCHAR(100) NOT NULL,
    scheduled_start TIMESTAMP NOT NULL,
    scheduled_end TIMESTAMP NOT NULL,
    actual_start TIMESTAMP,
    actual_end TIMESTAMP,
    status VARCHAR(50) DEFAULT 'scheduled', -- 'scheduled', 'confirmed', 'in_progress', 'completed', 'cancelled', 'no_show'
    cancellation_reason TEXT,
    cancelled_by VARCHAR(255),
    cancelled_at TIMESTAMP,
    meeting_link VARCHAR(500),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE,
    FOREIGN KEY (practitioner_email) REFERENCES spiritual_practitioners(email) ON DELETE CASCADE
);

-- 20. Reviews
CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    practitioner_email VARCHAR(255),
    service_type VARCHAR(100),
    session_id VARCHAR(255),
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(255),
    comment TEXT,
    is_verified_purchase BOOLEAN DEFAULT true,
    helpful_count INTEGER DEFAULT 0,
    not_helpful_count INTEGER DEFAULT 0,
    admin_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
);

-- =====================================================
-- PART 6: Support and Help Center Tables
-- =====================================================

-- 21. Support Tickets
CREATE TABLE IF NOT EXISTS support_tickets (
    id SERIAL PRIMARY KEY,
    ticket_id VARCHAR(100) UNIQUE NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    priority VARCHAR(50) DEFAULT 'medium',
    subject VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'open',
    assigned_to VARCHAR(255),
    resolved_at TIMESTAMP,
    satisfaction_rating INTEGER,
    tags JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
);

-- 22. Knowledge Articles
CREATE TABLE IF NOT EXISTS knowledge_articles (
    id SERIAL PRIMARY KEY,
    article_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    slug VARCHAR(500) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    tags JSONB DEFAULT '[]',
    author_email VARCHAR(255),
    is_published BOOLEAN DEFAULT false,
    view_count INTEGER DEFAULT 0,
    helpful_count INTEGER DEFAULT 0,
    not_helpful_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- PART 7: Security and Compliance Tables
-- =====================================================

-- 23. Audit Logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id VARCHAR(255),
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 24. Rate Limits
CREATE TABLE IF NOT EXISTS rate_limits (
    id SERIAL PRIMARY KEY,
    identifier VARCHAR(255) NOT NULL, -- can be user_email, ip_address, api_key
    endpoint VARCHAR(255) NOT NULL,
    window_start TIMESTAMP NOT NULL,
    request_count INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(identifier, endpoint, window_start)
);

-- 25. Data Exports (GDPR Compliance)
CREATE TABLE IF NOT EXISTS data_exports (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    export_type VARCHAR(50) NOT NULL, -- 'gdpr', 'backup', 'deletion'
    status VARCHAR(50) DEFAULT 'pending',
    file_url VARCHAR(500),
    expires_at TIMESTAMP,
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
);

-- 26. Consent Logs
CREATE TABLE IF NOT EXISTS consent_logs (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    consent_type VARCHAR(100) NOT NULL,
    granted BOOLEAN NOT NULL,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
);

-- =====================================================
-- PART 8: Advanced Features Tables
-- =====================================================

-- 27. Session Transcripts
CREATE TABLE IF NOT EXISTS session_transcripts (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    turn_number INTEGER NOT NULL,
    speaker VARCHAR(50) NOT NULL, -- 'user', 'ai', 'expert'
    content TEXT NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- 28. Remedy Recommendations
CREATE TABLE IF NOT EXISTS remedy_recommendations (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    remedy_type VARCHAR(100) NOT NULL,
    remedy_name VARCHAR(255) NOT NULL,
    description TEXT,
    instructions TEXT,
    duration_days INTEGER,
    priority VARCHAR(50) DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
);

-- 29. User Birth Charts
CREATE TABLE IF NOT EXISTS user_birth_charts (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    chart_type VARCHAR(50) NOT NULL, -- 'natal', 'transit', 'progression'
    chart_data JSONB NOT NULL,
    interpretation JSONB,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
);

-- 30. Compatibility Reports
CREATE TABLE IF NOT EXISTS compatibility_reports (
    id SERIAL PRIMARY KEY,
    user1_email VARCHAR(255) NOT NULL,
    user2_email VARCHAR(255) NOT NULL,
    compatibility_score DECIMAL(3,2),
    analysis JSONB NOT NULL,
    report_type VARCHAR(50) DEFAULT 'romantic',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user1_email) REFERENCES users(email) ON DELETE CASCADE,
    FOREIGN KEY (user2_email) REFERENCES users(email) ON DELETE CASCADE
);

-- =====================================================
-- PART 9: Create Indexes for Performance
-- =====================================================

-- Service Configuration Cache
CREATE INDEX IF NOT EXISTS idx_service_config_cache_name ON service_configuration_cache(service_name);
CREATE INDEX IF NOT EXISTS idx_service_config_cache_expires ON service_configuration_cache(expires_at);

-- Credit Transactions
CREATE INDEX IF NOT EXISTS idx_credit_trans_user ON credit_transactions(user_email);
CREATE INDEX IF NOT EXISTS idx_credit_trans_status ON credit_transactions(status);

-- Email/SMS Logs
CREATE INDEX IF NOT EXISTS idx_email_logs_user ON email_logs(user_email);
CREATE INDEX IF NOT EXISTS idx_email_logs_status ON email_logs(status);
CREATE INDEX IF NOT EXISTS idx_sms_logs_user ON sms_logs(user_email);

-- Notifications
CREATE INDEX IF NOT EXISTS idx_notif_queue_user ON notification_queue(user_email);
CREATE INDEX IF NOT EXISTS idx_notif_queue_status ON notification_queue(status);

-- Sessions and Appointments
CREATE INDEX IF NOT EXISTS idx_appointments_user ON appointments(user_email);
CREATE INDEX IF NOT EXISTS idx_appointments_practitioner ON appointments(practitioner_email);
CREATE INDEX IF NOT EXISTS idx_appointments_scheduled ON appointments(scheduled_start);

-- Support
CREATE INDEX IF NOT EXISTS idx_support_tickets_user ON support_tickets(user_email);
CREATE INDEX IF NOT EXISTS idx_support_tickets_status ON support_tickets(status);

-- Audit and Security
CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_email);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_rate_limits_identifier ON rate_limits(identifier, endpoint);

-- =====================================================
-- PART 10: Insert Essential Data
-- =====================================================

-- Insert default notification templates
INSERT INTO notification_templates (template_id, name, type, subject, content, variables) VALUES
    ('welcome_email', 'Welcome Email', 'email', 'Welcome to JyotiFlow.ai', 'Dear {{name}}, Welcome to your spiritual journey...', '["name"]'),
    ('session_reminder', 'Session Reminder', 'email', 'Your upcoming spiritual guidance session', 'Your session is scheduled for {{date}} at {{time}}...', '["date", "time"]'),
    ('payment_success', 'Payment Success', 'email', 'Payment received - Thank you!', 'We have received your payment of {{amount}}...', '["amount"]')
ON CONFLICT (template_id) DO NOTHING;

-- Insert default subscription plans
INSERT INTO subscription_plans (plan_id, name, description, price_usd, billing_period, credits_per_period, features) VALUES
    ('basic_monthly', 'Basic Monthly', 'Perfect for beginners', 19.99, 'monthly', 20, '["Basic spiritual guidance", "Birth chart analysis", "Email support"]'),
    ('premium_monthly', 'Premium Monthly', 'Most popular choice', 49.99, 'monthly', 60, '["All Basic features", "Live chat sessions", "Priority support", "Personalized remedies"]'),
    ('divine_yearly', 'Divine Yearly', 'Best value for dedicated seekers', 399.99, 'yearly', 1000, '["All Premium features", "Unlimited sessions", "1-on-1 expert consultations", "Advanced predictions"]')
ON CONFLICT (plan_id) DO NOTHING;

-- Insert default service configuration cache entries
INSERT INTO service_configuration_cache (service_name, configuration) VALUES
    ('tarot_ai', '{"enabled": true, "model": "gpt-4", "temperature": 0.7, "max_tokens": 1000}'),
    ('spiritual_guidance', '{"enabled": true, "model": "gpt-4", "temperature": 0.8, "max_tokens": 1500}'),
    ('birth_chart_analysis', '{"enabled": true, "calculation_method": "tropical", "house_system": "placidus"}')
ON CONFLICT (service_name, config_key) DO UPDATE SET configuration = EXCLUDED.configuration;

-- Insert feature flags
INSERT INTO feature_flags (flag_name, is_enabled, description) VALUES
    ('avatar_generation', true, 'Enable AI avatar generation feature'),
    ('live_chat', true, 'Enable live chat with spiritual experts'),
    ('social_media_integration', true, 'Enable social media marketing features'),
    ('advanced_analytics', true, 'Enable advanced analytics dashboard'),
    ('multi_language', false, 'Enable multi-language support')
ON CONFLICT (flag_name) DO NOTHING;

-- Grant permissions to database user
DO $$
BEGIN
    -- Grant permissions on all new tables
    GRANT ALL ON ALL TABLES IN SCHEMA public TO jyotiflow_db_user;
    GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO jyotiflow_db_user;
    GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO jyotiflow_db_user;
EXCEPTION
    WHEN undefined_object THEN
        -- User doesn't exist, skip grants
        NULL;
END $$;

-- Commit transaction
COMMIT;

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================
-- After running this script, you can verify with:
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;
-- This should show all tables including the newly created ones