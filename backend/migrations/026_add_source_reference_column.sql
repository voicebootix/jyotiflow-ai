-- Add source_reference column to rag_knowledge_base table
-- This is a critical fix to ensure all knowledge sources are tracked
-- FIX: Removed non-standard DO block and separated commands for robustness

-- Add the column if it doesn't exist
ALTER TABLE public.rag_knowledge_base
ADD COLUMN IF NOT EXISTS source_reference VARCHAR(255);

-- Comment to track the change
COMMENT ON COLUMN public.rag_knowledge_base.source_reference IS 'Tracks the original source URL or reference for the knowledge piece. Type changed to VARCHAR(255) per project guidelines.';

-- Backfill data in a separate, robust block.
-- This checks for the existence of the 'source_url' column before attempting to backfill.
DO $$
BEGIN
    -- Check if the old 'source_url' column exists
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'rag_knowledge_base' AND column_name = 'source_url' AND table_schema = 'public'
    ) THEN
        -- If it exists, update the new 'source_reference' column, truncating if necessary
        EXECUTE '
            UPDATE public.rag_knowledge_base
            SET source_reference = LEFT(source_url, 255)
            WHERE source_reference IS NULL AND source_url IS NOT NULL
        ';
        
        -- Log a notice for any URLs that were truncated
        RAISE NOTICE 'Backfilled data from source_url to source_reference. Any URLs longer than 255 characters were truncated.';
        
    ELSE
        RAISE NOTICE 'Column source_url does not exist, skipping backfill.';
    END IF;
END;
$$;
