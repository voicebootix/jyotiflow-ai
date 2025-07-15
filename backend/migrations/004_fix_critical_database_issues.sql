-- =================================================================
-- CRITICAL DATABASE ISSUES FIX MIGRATION
-- =================================================================
-- This migration fixes the critical database issues causing runtime errors:
-- 1. Missing follow_up_templates table
-- 2. Missing birth_chart_cached_at column in users table
-- 3. Missing recommendation_data column in sessions table
-- 4. Foreign key constraint issues
-- =================================================================

-- 1. CREATE FOLLOW_UP_TEMPLATES TABLE
-- =================================================================

DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'follow_up_templates') THEN
        RAISE NOTICE '📋 Creating follow_up_templates table...';
        
        CREATE TABLE follow_up_templates (
            id SERIAL PRIMARY KEY,
            template_name VARCHAR(255) NOT NULL,
            template_type VARCHAR(100) NOT NULL,
            subject VARCHAR(255),
            content TEXT NOT NULL,
            variables JSONB DEFAULT '[]'::jsonb,
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        
        -- Insert default templates
        INSERT INTO follow_up_templates (template_name, template_type, subject, content, variables) VALUES
        ('birth_chart_followup', 'email', 'Your Birth Chart Analysis is Ready', 
         'Dear {{user_name}},\n\nThank you for your birth chart session on {{session_date}}. Here are some key insights from your {{service_type}} reading:\n\n{{key_insights}}\n\nWe hope this guidance helps you on your spiritual journey.\n\nBlessings,\nThe JyotiFlow Team', 
         '["user_name", "session_date", "service_type", "key_insights"]'),
        ('general_followup', 'email', 'Thank You for Your Spiritual Session', 
         'Dear {{user_name}},\n\nWe hope your {{service_type}} session on {{session_date}} provided valuable insights.\n\nRemember to practice the guidance shared and stay connected to your spiritual path.\n\nWith gratitude,\nThe JyotiFlow Team', 
         '["user_name", "session_date", "service_type"]'),
        ('career_followup', 'email', 'Your Career Guidance Summary', 
         'Dear {{user_name}},\n\nHere''s a summary of your career consultation on {{session_date}}:\n\n{{career_insights}}\n\nKeep working towards your goals with faith and determination.\n\nBest regards,\nThe JyotiFlow Team', 
         '["user_name", "session_date", "career_insights"]');
        
        RAISE NOTICE '✅ Created follow_up_templates table with default templates';
    ELSE
        RAISE NOTICE '✅ follow_up_templates table already exists';
    END IF;
END $$;

-- 2. ADD MISSING COLUMNS TO USERS TABLE
-- =================================================================

DO $$ 
BEGIN
    -- Add birth_chart_cached_at column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'birth_chart_cached_at'
    ) THEN
        ALTER TABLE users ADD COLUMN birth_chart_cached_at TIMESTAMP;
        RAISE NOTICE '✅ Added birth_chart_cached_at column to users table';
    ELSE
        RAISE NOTICE '✅ birth_chart_cached_at column already exists in users table';
    END IF;
    
    -- Add birth_chart_cache_status column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'birth_chart_cache_status'
    ) THEN
        ALTER TABLE users ADD COLUMN birth_chart_cache_status VARCHAR(50) DEFAULT 'not_cached';
        RAISE NOTICE '✅ Added birth_chart_cache_status column to users table';
    ELSE
        RAISE NOTICE '✅ birth_chart_cache_status column already exists in users table';
    END IF;
END $$;

-- 3. ADD MISSING COLUMNS TO SESSIONS TABLE
-- =================================================================

DO $$ 
BEGIN
    -- Add recommendation_data column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'sessions' AND column_name = 'recommendation_data'
    ) THEN
        ALTER TABLE sessions ADD COLUMN recommendation_data JSONB DEFAULT '{}'::jsonb;
        RAISE NOTICE '✅ Added recommendation_data column to sessions table';
    ELSE
        RAISE NOTICE '✅ recommendation_data column already exists in sessions table';
    END IF;
    
    -- Add question column if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'sessions' AND column_name = 'question'
    ) THEN
        ALTER TABLE sessions ADD COLUMN question TEXT;
        RAISE NOTICE '✅ Added question column to sessions table';
    ELSE
        RAISE NOTICE '✅ question column already exists in sessions table';
    END IF;
    
    -- Add user_email column if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'sessions' AND column_name = 'user_email'
    ) THEN
        ALTER TABLE sessions ADD COLUMN user_email VARCHAR(255);
        RAISE NOTICE '✅ Added user_email column to sessions table';
    ELSE
        RAISE NOTICE '✅ user_email column already exists in sessions table';
    END IF;
END $$;

-- 4. FIX FOREIGN KEY CONSTRAINT ISSUES
-- =================================================================

DO $$ 
BEGIN
    -- Fix user_subscriptions table plan_id foreign key constraint
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'user_subscriptions') THEN
        -- Check if plan_id column exists and is the wrong type
        IF EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'user_subscriptions' 
            AND column_name = 'plan_id' 
            AND data_type = 'uuid'
        ) THEN
            -- Drop the foreign key constraint if it exists
            IF EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE table_name = 'user_subscriptions' 
                AND constraint_name = 'user_subscriptions_plan_id_fkey'
            ) THEN
                ALTER TABLE user_subscriptions DROP CONSTRAINT user_subscriptions_plan_id_fkey;
                RAISE NOTICE '✅ Dropped problematic user_subscriptions_plan_id_fkey constraint';
            END IF;
            
            -- Change plan_id column type to INTEGER
            ALTER TABLE user_subscriptions ALTER COLUMN plan_id TYPE INTEGER USING plan_id::text::integer;
            RAISE NOTICE '✅ Changed user_subscriptions.plan_id from UUID to INTEGER';
            
            -- Re-add the foreign key constraint
            ALTER TABLE user_subscriptions 
            ADD CONSTRAINT user_subscriptions_plan_id_fkey 
            FOREIGN KEY (plan_id) REFERENCES subscription_plans(id);
            RAISE NOTICE '✅ Re-added user_subscriptions_plan_id_fkey constraint with correct types';
        END IF;
    END IF;
END $$;

-- 5. CREATE MISSING TABLES
-- =================================================================

-- Create subscription_plans table if missing
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'subscription_plans') THEN
        RAISE NOTICE '📋 Creating subscription_plans table...';
        
        CREATE TABLE subscription_plans (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            price_usd DECIMAL(10,2) NOT NULL,
            credits_per_month INTEGER DEFAULT 0,
            features JSONB DEFAULT '[]'::jsonb,
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        
        -- Insert default plans
        INSERT INTO subscription_plans (name, description, price_usd, credits_per_month, features) VALUES
        ('Basic', 'Basic spiritual guidance access', 9.99, 10, '["basic_guidance", "email_support"]'),
        ('Premium', 'Premium spiritual services with priority support', 19.99, 25, '["all_services", "priority_support", "birth_chart_analysis"]'),
        ('Master', 'Complete spiritual journey package', 39.99, 50, '["all_services", "priority_support", "personal_consultation", "advanced_analytics"]');
        
        RAISE NOTICE '✅ Created subscription_plans table with default plans';
    ELSE
        RAISE NOTICE '✅ subscription_plans table already exists';
    END IF;
END $$;

-- Create user_subscriptions table if missing
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'user_subscriptions') THEN
        RAISE NOTICE '📋 Creating user_subscriptions table...';
        
        CREATE TABLE user_subscriptions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            plan_id INTEGER NOT NULL REFERENCES subscription_plans(id),
            status VARCHAR(50) DEFAULT 'active',
            start_date TIMESTAMP DEFAULT NOW(),
            end_date TIMESTAMP,
            auto_renew BOOLEAN DEFAULT true,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        
        RAISE NOTICE '✅ Created user_subscriptions table';
    ELSE
        RAISE NOTICE '✅ user_subscriptions table already exists';
    END IF;
END $$;

-- 6. CREATE INDEXES FOR PERFORMANCE
-- =================================================================

CREATE INDEX IF NOT EXISTS idx_follow_up_templates_type ON follow_up_templates(template_type);
CREATE INDEX IF NOT EXISTS idx_follow_up_templates_active ON follow_up_templates(is_active);
CREATE INDEX IF NOT EXISTS idx_users_birth_chart_cache ON users(birth_chart_cached_at);
CREATE INDEX IF NOT EXISTS idx_sessions_recommendation_data ON sessions USING GIN(recommendation_data);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user_id ON user_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_status ON user_subscriptions(status);

-- 7. VERIFICATION
-- =================================================================

DO $$ 
BEGIN
    RAISE NOTICE '🔍 VERIFICATION RESULTS:';
    
    -- Check follow_up_templates table
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'follow_up_templates') THEN
        RAISE NOTICE '✅ follow_up_templates table exists';
    ELSE
        RAISE NOTICE '❌ follow_up_templates table missing';
    END IF;
    
    -- Check users table columns
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'birth_chart_cached_at') THEN
        RAISE NOTICE '✅ birth_chart_cached_at column exists in users';
    ELSE
        RAISE NOTICE '❌ birth_chart_cached_at column missing from users';
    END IF;
    
    -- Check sessions table columns
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'sessions' AND column_name = 'recommendation_data') THEN
        RAISE NOTICE '✅ recommendation_data column exists in sessions';
    ELSE
        RAISE NOTICE '❌ recommendation_data column missing from sessions';
    END IF;
    
    -- Check subscription tables
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'subscription_plans') THEN
        RAISE NOTICE '✅ subscription_plans table exists';
    ELSE
        RAISE NOTICE '❌ subscription_plans table missing';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'user_subscriptions') THEN
        RAISE NOTICE '✅ user_subscriptions table exists';
    ELSE
        RAISE NOTICE '❌ user_subscriptions table missing';
    END IF;
    
END $$;

-- =================================================================
-- COMPLETED: Critical database issues fix migration
-- ================================================================= 