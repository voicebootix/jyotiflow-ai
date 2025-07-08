-- Birth Chart Caching System Migration
-- Adds columns to users table for caching birth chart data from Prokerala API

-- Add birth chart caching columns to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS birth_chart_data JSONB,
ADD COLUMN IF NOT EXISTS birth_chart_hash VARCHAR(64),
ADD COLUMN IF NOT EXISTS birth_chart_cached_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS birth_chart_expires_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS has_free_birth_chart BOOLEAN DEFAULT false;

-- Create index on birth_chart_hash for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_birth_chart_hash ON users(birth_chart_hash);

-- Create index on birth_chart_expires_at for cache cleanup
CREATE INDEX IF NOT EXISTS idx_users_birth_chart_expires ON users(birth_chart_expires_at);

-- Add comment for documentation
COMMENT ON COLUMN users.birth_chart_data IS 'Cached birth chart data from Prokerala API to avoid repeated API calls';
COMMENT ON COLUMN users.birth_chart_hash IS 'SHA256 hash of birth details (date+time+location) for cache validation';
COMMENT ON COLUMN users.birth_chart_cached_at IS 'When the birth chart data was cached';
COMMENT ON COLUMN users.birth_chart_expires_at IS 'When the cached birth chart data expires (usually 1 year)';
COMMENT ON COLUMN users.has_free_birth_chart IS 'Whether user has received their free birth chart on signup';