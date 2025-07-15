# 🗄️ JyotiFlow Database Cleanup System

## Overview
This comprehensive database analysis and cleanup system helps identify and fix all database issues in the JyotiFlow project. After thorough analysis, we found:
- **67 tables defined** in migrations
- **Only 35 tables actually used** (~52%)
- **20 dead code tables** (~30%)
- **7 partially implemented** (~10%)

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
# First, analyze what you have
npm run db:analyze

# Then clean up dead tables (preview)
npm run db:cleanup-dead

# Actually remove dead tables
npm run db:cleanup-dead-confirm

# Fix remaining issues
npm run db:fix
```

## 📚 Available Commands

### Analysis Commands
- `npm run db:analyze` - Comprehensive database analysis
- `npm run db:check-type <table> <column>` - Check specific column type
- `npm run db:clean-migrations` - Analyze migration files
- `npm run db:test-connection` - Test database connection

### Fix Commands
- `npm run db:fix` - Apply all automatic fixes
- `npm run db:cleanup-dead` - Preview dead tables removal
- `npm run db:cleanup-dead-confirm` - Actually remove dead tables
- `npm run db:full-cleanup` - Complete analysis and fix

### Backup Commands
- `npm run db:backup` - Create timestamped backup

## 📋 Key Findings

### 🟢 Actually Used Tables (35)
These tables have real INSERT/UPDATE/SELECT queries:
- Core: users, sessions, service_types
- Credits: credit_packages, pricing_config, user_purchases
- Features: avatar_sessions, live_chat_sessions, social_content
- AI: ai_recommendations, rag_knowledge_base
- Followup: follow_up_templates, follow_up_schedules

### 🔴 Dead Code Tables (20)
These exist but have NO functionality:
- admin_analytics, admin_notifications
- performance_analytics, system_logs, user_analytics
- revenue_analytics, monetization_insights
- cost_tracking, demand_analytics
- marketing_campaigns, marketing_insights
- And more...

### ⚠️ Common Issues Found

1. **Naming Conflicts**
   - `follow_up_templates` vs `followup_templates`
   - `satsangs` vs `satsang_events`
   - `user_sessions` - Not a table! It's a method name

2. **Type Mismatches**
   - `sessions.user_id`: TEXT but code expects INTEGER
   - `users.id`: Mixed INTEGER/STRING usage

3. **Duplicate Features**
   - `avatar_generation_queue`: Defined as table but used as in-memory queue
   - `credit_transactions` vs `user_purchases`: Same functionality

## 🔧 Common Issues & Fixes

### 1. User ID Type Mismatch
**Issue**: `sessions.user_id` is TEXT but should be INTEGER
```sql
ALTER TABLE sessions 
ALTER COLUMN user_id TYPE INTEGER 
USING NULLIF(user_id, '')::INTEGER;
```

### 2. Dead Tables Cleanup
**Issue**: 20 tables with no functionality
```bash
# Preview what will be removed
npm run db:cleanup-dead

# Actually remove them
npm run db:cleanup-dead-confirm
```

### 3. Naming Standardization
**Issue**: Inconsistent table names
```sql
-- Fix followup tables
ALTER TABLE followup_templates RENAME TO follow_up_templates;
```

## 📊 Database Schema Reference

### Actually Used Tables (35)

#### Core Tables
1. **users** - User accounts (SERIAL id, not UUID!)
2. **sessions** - User sessions (user_id should be INTEGER)
3. **service_types** - Service catalog

#### Feature Tables
1. **avatar_sessions** - D-ID avatar tracking
2. **live_chat_sessions** - Agora video chat
3. **social_content** - Social media posts
4. **rag_knowledge_base** - AI knowledge storage

#### Transaction Tables
1. **user_purchases** - Purchase history
2. **payments** - Stripe payments
3. **donation_transactions** - Donation tracking

## ⚠️ Important Notes

1. **Always backup before cleanup**
   ```bash
   npm run db:backup
   ```

2. **Dead tables may have data**
   - The cleanup script shows row counts
   - Review before confirming deletion

3. **Some "missing" tables aren't missing**
   - They were designed but never needed
   - Safe to ignore or remove

## 🐛 Troubleshooting

### "Table not found" errors
Check if it's a dead table:
```bash
npm run db:analyze
# Look for table in "Dead Code Tables" section
```

### Type conversion failures
```bash
# Check specific column type
npm run db:check-type sessions user_id
```

### After cleanup
1. Update code references:
   - Change `satsangs` → `satsang_events`
   - Remove references to dead tables
2. Archive old migrations
3. Test thoroughly

## 📝 Migration Best Practices

1. **Don't create tables "just in case"**
   - Only create what you'll actually use
   - 30% of your tables are unused!

2. **Use consistent naming**
   - Stick to one convention (underscore_case)
   - Avoid creating similar tables

3. **Complete features before moving on**
   - 7 tables are partially implemented
   - Either finish or remove them

## 🔍 Files Created

1. **`database-analysis-report.md`** - Full analysis with active vs dead tables
2. **`DATABASE_FEATURE_ANALYSIS.md`** - Detailed breakdown of each table's usage
3. **`.cursorrules`** - Database schema rules
4. **Scripts**:
   - `analyze-database.js` - Analysis tool
   - `fix-database.js` - Auto-fixer
   - `cleanup-dead-tables.js` - Dead code remover
   - `check-column-type.js` - Type checker
   - `migration-analyzer.js` - Migration analyzer

## 💡 Key Takeaway
**You have 35 working tables, not 67!** The rest is technical debt. Clean it up with:
```bash
npm run db:cleanup-dead-confirm
```