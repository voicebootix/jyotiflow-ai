-- Add source_reference column to rag_knowledge_base table
-- This is a critical fix to ensure all knowledge sources are tracked
-- FIX: Removed DO block for simplicity and robustness. The UPDATE will gracefully do nothing if the column doesn't exist.

-- Add the column if it doesn't exist
ALTER TABLE public.rag_knowledge_base
ADD COLUMN IF NOT EXISTS source_reference VARCHAR(255);

-- Enforce the column type is VARCHAR(255) and truncate existing data if necessary
ALTER TABLE public.rag_knowledge_base
ALTER COLUMN source_reference TYPE VARCHAR(255)
USING LEFT(source_reference, 255);

-- Comment to track the change
COMMENT ON COLUMN public.rag_knowledge_base.source_reference IS 'Tracks the original source URL or reference for the knowledge piece. Type changed to VARCHAR(255) per project guidelines.';

-- Note: Backfill logic for copying source_url to source_reference is handled by the migration runner
-- to ensure robustness across different environments and avoid SQL parsing issues.
