# Database Self-Healing Flow: Visual Guide

## High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     TRIGGER POINTS                               │
├─────────────────────────────────────────────────────────────────┤
│ 1. File Save Event    │ 2. Periodic Scan    │ 3. Runtime Error │
│ 4. Manual Trigger     │ 5. Server Startup   │ 6. Git Hook      │
└────────┬──────────────┴────────┬───────────┴──────────┬────────┘
         │                       │                       │
         └───────────────────────┴───────────────────────┘
                                 │
                                 ▼
```

## Detailed Technical Flow

### 1️⃣ Code Analysis Phase

```
File Changed: routes/auth.js
         │
         ▼
┌─────────────────────────────────────────┐
│          AST PARSER                     │
│  - Parse JavaScript/TypeScript          │
│  - Extract all database queries         │
│  - Identify patterns                    │
└─────────────────────────────────────────┘
         │
         ▼
Found Query: "SELECT * FROM sessions WHERE user_id = ${parseInt(userId)}"
         │
         ▼
┌─────────────────────────────────────────┐
│        PATTERN MATCHER                  │
│  - Regex: /user_id.*parseInt/          │
│  - Type: TYPE_MISMATCH                  │
│  - Helper: parseInt()                   │
└─────────────────────────────────────────┘
```

### 2️⃣ Issue Detection Phase

```
┌─────────────────────────────────────────┐
│         ISSUE ANALYZER                  │
├─────────────────────────────────────────┤
│ Issue Type: TYPE_MISMATCH               │
│ Table: sessions                         │
│ Column: user_id                         │
│ Current Type: TEXT (in DB)              │
│ Expected Type: INTEGER (in code)        │
│ File: routes/auth.js                    │
│ Line: 45                                │
│ Helper Function: parseInt()             │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│      SEVERITY CALCULATOR                │
│  - Critical: Causes runtime errors      │
│  - High: Performance impact             │
│  - Medium: Inconsistency                │
│  - Low: Best practice violation         │
└─────────────────────────────────────────┘
```

### 3️⃣ Code Correction Phase

```
Original Code (routes/auth.js:45):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
const session = await db.query(
  `SELECT * FROM sessions WHERE user_id = ${parseInt(userId)}`
);

         │
         ▼
┌─────────────────────────────────────────┐
│         CODE TRANSFORMER                │
├─────────────────────────────────────────┤
│ 1. Create Backup                        │
│    routes/auth.js.backup.1699123456     │
│                                         │
│ 2. Apply AST Transformation             │
│    - Find CallExpression: parseInt      │
│    - Replace with: userId               │
│                                         │
│ 3. Generate New Code                    │
│ 4. Write to File                        │
└─────────────────────────────────────────┘
         │
         ▼

Fixed Code (routes/auth.js:45):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
const session = await db.query(
  `SELECT * FROM sessions WHERE user_id = ${userId}`
);
```

### 4️⃣ Database Schema Correction Phase

```
┌─────────────────────────────────────────┐
│      DATABASE SCHEMA FIXER              │
├─────────────────────────────────────────┤
│ SQLite Limitation:                      │
│ Cannot ALTER COLUMN type directly       │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│         MIGRATION PROCESS               │
├─────────────────────────────────────────┤
│ BEGIN TRANSACTION;                      │
│                                         │
│ -- Step 1: Create new table             │
│ CREATE TABLE sessions_new (             │
│   id TEXT PRIMARY KEY,                  │
│   user_id INTEGER NOT NULL,  ← Fixed!   │
│   token TEXT NOT NULL,                  │
│   created_at INTEGER                    │
│ );                                      │
│                                         │
│ -- Step 2: Copy & convert data          │
│ INSERT INTO sessions_new                │
│ SELECT                                  │
│   id,                                   │
│   CAST(user_id AS INTEGER), ← Convert!  │
│   token,                                │
│   created_at                            │
│ FROM sessions;                          │
│                                         │
│ -- Step 3: Swap tables                  │
│ DROP TABLE sessions;                    │
│ ALTER TABLE sessions_new                │
│   RENAME TO sessions;                   │
│                                         │
│ COMMIT;                                 │
└─────────────────────────────────────────┘
```

### 5️⃣ Verification Phase

```
┌─────────────────────────────────────────┐
│          VERIFICATION                   │
├─────────────────────────────────────────┤
│ 1. Test Query Execution                 │
│    ✓ No parseInt() needed               │
│    ✓ Query runs successfully            │
│                                         │
│ 2. Type Check                           │
│    ✓ user_id is INTEGER in DB          │
│    ✓ userId is number in code          │
│                                         │
│ 3. Data Integrity                       │
│    ✓ All records migrated               │
│    ✓ No data loss                      │
└─────────────────────────────────────────┘
```

## Real Example: Missing Table Creation

```
Error Caught: "no such table: user_preferences"
         │
         ▼
┌─────────────────────────────────────────┐
│      ERROR HANDLER INTERCEPTOR          │
├─────────────────────────────────────────┤
│ Error Type: SQLITE_ERROR                │
│ Message: "no such table: user_preferences"│
│ Query: "SELECT * FROM user_preferences" │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│     MIGRATION FILE SCANNER              │
├─────────────────────────────────────────┤
│ Searching: migrations/*.sql             │
│ Found: 004_user_preferences.sql         │
│                                         │
│ CREATE TABLE IF NOT EXISTS              │
│   user_preferences (                    │
│     user_id INTEGER PRIMARY KEY,        │
│     theme TEXT DEFAULT 'light',         │
│     notifications BOOLEAN DEFAULT 1     │
│   );                                    │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│        AUTO TABLE CREATOR               │
├─────────────────────────────────────────┤
│ 1. Execute CREATE TABLE                 │
│ 2. Log creation                         │
│ 3. Retry original query                 │
│ 4. Success!                             │
└─────────────────────────────────────────┘
```

## Complete System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ADMIN PANEL UI                           │
├─────────────────────────────────────────────────────────────┤
│  Dashboard │ Issues │ History │ Settings │ Manual Fix      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  ORCHESTRATOR SERVICE                       │
├─────────────────────────────────────────────────────────────┤
│  • Coordinates all components                               │
│  • Manages fix queue and priorities                         │
│  • Prevents duplicate fixes                                 │
│  • Handles rollbacks                                        │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ FILE WATCHER    │  │ ERROR HANDLER   │  │ PERIODIC SCANNER│
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ • Chokidar      │  │ • DB Wrapper    │  │ • Cron Job      │
│ • Git Hooks     │  │ • Try/Catch     │  │ • Health Check  │
│ • Save Events   │  │ • Stack Trace   │  │ • Cleanup       │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │                    │                    │
         └────────────────────┴────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    ANALYSIS ENGINE                          │
├─────────────────────────────────────────────────────────────┤
│  AST Parser │ Pattern Matcher │ Schema Analyzer │ AI Helper │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      FIX ENGINE                             │
├─────────────────┬───────────────────┬───────────────────────┤
│ CODE FIXER      │ SCHEMA FIXER      │ DATA MIGRATOR        │
├─────────────────┼───────────────────┼───────────────────────┤
│ • AST Transform │ • Table Creator   │ • Type Converter     │
│ • Regex Replace │ • Column Modifier │ • Data Validator     │
│ • File Backup   │ • Index Builder   │ • Integrity Check    │
└─────────────────┴───────────────────┴───────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    SAFETY LAYER                             │
├─────────────────────────────────────────────────────────────┤
│  Rollback Manager │ Fix History │ Loop Prevention │ Backup │
└─────────────────────────────────────────────────────────────┘
```

## Timing & Performance

```
Average Fix Times:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Code Pattern Fix:        ~50ms per file
AST Transformation:      ~200ms per file
Table Creation:          ~100ms
Schema Migration:        ~500ms-2s (depends on data)
Full Analysis Scan:      ~5-10s (entire codebase)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Triggers:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
File Save:              Instant (debounced 100ms)
Periodic Scan:          Every 5 minutes
Error Detection:        Instant
Manual Trigger:         On-demand
Server Startup:         During initialization
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

This is exactly how the automated database self-healing system works technically!