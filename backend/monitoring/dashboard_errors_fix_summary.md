# Monitoring Dashboard Errors Fix Summary

## Errors Found in Deployment Logs

1. **Syntax Error**: `Failed to get integration statistics: syntax error at or near ")"`
   - **Cause**: Missing `END` keyword in nested `CASE WHEN` statements
   - **Location**: Lines 387 and 401 in `backend/monitoring/dashboard.py`
   - **Fix**: Added `END` to close the inner `CASE WHEN` statements

2. **JSON Operator Error**: `Failed to calculate overall metrics: operator does not exist: text ->> unknown`
   - **Cause**: Incorrect chaining of JSON operators (`->>'key'->>'nested_key'`)
   - **Location**: Lines 529-530 in `backend/monitoring/dashboard.py`
   - **Fix**: Changed to proper JSON navigation syntax: `(jsonb->'key')->>'nested_key'`

## Root Cause Analysis

The PR #171 attempted to fix these issues but introduced new syntax errors:
- The nested `CASE WHEN` statements were missing the `END` keyword
- The JSON operator fix attempted to chain `->>` operators which is invalid PostgreSQL syntax

## Database Schema Issues

Additionally, the monitoring tables are missing required columns:
- `integration_validations` table needs:
  - `actual_value` (JSONB)
  - `integration_name` (VARCHAR)
- `validation_sessions` table needs:
  - `validation_results` (JSONB)

## Complete Fix

1. **SQL Script to add missing columns**: `backend/monitoring/dashboard_fix.sql`
2. **Code fixes applied**:
   - Fixed missing `END` keywords in CASE statements
   - Fixed JSON operator chaining to use proper syntax

## To Apply the Fix

Run the SQL script on your production database:
```bash
psql $DATABASE_URL -f backend/monitoring/dashboard_fix.sql
```

Then deploy the updated `backend/monitoring/dashboard.py` file.