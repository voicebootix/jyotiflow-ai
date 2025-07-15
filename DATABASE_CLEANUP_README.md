# 🗄️ JyotiFlow Database Cleanup System

## Overview
This comprehensive database analysis and cleanup system helps identify and fix all database issues in the JyotiFlow project, including:
- Type mismatches between code and database
- Missing tables and columns
- Unused migrations and tables
- Data integrity issues

## 🚀 Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Set Database URL
```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/yourdb"
```

### 3. Run Full Analysis & Cleanup
```bash
npm run db:full-cleanup
```

## 📚 Available Commands

### Analysis Commands
- `npm run db:analyze` - Comprehensive database analysis
- `npm run db:check-type <table> <column>` - Check specific column type
- `npm run db:clean-migrations` - Analyze migration files
- `npm run db:test-connection` - Test database connection

### Fix Commands
- `npm run db:fix` - Apply all automatic fixes
- `npm run db:full-cleanup` - Complete analysis and fix

### Backup Commands
- `npm run db:backup` - Create timestamped backup

## 📋 Files Created

### 1. `database-analysis-report.md`
Comprehensive report showing:
- All tables referenced in code vs existing in database
- Type mismatches
- Missing columns
- Broken features
- Cleanup opportunities

### 2. `.cursorrules`
Database schema rules for the project:
- Correct data types for each column
- Known issues and fixes
- Migration guidelines
- Common mistakes to avoid

### 3. Scripts Directory
- `analyze-database.js` - Main analysis script
- `fix-database.js` - Automatic fix script
- `check-column-type.js` - Type checker utility
- `migration-analyzer.js` - Migration file analyzer

## 🔧 Common Issues & Fixes

### 1. User ID Type Mismatch
**Issue**: `sessions.user_id` is TEXT but should be INTEGER
```sql
ALTER TABLE sessions 
ALTER COLUMN user_id TYPE INTEGER 
USING NULLIF(user_id, '')::INTEGER;
```

### 2. Missing Tables
**Issue**: Tables referenced in code but don't exist
- Run `npm run db:fix` to create all missing tables

### 3. Missing Columns
**Issue**: `service_types.credits_required` often missing
```sql
ALTER TABLE service_types 
ADD COLUMN credits_required INTEGER DEFAULT 5;
```

## 📊 Database Schema Reference

### Core Tables
1. **users** - User accounts
   - id: SERIAL (not UUID!)
   - email: VARCHAR(255)
   - password_hash: VARCHAR(255)
   
2. **sessions** - User sessions
   - id: SERIAL
   - user_id: INTEGER (not TEXT!)
   - session_id: VARCHAR(255)
   
3. **service_types** - Available services
   - id: SERIAL
   - credits_required: INTEGER
   - base_credits: INTEGER

## ⚠️ Important Notes

1. **Always backup before running fixes**
   ```bash
   npm run db:backup
   ```

2. **Type conversions may fail if data is invalid**
   - The fix script creates backup columns first
   - Invalid data is set to NULL during conversion

3. **Foreign key constraints**
   - Added automatically by fix script
   - May fail if referential integrity is broken

4. **Unused columns are backed up**
   - Original table is copied before removing columns
   - Backup tables named: `tablename_backup_YYYY_MM_DD`

## 🐛 Troubleshooting

### Connection Issues
```bash
npm run db:test-connection
```

### Permission Errors
Ensure your database user has permissions:
```sql
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_user;
```

### Type Conversion Failures
Check data validity:
```sql
-- Find invalid integer data
SELECT * FROM sessions 
WHERE user_id IS NOT NULL 
AND user_id !~ '^[0-9]+$';
```

## 📝 Migration Best Practices

1. **Check before creating**
   ```bash
   npm run db:check-type <table> <column>
   ```

2. **Use correct types**
   - IDs: SERIAL (not UUID)
   - Strings: VARCHAR(255)
   - Long text: TEXT
   - JSON: JSONB

3. **Archive unused migrations**
   ```bash
   npm run db:clean-migrations
   ```

## 🔍 Manual Verification

After running fixes, verify:

1. **Check critical tables**
   ```sql
   SELECT COUNT(*) FROM users;
   SELECT COUNT(*) FROM sessions;
   SELECT COUNT(*) FROM service_types;
   ```

2. **Verify type fixes**
   ```sql
   SELECT column_name, data_type 
   FROM information_schema.columns 
   WHERE table_name = 'sessions' 
   AND column_name = 'user_id';
   ```

3. **Test application**
   - Login/logout
   - Create sessions
   - Use services

## 📞 Support

If you encounter issues:
1. Check the generated report: `database-analysis-report.md`
2. Review `.cursorrules` for schema guidelines
3. Run individual fix commands instead of full cleanup
4. Create manual migrations if automatic fixes fail