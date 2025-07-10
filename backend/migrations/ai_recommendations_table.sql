-- AI Recommendations Storage Table
-- தமிழ் - AI பரிந்துரைகள் சேமிப்பு அட்டவணை

CREATE TABLE IF NOT EXISTS ai_recommendations (
    id SERIAL PRIMARY KEY,
    recommendation_type VARCHAR(50) NOT NULL, -- 'pricing', 'retention', 'content', etc.
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    expected_revenue_impact DECIMAL(10,2) DEFAULT 0,
    implementation_difficulty INTEGER CHECK (implementation_difficulty BETWEEN 1 AND 5),
    timeline_weeks INTEGER DEFAULT 4,
    priority_score DECIMAL(5,3) DEFAULT 0,
    priority_level VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high'
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'approved', 'implemented', 'rejected'
    ai_model_version VARCHAR(50) DEFAULT 'gpt-4',
    confidence_level DECIMAL(3,2) DEFAULT 0.7,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    implemented_at TIMESTAMP NULL,
    implemented_by INTEGER REFERENCES users(id),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Index for efficient querying
CREATE INDEX IF NOT EXISTS idx_ai_recommendations_type ON ai_recommendations(recommendation_type);
CREATE INDEX IF NOT EXISTS idx_ai_recommendations_status ON ai_recommendations(status);
CREATE INDEX IF NOT EXISTS idx_ai_recommendations_priority ON ai_recommendations(priority_score DESC);
CREATE INDEX IF NOT EXISTS idx_ai_recommendations_created ON ai_recommendations(created_at DESC);

-- Monetization Experiments Table
-- தமிழ் - நிதியாதார சோதனைகள் அட்டவணை

CREATE TABLE IF NOT EXISTS monetization_experiments (
    id SERIAL PRIMARY KEY,
    experiment_name VARCHAR(255) NOT NULL,
    experiment_type VARCHAR(50) NOT NULL, -- 'pricing', 'ui', 'content', 'timing'
    description TEXT NOT NULL,
    control_group_size INTEGER DEFAULT 0,
    test_group_size INTEGER DEFAULT 0,
    control_conversion_rate DECIMAL(5,4) DEFAULT 0,
    test_conversion_rate DECIMAL(5,4) DEFAULT 0,
    control_revenue DECIMAL(10,2) DEFAULT 0,
    test_revenue DECIMAL(10,2) DEFAULT 0,
    statistical_significance DECIMAL(5,4) DEFAULT 0,
    confidence_interval_lower DECIMAL(5,4) DEFAULT 0,
    confidence_interval_upper DECIMAL(5,4) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'running', -- 'running', 'completed', 'paused', 'cancelled'
    start_date TIMESTAMP DEFAULT NOW(),
    end_date TIMESTAMP NULL,
    winner VARCHAR(10) DEFAULT NULL, -- 'control', 'test', 'null'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Index for experiments
CREATE INDEX IF NOT EXISTS idx_monetization_experiments_type ON monetization_experiments(experiment_type);
CREATE INDEX IF NOT EXISTS idx_monetization_experiments_status ON monetization_experiments(status);
CREATE INDEX IF NOT EXISTS idx_monetization_experiments_date ON monetization_experiments(start_date DESC);

-- AI Insights Cache Table
-- தமிழ் - AI நுண்ணறிவு கேஷ் அட்டவணை

CREATE TABLE IF NOT EXISTS ai_insights_cache (
    id SERIAL PRIMARY KEY,
    insight_type VARCHAR(50) NOT NULL, -- 'pricing_recommendations', 'retention_strategies', 'market_analysis'
    data JSONB NOT NULL,
    generated_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Index for cache
CREATE INDEX IF NOT EXISTS idx_ai_insights_cache_type ON ai_insights_cache(insight_type);
CREATE INDEX IF NOT EXISTS idx_ai_insights_cache_expires ON ai_insights_cache(expires_at);
CREATE INDEX IF NOT EXISTS idx_ai_insights_cache_active ON ai_insights_cache(is_active);

-- Insert sample data for testing
INSERT INTO ai_recommendations (recommendation_type, title, description, expected_revenue_impact, implementation_difficulty, timeline_weeks, priority_score, priority_level) VALUES
('pricing', 'விலை உகந்தமயமாக்கல்', 'கிரெடிட் தொகுப்புகளின் விலையை 15% குறைப்பதன் மூலம் விற்பனையை அதிகரிக்கலாம்', 25000.00, 2, 2, 0.85, 'high'),
('content', 'உள்ளடக்க மூலோபாயம்', 'சத்சங்க் நிகழ்வுகளை வாரத்திற்கு 3 ஆக அதிகரிப்பதன் மூலம் பயனர் ஈடுபாட்டை அதிகரிக்கலாம்', 12000.00, 3, 4, 0.72, 'medium'),
('retention', 'சந்தா தக்கவைப்பு', 'மாதாந்திர சந்தாக்களுக்கு 7 நாள் இலவச சோதனை காலம் வழங்குவதன் மூலம் மாற்ற விகிதத்தை அதிகரிக்கலாம்', 18000.00, 1, 1, 0.91, 'high');

INSERT INTO monetization_experiments (experiment_name, experiment_type, description, control_group_size, test_group_size, control_conversion_rate, test_conversion_rate, status, winner) VALUES
('Credit Package Pricing Test', 'pricing', 'Testing 10% discount on credit packages', 1000, 1000, 0.045, 0.052, 'completed', 'test'),
('UI Button Color Test', 'ui', 'Testing blue vs green CTA buttons', 500, 500, 0.038, 0.041, 'running', NULL); 