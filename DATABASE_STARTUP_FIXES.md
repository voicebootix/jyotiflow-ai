# Database Startup Issues - Fixed

## Issues Identified in Logs

Based on the startup logs from JyotiFlow.ai backend, two critical database-related issues were identified and fixed:

### 1. Database Schema Fix Function Signature Error

**Error Message:**
```
⚠️ Database schema fix failed: fix_database_schema() takes 0 positional arguments but 1 was given
```

**Root Cause:**
In `backend/main.py` line 147, the code was calling:
```python
schema_fix_success = await fix_database_schema(db_pool)
```

But the function `fix_database_schema()` in `backend/db_schema_fix.py` takes no arguments.

**Fix Applied:**
```python
# Changed from:
schema_fix_success = await fix_database_schema(db_pool)

# To:
schema_fix_success = await fix_database_schema()
```

### 2. ON CONFLICT Constraint Error

**Error Message:**
```
2025-07-11 05:41:34,669 - init_database - ERROR - Error inserting initial data: there is no unique or exclusion constraint matching the ON CONFLICT specification
```

**Root Cause:**
The `_insert_initial_data()` method in `backend/init_database.py` was using `ON CONFLICT` clauses that didn't match the actual database constraints. This can happen due to:
- Tables not having the expected unique constraints
- Timing issues during table creation
- Constraint names not matching expectations

**Fix Applied:**
Replaced all `ON CONFLICT` clauses with explicit existence checks for safer data insertion:

#### Before (Problematic):
```python
await conn.execute("""
    INSERT INTO service_types (name, description, base_credits, duration_minutes, video_enabled)
    VALUES ($1, $2, $3, $4, $5)
    ON CONFLICT (name) DO NOTHING
""", *service)
```

#### After (Fixed):
```python
# Check if service already exists
existing = await conn.fetchrow(
    "SELECT id FROM service_types WHERE name = $1", service[0]
)
if not existing:
    await conn.execute("""
        INSERT INTO service_types (name, description, base_credits, duration_minutes, video_enabled)
        VALUES ($1, $2, $3, $4, $5)
    """, *service)
```

## Tables Fixed

The following tables had their insert operations updated to use explicit existence checks:

1. **service_types** - Default spiritual guidance services
2. **avatar_templates** - Avatar generation templates  
3. **service_configuration_cache** - Service configuration data
4. **platform_settings** - Platform API credentials and settings
5. **social_content** - Sample social media content

## Benefits of the Fix

1. **More Robust**: Doesn't rely on specific constraint names or timing
2. **Explicit**: Clear about what's being checked before insertion
3. **Safer**: Works even if unique constraints aren't properly created
4. **Debuggable**: Easier to trace what's happening during initialization

## Expected Results

After these fixes, the application should:
- ✅ Start without the function signature error
- ✅ Successfully insert initial data without ON CONFLICT errors
- ✅ Complete database initialization successfully
- ✅ Proceed with enhanced system initialization

## Files Modified

1. `backend/main.py` - Fixed function call signature
2. `backend/init_database.py` - Replaced ON CONFLICT with explicit checks

## Testing Recommendation

To verify the fixes work correctly:

1. **Clean restart**: Test with a fresh database to ensure initialization works
2. **Repeated starts**: Test multiple startups to ensure duplicate insertion is handled correctly
3. **Partial data**: Test with some initial data already present

The fixes maintain the same functionality while being more robust and less prone to constraint-related errors.