-- Add source_reference column to rag_knowledge_base table
-- This is a critical fix to ensure all knowledge sources are tracked

ALTER TABLE public.rag_knowledge_base
ADD COLUMN IF NOT EXISTS source_reference TEXT;

-- Backfill source_reference from existing source_url column if it exists
DO $$
BEGIN
    IF EXISTS (
        SELECT FROM information_schema.columns 
        WHERE table_name = 'rag_knowledge_base' 
        AND column_name = 'source_url'
    ) THEN
        UPDATE public.rag_knowledge_base
        SET source_reference = source_url
        WHERE source_reference IS NULL AND source_url IS NOT NULL;
    END IF;
END $$;
