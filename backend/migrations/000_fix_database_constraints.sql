-- 🔧 Database Constraint Fixes - Run BEFORE other migrations
-- This migration fixes all constraint and schema issues preventing other migrations from running
-- Priority: 000 (runs first)

-- ========================================
-- 1. FIX SESSIONS TABLE CONSTRAINTS
-- ========================================

-- Ensure sessions table exists with proper structure
CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    user_email VARCHAR(255),
    user_id TEXT,
    service_type TEXT NOT NULL,
    duration_minutes INTEGER DEFAULT 0,
    credits_used INTEGER DEFAULT 0,
    session_data TEXT,
    question TEXT,
    birth_details JSONB,
    status VARCHAR(50) DEFAULT 'active',
    result_summary TEXT,
    full_result TEXT,
    guidance TEXT,
    avatar_video_url VARCHAR(500),
    avatar_duration_seconds INTEGER,
    avatar_generation_cost DECIMAL(10,2),
    voice_synthesis_used BOOLEAN DEFAULT false,
    avatar_quality VARCHAR(20) DEFAULT 'high',
    original_price DECIMAL(10,2),
    user_rating INTEGER CHECK (user_rating >= 1 AND user_rating <= 5),
    user_feedback TEXT,
    session_quality_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Add unique constraint on id for foreign key references
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'sessions_id_unique'
    ) THEN
        ALTER TABLE public.sessions ADD CONSTRAINT sessions_id_unique UNIQUE (id);
    END IF;
END $$;

-- Add unique constraint on session_id
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'sessions_session_id_unique'
    ) THEN
        ALTER TABLE public.sessions ADD CONSTRAINT sessions_session_id_unique UNIQUE (session_id);
    END IF;
END $$;

-- ========================================
-- 2. FIX SERVICE_TYPES TABLE
-- ========================================

-- Ensure service_types table exists with proper structure and ID generation
CREATE TABLE IF NOT EXISTS public.service_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    base_credits INTEGER NOT NULL DEFAULT 10,
    duration_minutes INTEGER DEFAULT 15,
    video_enabled BOOLEAN DEFAULT true,
    knowledge_configuration JSONB DEFAULT '{}',
    specialized_prompts JSONB DEFAULT '{}',
    response_behavior JSONB DEFAULT '{}',
    swami_persona_mode VARCHAR(100) DEFAULT 'general',
    analysis_depth VARCHAR(50) DEFAULT 'standard',
    icon VARCHAR(50) DEFAULT '🔮',
    gradient_class VARCHAR(100) DEFAULT 'from-purple-500 to-indigo-600',
    is_premium BOOLEAN DEFAULT false,
    requires_birth_details BOOLEAN DEFAULT false,
    supports_followup BOOLEAN DEFAULT true,
    max_followup_questions INTEGER DEFAULT 3,
    ai_model VARCHAR(50) DEFAULT 'gpt-4',
    voice_enabled BOOLEAN DEFAULT true,
    avatar_enabled BOOLEAN DEFAULT true,
    category VARCHAR(50) DEFAULT 'guidance',
    metadata JSONB DEFAULT '{}',
    pricing_config JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add unique constraint on name for ON CONFLICT clauses
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'service_types_name_unique'
    ) THEN
        ALTER TABLE public.service_types ADD CONSTRAINT service_types_name_unique UNIQUE (name);
    END IF;
END $$;

-- Ensure ID sequence exists and is properly set (PostgreSQL handles SERIAL automatically)
DO $$ 
BEGIN
    -- PostgreSQL automatically creates sequences for SERIAL columns
    -- Only manually set if sequence doesn't exist or isn't properly linked
    IF NOT EXISTS (
        SELECT 1 FROM pg_depend d 
        JOIN pg_class c ON d.objid = c.oid 
        JOIN pg_attribute a ON d.refobjid = a.attrelid AND d.refobjsubid = a.attnum
        WHERE c.relname = 'service_types_id_seq' 
        AND a.attname = 'id' 
        AND a.attrelid = 'public.service_types'::regclass
    ) THEN
        -- Only create sequence if it doesn't exist and isn't linked
        IF NOT EXISTS (SELECT 1 FROM pg_sequences WHERE sequencename = 'service_types_id_seq') THEN
            CREATE SEQUENCE public.service_types_id_seq;
        END IF;
        ALTER TABLE public.service_types ALTER COLUMN id SET DEFAULT nextval('public.service_types_id_seq');
        ALTER SEQUENCE public.service_types_id_seq OWNED BY public.service_types.id;
    END IF;
END $$;

-- ========================================
-- 3. FIX USERS TABLE FOR FOREIGN KEYS
-- ========================================

-- Ensure users table exists for foreign key references
CREATE TABLE IF NOT EXISTS public.users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    credits INTEGER DEFAULT 0,
    base_credits INTEGER DEFAULT 0,
    phone VARCHAR(20),
    birth_date DATE,
    birth_time TIME,
    birth_location VARCHAR(255),
    spiritual_level VARCHAR(50) DEFAULT 'beginner',
    preferred_language VARCHAR(10) DEFAULT 'en',
    avatar_sessions_count INTEGER DEFAULT 0,
    total_avatar_minutes INTEGER DEFAULT 0,
    preferred_avatar_style VARCHAR(50) DEFAULT 'traditional',
    voice_preference VARCHAR(50) DEFAULT 'compassionate',
    video_quality_preference VARCHAR(20) DEFAULT 'high',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP
);

-- Add unique constraint on email for foreign key references
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'users_email_unique'
    ) THEN
        ALTER TABLE public.users ADD CONSTRAINT users_email_unique UNIQUE (email);
    END IF;
END $$;

-- ========================================
-- 4. FIX SERVICE CONFIGURATION TABLES
-- ========================================

-- Service configurations table with proper constraints
CREATE TABLE IF NOT EXISTS public.service_configurations (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(100) UNIQUE NOT NULL,
    base_credits INTEGER NOT NULL DEFAULT 10,
    duration_minutes INTEGER DEFAULT 15,
    video_enabled BOOLEAN DEFAULT true,
    premium_features JSONB DEFAULT '{}',
    ai_model VARCHAR(50) DEFAULT 'gpt-4',
    voice_enabled BOOLEAN DEFAULT true,
    avatar_enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add unique constraint for ON CONFLICT
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'service_configurations_service_name_unique'
    ) THEN
        ALTER TABLE public.service_configurations ADD CONSTRAINT service_configurations_service_name_unique UNIQUE (service_name);
    END IF;
END $$;

-- ========================================
-- 5. ADD MISSING COLUMNS
-- ========================================

-- Add service_type column to tables that need it (with proper table existence checks)
DO $$ 
BEGIN
    -- Add service_type to service_usage_logs if table exists
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'service_usage_logs') THEN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'service_usage_logs' AND column_name = 'service_type'
        ) THEN
            ALTER TABLE public.service_usage_logs ADD COLUMN service_type VARCHAR(100);
        END IF;
    END IF;
    
    -- Add service_type to ai_pricing_recommendations if table exists
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'ai_pricing_recommendations') THEN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'ai_pricing_recommendations' AND column_name = 'service_type'
        ) THEN
            ALTER TABLE public.ai_pricing_recommendations ADD COLUMN service_type VARCHAR(100);
        END IF;
    END IF;
    
    -- Add base_credits column to users if missing
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') THEN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'base_credits'
        ) THEN
            ALTER TABLE public.users ADD COLUMN base_credits INTEGER DEFAULT 0;
        END IF;
    END IF;
    
    -- Add unique constraints only if tables exist
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'api_usage_metrics') THEN
        IF NOT EXISTS (
            SELECT 1 FROM pg_constraint 
            WHERE conname = 'api_usage_metrics_unique_daily'
        ) THEN
            ALTER TABLE public.api_usage_metrics ADD CONSTRAINT api_usage_metrics_unique_daily UNIQUE (api_name, endpoint, date);
        END IF;
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'satsang_attendees') THEN
        IF NOT EXISTS (
            SELECT 1 FROM pg_constraint 
            WHERE conname = 'satsang_attendees_unique_attendance'
        ) THEN
            ALTER TABLE public.satsang_attendees ADD CONSTRAINT satsang_attendees_unique_attendance UNIQUE (satsang_event_id, user_id);
        END IF;
    END IF;
    
EXCEPTION 
    WHEN undefined_table THEN
        -- Table doesn't exist, skip gracefully
        RAISE NOTICE 'Skipping constraint addition for non-existent table';
    WHEN undefined_column THEN
        -- Column doesn't exist, skip gracefully  
        RAISE NOTICE 'Skipping constraint addition for non-existent column';
    WHEN duplicate_object THEN
        -- Constraint already exists, skip gracefully
        RAISE NOTICE 'Constraint already exists, skipping';
    WHEN unique_violation THEN
        -- Unique constraint violation, skip gracefully
        RAISE NOTICE 'Unique constraint violation, skipping';
END $$;

-- ========================================
-- 6. CREATE PLATFORM SETTINGS TABLE
-- ========================================

-- Platform settings table for social media integrations
CREATE TABLE IF NOT EXISTS platform_settings (
    id SERIAL PRIMARY KEY,
    platform_name VARCHAR(100) NOT NULL,
    api_key TEXT,
    api_secret TEXT,
    access_token TEXT,
    refresh_token TEXT,
    channel_id VARCHAR(255),
    page_id VARCHAR(255),
    account_id VARCHAR(255),
    additional_config JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT false,
    last_sync_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(platform_name)
);

-- ========================================
-- 7. INSERT INITIAL SERVICE TYPES DATA
-- ========================================

-- Insert basic service types with proper ID generation
INSERT INTO public.service_types (
    name, description, base_credits, duration_minutes, video_enabled, 
    icon, gradient_class, is_premium, category
) VALUES 
    ('clarity', 'Basic spiritual clarity session', 15, 15, true, '🔮', 'from-purple-500 to-indigo-600', false, 'guidance'),
    ('love', 'Love and relationship guidance', 20, 20, true, '💕', 'from-pink-500 to-rose-600', false, 'guidance'),
    ('premium', 'Premium spiritual consultation', 50, 45, true, '⭐', 'from-gold-500 to-yellow-600', true, 'guidance')
ON CONFLICT (name) DO UPDATE SET
    description = EXCLUDED.description,
    base_credits = EXCLUDED.base_credits,
    duration_minutes = EXCLUDED.duration_minutes,
    updated_at = CURRENT_TIMESTAMP;

-- ========================================
-- 8. CREATE INDEXES FOR PERFORMANCE
-- ========================================

-- Create indexes that were failing due to missing columns
CREATE INDEX IF NOT EXISTS idx_sessions_service_type ON sessions(service_type);
CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_sessions_user_email ON sessions(user_email);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_service_types_name ON service_types(name);
CREATE INDEX IF NOT EXISTS idx_platform_settings_platform ON platform_settings(platform_name);

-- ========================================
-- 9. CREATE UPDATE TRIGGERS
-- ========================================

-- Function for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at timestamps
DROP TRIGGER IF EXISTS update_sessions_timestamp ON sessions;
CREATE TRIGGER update_sessions_timestamp 
    BEFORE UPDATE ON sessions 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_service_types_timestamp ON service_types;
CREATE TRIGGER update_service_types_timestamp 
    BEFORE UPDATE ON service_types 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_users_timestamp ON users;
CREATE TRIGGER update_users_timestamp 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_platform_settings_timestamp ON platform_settings;
CREATE TRIGGER update_platform_settings_timestamp 
    BEFORE UPDATE ON platform_settings 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- CONSTRAINT FIXES COMPLETED
-- ========================================

-- This migration should resolve:
-- 1. ❌ Migration failed: add_missing_pricing_tables.sql - there is no unique constraint matching given keys for referenced table "sessions"
-- 2. ❌ Constraint fix error: there is no unique constraint matching given keys for referenced table "sessions"  
-- 3. ❌ Could not insert service clarity: there is no unique or exclusion constraint matching the ON CONFLICT specification
-- 4. ❌ Error inserting initial data: null value in column "id" of relation "service_types" violates not-null constraint
-- 5. ❌ Could not create index: column "service_type" does not exist

