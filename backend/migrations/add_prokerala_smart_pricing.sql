-- Add Prokerala configuration to service_types
ALTER TABLE service_types 
ADD COLUMN IF NOT EXISTS prokerala_endpoints TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS estimated_api_calls INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS cache_effectiveness DECIMAL(5,2) DEFAULT 70.00;

-- Create Prokerala cost configuration
CREATE TABLE IF NOT EXISTS prokerala_cost_config (
    id SERIAL PRIMARY KEY,
    margin_percentage DECIMAL(10,2) DEFAULT 500.00,
    cache_discount_enabled BOOLEAN DEFAULT TRUE,
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Add missing columns if they don't exist
ALTER TABLE prokerala_cost_config 
ADD COLUMN IF NOT EXISTS max_cost_per_call DECIMAL(10,2) DEFAULT 0.04;

-- Insert default configuration (only if table is empty)
INSERT INTO prokerala_cost_config (max_cost_per_call, margin_percentage) 
SELECT 0.04, 500.00
WHERE NOT EXISTS (SELECT 1 FROM prokerala_cost_config);

-- Create cache effectiveness tracking
CREATE TABLE IF NOT EXISTS cache_analytics (
    id SERIAL PRIMARY KEY,
    service_type_id INTEGER REFERENCES service_types(id),
    date DATE DEFAULT CURRENT_DATE,
    total_requests INTEGER DEFAULT 0,
    cache_hits INTEGER DEFAULT 0,
    cache_hit_rate DECIMAL(5,2) GENERATED ALWAYS AS 
        (CASE WHEN total_requests > 0 THEN (cache_hits::DECIMAL / total_requests * 100) ELSE 0 END) STORED,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(service_type_id, date)
);

-- Prokerala endpoint suggestions
CREATE TABLE IF NOT EXISTS endpoint_suggestions (
    id SERIAL PRIMARY KEY,
    endpoint_group VARCHAR(100) NOT NULL,
    endpoints TEXT[] NOT NULL,
    description TEXT,
    typical_use_case VARCHAR(255),
    value_score INTEGER DEFAULT 5, -- 1-10 scale
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insert endpoint group suggestions
INSERT INTO endpoint_suggestions (endpoint_group, endpoints, description, typical_use_case, value_score) VALUES
('quick_love', ARRAY['/astrology/nakshatra-porutham', '/horoscope/daily/love-compatibility'], 
 'Basic compatibility check', 'Quick love compatibility reading', 6),
('deep_love', ARRAY['/astrology/birth-details', '/astrology/nakshatra-porutham', '/astrology/kundli-matching', '/numerology/life-path-number'], 
 'Comprehensive relationship analysis', 'Detailed compatibility reading', 9),
('career_basic', ARRAY['/astrology/birth-details', '/horoscope/daily'], 
 'Basic career insights', 'Quick career guidance', 5),
('career_comprehensive', ARRAY['/astrology/birth-details', '/astrology/planet-position', '/astrology/dasha-periods', '/numerology/destiny-number', '/astrology/auspicious-period'], 
 'Complete career analysis with timing', 'Professional career consultation', 10),
('life_reading', ARRAY['/astrology/birth-details', '/astrology/kundli/advanced', '/astrology/planet-position', '/astrology/dasha-periods', '/astrology/yoga', '/astrology/mangal-dosha', '/astrology/kaal-sarp-dosha', '/astrology/sade-sati', '/numerology/life-path-number', '/numerology/destiny-number', '/numerology/soul-urge-number'], 
 'Complete life analysis', '30-minute comprehensive reading', 10)
ON CONFLICT DO NOTHING;

-- Add cache tracking to sessions table
ALTER TABLE sessions 
ADD COLUMN IF NOT EXISTS prokerala_cache_used BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS prokerala_endpoints_used TEXT[] DEFAULT '{}';

-- Create API cache table if it doesn't exist
CREATE TABLE IF NOT EXISTS api_cache (
    id SERIAL PRIMARY KEY,
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index for cache lookup
CREATE INDEX IF NOT EXISTS idx_api_cache_key ON api_cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_api_cache_created_at ON api_cache(created_at);