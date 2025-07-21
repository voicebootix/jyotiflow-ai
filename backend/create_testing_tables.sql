-- JyotiFlow Testing Infrastructure Tables
-- Safe backward-compatible extensions to existing monitoring system
-- These integrate with the existing validation_sessions and health_check_results tables

-- =====================================================
-- TEST EXECUTION TRACKING
-- =====================================================

-- Main test execution sessions table
CREATE TABLE IF NOT EXISTS test_execution_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_type VARCHAR(50) NOT NULL,  -- 'unit', 'integration', 'e2e', 'performance', 'security'
    test_category VARCHAR(50),       -- 'auth', 'api', 'ui', 'business_logic', 'self_healing'
    environment VARCHAR(20) DEFAULT 'production', -- 'development', 'staging', 'production'
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'running', -- 'running', 'passed', 'failed', 'partial', 'cancelled'
    total_tests INTEGER DEFAULT 0,
    passed_tests INTEGER DEFAULT 0,
    failed_tests INTEGER DEFAULT 0,
    skipped_tests INTEGER DEFAULT 0,
    coverage_percentage DECIMAL(5,2),
    execution_time_seconds INTEGER,
    triggered_by VARCHAR(50),        -- 'manual', 'auto_heal', 'deployment', 'scheduled'
    trigger_context JSONB,           -- Additional context about what triggered the test
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Individual test case results
CREATE TABLE IF NOT EXISTS test_case_results (
    result_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES test_execution_sessions(session_id) ON DELETE CASCADE,
    test_name VARCHAR(200) NOT NULL,
    test_file VARCHAR(500),
    test_function VARCHAR(200),
    test_category VARCHAR(50),       -- 'auth', 'api', 'ui', 'business_logic', 'integration'
    status VARCHAR(20) NOT NULL,     -- 'passed', 'failed', 'skipped', 'error'
    execution_time_ms INTEGER,
    error_message TEXT,
    stack_trace TEXT,
    assertions_passed INTEGER DEFAULT 0,
    assertions_failed INTEGER DEFAULT 0,
    test_data JSONB,                 -- Input data, mocks, configuration used
    output_data JSONB,               -- Actual output/response data
    expected_data JSONB,             -- Expected output data
    created_at TIMESTAMP DEFAULT NOW()
);

-- Test coverage tracking per file/module
CREATE TABLE IF NOT EXISTS test_coverage_reports (
    coverage_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES test_execution_sessions(session_id) ON DELETE CASCADE,
    file_path VARCHAR(500) NOT NULL,
    module_name VARCHAR(200),
    total_lines INTEGER,
    covered_lines INTEGER,
    coverage_percentage DECIMAL(5,2),
    missing_lines JSONB,             -- Array of uncovered line numbers
    branch_coverage DECIMAL(5,2),
    function_coverage DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- INTEGRATION WITH EXISTING MONITORING SYSTEM
-- =====================================================

-- Extend existing health_check_results table with test data
ALTER TABLE health_check_results 
ADD COLUMN IF NOT EXISTS test_session_id UUID REFERENCES test_execution_sessions(session_id),
ADD COLUMN IF NOT EXISTS test_triggered BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS test_results_summary JSONB;

-- Extend existing validation_sessions table with test execution link
ALTER TABLE validation_sessions 
ADD COLUMN IF NOT EXISTS test_session_id UUID REFERENCES test_execution_sessions(session_id),
ADD COLUMN IF NOT EXISTS test_status VARCHAR(20),
ADD COLUMN IF NOT EXISTS test_completion_time TIMESTAMP;

-- =====================================================
-- AUTO-FIX TESTING INTEGRATION
-- =====================================================

-- Track auto-fix testing results
CREATE TABLE IF NOT EXISTS autofix_test_results (
    autofix_test_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_session_id UUID REFERENCES test_execution_sessions(session_id),
    issue_id VARCHAR(255),           -- Links to DatabaseIssue.issue_id
    issue_type VARCHAR(50),          -- MISSING_TABLE, MISSING_COLUMN, etc.
    table_name VARCHAR(255),
    pre_fix_test_status VARCHAR(20), -- 'passed', 'failed', 'error'
    fix_applied BOOLEAN DEFAULT FALSE,
    fix_success BOOLEAN DEFAULT FALSE,
    post_fix_test_status VARCHAR(20), -- 'passed', 'failed', 'error'
    test_improvement BOOLEAN DEFAULT FALSE, -- Did the fix improve test results?
    rollback_required BOOLEAN DEFAULT FALSE,
    rollback_executed BOOLEAN DEFAULT FALSE,
    test_details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- PERFORMANCE AND MONITORING METRICS
-- =====================================================

-- Test performance benchmarks
CREATE TABLE IF NOT EXISTS test_performance_metrics (
    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES test_execution_sessions(session_id) ON DELETE CASCADE,
    test_name VARCHAR(200),
    metric_type VARCHAR(50),         -- 'response_time', 'memory_usage', 'cpu_usage', 'throughput'
    metric_value DECIMAL(12,4),
    metric_unit VARCHAR(20),         -- 'ms', 'mb', 'percent', 'requests_per_second'
    threshold_value DECIMAL(12,4),
    threshold_status VARCHAR(20),    -- 'within_threshold', 'warning', 'critical'
    environment_context JSONB,      -- System state during test
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Test execution sessions indexes
CREATE INDEX IF NOT EXISTS idx_test_execution_sessions_type 
ON test_execution_sessions(test_type);

CREATE INDEX IF NOT EXISTS idx_test_execution_sessions_status 
ON test_execution_sessions(status);

CREATE INDEX IF NOT EXISTS idx_test_execution_sessions_started_at 
ON test_execution_sessions(started_at DESC);

CREATE INDEX IF NOT EXISTS idx_test_execution_sessions_environment 
ON test_execution_sessions(environment);

-- Test case results indexes
CREATE INDEX IF NOT EXISTS idx_test_case_results_session_id 
ON test_case_results(session_id);

CREATE INDEX IF NOT EXISTS idx_test_case_results_status 
ON test_case_results(status);

CREATE INDEX IF NOT EXISTS idx_test_case_results_category 
ON test_case_results(test_category);

CREATE INDEX IF NOT EXISTS idx_test_case_results_name 
ON test_case_results(test_name);

-- Test coverage indexes
CREATE INDEX IF NOT EXISTS idx_test_coverage_session_id 
ON test_coverage_reports(session_id);

CREATE INDEX IF NOT EXISTS idx_test_coverage_file_path 
ON test_coverage_reports(file_path);

-- Performance metrics indexes
CREATE INDEX IF NOT EXISTS idx_test_performance_session_id 
ON test_performance_metrics(session_id);

CREATE INDEX IF NOT EXISTS idx_test_performance_metric_type 
ON test_performance_metrics(metric_type);

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Verify all tables were created successfully
SELECT 
    'test_execution_sessions' as table_name,
    EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'test_execution_sessions') as exists
UNION ALL
SELECT 
    'test_case_results' as table_name,
    EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'test_case_results') as exists
UNION ALL
SELECT 
    'test_coverage_reports' as table_name,
    EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'test_coverage_reports') as exists
UNION ALL
SELECT 
    'autofix_test_results' as table_name,
    EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'autofix_test_results') as exists
UNION ALL
SELECT 
    'test_performance_metrics' as table_name,
    EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'test_performance_metrics') as exists;