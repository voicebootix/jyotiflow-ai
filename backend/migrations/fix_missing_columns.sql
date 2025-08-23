-- Migration: fix_missing_columns.sql
-- Fix missing columns causing SQL errors in admin and service features
-- Simplified version to avoid RAISE NOTICE syntax issues

-- =================================================================
-- 0. ENSURE REQUIRED EXTENSIONS
-- =================================================================

-- Enable pgcrypto extension for gen_random_uuid() support
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- =================================================================
-- 1. FIX SERVICE_TYPES TABLE - Add missing credits_required column
-- =================================================================

-- Add credits_required column if missing
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'service_types') THEN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'service_types' AND column_name = 'credits_required'
        ) THEN
            ALTER TABLE service_types ADD COLUMN credits_required INTEGER DEFAULT 5;
            UPDATE service_types 
            SET credits_required = COALESCE(base_credits, 5)
            WHERE credits_required = 5;
        END IF;
        
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'service_types' AND column_name = 'display_name'
        ) THEN
            ALTER TABLE service_types ADD COLUMN display_name VARCHAR(255);
            UPDATE service_types SET display_name = name WHERE display_name IS NULL;
        END IF;
        
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'service_types' AND column_name = 'price_usd'
        ) THEN
            ALTER TABLE service_types ADD COLUMN price_usd DECIMAL(10,2) DEFAULT 0.0;
        END IF;
        
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'service_types' AND column_name = 'service_category'
        ) THEN
            ALTER TABLE service_types ADD COLUMN service_category VARCHAR(255) DEFAULT 'guidance';
        END IF;
        
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'service_types' AND column_name = 'enabled'
        ) THEN
            ALTER TABLE service_types ADD COLUMN enabled BOOLEAN DEFAULT true;
        END IF;
        
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'service_types' AND column_name = 'icon'
        ) THEN
            ALTER TABLE service_types ADD COLUMN icon VARCHAR(255) DEFAULT '🔮';
        END IF;
        
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'service_types' AND column_name = 'video_enabled'
        ) THEN
            ALTER TABLE service_types ADD COLUMN video_enabled BOOLEAN DEFAULT true;
        END IF;
    ELSE
        -- Create service_types table if it doesn't exist
        CREATE TABLE service_types (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) UNIQUE NOT NULL,
            display_name VARCHAR(255),
            description TEXT,
            base_credits INTEGER DEFAULT 5,
            credits_required INTEGER DEFAULT 5,
            price_usd DECIMAL(10,2) DEFAULT 0.0,
            duration_minutes INTEGER DEFAULT 15,
            service_category VARCHAR(255) DEFAULT 'guidance',
            enabled BOOLEAN DEFAULT true,
            icon VARCHAR(255) DEFAULT '🔮',
            video_enabled BOOLEAN DEFAULT true,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    END IF;
END $$;

-- =================================================================
-- 2. ENSURE BASIC TABLES EXIST
-- =================================================================

-- Create donations table if missing
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'donations') THEN
        CREATE TABLE donations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(255) NOT NULL,
            description TEXT,
            price_usd DECIMAL(10,2) NOT NULL,
            icon VARCHAR(255) DEFAULT '🙏',
            category VARCHAR(255) DEFAULT 'offering',
            enabled BOOLEAN DEFAULT true,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        INSERT INTO donations (name, description, price_usd, icon, category) VALUES
        ('Digital Flowers', 'Offer digital flowers to the divine', 1.00, '🌺', 'offering'),
        ('Lamp Offering', 'Light a virtual lamp for blessings', 3.00, '🪔', 'offering'),
        ('Temple Donation', 'General temple donation', 10.00, '🏛️', 'donation');
    END IF;
END $$;

-- Create donation_transactions table if missing
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'donation_transactions') THEN
        CREATE TABLE donation_transactions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id INTEGER,
            donation_id UUID,
            amount_usd DECIMAL(10,2) NOT NULL,
            currency VARCHAR(255) DEFAULT 'USD',
            payment_method VARCHAR(255) DEFAULT 'stripe',
            status VARCHAR(255) DEFAULT 'pending',
            transaction_type VARCHAR(255) DEFAULT 'donation',
            session_id UUID,
            message TEXT,
            metadata JSONB DEFAULT '{}'::jsonb,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX idx_donation_transactions_user_id ON donation_transactions(user_id);
        CREATE INDEX idx_donation_transactions_status ON donation_transactions(status);
        CREATE INDEX idx_donation_transactions_created ON donation_transactions(created_at DESC);
    END IF;
END $$;

-- Insert default service types if table is empty
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'service_types') THEN
        IF NOT EXISTS (SELECT 1 FROM service_types LIMIT 1) THEN
            INSERT INTO service_types (
                name, display_name, description, credits_required, price_usd, 
                duration_minutes, service_category, enabled, icon
            ) VALUES
            ('basic_guidance', 'Basic Spiritual Guidance', 'Basic spiritual guidance and advice', 5, 5.00, 15, 'guidance', true, '🔮'),
            ('birth_chart_analysis', 'Birth Chart Analysis', 'Complete birth chart analysis', 15, 15.00, 45, 'astrology', true, '⭐'),
            ('relationship_guidance', 'Relationship Guidance', 'Guidance on relationships', 8, 8.00, 20, 'guidance', true, '💕')
            ON CONFLICT (name) DO NOTHING;
        END IF;
    END IF;
END $$;