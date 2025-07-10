-- Session Donations Table
-- தமிழ் - அமர்வு தானங்கள் அட்டவணை

CREATE TABLE IF NOT EXISTS session_donations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    donation_id UUID REFERENCES donations(id) ON DELETE CASCADE,
    amount_usd DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_session_donations_session_id ON session_donations(session_id);
CREATE INDEX IF NOT EXISTS idx_session_donations_donation_id ON session_donations(donation_id);
CREATE INDEX IF NOT EXISTS idx_session_donations_created ON session_donations(created_at DESC); 