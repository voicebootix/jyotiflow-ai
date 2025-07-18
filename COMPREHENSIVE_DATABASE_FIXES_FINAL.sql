-- COMPREHENSIVE DATABASE FIXES FOR JYOTIFLOW.AI
-- This script fixes all database issues found in the logs

-- ===========================================
-- 1. CREATE MISSING TABLES
-- ===========================================

-- Create follow_up_templates table if it doesn't exist
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

-- Create user_subscriptions table if it doesn't exist
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    plan_id INTEGER NOT NULL, -- Changed from UUID to INTEGER
    status VARCHAR(50) DEFAULT 'active',
    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===========================================
-- 2. ADD MISSING COLUMNS
-- ===========================================

-- Add missing columns to credit_packages table
DO $$ 
BEGIN
    -- Add price column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='credit_packages' AND column_name='price') THEN
        ALTER TABLE credit_packages ADD COLUMN price DECIMAL(10,2) DEFAULT 0.0;
    END IF;
    
    -- Add package_name column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='credit_packages' AND column_name='package_name') THEN
        ALTER TABLE credit_packages ADD COLUMN package_name VARCHAR(255);
    END IF;
    
    -- Add description column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='credit_packages' AND column_name='description') THEN
        ALTER TABLE credit_packages ADD COLUMN description TEXT;
    END IF;
END $$;

-- Add missing columns to donations table
DO $$ 
BEGIN
    -- Add user_id column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='donations' AND column_name='user_id') THEN
        ALTER TABLE donations ADD COLUMN user_id INTEGER REFERENCES users(id);
    END IF;
    
    -- Add donor_name column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='donations' AND column_name='donor_name') THEN
        ALTER TABLE donations ADD COLUMN donor_name VARCHAR(255);
    END IF;
    
    -- Add amount column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='donations' AND column_name='amount') THEN
        ALTER TABLE donations ADD COLUMN amount DECIMAL(10,2) DEFAULT 0.0;
    END IF;
    
    -- Add donation_date column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='donations' AND column_name='donation_date') THEN
        ALTER TABLE donations ADD COLUMN donation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    END IF;
END $$;

-- Add missing columns to service_types table
DO $$ 
BEGIN
    -- Add credits_required column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='service_types' AND column_name='credits_required') THEN
        ALTER TABLE service_types ADD COLUMN credits_required INTEGER DEFAULT 5;
    END IF;
    
    -- Add base_credits column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='service_types' AND column_name='base_credits') THEN
        ALTER TABLE service_types ADD COLUMN base_credits INTEGER DEFAULT 10;
    END IF;
END $$;

-- ===========================================
-- 3. INSERT DEFAULT DATA
-- ===========================================

-- Insert default follow-up templates (without ON CONFLICT)
INSERT INTO follow_up_templates (service_type, template_name, email_subject, email_body, created_at, updated_at) 
SELECT 
    'birth_chart',
    'Birth Chart Follow-up',
    'Your Birth Chart Analysis - Next Steps',
    'Dear {user_name},

Thank you for your birth chart analysis with JyotiFlow AI. 

Here are some next steps to deepen your spiritual journey:

1. **Daily Wisdom**: Check our daily spiritual guidance
2. **Community**: Join our spiritual community discussions
3. **Personalized Sessions**: Book a personalized consultation

May your spiritual journey be blessed.

With divine blessings,
JyotiFlow AI Team',
    NOW(),
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM follow_up_templates 
    WHERE service_type = 'birth_chart' AND template_name = 'Birth Chart Follow-up'
);

-- Insert default credit packages if table is empty
INSERT INTO credit_packages (name, credits_amount, price_usd, bonus_credits, enabled, created_at, package_name, description, price) 
SELECT 
    'Basic Package',
    50,
    9.99,
    5,
    true,
    NOW(),
    'Basic Package',
    'Perfect for beginners starting their spiritual journey',
    9.99
WHERE NOT EXISTS (SELECT 1 FROM credit_packages LIMIT 1);

-- ===========================================
-- 4. FIX FOREIGN KEY CONSTRAINTS
-- ===========================================

-- Drop problematic foreign key constraints if they exist
DO $$ 
BEGIN
    -- Drop user_subscriptions_plan_id_fkey if it exists
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'user_subscriptions_plan_id_fkey') THEN
        ALTER TABLE user_subscriptions DROP CONSTRAINT user_subscriptions_plan_id_fkey;
    END IF;
END $$;

-- ===========================================
-- 5. CREATE INDEXES FOR PERFORMANCE
-- ===========================================

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_followup_templates_service_type ON follow_up_templates(service_type);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user_id ON user_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_donations_user_id ON donations(user_id);
CREATE INDEX IF NOT EXISTS idx_donations_donation_date ON donations(donation_date);

-- ===========================================
-- 6. VERIFICATION QUERIES
-- ===========================================

-- Verify tables exist
SELECT 'follow_up_templates' as table_name, COUNT(*) as row_count FROM follow_up_templates
UNION ALL
SELECT 'user_subscriptions' as table_name, COUNT(*) as row_count FROM user_subscriptions
UNION ALL
SELECT 'credit_packages' as table_name, COUNT(*) as row_count FROM credit_packages
UNION ALL
SELECT 'donations' as table_name, COUNT(*) as row_count FROM donations;

-- Verify columns exist
SELECT 
    table_name, 
    column_name, 
    data_type 
FROM information_schema.columns 
WHERE table_name IN ('credit_packages', 'donations', 'service_types')
AND column_name IN ('price', 'package_name', 'user_id', 'donor_name', 'amount', 'credits_required', 'base_credits')
ORDER BY table_name, column_name; 