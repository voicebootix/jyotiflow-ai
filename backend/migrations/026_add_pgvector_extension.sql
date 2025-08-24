-- Add PostgreSQL vector extension for RAG similarity search
-- This enables vector operations needed for RAG knowledge retrieval

-- Enable the vector extension for similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify the extension is available
SELECT extname FROM pg_extension WHERE extname = 'vector';

-- Alter the embedding_vector column to use proper vector type
-- This statement will only succeed if the column exists
ALTER TABLE IF EXISTS public.rag_knowledge_base 
ALTER COLUMN embedding_vector TYPE vector(1536) 
USING (embedding_vector::vector);

-- Create index for faster similarity search with cosine distance
CREATE INDEX IF NOT EXISTS rag_knowledge_base_embedding_vector_cosine_idx ON public.rag_knowledge_base USING hnsw (embedding_vector vector_cosine_ops);
