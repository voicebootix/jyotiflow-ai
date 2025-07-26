-- Fix Test Execution System Database Schema Issues
-- Missing columns causing test storage failures

-- Add missing error_message column to test_execution_sessions
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'test_execution_sessions' 
        AND column_name = 'error_message'
    ) THEN
        ALTER TABLE test_execution_sessions ADD COLUMN error_message TEXT;
        RAISE NOTICE 'Added error_message column to test_execution_sessions';
    ELSE
        RAISE NOTICE 'error_message column already exists in test_execution_sessions';
    END IF;
END
$$;

-- Add missing columns if they don't exist
DO $$
BEGIN
    -- Add environment column if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'test_execution_sessions' 
        AND column_name = 'environment'
    ) THEN
        ALTER TABLE test_execution_sessions ADD COLUMN environment VARCHAR(50) DEFAULT 'production';
        RAISE NOTICE 'Added environment column to test_execution_sessions';
    END IF;

    -- Add triggered_by column if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'test_execution_sessions' 
        AND column_name = 'triggered_by'
    ) THEN
        ALTER TABLE test_execution_sessions ADD COLUMN triggered_by VARCHAR(50) DEFAULT 'manual';
        RAISE NOTICE 'Added triggered_by column to test_execution_sessions';
    END IF;

    -- Add coverage_percentage column if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'test_execution_sessions' 
        AND column_name = 'coverage_percentage'
    ) THEN
        ALTER TABLE test_execution_sessions ADD COLUMN coverage_percentage DECIMAL(5,2);
        RAISE NOTICE 'Added coverage_percentage column to test_execution_sessions';
    END IF;

    -- Add execution_time_seconds column if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'test_execution_sessions' 
        AND column_name = 'execution_time_seconds'
    ) THEN
        ALTER TABLE test_execution_sessions ADD COLUMN execution_time_seconds INTEGER;
        RAISE NOTICE 'Added execution_time_seconds column to test_execution_sessions';
    END IF;
END
$$;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_test_sessions_status ON test_execution_sessions(status);
CREATE INDEX IF NOT EXISTS idx_test_sessions_started_at ON test_execution_sessions(started_at);
CREATE INDEX IF NOT EXISTS idx_test_sessions_test_type ON test_execution_sessions(test_type);

-- Verify the schema changes
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'test_execution_sessions' 
ORDER BY ordinal_position;