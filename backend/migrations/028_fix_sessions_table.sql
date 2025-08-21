-- Add missing user_id and updated_at columns to the sessions table
ALTER TABLE sessions
ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id),
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();

-- Backfill user_id from the user_email column for existing sessions
-- This is a critical data integrity fix
UPDATE sessions s
SET user_id = u.id
FROM users u
WHERE s.user_email = u.email
AND s.user_id IS NULL;

-- Set a default for updated_at on older records
UPDATE sessions
SET updated_at = created_at
WHERE updated_at IS NULL;
