-- SIMPLE DATABASE FIXES FOR JYOTIFLOW.AI
-- This script fixes the most critical database issues

-- ===========================================
-- 1. CREATE MISSING TABLES
-- ===========================================

-- Create follow_up_templates table
CREATE TABLE IF NOT EXISTS follow_up_templates (
    id SERIAL PRIMARY KEY,
    service_type VARCHAR(100) NOT NULL,
    template_name VARCHAR(255) NOT NULL,
    email_subject VARCHAR(255),
    email_body TEXT,
    sms_body TEXT,
    whatsapp_body TEXT,
    variables JSONB DEFAULT '{}',
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create user_subscriptions table
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    plan_id INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===========================================
-- 2. ADD MISSING COLUMNS
-- ===========================================

-- Add price column to credit_packages
ALTER TABLE credit_packages ADD COLUMN IF NOT EXISTS price DECIMAL(10,2) DEFAULT 0.0;

-- Add package_name column to credit_packages
ALTER TABLE credit_packages ADD COLUMN IF NOT EXISTS package_name VARCHAR(255);

-- Add description column to credit_packages
ALTER TABLE credit_packages ADD COLUMN IF NOT EXISTS description TEXT;

-- Add user_id column to donations
ALTER TABLE donations ADD COLUMN IF NOT EXISTS user_id INTEGER;

-- Add donor_name column to donations
ALTER TABLE donations ADD COLUMN IF NOT EXISTS donor_name VARCHAR(255);

-- Add amount column to donations
ALTER TABLE donations ADD COLUMN IF NOT EXISTS amount DECIMAL(10,2) DEFAULT 0.0;

-- Add donation_date column to donations
ALTER TABLE donations ADD COLUMN IF NOT EXISTS donation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Add credits_required column to service_types
ALTER TABLE service_types ADD COLUMN IF NOT EXISTS credits_required INTEGER DEFAULT 5;

-- Add base_credits column to service_types
ALTER TABLE service_types ADD COLUMN IF NOT EXISTS base_credits INTEGER DEFAULT 10;

-- ===========================================
-- 3. INSERT DEFAULT DATA
-- ===========================================

-- Insert follow-up template if not exists
INSERT INTO follow_up_templates (service_type, template_name, email_subject, email_body)
SELECT 'birth_chart', 'Birth Chart Follow-up', 'Your Birth Chart Analysis', 'Thank you for your birth chart analysis...'
WHERE NOT EXISTS (SELECT 1 FROM follow_up_templates WHERE service_type = 'birth_chart');

-- Insert credit package if table is empty
INSERT INTO credit_packages (name, credits_amount, price_usd, bonus_credits, enabled, package_name, description, price)
SELECT 'Basic Package', 50, 9.99, 5, true, 'Basic Package', 'Perfect for beginners', 9.99
WHERE NOT EXISTS (SELECT 1 FROM credit_packages LIMIT 1);

-- ===========================================
-- 4. CREATE INDEXES
-- ===========================================

CREATE INDEX IF NOT EXISTS idx_followup_templates_service_type ON follow_up_templates(service_type);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user_id ON user_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_donations_user_id ON donations(user_id);

-- ===========================================
-- 5. VERIFICATION
-- ===========================================

-- Check if tables exist
SELECT 'follow_up_templates' as table_name, COUNT(*) as row_count FROM follow_up_templates
UNION ALL
SELECT 'user_subscriptions' as table_name, COUNT(*) as row_count FROM user_subscriptions
UNION ALL
SELECT 'credit_packages' as table_name, COUNT(*) as row_count FROM credit_packages
UNION ALL
SELECT 'donations' as table_name, COUNT(*) as row_count FROM donations; 