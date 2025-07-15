# Database Analysis Report
Generated: 2024-12-29

## 🔍 Code Analysis Results

### Tables Referenced in Code:
| Table Name | Status | Found In Files | Issues |
|------------|--------|----------------|---------|
| users | ✅ Exists | auth.py, ai.py, core_foundation.py, auth_helpers.py | Type consistency: id (SERIAL vs INT references) |
| sessions | ✅ Exists | sessions.py, followup.py, ai.py, spiritual.py | Missing columns: user_id (TEXT) vs id (INT) inconsistency |
| service_types | ✅ Exists | services.py, ai.py, startup_database_validator.py | Missing column: credits_required (added via migration) |
| credit_packages | ✅ Exists | admin_products.py, credits.py, safe_database_init.py | No issues |
| donations | ✅ Exists | donations.py, admin_products.py | No issues |
| pricing_config | ✅ Exists | admin_products.py, welcome_credits_utils.py | No issues |
| platform_settings | ✅ Exists | tiktok_service.py, social_media_marketing_router.py | Missing columns: created_at, updated_at (added via migration) |
| ai_recommendations | ✅ Exists | run_ai_migration.py, safe_database_init.py | No issues |
| monetization_experiments | ✅ Exists | run_ai_migration.py, safe_database_init.py | No issues |
| followup_templates | ✅ Exists | followup.py, database_schema_fixes.py | No issues |
| avatar_sessions | ✅ Exists | spiritual_avatar_generation_engine.py, avatar_generation_router.py | No issues |
| rag_knowledge_base | ✅ Exists | enhanced_startup_integration.py, test_knowledge_seeding.py | No issues |
| cache_analytics | ✅ Exists | database_schema_fixes.py | No issues |
| payments | ✅ Exists | admin_overview.py, verify_admin_tables.py | No issues |
| user_purchases | ✅ Exists | init_database.py, safe_database_init.py | No issues |
| user_subscriptions | ❌ Missing | init_database.py | Feature potentially broken |
| session_donations | ✅ Exists | Migration file exists | No issues |
| satsang_events | ❌ Missing | core_foundation.py (schema defined) | Feature broken |
| satsang_attendees | ❌ Missing | core_foundation.py (schema defined) | Feature broken |
| social_content | ❌ Missing | core_foundation.py (schema defined) | Feature broken |
| ai_pricing_recommendations | ✅ Exists | safe_database_init.py | No issues |
| ai_insights_cache | ✅ Exists | safe_database_init.py, test_ai_scheduler.py | No issues |
| service_configuration_cache | ✅ Exists | enhanced_startup_integration.py | No issues |
| birth_chart_cache | ❌ Missing | Referenced in migration script | Feature potentially broken |
| prokerala_tokens | ❌ Missing | Referenced in migration script | Feature potentially broken |
| schema_migrations | ✅ Exists | safe_database_init.py | No issues |

### Type Mismatches:
| Table | Column | Code Type | DB Type | Files | Severity |
|-------|--------|-----------|---------|-------|----------|
| users | id | int/str mixed | SERIAL (INTEGER) | auth.py (str conversion), ai.py (int) | High |
| sessions | user_id | int expected | TEXT | follow_up_service.py, followup.py | High |
| sessions | session_id | str | VARCHAR(255) | sessions.py | Low |
| users | email | EmailStr | VARCHAR(255) | auth.py, core_foundation.py | Low (compatible) |
| service_types | base_credits | int | INTEGER | Consistent | None |
| service_types | credits_required | int | INTEGER (missing, added via migration) | Medium |

### Migration Files Analysis:
| Migration File | Status | Applied | Used in Code | Action |
|---------------|---------|---------|--------------|--------|
| 000_fix_database_constraints.sql | ✅ | Unknown | Yes - Core tables | Keep |
| 001_add_platform_settings_columns.sql | ✅ | Unknown | Yes - platform_settings | Keep |
| 001_fix_service_types_constraints.sql | ✅ | Unknown | Yes - service_types | Keep |
| 002_fix_missing_tables_and_columns.sql | ✅ | Unknown | Yes - Various tables | Keep |
| 003_add_all_feature_tables.sql | ✅ | Unknown | Partial - Some tables missing | Review |
| 004_fix_critical_database_issues.sql | ✅ | Unknown | Yes - Critical fixes | Keep |
| add_enhanced_service_fields.sql | ✅ | Unknown | Yes - service_types | Keep |
| add_followup_tracking_columns.sql | ✅ | Unknown | Yes - sessions table | Keep |
| add_missing_pricing_tables.sql | ✅ | Unknown | Yes - pricing tables | Keep |
| add_pricing_tables.sql | ⚠️ | Unknown | Duplicate of above? | Can be deleted |
| add_prokerala_smart_pricing.sql | ✅ | Unknown | No - prokerala_tokens table not used | Can be deleted |
| add_welcome_credits_config.sql | ✅ | Unknown | Yes - pricing_config | Keep |
| ai_recommendations_table.sql | ✅ | Unknown | Yes - ai_recommendations | Keep |
| donation_transactions_table.sql | ✅ | Unknown | Partial - session_donations | Keep |
| fix_missing_columns.sql | ✅ | Unknown | Yes - Various fixes | Keep |
| followup_system.sql | ✅ | Unknown | Yes - followup tables | Keep |
| session_donations_table.sql | ✅ | Unknown | Yes - session_donations | Keep |

### 🚨 Critical Issues (Broken Features):
1. **Feature: User ID Type Inconsistency**
   - Issue: Mixed usage of integer and string for user IDs
   - Files affected: auth.py, followup.py, follow_up_service.py
   - Impact: Authentication and session tracking errors
   
2. **Feature: Satsang Events**
   - Missing tables: satsang_events, satsang_attendees
   - Files affected: core_foundation.py (models defined but tables missing)
   - Impact: Satsang feature completely broken

3. **Feature: Social Content Management**
   - Missing table: social_content
   - Files affected: core_foundation.py (model defined)
   - Impact: Social media content features broken

4. **Feature: User Subscriptions**
   - Missing table: user_subscriptions
   - Files affected: init_database.py
   - Impact: Subscription management broken

5. **Feature: Birth Chart Caching**
   - Missing tables: birth_chart_cache, prokerala_tokens
   - Files affected: Referenced in migration scripts
   - Impact: Birth chart performance issues

### 🧹 Cleanup Opportunities:
- **Unused columns**: 
  - sessions.instance_id (from auth system)
  - sessions.role (moved to users table)
  - sessions.aud (Supabase specific, not used)
  
- **Duplicate migration files**: 
  - add_pricing_tables.sql (duplicate of add_missing_pricing_tables.sql)
  
- **Unused migration files**: 
  - add_prokerala_smart_pricing.sql (tables not referenced in code)
  
- **Tables in DB but not in code**: 
  - Potentially legacy tables from previous versions

### 📊 Summary:
- Tables in code: 27
- Tables confirmed in DB: 20
- Missing tables: 7
- Type mismatches: 6 (2 critical)
- Migration files: 16
- Unused migrations: 2
- Critical issues: 5
- Features broken: 4+

### 🔧 Recommended Actions:
1. **Immediate**: Fix user ID type consistency (int vs string)
2. **High Priority**: Create missing tables for broken features
3. **Medium Priority**: Fix session user_id column type mismatch
4. **Low Priority**: Clean up unused migrations and columns
5. **Maintenance**: Archive old migration files after verification