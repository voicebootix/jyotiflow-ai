-- JyotiFlow Enhancement Migration: Add RAG and Configuration Support
-- This migration enhances existing service_types table without breaking current functionality

-- Add knowledge configuration columns to existing service_types table
ALTER TABLE service_types ADD COLUMN IF NOT EXISTS knowledge_configuration JSONB DEFAULT '{}';
ALTER TABLE service_types ADD COLUMN IF NOT EXISTS specialized_prompts JSONB DEFAULT '{}';
ALTER TABLE service_types ADD COLUMN IF NOT EXISTS response_behavior JSONB DEFAULT '{}';
ALTER TABLE service_types ADD COLUMN IF NOT EXISTS swami_persona_mode VARCHAR(100) DEFAULT 'general';
ALTER TABLE service_types ADD COLUMN IF NOT EXISTS analysis_depth VARCHAR(50) DEFAULT 'standard';
ALTER TABLE service_types ADD COLUMN IF NOT EXISTS cultural_context VARCHAR(100) DEFAULT 'tamil_vedic';
ALTER TABLE service_types ADD COLUMN IF NOT EXISTS automated_learning BOOLEAN DEFAULT true;

-- Create RAG knowledge base tables
CREATE TABLE IF NOT EXISTS rag_knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    knowledge_domain VARCHAR(100) NOT NULL,
    content_type VARCHAR(50) NOT NULL, -- classical_text, case_study, world_knowledge, etc.
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding_vector VECTOR(1536), -- OpenAI embedding dimension
    tags TEXT[] DEFAULT '{}',
    source_reference VARCHAR(500),
    authority_level INTEGER DEFAULT 1, -- 1-5 scale
    cultural_context VARCHAR(100) DEFAULT 'universal',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create index for efficient vector similarity search
CREATE INDEX IF NOT EXISTS idx_rag_knowledge_embedding ON rag_knowledge_base USING ivfflat (embedding_vector vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_rag_knowledge_domain ON rag_knowledge_base(knowledge_domain);
CREATE INDEX IF NOT EXISTS idx_rag_knowledge_type ON rag_knowledge_base(content_type);
CREATE INDEX IF NOT EXISTS idx_rag_knowledge_tags ON rag_knowledge_base USING GIN(tags);

-- Create Swami persona consistency table
CREATE TABLE IF NOT EXISTS swami_persona_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    persona_mode VARCHAR(100) NOT NULL,
    response_type VARCHAR(100) NOT NULL,
    context_hash VARCHAR(64) NOT NULL, -- Hash of similar contexts
    response_template TEXT NOT NULL,
    authority_markers JSONB DEFAULT '{}',
    cultural_elements JSONB DEFAULT '{}',
    speaking_patterns JSONB DEFAULT '{}',
    usage_count INTEGER DEFAULT 0,
    effectiveness_score DECIMAL(3,2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT NOW(),
    last_used TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_persona_mode ON swami_persona_responses(persona_mode);
CREATE INDEX IF NOT EXISTS idx_response_type ON swami_persona_responses(response_type);
CREATE INDEX IF NOT EXISTS idx_context_hash ON swami_persona_responses(context_hash);

-- Create knowledge effectiveness tracking
CREATE TABLE IF NOT EXISTS knowledge_effectiveness_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255),
    knowledge_used JSONB NOT NULL, -- References to knowledge pieces used
    user_feedback INTEGER, -- 1-5 rating
    prediction_accuracy BOOLEAN,
    remedy_effectiveness BOOLEAN,
    user_satisfaction INTEGER, -- 1-5 rating
    follow_up_success BOOLEAN,
    tracked_at TIMESTAMP DEFAULT NOW()
);

-- Create automated knowledge updates log
CREATE TABLE IF NOT EXISTS automated_knowledge_updates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    update_type VARCHAR(100) NOT NULL, -- world_events, user_feedback, research, etc.
    source VARCHAR(200) NOT NULL,
    content_added INTEGER DEFAULT 0,
    content_updated INTEGER DEFAULT 0,
    effectiveness_improvement DECIMAL(5,4) DEFAULT 0.0,
    update_summary TEXT,
    processed_at TIMESTAMP DEFAULT NOW()
);

-- Create service configuration cache for performance
CREATE TABLE IF NOT EXISTS service_configuration_cache (
    service_name VARCHAR(100) PRIMARY KEY,
    configuration JSONB NOT NULL,
    persona_config JSONB NOT NULL,
    knowledge_domains TEXT[] NOT NULL,
    cached_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '1 hour')
);

-- Insert default configurations for existing services (if they don't have them)
UPDATE service_types 
SET 
    knowledge_configuration = '{
        "primary_focus": "general_guidance",
        "knowledge_domains": ["classical_astrology", "basic_remedies", "general_predictions"],
        "analysis_depth": "standard"
    }'::jsonb,
    specialized_prompts = '{
        "system_prompt": "You are Swami Jyotirananthan, a wise Tamil spiritual master providing authentic Vedic guidance",
        "analysis_sections": ["birth_chart_analysis", "current_guidance", "remedial_suggestions"]
    }'::jsonb,
    response_behavior = '{
        "tone": "compassionate_wisdom",
        "authority_level": "experienced_guide",
        "cultural_context": "tamil_spiritual_tradition"
    }'::jsonb
WHERE knowledge_configuration = '{}'::jsonb OR knowledge_configuration IS NULL;

-- Create function to update service configuration cache
CREATE OR REPLACE FUNCTION update_service_config_cache()
RETURNS TRIGGER AS $$
BEGIN
    -- Update cache when service_types is modified
    INSERT INTO service_configuration_cache (
        service_name, configuration, persona_config, knowledge_domains, cached_at, expires_at
    )
    VALUES (
        NEW.name,
        NEW.knowledge_configuration,
        NEW.response_behavior,
        ARRAY(SELECT jsonb_array_elements_text(NEW.knowledge_configuration->'knowledge_domains')),
        NOW(),
        NOW() + INTERVAL '1 hour'
    )
    ON CONFLICT (service_name) 
    DO UPDATE SET
        configuration = NEW.knowledge_configuration,
        persona_config = NEW.response_behavior,
        knowledge_domains = ARRAY(SELECT jsonb_array_elements_text(NEW.knowledge_configuration->'knowledge_domains')),
        cached_at = NOW(),
        expires_at = NOW() + INTERVAL '1 hour';
        
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for automatic cache updates
DROP TRIGGER IF EXISTS trigger_update_service_config_cache ON service_types;
CREATE TRIGGER trigger_update_service_config_cache
    AFTER INSERT OR UPDATE OF knowledge_configuration, response_behavior
    ON service_types
    FOR EACH ROW
    EXECUTE FUNCTION update_service_config_cache();

-- Grant necessary permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON rag_knowledge_base TO jyotiflow_db_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON swami_persona_responses TO jyotiflow_db_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON knowledge_effectiveness_tracking TO jyotiflow_db_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON automated_knowledge_updates TO jyotiflow_db_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON service_configuration_cache TO jyotiflow_db_user;