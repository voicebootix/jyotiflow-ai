-- Migration: Optimize integration_validations table indexes
-- Purpose: Add performance indexes for monitoring dashboard queries
-- Author: JyotiFlow Team
-- Date: 2024-12-29
-- Follows: .cursor rules - optimize database performance without duplication

-- Create index on status column for filtering
CREATE INDEX IF NOT EXISTS idx_integration_validations_status 
ON integration_validations(status);

-- Create composite index on (status, validation_time DESC) for optimal query performance
-- This supports queries filtering by status and ordering by validation_time
CREATE INDEX IF NOT EXISTS idx_integration_validations_status_time 
ON integration_validations(status, validation_time DESC);

-- Add comment for documentation
COMMENT ON INDEX idx_integration_validations_status IS 'Index for filtering integration validations by status (error, warning, success)';
COMMENT ON INDEX idx_integration_validations_status_time IS 'Composite index for monitoring dashboard queries filtering by status and ordering by validation_time DESC';

-- Example usage optimization:
-- Before: Full table scan on WHERE status IN ('error', 'warning') AND validation_time > NOW() - INTERVAL '1 hour'
-- After: Index scan using idx_integration_validations_status_time for optimal performance