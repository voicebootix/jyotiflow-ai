-- Migration: 001_align_service_types_schema.sql
-- Fix service_types table schema alignment
-- This fixes the is_premium column issue and other missing columns

-- Add missing columns to service_types table
DO $$ 
BEGIN
    -- Add is_premium column if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'service_types' AND column_name = 'is_premium'
    ) THEN
        ALTER TABLE service_types ADD COLUMN is_premium BOOLEAN DEFAULT false;
    END IF;
    
    -- Add display_name column if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'service_types' AND column_name = 'display_name'
    ) THEN
        ALTER TABLE service_types ADD COLUMN display_name VARCHAR(255);
    END IF;
    
    -- Add credits_required column if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'service_types' AND column_name = 'credits_required'
    ) THEN
        ALTER TABLE service_types ADD COLUMN credits_required INTEGER DEFAULT 5;
    END IF;
    
    -- Add color_gradient column if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'service_types' AND column_name = 'color_gradient'
    ) THEN
        ALTER TABLE service_types ADD COLUMN color_gradient VARCHAR(100) DEFAULT 'from-purple-500 to-indigo-600';
    END IF;
    
    -- Add dynamic_pricing_enabled column if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'service_types' AND column_name = 'dynamic_pricing_enabled'
    ) THEN
        ALTER TABLE service_types ADD COLUMN dynamic_pricing_enabled BOOLEAN DEFAULT false;
    END IF;
    
    -- Add knowledge_domains column if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'service_types' AND column_name = 'knowledge_domains'
    ) THEN
        ALTER TABLE service_types ADD COLUMN knowledge_domains JSONB DEFAULT '[]';
    END IF;
    
    -- Add persona_modes column if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'service_types' AND column_name = 'persona_modes'
    ) THEN
        ALTER TABLE service_types ADD COLUMN persona_modes JSONB DEFAULT '[]';
    END IF;
    
    -- Add comprehensive_reading_enabled column if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'service_types' AND column_name = 'comprehensive_reading_enabled'
    ) THEN
        ALTER TABLE service_types ADD COLUMN comprehensive_reading_enabled BOOLEAN DEFAULT false;
    END IF;
    
    -- Add birth_chart_enabled column if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'service_types' AND column_name = 'birth_chart_enabled'
    ) THEN
        ALTER TABLE service_types ADD COLUMN birth_chart_enabled BOOLEAN DEFAULT false;
    END IF;
    
    -- Add remedies_enabled column if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'service_types' AND column_name = 'remedies_enabled'
    ) THEN
        ALTER TABLE service_types ADD COLUMN remedies_enabled BOOLEAN DEFAULT false;
    END IF;
    
END $$;

-- Update existing service_types with display_name if it's null
UPDATE service_types SET display_name = 
    CASE 
        WHEN name = 'clarity' THEN 'Spiritual Clarity Session'
        WHEN name = 'love' THEN 'Love & Relationship Guidance'
        WHEN name = 'premium' THEN 'Premium Comprehensive Reading'
        WHEN name = 'elite' THEN 'Elite Personalized Consultation'
        WHEN name = 'comprehensive_life_reading_30min' THEN 'Comprehensive Life Reading (30 min)'
        WHEN name = 'horoscope_reading_quick' THEN 'Quick Horoscope Reading'
        WHEN name = 'satsang_community' THEN 'Satsang Community Access'
        ELSE INITCAP(REPLACE(name, '_', ' '))
    END
WHERE display_name IS NULL;

-- Update service_types with credits_required if it's null or 0
UPDATE service_types SET credits_required = 
    CASE 
        WHEN name = 'clarity' THEN 5
        WHEN name = 'love' THEN 8
        WHEN name = 'premium' THEN 12
        WHEN name = 'elite' THEN 20
        WHEN name = 'comprehensive_life_reading_30min' THEN 15
        WHEN name = 'horoscope_reading_quick' THEN 3
        WHEN name = 'satsang_community' THEN 2
        ELSE 5
    END
WHERE credits_required IS NULL OR credits_required = 0;

-- Create service_configuration_cache table if missing
CREATE TABLE IF NOT EXISTS service_configuration_cache (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(100) UNIQUE NOT NULL,
    configuration JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

-- Insert default service configurations
INSERT INTO service_configuration_cache (service_name, configuration) VALUES 
    ('clarity', '{"base_credits": 5, "duration_minutes": 15, "features": ["basic_guidance"]}'),
    ('love', '{"base_credits": 8, "duration_minutes": 20, "features": ["relationship_guidance"]}'),
    ('premium', '{"base_credits": 12, "duration_minutes": 30, "features": ["comprehensive_reading", "birth_chart"]}')
ON CONFLICT (service_name) DO UPDATE SET
    configuration = EXCLUDED.configuration,
    updated_at = CURRENT_TIMESTAMP;