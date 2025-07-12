-- JyotiFlow.ai Quick Critical Fix
-- This script fixes only the most critical database issues to get the platform running

-- Fix display_name constraint issue
ALTER TABLE service_types ALTER COLUMN display_name DROP NOT NULL;

-- Create the critical missing table: service_configuration_cache
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

-- Insert essential service configurations
INSERT INTO service_configuration_cache (service_name, configuration) VALUES
    ('tarot_ai', '{"enabled": true, "model": "gpt-4", "temperature": 0.7, "max_tokens": 1000}'),
    ('spiritual_guidance', '{"enabled": true, "model": "gpt-4", "temperature": 0.8, "max_tokens": 1500}'),
    ('birth_chart_analysis', '{"enabled": true, "calculation_method": "tropical", "house_system": "placidus"}'),
    ('spiritual_consultation', '{"enabled": true, "model": "gpt-4", "temperature": 0.7}'),
    ('astrology_reading', '{"enabled": true, "model": "gpt-4", "temperature": 0.8}'),
    ('numerology_analysis', '{"enabled": true, "calculation_method": "pythagorean"}'),
    ('love_compatibility', '{"enabled": true, "compatibility_method": "synastry"}')
ON CONFLICT (service_name, config_key) DO UPDATE SET configuration = EXCLUDED.configuration;

-- Create credit_transactions table (needed for credit purchases)
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

-- Fix users table column naming if needed
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

-- Add missing columns to service_types if they don't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='service_types' AND column_name='is_premium') THEN
        ALTER TABLE service_types ADD COLUMN is_premium BOOLEAN DEFAULT false;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='service_types' AND column_name='enabled') THEN
        ALTER TABLE service_types ADD COLUMN enabled BOOLEAN DEFAULT true;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='service_types' AND column_name='price_usd') THEN
        ALTER TABLE service_types ADD COLUMN price_usd DECIMAL(10,2) DEFAULT 0;
    END IF;
END $$;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_service_config_cache_name ON service_configuration_cache(service_name);
CREATE INDEX IF NOT EXISTS idx_credit_trans_user ON credit_transactions(user_email);

-- Grant permissions (if user exists)
DO $$
BEGIN
    GRANT ALL ON service_configuration_cache TO jyotiflow_db_user;
    GRANT ALL ON credit_transactions TO jyotiflow_db_user;
    GRANT USAGE ON SEQUENCE service_configuration_cache_id_seq TO jyotiflow_db_user;
    GRANT USAGE ON SEQUENCE credit_transactions_id_seq TO jyotiflow_db_user;
EXCEPTION
    WHEN undefined_object THEN
        NULL;
END $$;

-- Quick verification
DO $$
DECLARE
    config_exists BOOLEAN;
    credit_exists BOOLEAN;
BEGIN
    SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'service_configuration_cache') INTO config_exists;
    SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'credit_transactions') INTO credit_exists;
    
    RAISE NOTICE 'Quick Fix Status:';
    RAISE NOTICE '  - service_configuration_cache: %', CASE WHEN config_exists THEN 'Created ✓' ELSE 'Failed ✗' END;
    RAISE NOTICE '  - credit_transactions: %', CASE WHEN credit_exists THEN 'Created ✓' ELSE 'Failed ✗' END;
END $$;