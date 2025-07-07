-- Add enhanced fields to service_types table for comprehensive reading support
-- Migration: Add enhanced service type fields

ALTER TABLE service_types 
ADD COLUMN IF NOT EXISTS dynamic_pricing_enabled BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS knowledge_domains TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS persona_modes TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS comprehensive_reading_enabled BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS birth_chart_enabled BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS remedies_enabled BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS voice_enabled BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS video_enabled BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS enhanced_features_updated_at TIMESTAMP DEFAULT NOW();

-- Update existing service with ID for comprehensive reading if it exists
UPDATE service_types 
SET 
    comprehensive_reading_enabled = TRUE,
    birth_chart_enabled = TRUE,
    remedies_enabled = TRUE,
    voice_enabled = TRUE,
    video_enabled = TRUE,
    dynamic_pricing_enabled = TRUE,
    knowledge_domains = ARRAY['vedic_astrology', 'tamil_spiritual_literature', 'health_astrology', 'career_astrology', 'relationship_astrology', 'remedial_measures'],
    persona_modes = ARRAY['traditional_guru', 'compassionate_healer'],
    enhanced_features_updated_at = NOW()
WHERE name = 'comprehensive_life_reading_30min' OR display_name LIKE '%Comprehensive%';