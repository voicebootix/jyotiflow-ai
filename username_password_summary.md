# Username and Password Summary

## Admin Credentials

### Primary Admin Account
- **Username/Email**: `admin@jyotiflow.ai`
- **Password**: `Jyoti@2024!` (Most recent/secure password from `safe_database_init.py`)
- **Alternative Password**: `admin123` (Legacy password found in multiple files)
- **Role**: admin
- **Credits**: 1000
- **Status**: Active

### Database Admin User
- **Username**: `jyotiflow_db_user`
- **Password**: `em0MmaZmvPzASryvzLHpR5g5rRZTQqpw`
- **Database**: `jyotiflow_db`
- **Host**: `dpg-d12ohqemcj7s73fjbqtg-a`
- **Usage**: PostgreSQL database connection

## Regular User Credentials

### Test User Account
- **Username/Email**: `user@jyotiflow.ai`
- **Password**: `user123`
- **Role**: user
- **Status**: Test account

## System User (Linux)
- **Username**: `ubuntu`
- **Environment Variable**: `$USER=ubuntu`

## Alternative Admin Passwords Found
- `admin123` - Legacy password found in multiple authentication files
- `StrongPass@123` - Found in some social media automation files
- `Jyoti@2024!` - Current secure password (recommended)

## Key Files Where Credentials Are Defined
- `backend/safe_database_init.py` - Main admin user creation with `Jyoti@2024!`
- `backend/surgical_admin_auth_fix.py` - Admin user with `admin123`
- `backend/fix_authentication_issues.py` - Test user credentials
- `run_followup_migration.py` - Database connection string

## Notes
- The system appears to have multiple password configurations, with `Jyoti@2024!` being the most recent and secure admin password
- Database username `jyotiflow_db_user` is used for PostgreSQL connections
- Test accounts are configured for development/testing purposes
- Some files reference legacy passwords that may no longer be active