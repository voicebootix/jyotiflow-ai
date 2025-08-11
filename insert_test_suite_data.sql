-- Insert test data into test_suite_configurations table
-- Using the actual column names you specified: suite_name, legacy_name, generator_method, description, enabled, category, priority, timeout_minutes, created_at, updated_at

INSERT INTO test_suite_configurations (
    suite_name,
    legacy_name,
    generator_method,
    description,
    enabled,
    category,
    priority,
    timeout_minutes,
    created_at,
    updated_at
) VALUES
-- Core Platform Tests
('database_health', 'Database Health Check', 'generate_database_health_tests', 'Comprehensive database connectivity and schema validation tests', true, 'database', 'critical', 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('api_endpoints', 'API Endpoints Test', 'generate_api_endpoint_tests', 'Test all API endpoints for functionality and response validation', true, 'api', 'critical', 3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('security_validation', 'Security Validation', 'generate_security_tests', 'Security checks including authentication, authorization, and data protection', true, 'security', 'critical', 3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- Revenue Critical Tests  
('payment_processing', 'Payment Processing', 'generate_payment_tests', 'Test payment gateway integration and transaction processing', true, 'payment', 'critical', 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('spiritual_services', 'Spiritual Services', 'generate_spiritual_tests', 'Test core spiritual guidance and birth chart services', true, 'spiritual', 'critical', 4, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- User Experience Tests
('user_management', 'User Management', 'generate_user_management_tests', 'Test user registration, authentication, and profile management', true, 'user_mgmt', 'high', 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('notifications', 'Notification System', 'generate_notification_tests', 'Test email, SMS, and push notification delivery', true, 'notifications', 'medium', 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)

ON CONFLICT (suite_name) DO UPDATE SET
    legacy_name = EXCLUDED.legacy_name,
    generator_method = EXCLUDED.generator_method,
    description = EXCLUDED.description,
    enabled = EXCLUDED.enabled,
    category = EXCLUDED.category,
    priority = EXCLUDED.priority,
    timeout_minutes = EXCLUDED.timeout_minutes,
    updated_at = CURRENT_TIMESTAMP;
