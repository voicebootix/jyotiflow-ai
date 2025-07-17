#!/usr/bin/env node

const { Client } = require('pg');
const { execSync } = require('child_process');
const path = require('path');

// Get command line arguments
const [table, column] = process.argv.slice(2);

if (!table || !column) {
  console.log('Usage: node check-column-type.js <table> <column>');
  console.log('Example: node check-column-type.js sessions user_id');
  process.exit(1);
}

const DATABASE_URL = process.env.DATABASE_URL || 'postgresql://user:password@localhost:5432/yourdb';

const client = new Client({
  connectionString: DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
});

async function checkColumnType() {
  try {
    await client.connect();
    
    console.log(`\n🔍 Checking type for ${table}.${column}...\n`);
    
    // Check database type
    const dbResult = await client.query(`
      SELECT 
        column_name,
        data_type,
        character_maximum_length,
        column_default,
        is_nullable,
        udt_name
      FROM information_schema.columns 
      WHERE table_name = $1 AND column_name = $2
    `, [table, column]);
    
    if (dbResult.rows.length === 0) {
      console.log(`❌ Column ${table}.${column} does not exist in database`);
    } else {
      const col = dbResult.rows[0];
      console.log('📊 Database Type:');
      console.log(`   Data Type: ${col.data_type.toUpperCase()}`);
      if (col.character_maximum_length) {
        console.log(`   Max Length: ${col.character_maximum_length}`);
      }
      console.log(`   Nullable: ${col.is_nullable}`);
      console.log(`   Default: ${col.column_default || 'none'}`);
      console.log(`   Full Type: ${col.udt_name}`);
    }
    
    // Search for column usage in code
    console.log('\n📝 Code Usage:');
    
    // Search for type annotations
    try {
      const typeSearch = execSync(
        `grep -r "${column}.*:.*\\(str\\|int\\|bool\\|float\\|Optional\\|VARCHAR\\|INTEGER\\|TEXT\\|BOOLEAN\\)" --include="*.py" backend/ 2>/dev/null | head -10`,
        { encoding: 'utf8' }
      );
      
      if (typeSearch) {
        console.log('\nType annotations found:');
        typeSearch.split('\n').filter(line => line.trim()).forEach(line => {
          const [file, ...content] = line.split(':');
          console.log(`   ${path.basename(file)}: ${content.join(':').trim()}`);
        });
      }
    } catch (e) {
      // Grep returns error if no matches
    }
    
    // Search for SQL queries using this column
    try {
      const sqlSearch = execSync(
        `grep -r "\\(SELECT\\|INSERT\\|UPDATE\\|WHERE\\).*${column}" --include="*.py" backend/ 2>/dev/null | grep -i "${table}\\|FROM.*${column}" | head -10`,
        { encoding: 'utf8' }
      );
      
      if (sqlSearch) {
        console.log('\nSQL queries found:');
        sqlSearch.split('\n').filter(line => line.trim()).forEach(line => {
          const [file, ...content] = line.split(':');
          console.log(`   ${path.basename(file)}: ${content.join(':').trim().substring(0, 80)}...`);
        });
      }
    } catch (e) {
      // Grep returns error if no matches
    }
    
    // Search for model definitions
    try {
      const modelSearch = execSync(
        `grep -r "class.*${table}\\|${column}.*=" --include="*.py" backend/ 2>/dev/null | head -10`,
        { encoding: 'utf8' }
      );
      
      if (modelSearch) {
        console.log('\nModel definitions found:');
        modelSearch.split('\n').filter(line => line.trim()).forEach(line => {
          const [file, ...content] = line.split(':');
          console.log(`   ${path.basename(file)}: ${content.join(':').trim()}`);
        });
      }
    } catch (e) {
      // Grep returns error if no matches
    }
    
    // Common type mismatches in this project
    console.log('\n⚠️  Known Type Issues:');
    const knownIssues = {
      'sessions.user_id': 'Should be INTEGER (not TEXT) to match users.id',
      'users.id': 'Should be SERIAL (auto-incrementing INTEGER), not UUID',
      'service_types.credits_required': 'Often missing, should be INTEGER',
      'sessions.session_id': 'Should be VARCHAR(255) for UUID strings'
    };
    
    const key = `${table}.${column}`;
    if (knownIssues[key]) {
      console.log(`   ⚠️  ${knownIssues[key]}`);
    }
    
    // Suggest fix if type mismatch detected
    if (dbResult.rows.length > 0) {
      const dbType = dbResult.rows[0].data_type.toUpperCase();
      console.log('\n💡 Recommendations:');
      
      if (column === 'user_id' && dbType === 'TEXT') {
        console.log('   1. Convert to INTEGER to match users.id');
        console.log('   2. Run: npm run db:fix');
        console.log('   3. Or manually: ALTER TABLE sessions ALTER COLUMN user_id TYPE INTEGER USING user_id::INTEGER;');
      } else if (column.includes('_id') && dbType !== 'INTEGER' && dbType !== 'UUID') {
        console.log('   1. ID columns should typically be INTEGER or UUID');
        console.log('   2. Check if this references another table\'s primary key');
      } else if (column.includes('email') && dbType !== 'VARCHAR') {
        console.log('   1. Email columns should be VARCHAR(255)');
      } else if (column.includes('_at') && dbType !== 'TIMESTAMP') {
        console.log('   1. Timestamp columns should use TIMESTAMP type');
      }
    }
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  } finally {
    await client.end();
  }
}

checkColumnType();