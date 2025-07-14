# Content Type Column Fix Summary

## Issue Description
The knowledge seeding system was failing with the error:
```
asyncpg.exceptions.UndefinedColumnError: column "content_type" of relation "rag_knowledge_base" does not exist
```

This error occurred because the `content_type` column was missing from the `rag_knowledge_base` table, but the application code was trying to insert data into it.

## Root Cause
The database schema was inconsistent - some table creation scripts included the `content_type` column while others didn't, and the knowledge seeding system assumed it always existed.

## Fixes Implemented

### 1. Updated Safe Database Initialization (`safe_database_init.py`)
- Added a check in `_fix_column_issues()` method to detect if the `content_type` column exists
- If missing, automatically adds the column with `VARCHAR(50) NOT NULL DEFAULT 'knowledge'`
- Updates existing records with appropriate content_type values based on title and content patterns:
  - `meditation` for meditation-related content
  - `ritual` for ritual-related content
  - `astrology` for astrology-related content
  - `psychology` for psychology-related content
  - `spiritual` for spiritual-related content
  - `knowledge` as default fallback

### 2. Updated Knowledge Seeding System (`knowledge_seeding_system.py`)
- Added column existence check during database validation
- If `content_type` column is missing, automatically adds it before seeding
- Modified insert statements to handle both scenarios:
  - **With content_type column**: Uses the full INSERT statement including content_type
  - **Without content_type column**: Uses fallback INSERT statement excluding content_type
- Applied the same logic to both database pool connections and direct connections
- Used `knowledge_data.get("content_type", "knowledge")` to provide safe fallback values

### 3. Integrated Solution
- The fix is integrated directly into the existing initialization and seeding systems
- No standalone scripts required - the fix is applied automatically during startup
- Self-healing mechanism ensures the system can recover from schema inconsistencies

## Key Changes

### Schema Validation
```python
# Check if content_type column exists
content_type_exists = await conn.fetchval("""
    SELECT EXISTS (
        SELECT FROM information_schema.columns 
        WHERE table_name = 'rag_knowledge_base' 
        AND column_name = 'content_type'
    )
""")

if not content_type_exists:
    await conn.execute("""
        ALTER TABLE rag_knowledge_base 
        ADD COLUMN content_type VARCHAR(50) NOT NULL DEFAULT 'knowledge'
    """)
```

### Adaptive Insert Logic
```python
if content_type_exists:
    # Full insert with content_type
    await conn.execute("""
        INSERT INTO rag_knowledge_base (
            knowledge_domain, content_type, title, content, metadata,
            embedding_vector, tags, source_reference, authority_level,
            cultural_context, created_at, updated_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW(), NOW())
        ...
    """, 
        knowledge_data["knowledge_domain"],
        knowledge_data.get("content_type", "knowledge"),
        # ... other parameters
    )
else:
    # Fallback insert without content_type
    await conn.execute("""
        INSERT INTO rag_knowledge_base (
            knowledge_domain, title, content, metadata,
            embedding_vector, tags, source_reference, authority_level,
            cultural_context, created_at, updated_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), NOW())
        ...
    """, 
        knowledge_data["knowledge_domain"],
        # ... other parameters without content_type
    )
```

## Testing and Verification
- The fix includes schema verification to display current table structure
- Both database pool and direct connection paths are handled
- Safe fallback values are provided for all scenarios
- Error handling ensures the system continues functioning even if column fixes fail

## Deployment Impact
- **Zero downtime**: The fix is applied automatically during startup
- **Backward compatible**: Works with existing tables that don't have the content_type column
- **Forward compatible**: Prepares the database for future content type categorization features
- **Self-healing**: The system automatically detects and fixes missing columns

## Benefits
1. **Immediate fix**: Resolves the current crash during knowledge seeding
2. **Robust handling**: Prevents similar issues in the future
3. **Data categorization**: Enables better content organization and retrieval
4. **Maintainable code**: Clear separation between schema validation and data insertion
5. **Production ready**: Safe deployment without manual intervention required

## Files Modified
- `/workspace/backend/safe_database_init.py` - Added content_type column fix in `_fix_column_issues()` method
- `/workspace/backend/knowledge_seeding_system.py` - Added adaptive insert logic and column validation

## Next Steps
After deployment, the system will:
1. Automatically detect missing content_type columns
2. Add the column with appropriate defaults
3. Categorize existing content based on patterns
4. Resume normal knowledge seeding operations
5. Enable improved content retrieval based on content types

This fix ensures the knowledge seeding system is resilient and can handle database schema variations gracefully.