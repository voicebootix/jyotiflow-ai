-- Fix user_id type mismatches across all tables
-- This migration consolidates all user_id columns to INTEGER
-- Auto-generated by Database Self-Healing System

BEGIN;

-- Validate data can be converted
DO $$
BEGIN
    -- Check for non-numeric values
    IF EXISTS (
        SELECT 1 FROM sessions WHERE user_id IS NOT NULL AND user_id !~ '^\d+$'
        UNION ALL
        SELECT 1 FROM credit_transactions WHERE user_id IS NOT NULL AND user_id !~ '^\d+$'
        UNION ALL
        SELECT 1 FROM user_purchases WHERE user_id IS NOT NULL AND user_id !~ '^\d+$'
        UNION ALL
        SELECT 1 FROM avatar_sessions WHERE user_id IS NOT NULL AND user_id !~ '^\d+$'
        UNION ALL
        SELECT 1 FROM live_chat_sessions WHERE user_id IS NOT NULL AND user_id !~ '^\d+$'
    ) THEN
        RAISE EXCEPTION 'Non-numeric user_id values found. Manual cleanup required.';
    END IF;
END $$;

-- 1. Fix sessions table
ALTER TABLE sessions 
ALTER COLUMN user_id TYPE INTEGER 
USING user_id::INTEGER;

-- 2. Fix credit_transactions table
ALTER TABLE credit_transactions 
ALTER COLUMN user_id TYPE INTEGER 
USING user_id::INTEGER;

-- 3. Fix user_purchases table
ALTER TABLE user_purchases 
ALTER COLUMN user_id TYPE INTEGER 
USING user_id::INTEGER;

-- 4. Fix avatar_sessions table
ALTER TABLE avatar_sessions 
ALTER COLUMN user_id TYPE INTEGER 
USING user_id::INTEGER;

-- 5. Fix live_chat_sessions table
ALTER TABLE live_chat_sessions 
ALTER COLUMN user_id TYPE INTEGER 
USING user_id::INTEGER;

-- 6. Check for orphaned records before adding constraints
DO $$
DECLARE
    orphans INTEGER;
BEGIN
    SELECT COUNT(*) INTO orphans FROM (
        SELECT user_id FROM sessions WHERE user_id NOT IN (SELECT id FROM users)
        UNION ALL
        SELECT user_id FROM credit_transactions WHERE user_id NOT IN (SELECT id FROM users)
        UNION ALL
        SELECT user_id FROM user_purchases WHERE user_id NOT IN (SELECT id FROM users)
    ) t;
    
    IF orphans > 0 THEN
        RAISE NOTICE 'Found % orphaned user_id values. Consider cleaning up or using SET NULL instead of CASCADE.', orphans;
    END IF;
END $$;

-- 7. Add missing foreign key constraints
ALTER TABLE sessions 
ADD CONSTRAINT fk_sessions_user_id 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE credit_transactions 
ADD CONSTRAINT fk_credit_transactions_user_id 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE user_purchases 
ADD CONSTRAINT fk_user_purchases_user_id 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- 8. Create indexes on foreign keys
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_user_id ON credit_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_purchases_user_id ON user_purchases(user_id);

COMMIT;