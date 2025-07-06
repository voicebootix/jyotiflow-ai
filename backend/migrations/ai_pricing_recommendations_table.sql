-- AI Pricing Recommendations Table
-- தமிழ் - AI விலை பரிந்துரைகள் அட்டவணை

CREATE TABLE IF NOT EXISTS ai_pricing_recommendations (
    id SERIAL PRIMARY KEY,
    recommendation_type VARCHAR(100) NOT NULL, -- 'service_price', 'credit_package', 'donation_price', 'subscription_plan'
    current_value DECIMAL(10,2) NOT NULL, -- Current price/value
    suggested_value DECIMAL(10,2) NOT NULL, -- AI suggested new price/value
    expected_impact DECIMAL(10,2) DEFAULT 0, -- Expected revenue impact in USD
    confidence_level DECIMAL(3,2) DEFAULT 0.7, -- AI confidence (0.0 to 1.0)
    reasoning TEXT, -- AI reasoning in Tamil
    implementation_difficulty INTEGER CHECK (implementation_difficulty BETWEEN 1 AND 5), -- 1=easy, 5=hard
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'approved', 'implemented', 'rejected'
    priority_level VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high'
    service_name VARCHAR(255), -- For service-specific recommendations
    metadata JSONB DEFAULT '{}'::jsonb, -- Additional data
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    implemented_at TIMESTAMP NULL,
    implemented_by INTEGER REFERENCES users(id)
);

-- Index for efficient querying
CREATE INDEX IF NOT EXISTS idx_ai_pricing_recommendations_type ON ai_pricing_recommendations(recommendation_type);
CREATE INDEX IF NOT EXISTS idx_ai_pricing_recommendations_status ON ai_pricing_recommendations(status);
CREATE INDEX IF NOT EXISTS idx_ai_pricing_recommendations_priority ON ai_pricing_recommendations(priority_level);
CREATE INDEX IF NOT EXISTS idx_ai_pricing_recommendations_service ON ai_pricing_recommendations(service_name);
CREATE INDEX IF NOT EXISTS idx_ai_pricing_recommendations_created ON ai_pricing_recommendations(created_at DESC);

-- Insert sample data for testing
INSERT INTO ai_pricing_recommendations (
    recommendation_type, current_value, suggested_value, expected_impact, 
    confidence_level, reasoning, implementation_difficulty, priority_level, service_name
) VALUES
('service_price', 29.00, 25.00, 15000.00, 0.85, 
 'தொட்டக்க தொகுப்பின் விலையை 14% குறைப்பதன் மூலம் விற்பனையை 25% அதிகரிக்கலாம். சந்தை பகுப்பாய்வு காட்டுகிறது இந்த விலை புள்ளி அதிக பயனர்களை ஈர்க்கும்.', 
 2, 'high', 'தொட்டக்க தொகுப்பு'),

('service_price', 79.00, 85.00, 8000.00, 0.72, 
 'பிரபல தொகுப்பின் விலையை 8% அதிகரிப்பதன் மூலம் வருவாயை அதிகரிக்கலாம். இந்த சேவைக்கான தேவை அதிகமாக உள்ளது.', 
 1, 'medium', 'பிரபல தொகுப்பு'),

('credit_package', 149.00, 139.00, 12000.00, 0.78, 
 'மாஸ்டர் தொகுப்புக்கு 7% தள்ளுபடி வழங்குவதன் மூலம் விற்பனையை அதிகரிக்கலாம். போட்டி பகுப்பாய்வு காட்டுகிறது இந்த விலை புள்ளி சிறந்த மதிப்பு.', 
 1, 'high', 'மாஸ்டர் தொகுப்பு'),

('donation_price', 5.00, 7.00, 3000.00, 0.65, 
 'பிரசாதம் விலையை 40% அதிகரிப்பதன் மூலம் வருவாயை அதிகரிக்கலாம். பயனர்கள் ஆன்மீக மதிப்புக்கு அதிகம் செலுத்த தயாராக உள்ளனர்.', 
 1, 'low', 'பிரசாதம்'),

('subscription_plan', 99.00, 89.00, 20000.00, 0.82, 
 'மாதாந்திர சந்தாவை 10% குறைப்பதன் மூலம் சந்தாதாரர்களின் எண்ணிக்கையை அதிகரிக்கலாம். இது நீண்ட கால வருவாயை அதிகரிக்கும்.', 
 2, 'high', 'மாதாந்திர சந்தா'); 