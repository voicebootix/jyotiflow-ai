# JyotiFlow.ai Database Fix Guide

## Overview
This guide provides step-by-step instructions to fix all database schema issues and enable full platform functionality.

## Quick Fix (Recommended)

### Option 1: Using the SQL Script Directly

1. **Access your Supabase Database**
   - Go to your Supabase project dashboard
   - Navigate to the SQL Editor

2. **Run the Comprehensive Fix Script**
   - Copy the entire contents of `/workspace/comprehensive_database_fix.sql`
   - Paste it into the SQL editor
   - Click "Run" to execute

3. **Verify the Fix**
   ```sql
   -- Check total number of tables (should be 80+)
   SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';
   
   -- Check if critical tables exist
   SELECT table_name FROM information_schema.tables 
   WHERE table_schema = 'public' 
   AND table_name IN ('service_configuration_cache', 'credit_transactions', 'notification_templates')
   ORDER BY table_name;
   ```

### Option 2: Using the Automatic Python Script

1. **Set Environment Variable**
   ```bash
   export DATABASE_URL="your_supabase_database_url"
   ```

2. **Install Dependencies**
   ```bash
   pip install asyncpg
   ```

3. **Run the Automatic Fixer**
   ```bash
   python /workspace/backend/automatic_database_fixer.py
   ```

## What This Fix Does

### 1. **Creates Missing Tables** (30+ new tables)
   - `service_configuration_cache` - Service configurations
   - `credit_transactions` - Credit purchase tracking
   - `notification_templates` - Email/SMS templates
   - `spiritual_practitioners` - Expert profiles
   - `appointments` - Booking management
   - And many more...

### 2. **Fixes Column Issues**
   - Removes NOT NULL constraint from `service_types.display_name`
   - Ensures `users.last_login_at` column exists
   - Adds missing columns to various tables

### 3. **Creates Indexes**
   - Performance indexes on frequently queried columns
   - Foreign key indexes for join optimization

### 4. **Inserts Essential Data**
   - Default notification templates
   - Subscription plans
   - Service configurations
   - Feature flags

## Verification Steps

After running the fix:

1. **Check Table Count**
   ```sql
   SELECT COUNT(*) as table_count 
   FROM information_schema.tables 
   WHERE table_schema = 'public';
   -- Should return 80+ tables
   ```

2. **Verify Critical Tables**
   ```sql
   SELECT 
     'service_configuration_cache' as table_name,
     EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'service_configuration_cache') as exists
   UNION ALL
   SELECT 
     'credit_transactions',
     EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'credit_transactions')
   UNION ALL
   SELECT 
     'notification_templates',
     EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'notification_templates');
   ```

3. **Check Service Configuration**
   ```sql
   SELECT * FROM service_configuration_cache;
   -- Should have entries for tarot_ai, spiritual_guidance, etc.
   ```

## Troubleshooting

### If the script fails:

1. **Transaction Error**
   - The script runs in a transaction, so if any part fails, nothing is applied
   - Check the error message and fix the specific issue
   - Common issue: Foreign key constraints - ensure users table exists first

2. **Permission Error**
   - Ensure your database user has CREATE TABLE permissions
   - In Supabase, use the service role key for full permissions

3. **Partial Application**
   - If the transaction was not used, some tables might be created
   - Run the verification queries to see what's missing
   - The script uses CREATE TABLE IF NOT EXISTS, so it's safe to run multiple times

## Manual Table Creation

If you prefer to create tables individually, here's the priority order:

1. **Critical Tables** (Create these first)
   ```sql
   -- service_configuration_cache
   CREATE TABLE IF NOT EXISTS service_configuration_cache (
       id SERIAL PRIMARY KEY,
       service_name VARCHAR(255) NOT NULL,
       configuration JSONB DEFAULT '{}',
       -- ... (see full script)
   );
   ```

2. **Transaction Tables**
   - credit_transactions
   - donation_transactions
   - payment related tables

3. **Communication Tables**
   - notification_templates
   - email_logs
   - sms_logs

4. **Feature Tables**
   - Based on which features you want to enable

## Post-Fix Steps

1. **Restart Your Application**
   - The application should now start without database errors

2. **Test Core Features**
   - User registration/login
   - Service selection
   - Credit purchases
   - Session creation

3. **Monitor Logs**
   - Check for any remaining database-related errors
   - The application logs will show if any tables are still missing

## Support

If you encounter issues:

1. Check the `database_fix_report.json` for detailed analysis
2. Review application logs for specific error messages
3. Ensure all environment variables are correctly set
4. Verify database connection string is correct

## Important Notes

- The fix script is idempotent (safe to run multiple times)
- All changes are wrapped in a transaction for safety
- Backup your database before running in production
- The script preserves existing data