-- Fix Critical Database Issues Preventing Self-Healing System
-- These are the 3 CRITICAL issues identified by the system

-- Issue 1: Missing deployment_test table
CREATE TABLE IF NOT EXISTS "deployment_test" (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Issue 2: Missing test_sessions table  
CREATE TABLE IF NOT EXISTS "test_sessions" (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Issue 3: Missing test_users table
CREATE TABLE IF NOT EXISTS "test_users" (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Add useful indexes for performance
CREATE INDEX IF NOT EXISTS "idx_test_sessions_session_id" ON "test_sessions"("session_id");
CREATE INDEX IF NOT EXISTS "idx_test_users_user_id" ON "test_users"("user_id");
CREATE INDEX IF NOT EXISTS "idx_deployment_test_created_at" ON "deployment_test"("created_at");

-- Also fix the missing indexes identified as warnings
CREATE INDEX IF NOT EXISTS "idx_autofix_test_results_test_session_id" ON "autofix_test_results"("test_session_id");
CREATE INDEX IF NOT EXISTS "idx_health_check_results_test_session_id" ON "health_check_results"("test_session_id");
CREATE INDEX IF NOT EXISTS "idx_validation_sessions_test_session_id" ON "validation_sessions"("test_session_id");

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Critical database issues fixed successfully - database healing system should now be able to start';
END
$$;