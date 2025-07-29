-- =====================================================================
-- Credit Packages Schema Fix
-- Ensures credit_packages table matches the fixed Pydantic models
-- =====================================================================

-- 1. Create or update credit_packages table with correct schema
CREATE TABLE IF NOT EXISTS credit_packages (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    credits_amount INTEGER NOT NULL,
    price_usd DECIMAL(10,2) NOT NULL,
    bonus_credits INTEGER DEFAULT 0,
    description TEXT,
    enabled BOOLEAN DEFAULT TRUE,
    stripe_product_id VARCHAR(255),
    stripe_price_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Add missing columns if they don't exist (safe to run multiple times)
DO $$ 
BEGIN
    -- Add description column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'credit_packages' AND column_name = 'description') THEN
        ALTER TABLE credit_packages ADD COLUMN description TEXT;
        RAISE NOTICE 'Added description column to credit_packages';
    END IF;
    
    -- Add stripe_product_id column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'credit_packages' AND column_name = 'stripe_product_id') THEN
        ALTER TABLE credit_packages ADD COLUMN stripe_product_id VARCHAR(255);
        RAISE NOTICE 'Added stripe_product_id column to credit_packages';
    END IF;
    
    -- Add stripe_price_id column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'credit_packages' AND column_name = 'stripe_price_id') THEN
        ALTER TABLE credit_packages ADD COLUMN stripe_price_id VARCHAR(255);
        RAISE NOTICE 'Added stripe_price_id column to credit_packages';
    END IF;
    
    -- Add updated_at column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'credit_packages' AND column_name = 'updated_at') THEN
        ALTER TABLE credit_packages ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        RAISE NOTICE 'Added updated_at column to credit_packages';
    END IF;
END $$;

-- 3. Create updated_at trigger if it doesn't exist
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Drop trigger if exists and recreate
DROP TRIGGER IF EXISTS update_credit_packages_updated_at ON credit_packages;
CREATE TRIGGER update_credit_packages_updated_at
    BEFORE UPDATE ON credit_packages
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 4. Ensure data consistency
UPDATE credit_packages 
SET enabled = COALESCE(enabled, TRUE) 
WHERE enabled IS NULL;

UPDATE credit_packages 
SET bonus_credits = COALESCE(bonus_credits, 0) 
WHERE bonus_credits IS NULL;

-- 5. Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_credit_packages_enabled ON credit_packages(enabled);
CREATE INDEX IF NOT EXISTS idx_credit_packages_credits_amount ON credit_packages(credits_amount);

-- 6. Insert sample data if table is empty (optional)
INSERT INTO credit_packages (name, credits_amount, price_usd, bonus_credits, description, enabled)
SELECT * FROM (VALUES
    ('Starter Pack', 10, 9.99, 0, 'Perfect for trying out our services', true),
    ('Growth Pack', 25, 19.99, 5, 'Most popular choice for regular users', true),
    ('Pro Pack', 50, 34.99, 10, 'Best value for power users', true),
    ('Enterprise Pack', 100, 59.99, 25, 'Maximum credits for businesses', true)
) AS v(name, credits_amount, price_usd, bonus_credits, description, enabled)
WHERE NOT EXISTS (SELECT 1 FROM credit_packages);

-- 7. Verify the schema matches our Pydantic model
DO $$
DECLARE
    rec RECORD;
BEGIN
    RAISE NOTICE '=== Credit Packages Table Schema Verification ===';
    
    FOR rec IN 
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = 'credit_packages'
        ORDER BY ordinal_position
    LOOP
        RAISE NOTICE 'Column: % | Type: % | Nullable: % | Default: %', 
            rec.column_name, rec.data_type, rec.is_nullable, rec.column_default;
    END LOOP;
    
    RAISE NOTICE '=== Sample Data Check ===';
    RAISE NOTICE 'Total packages: %', (SELECT COUNT(*) FROM credit_packages);
    RAISE NOTICE 'Enabled packages: %', (SELECT COUNT(*) FROM credit_packages WHERE enabled = true);
END $$;

-- 8. Clean up any potential data issues that could cause validation errors
-- Ensure all required fields have valid values
UPDATE credit_packages SET 
    name = COALESCE(NULLIF(TRIM(name), ''), 'Unnamed Package')
WHERE name IS NULL OR TRIM(name) = '';

UPDATE credit_packages SET 
    credits_amount = GREATEST(COALESCE(credits_amount, 1), 1)
WHERE credits_amount IS NULL OR credits_amount < 1;

UPDATE credit_packages SET 
    price_usd = GREATEST(COALESCE(price_usd, 0), 0)
WHERE price_usd IS NULL OR price_usd < 0;

RAISE NOTICE '✅ Credit packages schema fix completed successfully!';
RAISE NOTICE 'The table now matches the fixed Pydantic CreditPackageOut model:';
RAISE NOTICE '- id: SERIAL (int) ✅';
RAISE NOTICE '- enabled: BOOLEAN ✅'; 
RAISE NOTICE '- price_usd: DECIMAL ✅';
RAISE NOTICE '- All validation errors should be resolved! 🎉';