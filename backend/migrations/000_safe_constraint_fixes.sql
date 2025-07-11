-- Safe Constraint Fixes Migration
-- Only adds missing constraints and columns without breaking existing functionality
-- Compatible with existing init_database.py schema

-- ========================================
-- 1. ADD MISSING COLUMNS SAFELY
-- ========================================

-- Add service_type column to service_usage_logs if table exists and column doesn't exist
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'service_usage_logs') THEN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'service_usage_logs' AND column_name = 'service_type'
        ) THEN
            ALTER TABLE service_usage_logs ADD COLUMN service_type VARCHAR(100);
            RAISE NOTICE 'Added service_type column to service_usage_logs';
        END IF;
    END IF;
END $$;

-- Add service_type column to ai_pricing_recommendations if table exists and column doesn't exist
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'ai_pricing_recommendations') THEN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'ai_pricing_recommendations' AND column_name = 'service_type'
        ) THEN
            ALTER TABLE ai_pricing_recommendations ADD COLUMN service_type VARCHAR(100);
            RAISE NOTICE 'Added service_type column to ai_pricing_recommendations';
        END IF;
    END IF;
END $$;

-- ========================================
-- 2. CREATE MISSING TABLES SAFELY
-- ========================================

-- Create api_usage_metrics table if it doesn't exist
CREATE TABLE IF NOT EXISTS api_usage_metrics (
    id SERIAL PRIMARY KEY,
    api_name VARCHAR(100) NOT NULL,
    endpoint VARCHAR(255),
    calls_count INTEGER DEFAULT 0,
    total_cost_usd DECIMAL(10,2) DEFAULT 0,
    date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create service_usage_logs table if it doesn't exist (compatible with existing schema)
CREATE TABLE IF NOT EXISTS service_usage_logs (
    id SERIAL PRIMARY KEY,
    service_type VARCHAR(100),
    api_name VARCHAR(100) NOT NULL,
    usage_type VARCHAR(50) NOT NULL,
    usage_amount DECIMAL(10,2) NOT NULL,
    cost_usd DECIMAL(10,2) NOT NULL,
    cost_credits DECIMAL(10,2) NOT NULL,
    session_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- 3. ADD SAFE UNIQUE CONSTRAINTS
-- ========================================

-- Add unique constraint to api_usage_metrics for daily tracking (only if not exists)
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'api_usage_metrics') THEN
        IF NOT EXISTS (
            SELECT 1 FROM pg_constraint 
            WHERE conname = 'api_usage_metrics_daily_unique'
        ) THEN
            ALTER TABLE api_usage_metrics 
            ADD CONSTRAINT api_usage_metrics_daily_unique 
            UNIQUE (api_name, endpoint, date);
            RAISE NOTICE 'Added unique constraint to api_usage_metrics';
        END IF;
    END IF;
EXCEPTION 
    WHEN duplicate_object THEN
        RAISE NOTICE 'Unique constraint already exists on api_usage_metrics';
    WHEN others THEN
        RAISE NOTICE 'Could not add unique constraint to api_usage_metrics: %', SQLERRM;
END $$;

-- ========================================
-- 4. ADD MISSING INDEXES FOR PERFORMANCE
-- ========================================

-- Add index on sessions.service_type if table exists
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'sessions') THEN
        IF NOT EXISTS (
            SELECT 1 FROM pg_indexes 
            WHERE tablename = 'sessions' AND indexname = 'idx_sessions_service_type'
        ) THEN
            CREATE INDEX idx_sessions_service_type ON sessions(service_type);
            RAISE NOTICE 'Added index on sessions.service_type';
        END IF;
    END IF;
EXCEPTION 
    WHEN others THEN
        RAISE NOTICE 'Could not add index to sessions: %', SQLERRM;
END $$;

-- Add index on service_usage_logs.service_type if table and column exist
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'service_usage_logs') 
       AND EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'service_usage_logs' AND column_name = 'service_type') THEN
        IF NOT EXISTS (
            SELECT 1 FROM pg_indexes 
            WHERE tablename = 'service_usage_logs' AND indexname = 'idx_service_usage_logs_service_type'
        ) THEN
            CREATE INDEX idx_service_usage_logs_service_type ON service_usage_logs(service_type);
            RAISE NOTICE 'Added index on service_usage_logs.service_type';
        END IF;
    END IF;
EXCEPTION 
    WHEN others THEN
        RAISE NOTICE 'Could not add index to service_usage_logs: %', SQLERRM;
END $$;

-- ========================================
-- 5. ENSURE PLATFORM SETTINGS COMPATIBILITY
-- ========================================

-- Ensure platform_settings table has all required columns
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'platform_settings') THEN
        -- Add created_at if missing
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'platform_settings' AND column_name = 'created_at'
        ) THEN
            ALTER TABLE platform_settings ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
            RAISE NOTICE 'Added created_at to platform_settings';
        END IF;
        
        -- Add updated_at if missing
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'platform_settings' AND column_name = 'updated_at'
        ) THEN
            ALTER TABLE platform_settings ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
            RAISE NOTICE 'Added updated_at to platform_settings';
        END IF;
    END IF;
EXCEPTION 
    WHEN others THEN
        RAISE NOTICE 'Could not update platform_settings: %', SQLERRM;
END $$;

-- ========================================
-- MIGRATION COMPLETE
-- ========================================

-- Log successful completion
DO $$ 
BEGIN
    RAISE NOTICE '✅ Safe constraint fixes migration completed successfully';
    RAISE NOTICE '📋 This migration only adds missing elements without breaking existing functionality';
END $$;

