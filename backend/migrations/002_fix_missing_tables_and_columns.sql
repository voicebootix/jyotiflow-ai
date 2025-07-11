-- Migration: Fix missing tables and column issues
-- This migration adds missing tables and fixes column naming issues

-- 1. Create credit_packages table (missing from comprehensive reset)
CREATE TABLE IF NOT EXISTS credit_packages (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    credits_amount INTEGER NOT NULL,
    price_usd DECIMAL(10,2) NOT NULL,
    bonus_credits INTEGER DEFAULT 0,
    description TEXT,
    enabled BOOLEAN DEFAULT TRUE,
    stripe_product_id VARCHAR(255),
    stripe_price_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Fix users table column naming (last_login -> last_login_at)
DO $$
BEGIN
    -- Check if last_login exists and last_login_at doesn't
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='users' AND column_name='last_login'
    ) AND NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='users' AND column_name='last_login_at'
    ) THEN
        ALTER TABLE users RENAME COLUMN last_login TO last_login_at;
    END IF;
    
    -- If neither exists, add last_login_at
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='users' AND column_name='last_login_at'
    ) THEN
        ALTER TABLE users ADD COLUMN last_login_at TIMESTAMP;
    END IF;
END $$;

-- 3. Add missing columns to service_types
DO $$
BEGIN
    -- Add enabled column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='service_types' AND column_name='enabled'
    ) THEN
        ALTER TABLE service_types ADD COLUMN enabled BOOLEAN DEFAULT true;
    END IF;
    
    -- Add price_usd column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='service_types' AND column_name='price_usd'
    ) THEN
        ALTER TABLE service_types ADD COLUMN price_usd DECIMAL(10,2) DEFAULT 0;
    END IF;
    
    -- Add service_category column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='service_types' AND column_name='service_category'
    ) THEN
        ALTER TABLE service_types ADD COLUMN service_category VARCHAR(100);
    END IF;
    
    -- Add avatar_video_enabled column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='service_types' AND column_name='avatar_video_enabled'
    ) THEN
        ALTER TABLE service_types ADD COLUMN avatar_video_enabled BOOLEAN DEFAULT false;
    END IF;
    
    -- Add live_chat_enabled column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='service_types' AND column_name='live_chat_enabled'
    ) THEN
        ALTER TABLE service_types ADD COLUMN live_chat_enabled BOOLEAN DEFAULT false;
    END IF;
END $$;

-- 4. Create payments table if missing
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(50) DEFAULT 'pending',
    payment_method VARCHAR(50),
    transaction_id VARCHAR(255),
    product_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Create ai_recommendations table if missing
CREATE TABLE IF NOT EXISTS ai_recommendations (
    id SERIAL PRIMARY KEY,
    recommendation_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    expected_revenue_impact DECIMAL(10,2),
    implementation_difficulty VARCHAR(20),
    timeline_weeks INTEGER,
    priority_score DECIMAL(3,2),
    priority_level VARCHAR(20),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Create monetization_experiments table if missing
CREATE TABLE IF NOT EXISTS monetization_experiments (
    id SERIAL PRIMARY KEY,
    experiment_name VARCHAR(255) NOT NULL,
    experiment_type VARCHAR(50) NOT NULL,
    control_conversion_rate DECIMAL(5,2),
    test_conversion_rate DECIMAL(5,2),
    control_revenue DECIMAL(10,2),
    test_revenue DECIMAL(10,2),
    status VARCHAR(50) DEFAULT 'running',
    winner VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Create ai_insights_cache table if missing
CREATE TABLE IF NOT EXISTS ai_insights_cache (
    id SERIAL PRIMARY KEY,
    insight_type VARCHAR(50) NOT NULL,
    data JSONB NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. Fix pricing_config table column naming
DO $$
BEGIN
    -- Add standard columns if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='pricing_config' AND column_name='key'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='pricing_config' AND column_name='config_key'
    ) THEN
        -- Create a duplicate column for compatibility
        ALTER TABLE pricing_config ADD COLUMN key VARCHAR(100);
        UPDATE pricing_config SET key = config_key;
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='pricing_config' AND column_name='value'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='pricing_config' AND column_name='config_value'
    ) THEN
        -- Create a duplicate column for compatibility
        ALTER TABLE pricing_config ADD COLUMN value VARCHAR(500);
        UPDATE pricing_config SET value = config_value;
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='pricing_config' AND column_name='type'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='pricing_config' AND column_name='config_type'
    ) THEN
        -- Create a duplicate column for compatibility
        ALTER TABLE pricing_config ADD COLUMN type VARCHAR(50);
        UPDATE pricing_config SET type = config_type;
    END IF;
END $$;

-- 9. Insert default credit packages if table is empty
INSERT INTO credit_packages (name, credits_amount, price_usd, bonus_credits, description, enabled)
SELECT * FROM (VALUES
    ('Starter Pack', 10, 9.99, 2, 'Perfect for beginners - try our spiritual guidance services', true),
    ('Spiritual Seeker', 25, 19.99, 5, 'Great value for regular users - most popular choice', true),
    ('Divine Wisdom', 50, 34.99, 15, 'Best value with maximum bonus credits for serious seekers', true),
    ('Enlightened Master', 100, 59.99, 30, 'Ultimate spiritual journey package for dedicated practitioners', true)
) AS v(name, credits_amount, price_usd, bonus_credits, description, enabled)
WHERE NOT EXISTS (SELECT 1 FROM credit_packages);

-- 10. Add missing columns to sessions table if needed
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='sessions' AND column_name='user_id'
    ) THEN
        ALTER TABLE sessions ADD COLUMN user_id INTEGER;
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='sessions' AND column_name='user_rating'
    ) THEN
        ALTER TABLE sessions ADD COLUMN user_rating INTEGER;
    END IF;
END $$;

-- 11. Add missing indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_sessions_user_email ON sessions(user_email);
CREATE INDEX IF NOT EXISTS idx_sessions_service_type ON sessions(service_type);
CREATE INDEX IF NOT EXISTS idx_payments_user_email ON payments(user_email);
CREATE INDEX IF NOT EXISTS idx_credit_packages_enabled ON credit_packages(enabled);