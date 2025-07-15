# User Table Analysis Report

## Table Name
**`users`** (PostgreSQL table in the public schema)

## Complete Column Structure

Based on analysis of multiple migration files, database initialization scripts, and application code, here is the comprehensive user table schema:

### Core Identity Columns
- `id` - SERIAL PRIMARY KEY (Auto-incrementing user ID)
- `email` - VARCHAR(255) UNIQUE NOT NULL (User's email address, used for login)
- `password_hash` - VARCHAR(255) NOT NULL (Hashed password for authentication)

### Personal Information
- `name` - VARCHAR(255) NOT NULL (User's display name)
- `full_name` - VARCHAR(255) (Complete full name)
- `first_name` - VARCHAR(100) (First name only)
- `last_name` - VARCHAR(100) (Last name only)
- `phone` - VARCHAR(20) (Phone number)

### Birth & Astrology Information
- `birth_date` - DATE (Date of birth)
- `date_of_birth` - DATE (Alternative column name for birth date)
- `birth_time` - TIME (Time of birth for astrology calculations)
- `birth_location` - VARCHAR(255) (Birth location for chart generation)
- `timezone` - VARCHAR(50) DEFAULT 'Asia/Colombo' (User's timezone)

### Birth Chart Caching System
- `birth_chart_data` - JSONB DEFAULT '{}' (Cached birth chart data from Prokerala API)
- `birth_chart_hash` - VARCHAR(64) (SHA256 hash of birth details for cache validation)
- `birth_chart_cached_at` - TIMESTAMP (When the chart was last cached)
- `birth_chart_expires_at` - TIMESTAMP (When the cached chart expires)
- `birth_chart_cache_status` - VARCHAR(50) DEFAULT 'not_cached' (Cache status)
- `has_free_birth_chart` - BOOLEAN DEFAULT false (Whether user has used free chart)

### Credits & Billing
- `credits` - INTEGER DEFAULT 0 (Current credit balance)
- `base_credits` - INTEGER DEFAULT 0 (Base credits assigned)
- `total_spent` - DECIMAL(10,2) DEFAULT 0.00 (Total amount spent by user)

### User Preferences & Settings
- `role` - VARCHAR(50) DEFAULT 'user' (User role: 'user', 'admin', etc.)
- `spiritual_level` - VARCHAR(50) DEFAULT 'beginner' (User's spiritual experience level)
- `preferred_language` - VARCHAR(10) DEFAULT 'en' (Language preference)
- `preferred_avatar_style` - VARCHAR(50) DEFAULT 'traditional' (Avatar appearance preference)
- `voice_preference` - VARCHAR(50) DEFAULT 'compassionate' (Voice style preference)
- `video_quality_preference` - VARCHAR(20) DEFAULT 'high' (Video quality setting)
- `preferences` - JSONB DEFAULT '{}' (Additional user preferences as JSON)

### Session & Usage Tracking
- `avatar_sessions_count` - INTEGER DEFAULT 0 (Number of avatar sessions)
- `total_avatar_minutes` - INTEGER DEFAULT 0 (Total minutes in avatar sessions)
- `total_sessions` - INTEGER DEFAULT 0 (Total sessions across all services)

### Account Status & Verification
- `is_active` - BOOLEAN DEFAULT true (Whether account is active)
- `email_verified` - BOOLEAN DEFAULT false (Email verification status)
- `phone_verified` - BOOLEAN DEFAULT false (Phone verification status)

### Subscription Information
- `subscription_status` - VARCHAR(50) DEFAULT 'free' (Current subscription tier)
- `subscription_expires_at` - TIMESTAMP (When subscription expires)

### Profile & Media
- `profile_picture_url` - VARCHAR(500) (URL to user's profile picture)

### Timestamps
- `created_at` - TIMESTAMP DEFAULT CURRENT_TIMESTAMP (Account creation time)
- `updated_at` - TIMESTAMP DEFAULT CURRENT_TIMESTAMP (Last update time)
- `last_login_at` - TIMESTAMP (Last login timestamp)

## Indexes

The following indexes should be created for optimal performance:

```sql
-- Unique constraint on email
ALTER TABLE users ADD CONSTRAINT users_email_unique UNIQUE (email);

-- Birth chart caching indexes
CREATE INDEX idx_users_birth_chart_hash ON users(birth_chart_hash);
CREATE INDEX idx_users_birth_chart_expires ON users(birth_chart_expires_at);
```

## Key Relationships

The `users` table is referenced by:
- `sessions.user_id` → `users.id`
- `user_purchases.user_id` → `users.id`
- `user_subscriptions.user_id` → `users.id`
- `credit_transactions.user_id` → `users.id`
- `donation_transactions.user_id` → `users.id`
- Various other tables that track user activities

## Notes

1. **Multiple Column Variants**: Some columns have alternative names (e.g., `birth_date` vs `date_of_birth`, `name` vs `full_name`) due to schema evolution
2. **Birth Chart System**: The application has a sophisticated birth chart caching system to avoid repeated API calls to Prokerala
3. **Credit System**: Users have a credit-based system for accessing services
4. **Flexible Preferences**: JSONB columns allow for extensible user preferences
5. **Multi-language Support**: The system supports multiple languages with user preferences
6. **Avatar Integration**: Specialized columns for avatar session tracking and preferences

## Database Type
- **PostgreSQL** (confirmed from connection strings and asyncpg usage)
- **Schema**: public (default PostgreSQL schema)
- **Connection Pool**: Uses asyncpg connection pooling for performance

This analysis is based on examination of migration files, database initialization scripts, router code, and service implementations throughout the codebase.