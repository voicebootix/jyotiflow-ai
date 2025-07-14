-- Migration: fix_missing_columns.sql
-- Fix missing columns causing SQL errors in admin and service features
-- This addresses the credits_required column in service_types and donation_transactions table issues

-- =================================================================
-- 1. FIX SERVICE_TYPES TABLE - Add missing credits_required column
-- =================================================================

DO $$ 
BEGIN
    -- Check if service_types table exists
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'service_types') THEN
        
        -- Add credits_required column if missing
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'service_types' AND column_name = 'credits_required'
        ) THEN
            ALTER TABLE service_types ADD COLUMN credits_required INTEGER DEFAULT 5;
            
            -- Update existing records based on base_credits if available
            UPDATE service_types 
            SET credits_required = COALESCE(base_credits, 5)
            WHERE credits_required = 5;
            
            RAISE NOTICE '✅ Added credits_required column to service_types table';
        ELSE
            RAISE NOTICE '✅ credits_required column already exists in service_types table';
        END IF;
        
        -- Add other missing columns that might be needed
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'service_types' AND column_name = 'display_name'
        ) THEN
            ALTER TABLE service_types ADD COLUMN display_name VARCHAR(255);
            UPDATE service_types SET display_name = name WHERE display_name IS NULL;
            RAISE NOTICE '✅ Added display_name column to service_types table';
        END IF;
        
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'service_types' AND column_name = 'price_usd'
        ) THEN
            ALTER TABLE service_types ADD COLUMN price_usd DECIMAL(10,2) DEFAULT 0.0;
            RAISE NOTICE '✅ Added price_usd column to service_types table';
        END IF;
        
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'service_types' AND column_name = 'service_category'
        ) THEN
            ALTER TABLE service_types ADD COLUMN service_category VARCHAR(100) DEFAULT 'guidance';
            RAISE NOTICE '✅ Added service_category column to service_types table';
        END IF;
        
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'service_types' AND column_name = 'enabled'
        ) THEN
            ALTER TABLE service_types ADD COLUMN enabled BOOLEAN DEFAULT true;
            RAISE NOTICE '✅ Added enabled column to service_types table';
        END IF;
        
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'service_types' AND column_name = 'icon'
        ) THEN
            ALTER TABLE service_types ADD COLUMN icon VARCHAR(50) DEFAULT '🔮';
            RAISE NOTICE '✅ Added icon column to service_types table';
        END IF;
        
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'service_types' AND column_name = 'avatar_video_enabled'
        ) THEN
            ALTER TABLE service_types ADD COLUMN avatar_video_enabled BOOLEAN DEFAULT false;
            RAISE NOTICE '✅ Added avatar_video_enabled column to service_types table';
        END IF;
        
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'service_types' AND column_name = 'live_chat_enabled'
        ) THEN
            ALTER TABLE service_types ADD COLUMN live_chat_enabled BOOLEAN DEFAULT false;
            RAISE NOTICE '✅ Added live_chat_enabled column to service_types table';
        END IF;
        
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'service_types' AND column_name = 'voice_enabled'
        ) THEN
            ALTER TABLE service_types ADD COLUMN voice_enabled BOOLEAN DEFAULT false;
            RAISE NOTICE '✅ Added voice_enabled column to service_types table';
        END IF;
        
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'service_types' AND column_name = 'video_enabled'
        ) THEN
            ALTER TABLE service_types ADD COLUMN video_enabled BOOLEAN DEFAULT false;
            RAISE NOTICE '✅ Added video_enabled column to service_types table';
        END IF;
        
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'service_types' AND column_name = 'interactive_enabled'
        ) THEN
            ALTER TABLE service_types ADD COLUMN interactive_enabled BOOLEAN DEFAULT false;
            RAISE NOTICE '✅ Added interactive_enabled column to service_types table';
        END IF;
        
    ELSE
        RAISE NOTICE '❌ service_types table does not exist. Creating it now...';
        
        -- Create service_types table with all required columns
        CREATE TABLE service_types (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL,
            display_name VARCHAR(255),
            description TEXT,
            base_credits INTEGER DEFAULT 5,
            credits_required INTEGER DEFAULT 5,
            price_usd DECIMAL(10,2) DEFAULT 0.0,
            duration_minutes INTEGER DEFAULT 15,
            service_category VARCHAR(100) DEFAULT 'guidance',
            enabled BOOLEAN DEFAULT true,
            icon VARCHAR(50) DEFAULT '🔮',
            avatar_video_enabled BOOLEAN DEFAULT false,
            live_chat_enabled BOOLEAN DEFAULT false,
            voice_enabled BOOLEAN DEFAULT false,
            video_enabled BOOLEAN DEFAULT true,
            interactive_enabled BOOLEAN DEFAULT false,
            knowledge_configuration JSONB DEFAULT '{}',
            specialized_prompts JSONB DEFAULT '{}',
            response_behavior JSONB DEFAULT '{}',
            swami_persona_mode VARCHAR(100) DEFAULT 'general',
            analysis_depth VARCHAR(50) DEFAULT 'standard',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        RAISE NOTICE '✅ Created service_types table with all required columns';
    END IF;
    
END $$;

-- =================================================================
-- 2. FIX DONATION_TRANSACTIONS TABLE - Ensure it exists with correct schema
-- =================================================================

DO $$ 
BEGIN
    -- Check if donation_transactions table exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'donation_transactions') THEN
        RAISE NOTICE '❌ donation_transactions table does not exist. Creating it now...';
        
        -- Create donation_transactions table
        CREATE TABLE donation_transactions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id INTEGER REFERENCES users(id),
            donation_id UUID REFERENCES donations(id),
            amount_usd DECIMAL(10,2) NOT NULL,
            currency VARCHAR(3) DEFAULT 'USD',
            payment_method VARCHAR(50) DEFAULT 'stripe',
            stripe_payment_intent_id VARCHAR(255),
            stripe_session_id VARCHAR(255),
            status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'completed', 'failed', 'refunded'
            transaction_type VARCHAR(50) DEFAULT 'donation', -- 'donation', 'offering', 'super_chat'
            session_id UUID REFERENCES sessions(id), -- Optional: link to spiritual session
            message TEXT, -- Optional: message for super chat donations
            metadata JSONB DEFAULT '{}'::jsonb, -- Additional transaction data
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            completed_at TIMESTAMP NULL
        );
        
        -- Create indexes for efficient querying
        CREATE INDEX idx_donation_transactions_user_id ON donation_transactions(user_id);
        CREATE INDEX idx_donation_transactions_donation_id ON donation_transactions(donation_id);
        CREATE INDEX idx_donation_transactions_status ON donation_transactions(status);
        CREATE INDEX idx_donation_transactions_created ON donation_transactions(created_at DESC);
        CREATE INDEX idx_donation_transactions_stripe_payment_intent ON donation_transactions(stripe_payment_intent_id);
        
        RAISE NOTICE '✅ Created donation_transactions table with all required columns and indexes';
    ELSE
        RAISE NOTICE '✅ donation_transactions table already exists';
        
        -- Check if user_id column exists (just in case)
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'donation_transactions' AND column_name = 'user_id'
        ) THEN
            ALTER TABLE donation_transactions ADD COLUMN user_id INTEGER REFERENCES users(id);
            RAISE NOTICE '✅ Added user_id column to donation_transactions table';
        END IF;
    END IF;
    
END $$;

-- =================================================================
-- 3. ENSURE DONATIONS TABLE EXISTS (Referenced by donation_transactions)
-- =================================================================

DO $$ 
BEGIN
    -- Check if donations table exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'donations') THEN
        RAISE NOTICE '❌ donations table does not exist. Creating it now...';
        
        -- Create donations table
        CREATE TABLE donations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(100) NOT NULL,
            tamil_name VARCHAR(100),
            description TEXT,
            price_usd DECIMAL(10,2) NOT NULL,
            icon VARCHAR(50) DEFAULT '🙏',
            category VARCHAR(50) DEFAULT 'offering',
            enabled BOOLEAN DEFAULT true,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        
        -- Insert default donation options
        INSERT INTO donations (name, tamil_name, description, price_usd, icon, category) VALUES
        ('Digital Flowers', 'டிஜிட்டல் பூக்கள்', 'Offer digital flowers to the divine', 1.00, '🌺', 'offering'),
        ('Lamp Offering', 'தீப அர்ப்பணம்', 'Light a virtual lamp for blessings', 3.00, '🪔', 'offering'),
        ('Prasadam Blessing', 'பிரசாத ஆசீர்வாதம்', 'Receive blessed prasadam', 5.00, '🍯', 'blessing'),
        ('Temple Donation', 'கோவில் நன்கொடை', 'General temple donation', 10.00, '🏛️', 'donation'),
        ('Super Chat - Priority', 'சூப்பர் சாட் - முன்னுரிமை', 'Priority message in live chat', 2.00, '💬', 'super_chat');
        
        RAISE NOTICE '✅ Created donations table with default donation options';
    ELSE
        RAISE NOTICE '✅ donations table already exists';
    END IF;
    
END $$;

-- =================================================================
-- 4. INSERT DEFAULT SERVICE TYPES IF NEEDED
-- =================================================================

DO $$ 
BEGIN
    -- Check if service_types table has any records
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'service_types') THEN
        -- Check if we have any service types
        IF NOT EXISTS (SELECT 1 FROM service_types LIMIT 1) THEN
            RAISE NOTICE '📋 Inserting default service types...';
            
            INSERT INTO service_types (
                name, display_name, description, credits_required, price_usd, 
                duration_minutes, service_category, enabled, icon
            ) VALUES
            ('basic_guidance', 'Basic Spiritual Guidance', 'Basic spiritual guidance and advice', 5, 5.00, 15, 'guidance', true, '🔮'),
            ('comprehensive_reading', 'Comprehensive Reading', 'Detailed spiritual reading with analysis', 10, 10.00, 30, 'reading', true, '📖'),
            ('birth_chart_analysis', 'Birth Chart Analysis', 'Complete birth chart analysis and predictions', 15, 15.00, 45, 'astrology', true, '⭐'),
            ('relationship_guidance', 'Relationship Guidance', 'Guidance on relationships and compatibility', 8, 8.00, 20, 'guidance', true, '💕'),
            ('career_consultation', 'Career Consultation', 'Professional guidance on career matters', 12, 12.00, 30, 'consultation', true, '💼'),
            ('health_wellness', 'Health & Wellness', 'Spiritual guidance for health and wellness', 10, 10.00, 25, 'wellness', true, '🌿')
            ON CONFLICT (name) DO NOTHING;
            
            RAISE NOTICE '✅ Inserted default service types';
        ELSE
            RAISE NOTICE '✅ Service types already exist';
        END IF;
    END IF;
    
END $$;

-- =================================================================
-- 5. VERIFICATION QUERIES
-- =================================================================

DO $$ 
BEGIN
    RAISE NOTICE '🔍 VERIFICATION RESULTS:';
    
    -- Check service_types table
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'service_types') THEN
        RAISE NOTICE '✅ service_types table exists';
        
        IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'service_types' AND column_name = 'credits_required') THEN
            RAISE NOTICE '✅ credits_required column exists in service_types';
        ELSE
            RAISE NOTICE '❌ credits_required column missing from service_types';
        END IF;
    ELSE
        RAISE NOTICE '❌ service_types table does not exist';
    END IF;
    
    -- Check donation_transactions table
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'donation_transactions') THEN
        RAISE NOTICE '✅ donation_transactions table exists';
        
        IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'donation_transactions' AND column_name = 'user_id') THEN
            RAISE NOTICE '✅ user_id column exists in donation_transactions';
        ELSE
            RAISE NOTICE '❌ user_id column missing from donation_transactions';
        END IF;
    ELSE
        RAISE NOTICE '❌ donation_transactions table does not exist';
    END IF;
    
    -- Check donations table
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'donations') THEN
        RAISE NOTICE '✅ donations table exists';
    ELSE
        RAISE NOTICE '❌ donations table does not exist';
    END IF;
    
END $$;

-- =================================================================
-- COMPLETED: Missing columns fix migration
-- =================================================================

COMMIT;