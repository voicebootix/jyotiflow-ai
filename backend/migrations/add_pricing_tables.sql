-- JyotiFlow Dynamic Pricing Tables Migration
-- Creates all required tables for the dynamic pricing system

-- Pricing history table - tracks all price changes
CREATE TABLE IF NOT EXISTS pricing_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_name VARCHAR(255) NOT NULL,
    old_price DECIMAL(10,2),
    new_price DECIMAL(10,2) NOT NULL,
    reasoning TEXT,
    changed_by VARCHAR(100) DEFAULT 'system',
    changed_at TIMESTAMP DEFAULT NOW(),
    approval_status VARCHAR(50) DEFAULT 'approved'
);

-- Pricing overrides table - manual admin overrides
CREATE TABLE IF NOT EXISTS pricing_overrides (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_type VARCHAR(255) NOT NULL,
    override_price DECIMAL(10,2) NOT NULL,
    duration_hours INTEGER DEFAULT 24,
    reason TEXT NOT NULL,
    created_by VARCHAR(100) DEFAULT 'admin',
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active'
);

-- AI pricing recommendations table - stores AI-generated recommendations
CREATE TABLE IF NOT EXISTS ai_pricing_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_type VARCHAR(255) NOT NULL,
    recommendation_data JSONB NOT NULL,
    confidence_score DECIMAL(3,2) DEFAULT 0.5,
    demand_factor DECIMAL(4,2) DEFAULT 1.0,
    cost_analysis JSONB DEFAULT '{}',
    market_conditions JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    reviewed_at TIMESTAMP,
    reviewed_by VARCHAR(100)
);

-- Service pricing configuration table - current pricing state
CREATE TABLE IF NOT EXISTS service_pricing_config (
    service_name VARCHAR(255) PRIMARY KEY,
    current_price DECIMAL(10,2) NOT NULL,
    base_cost DECIMAL(10,2) NOT NULL,
    pricing_model VARCHAR(100) DEFAULT 'dynamic',
    last_price_update TIMESTAMP DEFAULT NOW(),
    pricing_data JSONB DEFAULT '{}',
    auto_pricing_enabled BOOLEAN DEFAULT false,
    admin_approval_required BOOLEAN DEFAULT true
);

-- Cost tracking table - tracks actual operational costs
CREATE TABLE IF NOT EXISTS cost_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_type VARCHAR(255) NOT NULL,
    session_id VARCHAR(255),
    cost_breakdown JSONB NOT NULL,
    total_cost DECIMAL(10,2) NOT NULL,
    cost_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Demand analytics table - tracks demand patterns
CREATE TABLE IF NOT EXISTS demand_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_type VARCHAR(255) NOT NULL,
    analytics_date DATE DEFAULT CURRENT_DATE,
    sessions_count INTEGER DEFAULT 0,
    avg_price DECIMAL(10,2),
    demand_factor DECIMAL(4,2) DEFAULT 1.0,
    peak_hours INTEGER[] DEFAULT '{}',
    demand_trend VARCHAR(50) DEFAULT 'stable',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Revenue impact tracking table
CREATE TABLE IF NOT EXISTS revenue_impact_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    price_change_id UUID REFERENCES pricing_history(id),
    before_revenue DECIMAL(12,2),
    after_revenue DECIMAL(12,2),
    sessions_before INTEGER,
    sessions_after INTEGER,
    impact_period_days INTEGER DEFAULT 7,
    conversion_rate_change DECIMAL(5,4),
    tracked_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_pricing_history_service ON pricing_history(service_name);
CREATE INDEX IF NOT EXISTS idx_pricing_history_date ON pricing_history(changed_at);
CREATE INDEX IF NOT EXISTS idx_pricing_overrides_service ON pricing_overrides(service_type);
CREATE INDEX IF NOT EXISTS idx_pricing_overrides_status ON pricing_overrides(status);
CREATE INDEX IF NOT EXISTS idx_ai_recommendations_service ON ai_pricing_recommendations(service_type);
CREATE INDEX IF NOT EXISTS idx_ai_recommendations_status ON ai_pricing_recommendations(status);
CREATE INDEX IF NOT EXISTS idx_cost_tracking_service ON cost_tracking(service_type);
CREATE INDEX IF NOT EXISTS idx_cost_tracking_date ON cost_tracking(cost_date);
CREATE INDEX IF NOT EXISTS idx_demand_analytics_service ON demand_analytics(service_type);
CREATE INDEX IF NOT EXISTS idx_demand_analytics_date ON demand_analytics(analytics_date);

-- Insert initial comprehensive reading pricing configuration
INSERT INTO service_pricing_config (
    service_name, 
    current_price, 
    base_cost, 
    pricing_model, 
    pricing_data,
    admin_approval_required
) VALUES (
    'comprehensive_life_reading_30min',
    15.0,
    14.5,
    'dynamic_market_based',
    '{
        "cost_breakdown": {
            "openai_api_cost": 2.5,
            "elevenlabs_voice_cost": 2.5,
            "did_video_generation_cost": 4.0,
            "knowledge_processing_cost": 1.8,
            "chart_generation_cost": 1.5,
            "remedies_generation_cost": 1.2,
            "server_processing_cost": 0.8
        },
        "profit_margin": 1.03,
        "price_range": {
            "min": 15.0,
            "max": 25.0
        }
    }'::jsonb,
    true
) ON CONFLICT (service_name) DO UPDATE SET
    base_cost = 14.5,
    pricing_data = '{
        "cost_breakdown": {
            "openai_api_cost": 2.5,
            "elevenlabs_voice_cost": 2.5,
            "did_video_generation_cost": 4.0,
            "knowledge_processing_cost": 1.8,
            "chart_generation_cost": 1.5,
            "remedies_generation_cost": 1.2,
            "server_processing_cost": 0.8
        },
        "profit_margin": 1.03,
        "price_range": {
            "min": 15.0,
            "max": 25.0
        }
    }'::jsonb;

-- Create function to automatically track price changes
CREATE OR REPLACE FUNCTION track_price_changes()
RETURNS TRIGGER AS $$
BEGIN
    -- Insert into pricing history when service_types price changes
    IF OLD.credits_required IS DISTINCT FROM NEW.credits_required THEN
        INSERT INTO pricing_history (
            service_name,
            old_price,
            new_price,
            reasoning,
            changed_at
        ) VALUES (
            NEW.name,
            OLD.credits_required,
            NEW.credits_required,
            'Service price updated',
            NOW()
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically track price changes
DROP TRIGGER IF EXISTS trigger_track_price_changes ON service_types;
CREATE TRIGGER trigger_track_price_changes
    AFTER UPDATE OF credits_required
    ON service_types
    FOR EACH ROW
    EXECUTE FUNCTION track_price_changes();

-- Create function to update demand analytics daily
CREATE OR REPLACE FUNCTION update_demand_analytics()
RETURNS void AS $$
DECLARE
    service_record RECORD;
    session_count INTEGER;
    avg_session_price DECIMAL(10,2);
    demand_factor DECIMAL(4,2);
BEGIN
    -- Update analytics for comprehensive reading service
    SELECT COUNT(*), AVG(credits_required) 
    INTO session_count, avg_session_price
    FROM sessions 
    WHERE service_type = 'comprehensive_life_reading_30min'
    AND created_at >= CURRENT_DATE;
    
    -- Calculate demand factor (simplified)
    demand_factor := CASE 
        WHEN session_count > 10 THEN 1.2
        WHEN session_count > 5 THEN 1.1
        WHEN session_count > 2 THEN 1.0
        WHEN session_count > 0 THEN 0.9
        ELSE 0.8
    END;
    
    INSERT INTO demand_analytics (
        service_type,
        analytics_date,
        sessions_count,
        avg_price,
        demand_factor,
        demand_trend
    ) VALUES (
        'comprehensive_life_reading_30min',
        CURRENT_DATE,
        session_count,
        avg_session_price,
        demand_factor,
        CASE 
            WHEN demand_factor > 1.1 THEN 'increasing'
            WHEN demand_factor < 0.9 THEN 'decreasing'
            ELSE 'stable'
        END
    ) ON CONFLICT (service_type, analytics_date) DO UPDATE SET
        sessions_count = EXCLUDED.sessions_count,
        avg_price = EXCLUDED.avg_price,
        demand_factor = EXCLUDED.demand_factor,
        demand_trend = EXCLUDED.demand_trend;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions (adjust username as needed)
GRANT SELECT, INSERT, UPDATE, DELETE ON pricing_history TO jyotiflow_db_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON pricing_overrides TO jyotiflow_db_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ai_pricing_recommendations TO jyotiflow_db_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON service_pricing_config TO jyotiflow_db_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON cost_tracking TO jyotiflow_db_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON demand_analytics TO jyotiflow_db_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON revenue_impact_tracking TO jyotiflow_db_user;

-- Note: Run this migration after the main JyotiFlow database is set up
-- This adds pricing functionality without breaking existing features