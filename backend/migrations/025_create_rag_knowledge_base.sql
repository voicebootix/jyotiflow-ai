-- Create the RAG knowledge base table
-- This is the foundational table for storing all spiritual and astrological wisdom
-- It was missing from the migrations, causing subsequent migrations to fail.

CREATE TABLE IF NOT EXISTS rag_knowledge_base (
    id SERIAL PRIMARY KEY,
    knowledge_domain VARCHAR(100) NOT NULL,
    title TEXT NOT NULL UNIQUE,
    content TEXT NOT NULL,
    content_type VARCHAR(50) DEFAULT 'knowledge',
    metadata JSONB,
    embedding_vector FLOAT[], -- Temporarily create as FLOAT[] which pgvector can convert
    tags TEXT[],
    source_reference TEXT,
    authority_level INTEGER DEFAULT 3,
    cultural_context VARCHAR(100) DEFAULT 'universal',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_rag_knowledge_domain ON rag_knowledge_base (knowledge_domain);
CREATE INDEX IF NOT EXISTS idx_rag_knowledge_tags_gin ON rag_knowledge_base USING GIN (tags);

-- Comment to track creation
COMMENT ON TABLE rag_knowledge_base IS 'Stores vectorized spiritual and astrological knowledge for the RAG system. Created on initial migration.';
