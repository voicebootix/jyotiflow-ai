-- Add Birth Chart Caching Columns to Users Table
-- This script adds the necessary columns for caching birth chart data

-- Add birth chart caching columns to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS birth_chart_data TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS birth_chart_hash VARCHAR(64);
ALTER TABLE users ADD COLUMN IF NOT EXISTS birth_chart_cached_at TIMESTAMP;
ALTER TABLE users ADD COLUMN IF NOT EXISTS birth_chart_expires_at TIMESTAMP;
ALTER TABLE users ADD COLUMN IF NOT EXISTS has_free_birth_chart BOOLEAN DEFAULT false;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_birth_chart_hash ON users(birth_chart_hash);
CREATE INDEX IF NOT EXISTS idx_users_birth_chart_expires ON users(birth_chart_expires_at);

-- Verify the columns were added
SELECT sql FROM sqlite_master WHERE type='table' AND name='users';