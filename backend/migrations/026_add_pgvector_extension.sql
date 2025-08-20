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
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'rag_knowledge_base' 
        AND column_name = 'embedding_vector' 
        AND data_type = 'ARRAY'
    ) THEN
        -- Convert FLOAT[] to vector type for better performance
        ALTER TABLE rag_knowledge_base 
        ALTER COLUMN embedding_vector TYPE vector(1536) USING embedding_vector::vector(1536);
        
        RAISE NOTICE 'Converted embedding_vector from FLOAT[] to vector(1536)';
    ELSIF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'rag_knowledge_base' 
        AND column_name = 'embedding_vector'
    ) THEN
        -- Add the column if it doesn't exist
        ALTER TABLE rag_knowledge_base 
        ADD COLUMN embedding_vector vector(1536);
        
        RAISE NOTICE 'Added embedding_vector column as vector(1536)';
    END IF;
END $$;

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
