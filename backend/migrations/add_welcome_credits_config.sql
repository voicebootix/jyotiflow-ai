-- Migration: Add welcome credits configuration
-- This allows dynamic control of welcome credits from admin dashboard

-- Add welcome credits configuration to pricing_config table
INSERT INTO pricing_config (key, value, description, is_active, created_at, updated_at)
VALUES (
    'welcome_credits',
    '20',
    'Number of credits given to new users upon registration',
    true,
    NOW(),
    NOW()
)
ON CONFLICT (key) DO UPDATE SET
    value = EXCLUDED.value,
    description = EXCLUDED.description,
    updated_at = NOW();

-- Add configuration for different user tiers if needed
INSERT INTO pricing_config (key, value, description, is_active, created_at, updated_at)
VALUES 
    ('premium_welcome_credits', '50', 'Welcome credits for premium users', true, NOW(), NOW()),
    ('vip_welcome_credits', '100', 'Welcome credits for VIP users', true, NOW(), NOW())
ON CONFLICT (key) DO UPDATE SET
    value = EXCLUDED.value,
    description = EXCLUDED.description,
    updated_at = NOW();