# JyotiFlow.ai Complete Database Schema

## Overview
This document provides a complete list of all tables required for full JyotiFlow.ai platform functionality, organized by feature area.

## Core User Management (5 tables)
1. **users** - User accounts and profiles
2. **user_sessions** - Active user sessions
3. **user_analytics** - User behavior tracking
4. **user_purchases** - Purchase history
5. **user_birth_charts** - Detailed astrological charts

## Service Management (4 tables)
6. **service_types** - Available spiritual services
7. **service_usage_logs** - Service usage tracking
8. **service_configuration_cache** ⚠️ - Dynamic service configurations
9. **sessions** - Spiritual guidance sessions

## Payment & Credits (10 tables)
10. **payments** - Payment transactions
11. **credit_packages** - Credit package offerings
12. **credit_transactions** ⚠️ - Credit purchase records
13. **donations** - Donation options
14. **donation_transactions** ⚠️ - Donation records
15. **session_donations** ⚠️ - Session-linked donations
16. **refunds** ⚠️ - Refund tracking
17. **coupons** ⚠️ - Discount codes
18. **user_coupons** ⚠️ - Coupon usage
19. **payment_methods** ⚠️ - Saved payment methods

## Subscription Management (3 tables)
20. **subscription_plans** ⚠️ - Available subscriptions
21. **subscription_history** ⚠️ - Subscription changes
22. **invoices** ⚠️ - Billing invoices

## AI & Spiritual Features (10 tables)
23. **ai_recommendations** - AI-generated recommendations
24. **ai_insights_cache** - Cached AI insights
25. **ai_pricing_recommendations** - Dynamic pricing
26. **rag_knowledge_base** - Knowledge base for RAG
27. **birth_chart_cache** - Cached birth charts
28. **followup_interactions** ⚠️ - Follow-up Q&A
29. **remedy_recommendations** ⚠️ - Spiritual remedies
30. **compatibility_reports** ⚠️ - Relationship compatibility
31. **session_transcripts** ⚠️ - Conversation history
32. **spiritual_goals** ⚠️ - User spiritual goals

## Avatar Generation (3 tables)
33. **avatar_templates** - Avatar style templates
34. **avatar_sessions** - Avatar generation sessions
35. **avatar_generation_queue** - Generation queue

## Live Chat & Video (4 tables)
36. **live_chat_sessions** - Live session management
37. **session_participants** - Session participants
38. **agora_usage_logs** - Agora platform logs
39. **chat_messages** ⚠️ - Chat message history

## Expert Management (5 tables)
40. **spiritual_practitioners** ⚠️ - Expert profiles
41. **practitioner_availability** ⚠️ - Expert schedules
42. **appointments** ⚠️ - Appointment bookings
43. **reviews** ⚠️ - User reviews
44. **practitioner_specializations** ⚠️ - Expert skills

## Marketing & Social Media (7 tables)
45. **marketing_campaigns** - Marketing campaigns
46. **marketing_insights** - Marketing analytics
47. **social_campaigns** - Social media campaigns
48. **social_content** - Social media content
49. **social_posts** - Scheduled posts
50. **referrals** ⚠️ - Referral program
51. **rewards** ⚠️ - Loyalty rewards

## Analytics & Reporting (6 tables)
52. **admin_analytics** - Admin dashboard metrics
53. **performance_analytics** - Performance metrics
54. **revenue_analytics** - Revenue tracking
55. **feature_usage_analytics** - Feature usage
56. **api_usage_metrics** - API usage tracking
57. **monetization_insights** - Revenue insights

## Communication (7 tables)
58. **admin_notifications** - Admin alerts
59. **notification_templates** ⚠️ - Message templates
60. **notification_queue** ⚠️ - Queued notifications
61. **email_logs** ⚠️ - Email tracking
62. **sms_logs** ⚠️ - SMS tracking
63. **webhook_logs** ⚠️ - Webhook events
64. **push_notifications** ⚠️ - Push notifications

## Support & Help (3 tables)
65. **support_tickets** ⚠️ - Customer support
66. **knowledge_articles** ⚠️ - Help articles
67. **feature_requests** ⚠️ - User suggestions

## Configuration & Settings (4 tables)
68. **platform_settings** - Platform configuration
69. **pricing_config** - Pricing configuration
70. **system_configuration** - System settings
71. **feature_flags** - Feature toggles

## Security & Compliance (8 tables)
72. **system_logs** - System event logs
73. **audit_logs** ⚠️ - Security audit trail
74. **rate_limits** ⚠️ - API rate limiting
75. **consent_logs** ⚠️ - Privacy consent
76. **data_exports** ⚠️ - GDPR exports
77. **blocked_users** ⚠️ - User blocking
78. **report_abuse** ⚠️ - Abuse reports
79. **user_devices** ⚠️ - Device tracking

## A/B Testing & Experiments (3 tables)
80. **monetization_experiments** - Pricing experiments
81. **ab_tests** ⚠️ - A/B test configurations
82. **ab_test_participants** ⚠️ - Test participants

## Other (2 tables)
83. **schema_migrations** - Database migrations
84. **third_party_integrations** ⚠️ - External integrations

## Summary
- **Total Tables Required**: 84
- **Existing Tables**: ~41
- **Missing Tables**: ~43 (marked with ⚠️)

## Critical Missing Tables
These tables are essential for core functionality:
1. **service_configuration_cache** - Required for service operations
2. **credit_transactions** - Required for credit purchases
3. **notification_templates** - Required for communications
4. **spiritual_practitioners** - Required for expert consultations
5. **appointments** - Required for booking system

## Implementation Priority
1. **Immediate** - Tables required for current errors
   - service_configuration_cache
   - credit_transactions
   - notification_templates

2. **High Priority** - Core features
   - Payment related tables
   - Communication tables
   - Expert management tables

3. **Medium Priority** - Enhanced features
   - Analytics tables
   - Support tables
   - Compliance tables

4. **Low Priority** - Future features
   - A/B testing tables
   - Advanced analytics
   - Integration logs