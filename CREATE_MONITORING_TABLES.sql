-- 🔧 MONITORING SYSTEM DATABASE TABLES
-- Run this SQL script to create all required monitoring tables
-- This fixes the database relation errors in your deployment logs

-- ============================================================================
-- MAIN MONITORING TABLES
-- ============================================================================

-- 1. Validation Sessions (Primary table)
CREATE TABLE IF NOT EXISTS validation_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id INTEGER NOT NULL,
    service_type VARCHAR(100),
    spiritual_question TEXT,
    birth_details JSONB,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    overall_status VARCHAR(50),
    issues_found INTEGER DEFAULT 0,
    auto_fixes_applied INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 2. Integration Validations (Referenced in your error logs)
CREATE TABLE IF NOT EXISTS integration_validations (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    integration_point VARCHAR(100) NOT NULL,
    validation_time TIMESTAMP DEFAULT NOW(),
    status VARCHAR(50),
    response_time_ms INTEGER,
    validation_score NUMERIC(5,2),
    issues JSONB,
    auto_fixed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (session_id) REFERENCES validation_sessions(session_id)
);

-- 3. Business Logic Issues (Referenced in your error logs)
CREATE TABLE IF NOT EXISTS business_logic_issues (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    issue_type VARCHAR(100),
    severity VARCHAR(20),
    description TEXT,
    context JSONB,
    resolved BOOLEAN DEFAULT FALSE,
    resolution_details TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (session_id) REFERENCES validation_sessions(session_id)
);

-- 4. Context Snapshots
CREATE TABLE IF NOT EXISTS context_snapshots (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    integration_point VARCHAR(100),
    snapshot_data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (session_id) REFERENCES validation_sessions(session_id)
);

-- 5. Monitoring API Calls (Referenced in your error logs)
CREATE TABLE IF NOT EXISTS monitoring_api_calls (
    id SERIAL PRIMARY KEY,
    endpoint VARCHAR(500) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER,
    response_time INTEGER,
    user_id INTEGER,
    request_body TEXT,
    error TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- 6. Monitoring Alerts
CREATE TABLE IF NOT EXISTS monitoring_alerts (
    id SERIAL PRIMARY KEY,
    alert_type VARCHAR(100),
    severity VARCHAR(20),
    title VARCHAR(255),
    description TEXT,
    context JSONB,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by INTEGER,
    acknowledged_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 7. System Health Snapshots
CREATE TABLE IF NOT EXISTS system_health_snapshots (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    overall_status VARCHAR(50),
    integration_health JSONB,
    performance_metrics JSONB,
    active_sessions INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- PERFORMANCE INDEXES
-- ============================================================================

-- Index for integration validations (frequently queried)
CREATE INDEX IF NOT EXISTS idx_integration_validations_session_id 
ON integration_validations(session_id);

CREATE INDEX IF NOT EXISTS idx_integration_validations_integration_point 
ON integration_validations(integration_point);

CREATE INDEX IF NOT EXISTS idx_integration_validations_timestamp 
ON integration_validations(validation_time DESC);

-- Index for business logic issues (for recent issues queries)
CREATE INDEX IF NOT EXISTS idx_business_logic_issues_created_at 
ON business_logic_issues(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_business_logic_issues_severity 
ON business_logic_issues(severity);

-- Index for monitoring API calls (for performance tracking)
CREATE INDEX IF NOT EXISTS idx_monitoring_api_calls_timestamp 
ON monitoring_api_calls(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_monitoring_api_calls_endpoint 
ON monitoring_api_calls(endpoint);

-- Index for validation sessions
CREATE INDEX IF NOT EXISTS idx_validation_sessions_user_id 
ON validation_sessions(user_id);

CREATE INDEX IF NOT EXISTS idx_validation_sessions_started_at 
ON validation_sessions(started_at DESC);

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check if all tables were created successfully
SELECT 
    'validation_sessions' as table_name,
    EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'validation_sessions') as exists
UNION ALL
SELECT 
    'integration_validations' as table_name,
    EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'integration_validations') as exists
UNION ALL
SELECT 
    'business_logic_issues' as table_name,
    EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'business_logic_issues') as exists
UNION ALL
SELECT 
    'monitoring_api_calls' as table_name,
    EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'monitoring_api_calls') as exists
UNION ALL
SELECT 
    'monitoring_alerts' as table_name,
    EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'monitoring_alerts') as exists;

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================

-- If you see this, all tables were created successfully!
SELECT '✅ All monitoring system tables created successfully!' as status;