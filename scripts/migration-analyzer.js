#!/usr/bin/env node

const fs = require('fs').promises;
const path = require('path');
const { Client } = require('pg');
const { execSync } = require('child_process');

const DATABASE_URL = process.env.DATABASE_URL || 'postgresql://user:password@localhost:5432/yourdb';

const client = new Client({
  connectionString: DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
});

async function analyzeMigrations() {
  const migrationsDir = path.join(__dirname, '..', 'backend', 'migrations');
  
  try {
    await client.connect();
    console.log('🔍 Analyzing migration files...\n');
    
    // Get all migration files
    const files = await fs.readdir(migrationsDir);
    const sqlFiles = files.filter(f => f.endsWith('.sql'));
    
    console.log(`Found ${sqlFiles.length} migration files\n`);
    
    const migrationAnalysis = [];
    
    for (const file of sqlFiles) {
      const filePath = path.join(migrationsDir, file);
      const content = await fs.readFile(filePath, 'utf8');
      
      const analysis = {
        file,
        status: '✅',
        tables: [],
        columns: [],
        usedInCode: false,
        canBeDeleted: false,
        issues: []
      };
      
      // Extract table names from CREATE TABLE statements
      const createTableMatches = content.match(/CREATE TABLE\s+(?:IF NOT EXISTS\s+)?(\w+)/gi) || [];
      createTableMatches.forEach(match => {
        const tableName = match.replace(/CREATE TABLE\s+(?:IF NOT EXISTS\s+)?/i, '').trim();
        analysis.tables.push(tableName);
      });
      
      // Extract ALTER TABLE statements
      const alterTableMatches = content.match(/ALTER TABLE\s+(\w+)\s+ADD COLUMN\s+(?:IF NOT EXISTS\s+)?(\w+)/gi) || [];
      alterTableMatches.forEach(match => {
        const parts = match.match(/ALTER TABLE\s+(\w+)\s+ADD COLUMN\s+(?:IF NOT EXISTS\s+)?(\w+)/i);
        if (parts) {
          analysis.columns.push({ table: parts[1], column: parts[2] });
        }
      });
      
      // Check if tables exist in database
      for (const table of analysis.tables) {
        const exists = await tableExists(table);
        if (!exists) {
          analysis.issues.push(`Table '${table}' does not exist in database`);
          analysis.status = '⚠️';
        }
      }
      
      // Check if tables/columns are used in code
      for (const table of analysis.tables) {
        try {
          const codeSearch = execSync(
            `grep -r "${table}" --include="*.py" backend/ 2>/dev/null | wc -l`,
            { encoding: 'utf8' }
          );
          
          if (parseInt(codeSearch) > 0) {
            analysis.usedInCode = true;
          }
        } catch (e) {
          // Grep returns error if no matches
        }
      }
      
      // Check for duplicate migrations
      const duplicateFiles = sqlFiles.filter(f => f !== file && areSimilarMigrations(file, f));
      if (duplicateFiles.length > 0) {
        analysis.issues.push(`Possible duplicate of: ${duplicateFiles.join(', ')}`);
        analysis.status = '⚠️';
      }
      
      // Determine if can be deleted
      if (!analysis.usedInCode && analysis.tables.length > 0) {
        analysis.canBeDeleted = true;
        analysis.status = '❌';
      }
      
      migrationAnalysis.push(analysis);
    }
    
    // Print report
    console.log('📊 Migration Analysis Report\n');
    console.log('| Migration File | Status | Tables | Used in Code | Action |');
    console.log('|----------------|--------|--------|--------------|--------|');
    
    migrationAnalysis.forEach(m => {
      const action = m.canBeDeleted ? 'Can be deleted' : 'Keep';
      console.log(`| ${m.file.padEnd(30)} | ${m.status} | ${m.tables.join(', ').padEnd(20).substring(0, 20)} | ${m.usedInCode ? 'Yes' : 'No'} | ${action} |`);
    });
    
    // Print detailed issues
    console.log('\n🚨 Issues Found:\n');
    migrationAnalysis.forEach(m => {
      if (m.issues.length > 0) {
        console.log(`${m.file}:`);
        m.issues.forEach(issue => console.log(`  - ${issue}`));
      }
    });
    
    // List migrations that can be archived
    const toArchive = migrationAnalysis.filter(m => m.canBeDeleted);
    if (toArchive.length > 0) {
      console.log('\n📦 Migrations that can be archived:');
      toArchive.forEach(m => console.log(`  - ${m.file}`));
      
      console.log('\nTo archive these files, run: npm run db:clean-migrations');
    }
    
    // Check for missing tables referenced in code
    console.log('\n🔍 Checking for missing tables referenced in code...');
    const commonTables = [
      'users', 'sessions', 'service_types', 'credit_packages', 'donations',
      'pricing_config', 'platform_settings', 'ai_recommendations', 'followup_templates',
      'avatar_sessions', 'rag_knowledge_base', 'cache_analytics', 'payments',
      'user_purchases', 'user_subscriptions', 'satsang_events', 'satsang_attendees',
      'social_content', 'birth_chart_cache', 'prokerala_tokens'
    ];
    
    const missingTables = [];
    for (const table of commonTables) {
      if (!await tableExists(table)) {
        // Check if used in code
        try {
          const codeSearch = execSync(
            `grep -r "FROM ${table}\\|INTO ${table}" --include="*.py" backend/ 2>/dev/null | wc -l`,
            { encoding: 'utf8' }
          );
          
          if (parseInt(codeSearch) > 0) {
            missingTables.push(table);
          }
        } catch (e) {
          // Grep returns error if no matches
        }
      }
    }
    
    if (missingTables.length > 0) {
      console.log('\n❌ Missing tables referenced in code:');
      missingTables.forEach(table => console.log(`  - ${table}`));
      console.log('\nRun "npm run db:fix" to create missing tables');
    }
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  } finally {
    await client.end();
  }
}

async function tableExists(tableName) {
  const result = await client.query(
    'SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = $1)',
    [tableName]
  );
  return result.rows[0].exists;
}

function areSimilarMigrations(file1, file2) {
  // Check if files have similar names (might be duplicates)
  const normalize = (f) => f.toLowerCase().replace(/[_-]/g, '').replace(/\d+/g, '');
  return normalize(file1) === normalize(file2);
}

// Run the analyzer
analyzeMigrations();