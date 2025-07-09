# 📊 JyotiFlow Database Architecture Guide

## 🚨 CRITICAL: PostgreSQL ONLY Policy

**THIS IS A HARD RULE - NO EXCEPTIONS**

JyotiFlow uses **PostgreSQL ONLY** for all database operations. SQLite is completely deprecated and must never be used in new development or existing code.

---

## 🏗️ Database Architecture Overview

### Production Database
- **Database Engine**: PostgreSQL 15+
- **Hosting**: Supabase (via Render)
- **Connection String**: `postgresql://jyotiflow_db_user:em0MmaZmvPzASryvzLHpR5g5rRZTQqpw@dpg-d12ohqemcj7s73fjbqtg-a/jyotiflow_db`
- **Environment Variable**: `DATABASE_URL`

### Development Database
- **Database Engine**: PostgreSQL (local or remote)
- **Fallback**: Use same production database for development
- **Never Use**: SQLite, aiosqlite, or any file-based database

---

## 🔧 Database Connection Standards

### ✅ CORRECT: PostgreSQL Connection Pattern

```python
import asyncpg
import os

async def get_database_connection():
    """Standard PostgreSQL connection pattern"""
    database_url = os.getenv("DATABASE_URL", "postgresql://jyotiflow_db_user:em0MmaZmvPzASryvzLHpR5g5rRZTQqpw@dpg-d12ohqemcj7s73fjbqtg-a/jyotiflow_db")
    conn = await asyncpg.connect(database_url)
    return conn

# Usage example
async def example_query():
    conn = await get_database_connection()
    try:
        result = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
        return result
    finally:
        await conn.close()
```

### ❌ FORBIDDEN: SQLite Patterns

```python
# NEVER USE THESE PATTERNS
import sqlite3
import aiosqlite

# FORBIDDEN - SQLite connections
conn = sqlite3.connect("any_file.db")
async with aiosqlite.connect("any_file.db") as conn:

# FORBIDDEN - SQLite-specific SQL
datetime('now', '-1 day')
strftime('%Y-%m-%d')
INTEGER PRIMARY KEY AUTOINCREMENT
```

---

## 📝 SQL Syntax Standards

### ✅ CORRECT: PostgreSQL SQL Syntax

```sql
-- Date/Time Functions
NOW()
NOW() - INTERVAL '1 day'
NOW() - INTERVAL '7 days'
EXTRACT(HOUR FROM created_at)
DATE(created_at)

-- Primary Keys
SERIAL PRIMARY KEY
id SERIAL PRIMARY KEY

-- Data Types
VARCHAR(255)
TEXT
TIMESTAMP
TIMESTAMP DEFAULT NOW()
DECIMAL(10,2)
BOOLEAN
JSONB

-- Parameterized Queries
SELECT * FROM users WHERE id = $1
INSERT INTO users (name, email) VALUES ($1, $2)
```

### ❌ FORBIDDEN: SQLite SQL Syntax

```sql
-- NEVER USE THESE
datetime('now', '-1 day')
strftime('%H', created_at)
INTEGER PRIMARY KEY AUTOINCREMENT
TEXT DEFAULT 'value'
REAL
INSERT OR REPLACE INTO
```

---

## 🗂️ Database Schema Standards

### Table Creation Template

```sql
CREATE TABLE IF NOT EXISTS table_name (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}'::jsonb
);
```

### Foreign Key Standards

```sql
-- Always use proper foreign key constraints
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
```

---

## 📋 Database Class Template

### Standard Database Service Class

```python
import asyncpg
import os
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    """Standard database service template"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv(
            "DATABASE_URL", 
            "postgresql://jyotiflow_db_user:em0MmaZmvPzASryvzLHpR5g5rRZTQqpw@dpg-d12ohqemcj7s73fjbqtg-a/jyotiflow_db"
        )
    
    async def get_connection(self):
        """Get database connection"""
        return await asyncpg.connect(self.database_url)
    
    async def execute_query(self, query: str, *args) -> Any:
        """Execute a query and return results"""
        conn = await self.get_connection()
        try:
            result = await conn.fetchrow(query, *args)
            return result
        finally:
            await conn.close()
    
    async def execute_many(self, query: str, *args) -> List[Any]:
        """Execute query and return multiple results"""
        conn = await self.get_connection()
        try:
            results = await conn.fetch(query, *args)
            return results
        finally:
            await conn.close()
    
    async def execute_command(self, query: str, *args) -> None:
        """Execute a command (INSERT, UPDATE, DELETE)"""
        conn = await self.get_connection()
        try:
            await conn.execute(query, *args)
        finally:
            await conn.close()
```

---

## 🚨 Migration Guidelines

### Converting SQLite to PostgreSQL

1. **Import Changes**:
   ```python
   # Replace this
   import sqlite3
   import aiosqlite
   
   # With this
   import asyncpg
   import os
   ```

2. **Constructor Changes**:
   ```python
   # Replace this
   def __init__(self, db_path: str = "backend/jyotiflow.db"):
       self.db_path = db_path
   
   # With this
   def __init__(self, database_url: str = None):
       self.database_url = database_url or os.getenv("DATABASE_URL", "postgresql://...")
   ```

3. **Connection Changes**:
   ```python
   # Replace this
   conn = sqlite3.connect(self.db_path)
   async with aiosqlite.connect(self.db_path) as conn:
   
   # With this
   conn = await asyncpg.connect(self.database_url)
   try:
       # ... operations
   finally:
       await conn.close()
   ```

4. **Query Changes**:
   ```python
   # Replace this
   cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
   result = cursor.fetchone()
   
   # With this
   result = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
   ```

---

## 🔍 Common Anti-Patterns to Avoid

### ❌ Bad: Mixed Database Usage
```python
# DON'T DO THIS
if self.use_sqlite:
    conn = sqlite3.connect(db_path)
else:
    conn = await asyncpg.connect(database_url)
```

### ❌ Bad: Hardcoded Database Paths
```python
# DON'T DO THIS
db_path = "backend/jyotiflow.db"
conn = sqlite3.connect(db_path)
```

### ❌ Bad: SQLite-specific SQL in PostgreSQL
```python
# DON'T DO THIS
query = "SELECT * FROM users WHERE created_at > datetime('now', '-1 day')"
```

### ✅ Good: Consistent PostgreSQL Usage
```python
# DO THIS
database_url = os.getenv("DATABASE_URL", "postgresql://...")
conn = await asyncpg.connect(database_url)
query = "SELECT * FROM users WHERE created_at > NOW() - INTERVAL '1 day'"
```

---

## 📊 Performance Guidelines

### Connection Pooling
```python
import asyncpg

# Use connection pooling for high-performance applications
pool = await asyncpg.create_pool(
    database_url,
    min_size=5,
    max_size=20,
    command_timeout=60
)

async with pool.acquire() as conn:
    result = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
```

### Query Optimization
```sql
-- Use proper indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_created_at ON sessions(created_at);

-- Use efficient queries
SELECT * FROM users WHERE email = $1 LIMIT 1;
SELECT COUNT(*) FROM sessions WHERE user_id = $1;
```

---

## 🧪 Testing Guidelines

### Database Tests
```python
import pytest
import asyncpg
import os

@pytest.fixture
async def db_connection():
    """Test database connection"""
    database_url = os.getenv("TEST_DATABASE_URL", "postgresql://...")
    conn = await asyncpg.connect(database_url)
    yield conn
    await conn.close()

async def test_user_creation(db_connection):
    """Test user creation with PostgreSQL"""
    await db_connection.execute("""
        INSERT INTO users (name, email) VALUES ($1, $2)
    """, "Test User", "test@example.com")
    
    result = await db_connection.fetchrow("""
        SELECT * FROM users WHERE email = $1
    """, "test@example.com")
    
    assert result is not None
    assert result['name'] == "Test User"
```

---

## 🚨 Code Review Checklist

### Before Merging ANY Code:

- [ ] No `import sqlite3` or `import aiosqlite`
- [ ] No SQLite-specific SQL syntax (datetime, strftime, etc.)
- [ ] All queries use PostgreSQL syntax
- [ ] All parameterized queries use $1, $2, etc.
- [ ] All database connections use asyncpg
- [ ] All datetime operations use PostgreSQL functions
- [ ] No hardcoded database paths
- [ ] All database services inherit from standard patterns

### Automated Checks:

Add these to your CI/CD pipeline:
```bash
# Check for SQLite imports
grep -r "import sqlite3" backend/ && exit 1
grep -r "import aiosqlite" backend/ && exit 1

# Check for SQLite syntax
grep -r "datetime('now'" backend/ && exit 1
grep -r "strftime(" backend/ && exit 1
```

---

## 📚 Reference Documentation

### PostgreSQL Documentation
- [PostgreSQL Official Docs](https://www.postgresql.org/docs/)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/)
- [PostgreSQL Data Types](https://www.postgresql.org/docs/current/datatype.html)

### JyotiFlow Database Schema
- Main database: `jyotiflow_db`
- Key tables: `users`, `sessions`, `service_types`, `subscriptions`
- Connection pool: Managed by `main.py`

---

## 🎯 Summary

**REMEMBER**: 
- PostgreSQL ONLY - no exceptions
- Always use asyncpg for database connections
- Use PostgreSQL-specific SQL syntax
- Test all database operations against PostgreSQL
- Never introduce SQLite dependencies

**FOR DEVELOPERS**:
If you see SQLite code anywhere, stop and convert it to PostgreSQL immediately. This is not optional.

**FOR CODE REVIEWERS**:
Reject any PR that contains SQLite code or SQLite-specific syntax.

---

*Last Updated: January 2025*
*Next Review: March 2025*