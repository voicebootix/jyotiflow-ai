# Example Scenario: Type Mismatch Fix

Let's walk through a real example of how the system automatically fixes a type mismatch issue.

## Initial State

### Database Schema (SQLite)
```sql
-- In database: sessions table
CREATE TABLE sessions (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,      -- ❌ Wrong type! Should be INTEGER
  token TEXT NOT NULL,
  created_at INTEGER
);
```

### Code File (routes/auth.js)
```javascript
// Developer expects user_id to be INTEGER
async function getSession(userId) {
  // Helper function used to convert number to string
  const session = await db.query(
    'SELECT * FROM sessions WHERE user_id = $1',
    [parseInt(userId, 10)]
  );
  return session;
}
```

## Step-by-Step Fix Process

### Step 1: Detection (Triggered by File Save)

When developer saves `routes/auth.js`, the file watcher triggers:

```javascript
// File watcher detects change
chokidar.on('change', 'routes/auth.js', async () => {
  console.log('📁 File changed: routes/auth.js');
  await analyzeFile('routes/auth.js');
});
```

### Step 2: Code Analysis

```javascript
// Parse the file to find database queries
const ast = parser.parse(fileContent);
const queries = [];

traverse(ast, {
  TemplateLiteral(path) {
    // Found: "SELECT * FROM sessions WHERE user_id = ${parseInt(userId)}"
    queries.push({
      query: path.node,
      hasParseInt: true,
      line: 5
    });
  }
});
```

### Step 3: Issue Identification

```javascript
// Pattern matching identifies the issue
const issue = {
  type: 'TYPE_MISMATCH',
  severity: 'CRITICAL',
  table: 'sessions',
  column: 'user_id',
  currentType: 'TEXT',
  expectedType: 'INTEGER',
  file: 'routes/auth.js',
  line: 5,
  helperFunction: 'parseInt'
};
```

### Step 4: Create Backup

```bash
# System creates backup
cp routes/auth.js routes/auth.js.backup.1699123456
```

### Step 5: Fix Code

```javascript
// Remove parseInt() from the code
const fixedCode = originalCode.replace(
  'user_id = ${parseInt(userId)}',
  'user_id = ${userId}'
);

// Write fixed code
fs.writeFileSync('routes/auth.js', fixedCode);
```

**Result in routes/auth.js:**
```javascript
async function getSession(userId) {
  // parseInt() removed automatically!
  const session = await db.query(
    'SELECT * FROM sessions WHERE user_id = $1',
    [userId]
  );
  return session;
}
```

### Step 6: Fix Database Schema

Since SQLite can't ALTER column types, we recreate the table:

```javascript
// Execute migration in transaction
await db.exec(`
  BEGIN TRANSACTION;
  
  -- Create new table with correct type
  CREATE TABLE sessions_new (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,    -- ✅ Fixed type!
    token TEXT NOT NULL,
    created_at INTEGER
  );
  
  -- Copy data with type conversion
  INSERT INTO sessions_new (id, user_id, token, created_at)
  SELECT id, CAST(user_id AS INTEGER), token, created_at
  FROM sessions;
  
  -- Replace old table
  DROP TABLE sessions;
  ALTER TABLE sessions_new RENAME TO sessions;
  
  COMMIT;
`);
```

### Step 7: Verification

```javascript
// Test the fix worked
try {
  const testQuery = await db.query(
    `SELECT * FROM sessions WHERE user_id = ${123}`
  );
  console.log('✅ Fix verified - query works without parseInt()');
} catch (error) {
  console.error('❌ Fix failed, rolling back...');
  // Restore from backup
}
```

### Step 8: Update Fix Log

```javascript
// Record the fix for history
await db.query(`
  INSERT INTO fix_history (timestamp, type, details)
  VALUES (?, ?, ?)
`, [Date.now(), 'TYPE_MISMATCH', JSON.stringify({
  file: 'routes/auth.js',
  table: 'sessions',
  column: 'user_id',
  oldType: 'TEXT',
  newType: 'INTEGER',
  codeFixed: true,
  schemaFixed: true
})]);
```

## Example 2: Missing Table Creation

### Scenario: Code tries to use non-existent table

```javascript
// Developer writes new feature
async function saveUserPreference(userId, theme) {
  // This will fail - table doesn't exist yet!
  await db.query(
    `INSERT INTO user_preferences (user_id, theme) VALUES (?, ?)`,
    [userId, theme]
  );
}
```

### Error Intercepted

```javascript
// Our wrapped db.query catches the error
Error: SQLITE_ERROR: no such table: user_preferences
```

### Automatic Fix Process

```javascript
// 1. Extract table name from error
const tableName = 'user_preferences';

// 2. Search migrations for CREATE TABLE
const migrationContent = fs.readFileSync('migrations/005_preferences.sql');
// Found: CREATE TABLE user_preferences (...)

// 3. Execute the CREATE TABLE
await db.exec(migrationContent);

// 4. Retry the original query
// Now it works!
await db.query(
  `INSERT INTO user_preferences (user_id, theme) VALUES (?, ?)`,
  [userId, theme]
);
```

## How It All Connects

```
Developer writes code → Save file → Watcher triggers → 
AST parses code → Finds issues → Creates backups →
Fixes code automatically → Updates database schema →
Verifies everything works → Logs the fix
```

The entire process happens in **under 2 seconds** for most fixes!

## Key Technical Points

1. **AST Parsing**: We don't use regex on code - we parse it into an Abstract Syntax Tree for accurate modifications

2. **Transactional Safety**: All database changes happen in transactions - if anything fails, we rollback

3. **Backup Everything**: Every file change creates a timestamped backup for easy rollback

4. **Smart Detection**: The system understands context - it knows `parseInt(userId)` in a `user_id` comparison is a type mismatch

5. **Self-Healing**: Once fixed, the system monitors to prevent regression

This is how your database issues get fixed automatically without manual intervention!