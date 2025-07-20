-- Fix for monitoring dashboard errors
-- Add missing columns that the dashboard.py code expects

-- 1. Add actual_value column to integration_validations table
ALTER TABLE integration_validations 
ADD COLUMN IF NOT EXISTS actual_value JSONB;

-- 2. Add integration_name column to integration_validations table
ALTER TABLE integration_validations 
ADD COLUMN IF NOT EXISTS integration_name VARCHAR(100);

-- 3. Add validation_results column to validation_sessions table
ALTER TABLE validation_sessions 
ADD COLUMN IF NOT EXISTS validation_results JSONB;

-- 4. Update integration_name from integration_point if needed
UPDATE integration_validations 
SET integration_name = integration_point 
WHERE integration_name IS NULL;

-- 5. Add some test data to actual_value for existing records
UPDATE integration_validations 
SET actual_value = jsonb_build_object('duration_ms', response_time_ms::text)
WHERE actual_value IS NULL AND response_time_ms IS NOT NULL;

-- Verify the changes
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'integration_validations' 
AND column_name IN ('actual_value', 'integration_name');

SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'validation_sessions' 
AND column_name = 'validation_results';