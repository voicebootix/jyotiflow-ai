-- Migration: Create integration_metrics_24h view
-- Purpose: Centralize duration calculation logic for monitoring dashboard
-- Author: JyotiFlow Team
-- Date: Created for DRY principle compliance

-- Drop view if exists (for idempotent migrations)
DROP VIEW IF EXISTS integration_metrics_24h CASCADE;

-- Create view with centralized duration calculation
CREATE VIEW integration_metrics_24h AS
SELECT 
    session_id,
    integration_name,
    status,
    CASE 
        WHEN actual_value IS NOT NULL AND actual_value->>'duration_ms' IS NOT NULL 
        THEN (actual_value->>'duration_ms')::INTEGER 
        ELSE NULL
    END as duration_ms,
    validation_time
FROM integration_validations
WHERE validation_time > NOW() - INTERVAL '24 hours';

-- Add comment for documentation
COMMENT ON VIEW integration_metrics_24h IS 'Centralized view for integration metrics over the last 24 hours with pre-calculated duration_ms';

-- Example usage:
-- Overall stats: SELECT COUNT(DISTINCT session_id), AVG(duration_ms) FROM integration_metrics_24h;
-- Per integration: SELECT integration_name, AVG(duration_ms) FROM integration_metrics_24h GROUP BY integration_name;