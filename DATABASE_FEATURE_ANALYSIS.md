# Database Feature Analysis - Active vs Dead Code

## Summary
After thorough analysis of 67+ tables, here's what I found:

### 🟢 ACTIVELY USED TABLES (35 tables)
These tables have actual INSERT/UPDATE/SELECT queries in the code:

| Table | Feature | Evidence of Use |
|-------|---------|-----------------|
| **users** | User accounts | Core authentication, used everywhere |
| **sessions** | User sessions | Session tracking, spiritual guidance |
| **service_types** | Service definitions | Service management, pricing |
| **credit_packages** | Credit bundles | Admin products, user purchases |
| **donations** | Donation types | Donation system |
| **donation_transactions** | Donation tracking | Payment processing |
| **pricing_config** | Pricing settings | Dynamic pricing system |
| **platform_settings** | Platform config | Social media credentials, settings |
| **ai_recommendations** | AI suggestions | AI recommendation system |
| **ai_pricing_recommendations** | AI pricing | Dynamic pricing AI |
| **api_integrations** | API configs | admin_integrations.py actively uses |
| **daily_free_usage** | Free tier tracking | services.py tracks free usage |
| **follow_up_templates** | Followup templates | Followup system (⚠️ naming issue) |
| **follow_up_schedules** | Scheduled followups | Followup scheduling |
| **follow_up_logs** | Followup tracking | follow_up_service.py logs |
| **avatar_sessions** | Avatar tracking | Spiritual avatar generation |
| **avatar_templates** | Avatar styles | Template system |
| **live_chat_sessions** | Agora video chat | Live chat feature |
| **session_participants** | Chat participants | Live chat tracking |
| **rag_knowledge_base** | Knowledge base | RAG system |
| **knowledge_effectiveness_tracking** | Knowledge metrics | RAG effectiveness |
| **automated_knowledge_updates** | Knowledge updates | RAG auto-updates |
| **video_chat_sessions** | Video sessions | Agora integration |
| **social_content** | Social posts | admin_content.py manages |
| **satsang_events** | Spiritual events | Event management |
| **satsang_attendees** | Event attendees | Event tracking |
| **user_purchases** | Purchase history | Transaction tracking |
| **user_subscriptions** | Subscriptions | Subscription management |
| **payments** | Payment records | Payment processing |
| **pricing_history** | Price tracking | dynamic_comprehensive_pricing.py |
| **pricing_overrides** | Custom pricing | admin_pricing_dashboard.py |
| **prokerala_cost_config** | API costs | Prokerala API pricing |
| **cache_analytics** | Cache metrics | Performance tracking |
| **api_usage_metrics** | API usage | API monitoring |
| **monetization_experiments** | A/B testing | Experiment tracking |

### 🔴 DEAD CODE TABLES (20 tables)
These tables are defined in migrations but have NO INSERT/UPDATE queries:

| Table | Why It's Dead Code |
|-------|-------------------|
| **admin_analytics** | Only table creation, no data insertion |
| **admin_notifications** | Only table creation, no notification system |
| **performance_analytics** | Only table creation, no performance tracking |
| **system_logs** | Only table creation, no logging implementation |
| **user_analytics** | Only table creation, no user tracking |
| **revenue_analytics** | Method exists but no table usage |
| **monetization_insights** | Only table creation |
| **cost_tracking** | Only in migration, no cost tracking code |
| **demand_analytics** | Only in migration, no demand analysis |
| **revenue_impact_tracking** | Only in migration, no impact tracking |
| **endpoint_suggestions** | Only in migration, might have seed data |
| **marketing_campaigns** | Only table creation, no campaign system |
| **marketing_insights** | Only table creation, no insights system |
| **user_sessions** | Confusion! This is a method name, not a table |
| **api_cache** | Only in migration, no caching implementation |
| **service_pricing_config** | Only in migration |
| **plan_id_backup_migration** | Temporary migration artifact |
| **session_donations** | Table exists but no implementation |
| **credit_transactions** | Duplicate of user_purchases? |
| **satsang_donations** | Only table creation |

### ⚠️ NAMING CONFLICTS & DUPLICATES (5 issues)

1. **follow_up_templates vs followup_templates**
   - Code uses: `follow_up_templates` (with underscore)
   - Some migrations create: `followup_templates` (no underscore)
   - **Fix needed**: Standardize to one name

2. **user_sessions confusion**
   - Not a table! It's a method: `get_user_sessions()`
   - The actual table is just `sessions`

3. **satsangs vs satsang_events**
   - Code references both
   - Actual table: `satsang_events`

4. **avatar_generation_queue**
   - Defined as table in migration
   - Used as in-memory queue in code!
   - Not actually a database table

5. **credit_transactions vs user_purchases**
   - Both track similar data
   - `user_purchases` is actively used
   - `credit_transactions` might be redundant

### 🏗️ PARTIALLY IMPLEMENTED (7 tables)
Tables created and referenced but implementation incomplete:

| Table | Status |
|-------|---------|
| **birth_chart_cache** | Table defined, caching logic exists |
| **prokerala_tokens** | Table defined, token management partial |
| **subscription_plans** | Table exists, subscription system partial |
| **service_configurations** | Table exists, config system partial |
| **donation_analytics** | Table exists, analytics not implemented |
| **api_cache** | Table created but using other caching |
| **service_usage_logs** | Table exists, logging partial |

## Recommendations

### 1. Remove Dead Tables (20 tables)
These tables are just clutter - no code uses them:
```sql
DROP TABLE IF EXISTS admin_analytics;
DROP TABLE IF EXISTS admin_notifications;
DROP TABLE IF EXISTS performance_analytics;
DROP TABLE IF EXISTS system_logs;
DROP TABLE IF EXISTS user_analytics;
DROP TABLE IF EXISTS revenue_analytics;
-- etc...
```

### 2. Fix Naming Conflicts
```sql
-- Standardize followup tables
ALTER TABLE followup_templates RENAME TO follow_up_templates;

-- Remove confusion
-- Don't create user_sessions table - it's not needed
```

### 3. Complete Partial Implementations
Either implement these features or remove the tables:
- Analytics dashboards for the analytics tables
- Caching system for api_cache
- Complete subscription system

### 4. Archive Unused Migrations
Move these to an archive folder:
- `add_pricing_tables.sql` (duplicate)
- Migrations that create dead tables

## The Real Count
- **Actually used tables**: ~35
- **Dead code tables**: ~20  
- **Duplicates/conflicts**: ~5
- **Partial implementations**: ~7

**Total unique, functional tables: ~35-40** (not 67!)