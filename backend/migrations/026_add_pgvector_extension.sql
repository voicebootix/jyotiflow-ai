-- Add PostgreSQL vector extension for RAG similarity search
-- This enables vector operations needed for RAG knowledge retrieval

-- Enable the vector extension for similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify the extension is available
SELECT extname FROM pg_extension WHERE extname = 'vector';

-- Update the embedding_vector column to use proper vector type if needed
-- (The column may already exist as FLOAT[] from previous migration)
DO $$
BEGIN
    -- Check if the column exists as FLOAT[] and needs conversion
    IF EXISTS (
        SELECT FROM information_schema.columns 
        WHERE table_name = 'rag_knowledge_base' 
        AND column_name = 'embedding_vector' 
        AND udt_name = 'float8'
    ) THEN
        RAISE NOTICE 'rag_knowledge_base.embedding_vector is already FLOAT[], skipping conversion.';
    ELSIF EXISTS (
        SELECT FROM information_schema.columns 
        WHERE table_name = 'rag_knowledge_base' 
        AND column_name = 'embedding_vector'
    ) THEN
        -- Alter column to vector type
        ALTER TABLE rag_knowledge_base 
        ALTER COLUMN embedding_vector TYPE VECTOR(1536)
        USING (embedding_vector::TEXT::VECTOR(1536));
        RAISE NOTICE 'rag_knowledge_base.embedding_vector converted to VECTOR(1536).';
    ELSE
        RAISE NOTICE 'rag_knowledge_base.embedding_vector column does not exist, skipping conversion.';
    END IF;
END $$;

-- Verify column type is now vector
SELECT column_name, data_type, udt_name 
FROM information_schema.columns
WHERE table_name = 'rag_knowledge_base' AND column_name = 'embedding_vector';

-- Create index for faster similarity search (non-concurrent for transaction compatibility)
CREATE INDEX IF NOT EXISTS idx_rag_knowledge_embedding 
ON rag_knowledge_base USING ivfflat (embedding_vector vector_cosine_ops)
WITH (lists = 100);

-- Create index for category-based filtering  
CREATE INDEX IF NOT EXISTS idx_rag_knowledge_category 
ON rag_knowledge_base (category) WHERE is_active = true;

-- Create index for tag-based search
CREATE INDEX IF NOT EXISTS idx_rag_knowledge_tags 
ON rag_knowledge_base USING GIN (tags) WHERE is_active = true;

-- Verify the setup
SELECT 
    schemaname, 
    tablename, 
    indexname 
FROM pg_indexes 
WHERE tablename = 'rag_knowledge_base'
ORDER BY indexname;
