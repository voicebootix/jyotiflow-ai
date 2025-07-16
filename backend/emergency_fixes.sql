-- Emergency Database Fixes for JyotiFlow
-- Based on actual error logs from 2025-07-16

-- Fix 1: Add missing recommendation_data column
ALTER TABLE sessions 
ADD COLUMN IF NOT EXISTS recommendation_data JSONB DEFAULT '{}';

-- Fix 2: Handle service_type_id references
-- Option A: Add computed column for backward compatibility
ALTER TABLE sessions 
ADD COLUMN IF NOT EXISTS service_type_id INTEGER 
GENERATED ALWAYS AS (
    CASE 
        WHEN service_type ~ '^\d+$' THEN service_type::INTEGER
        ELSE NULL
    END
) STORED;

-- Option B: Or rename the column if that's the intent
-- ALTER TABLE sessions RENAME COLUMN service_type TO service_type_id;

-- Fix 3: Add missing package_name to credit_packages
ALTER TABLE credit_packages 
ADD COLUMN IF NOT EXISTS package_name VARCHAR(255);

-- Update package_name from existing data if possible
UPDATE credit_packages 
SET package_name = COALESCE(
    name, 
    title, 
    CONCAT('Package ', credits, ' credits')
) 
WHERE package_name IS NULL;

-- Fix 4: Ensure ai_recommendations table has required columns
ALTER TABLE ai_recommendations 
ADD COLUMN IF NOT EXISTS service_type_id INTEGER,
ADD COLUMN IF NOT EXISTS recommendation_data JSONB DEFAULT '{}';

-- Fix 5: Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_service_type ON sessions(service_type);
CREATE INDEX IF NOT EXISTS idx_credit_packages_user_id ON credit_packages(user_id);

-- Verify fixes
SELECT 
    'sessions' as table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_name = 'sessions'
AND column_name IN ('recommendation_data', 'service_type', 'service_type_id')

UNION ALL

SELECT 
    'credit_packages' as table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_name = 'credit_packages'
AND column_name = 'package_name';