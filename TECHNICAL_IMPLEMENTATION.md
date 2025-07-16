# Technical Implementation: Database Self-Healing System

## Overview
This document explains the technical mechanisms behind the automated code correction and table creation in the JyotiFlow database self-healing system.

## 1. Code Scanning & Analysis Phase

### Step 1: File Discovery
```javascript
const glob = require('glob');
const files = glob.sync('**/*.{js,ts}', {
  ignore: ['node_modules/**', 'dist/**', 'build/**']
});
```

### Step 2: AST Parsing for Query Detection
```javascript
const parser = require('@babel/parser');
const traverse = require('@babel/traverse').default;

function analyzeFile(filePath) {
  const code = fs.readFileSync(filePath, 'utf8');
  const ast = parser.parse(code, {
    sourceType: 'module',
    plugins: ['jsx', 'typescript']
  });

  const queries = [];
  
  traverse(ast, {
    // Find db.query() calls
    CallExpression(path) {
      if (path.node.callee.property?.name === 'query') {
        const query = extractQueryString(path.node.arguments[0]);
        queries.push({
          query,
          location: path.node.loc,
          node: path.node
        });
      }
    },
    
    // Find template literals with SQL
    TemplateLiteral(path) {
      const query = path.node.quasis.map(q => q.value.raw).join('');
      if (looksLikeSQL(query)) {
        queries.push({
          query,
          location: path.node.loc,
          node: path.node
        });
      }
    }
  });
  
  return queries;
}
```

## 2. Issue Detection Phase

### Type Mismatch Detection
```javascript
function detectTypeMismatches(queries) {
  const issues = [];
  
  queries.forEach(q => {
    // Example: Finding user_id = ${parseInt(userId)}
    const typeConversionPattern = /user_id\s*=\s*\$\{parseInt\((.*?)\)\}/g;
    const matches = q.query.matchAll(typeConversionPattern);
    
    for (const match of matches) {
      issues.push({
        type: 'TYPE_MISMATCH',
        table: 'sessions',
        column: 'user_id',
        currentType: 'TEXT',
        expectedType: 'INTEGER',
        helperFunction: 'parseInt',
        location: q.location,
        file: q.file
      });
    }
  });
  
  return issues;
}
```

### Missing Table/Column Detection
```javascript
async function detectMissingSchema(queries, db) {
  const issues = [];
  
  for (const q of queries) {
    const tables = extractTableNames(q.query);
    
    for (const table of tables) {
      // Check if table exists
      const tableExists = await db.query(
        `SELECT name FROM sqlite_master WHERE type='table' AND name=?`,
        [table]
      );
      
      if (!tableExists.length) {
        issues.push({
          type: 'MISSING_TABLE',
          table,
          query: q.query,
          location: q.location
        });
      }
    }
  }
  
  return issues;
}
```

## 3. Code Correction Phase

### AST-Based Code Transformation
```javascript
const generate = require('@babel/generator').default;

function fixTypeConversion(ast, issue) {
  traverse(ast, {
    CallExpression(path) {
      // Find parseInt(userId) and remove it
      if (path.node.callee.name === 'parseInt' && 
          isUserIdContext(path)) {
        // Replace parseInt(userId) with just userId
        path.replaceWith(path.node.arguments[0]);
      }
    }
  });
  
  return generate(ast).code;
}
```

### Pattern-Based Code Replacement
```javascript
function fixCodePattern(code, issue) {
  const replacements = {
    'TYPE_MISMATCH': {
      // Remove parseInt for user_id comparisons
      pattern: /user_id\s*=\s*\$\{parseInt\((.*?)\)\}/g,
      replacement: 'user_id = ${$1}'
    },
    'STRING_CONVERSION': {
      // Remove toString() for TEXT columns
      pattern: /(\w+)\s*=\s*\$\{(.*?)\.toString\(\)\}/g,
      replacement: '$1 = ${$2}'
    }
  };
  
  const fix = replacements[issue.type];
  if (fix) {
    return code.replace(fix.pattern, fix.replacement);
  }
  
  return code;
}
```

### Safe File Writing with Backup
```javascript
function applyCodeFix(filePath, newCode) {
  // Create backup
  const backupPath = `${filePath}.backup.${Date.now()}`;
  fs.copyFileSync(filePath, backupPath);
  
  try {
    // Write fixed code
    fs.writeFileSync(filePath, newCode, 'utf8');
    
    // Verify syntax without execution
    const { execSync } = require('child_process');
    execSync(`node --check "${filePath}"`);
    
    console.log(`✅ Fixed: ${filePath}`);
  } catch (error) {
    // Rollback on error
    fs.copyFileSync(backupPath, filePath);
    console.error(`❌ Failed to fix ${filePath}, rolled back`);
    throw error;
  }
}
```

## 4. Database Schema Correction Phase

### Schema Analysis
```javascript
async function analyzeCurrentSchema(db) {
  // Get all tables
  const tables = await db.query(
    `SELECT name FROM sqlite_master WHERE type='table'`
  );
  
  const schema = {};
  
  for (const table of tables) {
    // Get column info
    const columns = await db.query(`PRAGMA table_info(${table.name})`);
    
    schema[table.name] = columns.map(col => ({
      name: col.name,
      type: col.type,
      notNull: col.notnull === 1,
      defaultValue: col.dflt_value,
      primaryKey: col.pk === 1
    }));
  }
  
  return schema;
}
```

### Type Mismatch Fixing
```javascript
async function fixColumnType(db, table, column, newType) {
  // SQLite doesn't support direct ALTER COLUMN
  // Must recreate table with correct schema
  
  await db.query('BEGIN TRANSACTION');
  
  try {
    // 1. Create new table with correct schema
    const createSQL = await generateCreateTableSQL(table, column, newType);
    await db.query(createSQL);
    
    // 2. Copy data with type conversion
    await db.query(`
      INSERT INTO ${table}_new 
      SELECT 
        ${column === 'user_id' ? 'CAST(user_id AS INTEGER)' : 'user_id'},
        -- other columns...
      FROM ${table}
    `);
    
    // 3. Drop old table
    await db.query(`DROP TABLE ${table}`);
    
    // 4. Rename new table
    await db.query(`ALTER TABLE ${table}_new RENAME TO ${table}`);
    
    await db.query('COMMIT');
  } catch (error) {
    await db.query('ROLLBACK');
    throw error;
  }
}
```

### Missing Table Creation
```javascript
async function createMissingTable(db, tableName) {
  // Read schema from migrations
  const migrationFiles = glob.sync('migrations/*.sql');
  let createStatement = null;
  
  for (const file of migrationFiles) {
    const content = fs.readFileSync(file, 'utf8');
    const regex = new RegExp(
      `CREATE TABLE (IF NOT EXISTS )?${tableName}\\s*\\([^;]+\\);`,
      'gis'
    );
    const match = content.match(regex);
    
    if (match) {
      createStatement = match[0];
      break;
    }
  }
  
  if (createStatement) {
    await db.query(createStatement);
    console.log(`✅ Created table: ${tableName}`);
  } else {
    // Infer schema from code usage
    const inferredSchema = await inferTableSchema(tableName);
    await db.query(inferredSchema);
  }
}
```

## 5. Integration & Automation

### File Watcher Integration
```javascript
const chokidar = require('chokidar');

function watchForChanges() {
  const watcher = chokidar.watch(['**/*.js', '**/*.ts'], {
    ignored: /node_modules/,
    persistent: true
  });
  
  watcher.on('change', async (path) => {
    console.log(`File changed: ${path}`);
    
    // Analyze only the changed file
    const issues = await analyzeFile(path);
    
    if (issues.length > 0) {
      await fixIssues(issues);
    }
  });
}
```

### Error Handler Integration
```javascript
// Monkey-patch database query method
const originalQuery = db.query;

db.query = async function(...args) {
  try {
    return await originalQuery.apply(this, args);
  } catch (error) {
    // Detect schema-related errors
    if (error.message.includes('no such table')) {
      const tableName = extractTableFromError(error);
      await createMissingTable(db, tableName);
      
      // Retry query
      return await originalQuery.apply(this, args);
    }
    
    if (error.message.includes('datatype mismatch')) {
      await handleDatatypeMismatch(error, args[0]);
      // Fix code that caused the error
      await fixCodeForError(error);
    }
    
    throw error;
  }
};
```

### Periodic Scanner
```javascript
function startPeriodicScan() {
  setInterval(async () => {
    console.log('🔍 Running periodic database health check...');
    
    // 1. Scan all code files
    const allIssues = await scanAllFiles();
    
    // 2. Fix critical issues immediately
    const critical = allIssues.filter(i => i.severity === 'CRITICAL');
    for (const issue of critical) {
      await fixIssue(issue);
    }
    
    // 3. Check for unused tables
    const unusedTables = await findUnusedTables();
    for (const table of unusedTables) {
      if (table.lastUsed < Date.now() - 30 * 24 * 60 * 60 * 1000) {
        await archiveTable(table);
      }
    }
    
  }, 5 * 60 * 1000); // Every 5 minutes
}
```

## 6. Complete Flow Example

Here's what happens when a type mismatch is detected:

1. **Detection**: Code scanner finds `user_id = ${parseInt(userId)}`
2. **Analysis**: System identifies this as a type mismatch (TEXT column, INTEGER comparison)
3. **Code Fix**: 
   - Creates backup: `auth.js.backup.1234567890`
   - Removes `parseInt()`: `user_id = ${userId}`
   - Writes updated file
4. **Database Fix**:
   - Creates new table with INTEGER user_id
   - Migrates data with type conversion
   - Drops old table, renames new
5. **Verification**:
   - Runs test query to ensure fix works
   - Updates fix log
6. **Monitoring**:
   - Watches for any new occurrences
   - Prevents regression

## 7. Safety Mechanisms

### Rollback Capability
```javascript
class FixHistory {
  async recordFix(fix) {
    const record = {
      id: uuidv4(),
      timestamp: Date.now(),
      type: fix.type,
      file: fix.file,
      backupPath: fix.backupPath,
      changes: fix.changes
    };
    
    await db.query(
      'INSERT INTO fix_history (id, data) VALUES (?, ?)',
      [record.id, JSON.stringify(record)]
    );
    
    return record.id;
  }
  
  async rollback(fixId) {
    const fix = await this.getFix(fixId);
    
    // Restore file from backup
    fs.copyFileSync(fix.backupPath, fix.file);
    
    // Reverse database changes if needed
    if (fix.dbChanges) {
      await this.reverseDbChanges(fix.dbChanges);
    }
  }
}
```

### Loop Prevention
```javascript
const recentFixes = new Map();

function shouldApplyFix(issue) {
  const key = `${issue.file}:${issue.line}:${issue.type}`;
  const lastFix = recentFixes.get(key);
  
  if (lastFix && Date.now() - lastFix < 60000) {
    // Skip if fixed in last minute
    return false;
  }
  
  recentFixes.set(key, Date.now());
  return true;
}
```

This is the complete technical implementation of how the self-healing system works!