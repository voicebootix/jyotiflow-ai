# Database Analysis Report
Generated: 2024-12-29

## 🔍 COMPREHENSIVE Code Analysis Results

### Total Tables Found: **57 unique tables defined in SQL files + 62 referenced in Python code**

### Tables Defined in SQL Files (57 total):
| Table Name | Migration File | Status |
|------------|----------------|---------|
| admin_analytics | 003_add_all_feature_tables.sql | Feature table |
| admin_notifications | 003_add_all_feature_tables.sql | Feature table |
| agora_usage_logs | 003_add_all_feature_tables.sql | Live chat feature |
| ai_insights_cache | ai_recommendations_table.sql, safe_database_init.py | AI caching |
| ai_pricing_recommendations | add_pricing_tables.sql, safe_database_init.py | AI pricing |
| ai_recommendations | ai_recommendations_table.sql, safe_database_init.py | AI features |
| api_cache | add_prokerala_smart_pricing.sql | API caching |
| api_usage_metrics | 003_add_all_feature_tables.sql | API tracking |
| avatar_generation_queue | 003_add_all_feature_tables.sql | Avatar feature |
| avatar_sessions | 003_add_all_feature_tables.sql | Avatar tracking |
| avatar_templates | 003_add_all_feature_tables.sql | Avatar templates |
| birth_chart_cache | 003_add_all_feature_tables.sql | Astrology caching |
| cache_analytics | add_prokerala_smart_pricing.sql, database_schema_fixes.py | Cache tracking |
| cost_tracking | add_pricing_tables.sql | Cost management |
| credit_packages | 002_fix_missing_tables_and_columns.sql | Credit system |
| credit_transactions | 002_fix_missing_tables_and_columns.sql | Credit tracking |
| demand_analytics | add_pricing_tables.sql | Demand tracking |
| donation_analytics | donation_transactions_table.sql | Donation tracking |
| donation_transactions | donation_transactions_table.sql | Donation system |
| donations | fix_missing_columns.sql | Donation config |
| endpoint_suggestions | add_prokerala_smart_pricing.sql | API suggestions |
| follow_up_analytics | followup_system.sql | Followup tracking |
| follow_up_schedules | followup_system.sql | Followup scheduling |
| follow_up_settings | followup_system.sql | Followup config |
| follow_up_templates | followup_system.sql, create_followup_templates.sql | Followup templates |
| live_chat_sessions | 003_add_all_feature_tables.sql | Live chat |
| marketing_campaigns | 003_add_all_feature_tables.sql | Marketing |
| marketing_insights | 003_add_all_feature_tables.sql | Marketing analytics |
| monetization_experiments | ai_recommendations_table.sql | A/B testing |
| monetization_insights | 003_add_all_feature_tables.sql | Revenue insights |
| payments | 002_fix_missing_tables_and_columns.sql | Payment tracking |
| performance_analytics | 003_add_all_feature_tables.sql | Performance metrics |
| plan_id_backup_migration | 004_fix_critical_database_issues.sql | Migration backup |
| platform_settings | 000_fix_database_constraints.sql | Platform config |
| pricing_history | add_pricing_tables.sql | Price tracking |
| pricing_overrides | add_pricing_tables.sql | Price overrides |
| pricing_config | safe_database_init.py | Pricing settings |
| prokerala_cost_config | add_prokerala_smart_pricing.sql | API costs |
| rag_knowledge_base | 003_add_all_feature_tables.sql | Knowledge base |
| revenue_analytics | 003_add_all_feature_tables.sql | Revenue tracking |
| revenue_impact_tracking | add_pricing_tables.sql | Revenue impact |
| satsang_attendees | add_missing_pricing_tables.sql | Event attendees |
| satsang_donations | add_missing_pricing_tables.sql | Event donations |
| satsang_events | add_missing_pricing_tables.sql | Events |
| service_configurations | 000_fix_database_constraints.sql | Service config |
| service_pricing_config | add_pricing_tables.sql | Service pricing |
| service_types | 000_fix_database_constraints.sql | Service definitions |
| service_usage_logs | 003_add_all_feature_tables.sql | Service tracking |
| session_donations | session_donations_table.sql | Session donations |
| session_participants | 003_add_all_feature_tables.sql | Session users |
| sessions | 000_fix_database_constraints.sql | User sessions |
| subscription_plans | 004_fix_critical_database_issues.sql | Subscription tiers |
| system_logs | 003_add_all_feature_tables.sql | System logging |
| user_analytics | 003_add_all_feature_tables.sql | User analytics |
| user_purchases | 003_add_all_feature_tables.sql | Purchase history |
| user_sessions | 003_add_all_feature_tables.sql | User session tracking |
| user_subscriptions | 004_fix_critical_database_issues.sql | User subscriptions |
| users | 000_fix_database_constraints.sql | User accounts |

### Additional Tables Referenced in Python Code Only:
| Table Name | Found In | Issue |
|------------|----------|--------|
| api_integrations | Python code | Not defined in SQL |
| automated_knowledge_updates | Python code | Not defined in SQL |
| daily_free_usage | Python code | Not defined in SQL |
| follow_up_logs | Python code | Not defined in SQL |
| knowledge_effectiveness_tracking | Python code | Not defined in SQL |
| permissions | Python code | System table reference |
| satsangs | Python code | Should be satsang_events |
| social_content | core_foundation.py | Model defined, table missing |
| transactions | Python code | Generic reference |
| video_chat_sessions | Python code | Not defined in SQL |

### Type Mismatches:
| Table | Column | Code Type | DB Type | Files | Severity |
|-------|--------|-----------|---------|-------|----------|
| users | id | int/str mixed | SERIAL (INTEGER) | auth.py (str conversion), ai.py (int) | High |
| sessions | user_id | int expected | TEXT | follow_up_service.py, followup.py | High |
| sessions | session_id | str | VARCHAR(255) | sessions.py | Low |
| users | email | EmailStr | VARCHAR(255) | auth.py, core_foundation.py | Low (compatible) |
| service_types | base_credits | int | INTEGER | Consistent | None |
| service_types | credits_required | int | INTEGER (missing, added via migration) | Medium |

### Migration Files Analysis (17 total):
| Migration File | Tables Created | Status | Action |
|----------------|----------------|---------|--------|
| 000_fix_database_constraints.sql | 5 core tables | Critical | Keep |
| 001_add_platform_settings_columns.sql | 0 (alters only) | Platform settings | Keep |
| 001_fix_service_types_constraints.sql | 0 (alters only) | Service fixes | Keep |
| 002_fix_missing_tables_and_columns.sql | 6 tables | Essential tables | Keep |
| 003_add_all_feature_tables.sql | 20 tables | Feature tables | Keep |
| 004_fix_critical_database_issues.sql | 4 tables | Critical fixes | Keep |
| add_enhanced_service_fields.sql | 0 (alters only) | Service enhancements | Keep |
| add_followup_tracking_columns.sql | 0 (alters only) | Followup tracking | Keep |
| add_missing_pricing_tables.sql | 7 tables | Pricing system | Keep |
| add_pricing_tables.sql | 7 tables | ⚠️ Duplicate | Can be deleted |
| add_prokerala_smart_pricing.sql | 4 tables | API features | Review usage |
| add_welcome_credits_config.sql | 0 (inserts only) | Config data | Keep |
| ai_recommendations_table.sql | 3 tables | AI features | Keep |
| donation_transactions_table.sql | 2 tables | Donation system | Keep |
| fix_missing_columns.sql | 5 tables | Column fixes | Keep |
| followup_system.sql | 4 tables | Followup system | Keep |
| session_donations_table.sql | 1 table | Session donations | Keep |

### 🚨 Critical Issues (Broken Features):
1. **Feature: User ID Type Inconsistency**
   - Issue: Mixed usage of integer and string for user IDs
   - Files affected: auth.py, followup.py, follow_up_service.py
   - Impact: Authentication and session tracking errors
   
2. **Feature: Social Content Management**
   - Missing table: social_content
   - Files affected: core_foundation.py (model defined)
   - Impact: Social media content features broken

3. **Feature: API Integrations**
   - Missing table: api_integrations
   - Referenced in Python code
   - Impact: API integration features may be broken

4. **Feature: Knowledge Updates**
   - Missing tables: automated_knowledge_updates, knowledge_effectiveness_tracking
   - Referenced in Python code
   - Impact: Knowledge base automation broken

5. **Feature: Video Chat**
   - Missing table: video_chat_sessions
   - Referenced in Python code
   - Impact: Video chat features broken

### 🧹 Cleanup Opportunities:
- **Duplicate migration files**: 
  - add_pricing_tables.sql (duplicate of add_missing_pricing_tables.sql)
  
- **Unused or questionable tables**:
  - plan_id_backup_migration (temporary migration table)
  - Some tables in add_prokerala_smart_pricing.sql may not be used
  
- **Tables referenced incorrectly**:
  - "satsangs" should be "satsang_events"
  - Generic references to "transactions" table

### 📊 Summary:
- **Tables defined in SQL**: 57 unique tables
- **Tables referenced in Python**: 62+ references (some duplicates/system tables)
- **Tables in both SQL and Python**: ~47 tables
- **Missing tables (in Python but not SQL)**: 10 tables
- **Type mismatches**: 6 (2 critical)
- **Migration files**: 17 files
- **Duplicate migrations**: 1 file
- **Critical issues**: 5 features broken

### 🔧 Recommended Actions:
1. **Immediate**: Fix user ID type consistency (int vs string)
2. **High Priority**: Create missing tables:
   - social_content
   - api_integrations
   - automated_knowledge_updates
   - knowledge_effectiveness_tracking
   - video_chat_sessions
   - daily_free_usage
   - follow_up_logs
3. **Medium Priority**: 
   - Fix session user_id column type mismatch
   - Review and remove duplicate migration file
   - Fix incorrect table references (satsangs → satsang_events)
4. **Low Priority**: 
   - Clean up temporary migration tables
   - Review prokerala tables usage
5. **Maintenance**: Archive old migration files after verification

## 🔍 Complete Table List (All 67+ unique tables found):
1. admin_analytics
2. admin_notifications
3. agora_usage_logs
4. ai_insights_cache
5. ai_pricing_recommendations
6. ai_recommendations
7. api_cache
8. api_integrations (missing)
9. api_usage_metrics
10. automated_knowledge_updates (missing)
11. avatar_generation_queue
12. avatar_sessions
13. avatar_templates
14. birth_chart_cache
15. cache_analytics
16. cost_tracking
17. credit_packages
18. credit_transactions
19. daily_free_usage (missing)
20. demand_analytics
21. donation_analytics
22. donation_transactions
23. donations
24. endpoint_suggestions
25. follow_up_analytics
26. follow_up_logs (missing)
27. follow_up_schedules
28. follow_up_settings
29. follow_up_templates
30. knowledge_effectiveness_tracking (missing)
31. live_chat_sessions
32. marketing_campaigns
33. marketing_insights
34. monetization_experiments
35. monetization_insights
36. payments
37. performance_analytics
38. plan_id_backup_migration
39. platform_settings
40. pricing_config
41. pricing_history
42. pricing_overrides
43. prokerala_cost_config
44. rag_knowledge_base
45. revenue_analytics
46. revenue_impact_tracking
47. satsang_attendees
48. satsang_donations
49. satsang_events
50. service_configurations
51. service_pricing_config
52. service_types
53. service_usage_logs
54. session_donations
55. session_participants
56. sessions
57. social_content (missing)
58. subscription_plans
59. system_logs
60. user_analytics
61. user_purchases
62. user_sessions
63. user_subscriptions
64. users
65. video_chat_sessions (missing)
66. transactions (generic reference)
67. satsangs (incorrect reference)