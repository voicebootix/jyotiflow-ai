-- Donation Transactions Table
-- தமிழ் - தான பரிவர்த்தனைகள் அட்டவணை

CREATE TABLE IF NOT EXISTS donation_transactions (
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

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_donation_transactions_user_id ON donation_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_donation_transactions_donation_id ON donation_transactions(donation_id);
CREATE INDEX IF NOT EXISTS idx_donation_transactions_status ON donation_transactions(status);
CREATE INDEX IF NOT EXISTS idx_donation_transactions_created ON donation_transactions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_donation_transactions_stripe_payment_intent ON donation_transactions(stripe_payment_intent_id);

-- Donation Analytics Table
-- தமிழ் - தான பகுப்பாய்வு அட்டவணை

CREATE TABLE IF NOT EXISTS donation_analytics (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    donation_id UUID REFERENCES donations(id),
    total_transactions INTEGER DEFAULT 0,
    total_amount_usd DECIMAL(10,2) DEFAULT 0,
    successful_transactions INTEGER DEFAULT 0,
    failed_transactions INTEGER DEFAULT 0,
    average_amount_usd DECIMAL(10,2) DEFAULT 0,
    unique_donors INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(date, donation_id)
);

-- Index for analytics
CREATE INDEX IF NOT EXISTS idx_donation_analytics_date ON donation_analytics(date DESC);
CREATE INDEX IF NOT EXISTS idx_donation_analytics_donation_id ON donation_analytics(donation_id);

-- Insert sample donation transaction data for testing
INSERT INTO donation_transactions (
    user_id, donation_id, amount_usd, status, transaction_type, created_at
) VALUES 
(1, (SELECT id FROM donations WHERE name = 'Digital Flowers' LIMIT 1), 1.00, 'completed', 'donation', NOW() - INTERVAL '2 days'),
(1, (SELECT id FROM donations WHERE name = 'Lamp Offering' LIMIT 1), 3.00, 'completed', 'donation', NOW() - INTERVAL '1 day'),
(2, (SELECT id FROM donations WHERE name = 'Prasadam Blessing' LIMIT 1), 5.00, 'completed', 'donation', NOW() - INTERVAL '12 hours'),
(3, (SELECT id FROM donations WHERE name = 'Temple Donation' LIMIT 1), 10.00, 'completed', 'donation', NOW() - INTERVAL '6 hours'),
(4, (SELECT id FROM donations WHERE name = 'Super Chat - Priority' LIMIT 1), 2.00, 'completed', 'super_chat', NOW() - INTERVAL '3 hours')
ON CONFLICT DO NOTHING; 