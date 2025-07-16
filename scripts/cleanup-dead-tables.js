#!/usr/bin/env node

const { Client } = require('pg');
const fs = require('fs').promises;
const path = require('path');

// Load environment variables
require('dotenv').config();

const DATABASE_URL = process.env.DATABASE_URL || 'postgresql://user:password@localhost:5432/yourdb';

const client = new Client({
  connectionString: DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
});

// Dead tables identified from comprehensive analysis
const DEAD_TABLES = [
  'admin_analytics',
  'admin_notifications', 
  'performance_analytics',
  'system_logs',
  'user_analytics',
  'revenue_analytics',
  'monetization_insights',
  'cost_tracking',
  'demand_analytics',
  'revenue_impact_tracking',
  'endpoint_suggestions',
  'marketing_campaigns',
  'marketing_insights',
  'api_cache',
  'service_pricing_config',
  'plan_id_backup_migration',
  'session_donations',
  'credit_transactions',
  'satsang_donations',
  'user_sessions' // This shouldn't exist - it's a method name!
];

// Tables with naming conflicts that need fixing
const NAMING_FIXES = [
  {
    from: 'followup_templates',
    to: 'follow_up_templates',
    reason: 'Code uses underscore version'
  }
];

// Tables that are confused in code
const CODE_REFERENCE_FIXES = {
  'satsangs': 'satsang_events',
  'user_sessions': 'sessions' // This is actually get_user_sessions() method
};

async function cleanupDeadTables() {
  try {
    await client.connect();
    console.log('🧹 Starting database cleanup...\n');
    
    // Step 1: Create backup of schema
    console.log('📦 Creating schema backup...');
    const backupFile = `schema_backup_${new Date().toISOString().split('T')[0]}.sql`;
    const schemaBackup = await backupDatabaseSchema();
    await fs.writeFile(backupFile, schemaBackup);
    console.log(`   ✅ Schema backed up to: ${backupFile}\n`);
    
    // Step 2: Check which dead tables actually exist
    console.log('🔍 Checking dead tables...');
    const existingDeadTables = [];
    
    for (const table of DEAD_TABLES) {
      const exists = await tableExists(table);
      if (exists) {
        const rowCount = await getTableRowCount(table);
        existingDeadTables.push({ table, rowCount });
        console.log(`   ❌ ${table}: ${rowCount} rows`);
      }
    }
    
    if (existingDeadTables.length === 0) {
      console.log('   ✅ No dead tables found!\n');
    } else {
      console.log(`\n   Found ${existingDeadTables.length} dead tables to remove\n`);
    }
    
    // Step 3: Fix naming conflicts
    console.log('🔧 Fixing naming conflicts...');
    for (const fix of NAMING_FIXES) {
      const fromExists = await tableExists(fix.from);
      const toExists = await tableExists(fix.to);
      
      if (fromExists && !toExists) {
        await client.query(`ALTER TABLE ${fix.from} RENAME TO ${fix.to}`);
        console.log(`   ✅ Renamed ${fix.from} → ${fix.to}`);
      } else if (fromExists && toExists) {
        console.log(`   ⚠️  Both ${fix.from} and ${fix.to} exist - manual merge needed`);
      }
    }
    
    // Step 4: Drop dead tables (with confirmation)
    if (existingDeadTables.length > 0) {
      console.log('\n⚠️  Ready to drop the following dead tables:');
      existingDeadTables.forEach(({ table, rowCount }) => {
        console.log(`   - ${table} (${rowCount} rows)`);
      });
      
      console.log('\n   Add --confirm flag to actually drop these tables');
      console.log('   Example: node cleanup-dead-tables.js --confirm\n');
      
      if (process.argv.includes('--confirm')) {
        console.log('🗑️  Dropping dead tables...');
        
        for (const { table } of existingDeadTables) {
          try {
            await client.query(`DROP TABLE IF EXISTS ${table} CASCADE`);
            console.log(`   ✅ Dropped: ${table}`);
          } catch (error) {
            console.log(`   ⚠️  Failed to drop ${table}: ${error.message}`);
          }
        }
      }
    }
    
    // Step 5: Report code reference fixes needed
    console.log('\n📝 Code reference fixes needed:');
    for (const [wrong, correct] of Object.entries(CODE_REFERENCE_FIXES)) {
      console.log(`   - Replace "${wrong}" with "${correct}" in code`);
    }
    
    // Step 6: Archive unused migrations
    console.log('\n📁 Migrations to archive:');
    const deadMigrations = [
      'add_pricing_tables.sql', // Duplicate
      'migrations creating only dead tables'
    ];
    deadMigrations.forEach(m => console.log(`   - ${m}`));
    
    console.log('\n✅ Cleanup analysis complete!');
    
  } catch (error) {
    console.error('❌ Error:', error);
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

async function getTableRowCount(tableName) {
  try {
    const result = await client.query(`SELECT COUNT(*) FROM ${tableName}`);
    return parseInt(result.rows[0].count);
  } catch (error) {
    return 0;
  }
}

async function backupDatabaseSchema() {
  // Get all table definitions
  const tablesResult = await client.query(`
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    ORDER BY table_name
  `);
  
  let schema = '-- Database Schema Backup\n';
  schema += `-- Generated: ${new Date().toISOString()}\n\n`;
  
  for (const row of tablesResult.rows) {
    const tableName = row.table_name;
    
    // Get CREATE TABLE statement
    const createTableResult = await client.query(`
      SELECT 
        'CREATE TABLE ' || table_name || ' (' || 
        string_agg(
          column_name || ' ' || 
          data_type || 
          CASE 
            WHEN character_maximum_length IS NOT NULL 
            THEN '(' || character_maximum_length || ')' 
            ELSE '' 
          END ||
          CASE WHEN is_nullable = 'NO' THEN ' NOT NULL' ELSE '' END ||
          CASE WHEN column_default IS NOT NULL THEN ' DEFAULT ' || column_default ELSE '' END,
          ', '
        ) || ');' as create_statement
      FROM information_schema.columns
      WHERE table_name = $1
      GROUP BY table_name
    `, [tableName]);
    
    if (createTableResult.rows.length > 0) {
      schema += `\n-- Table: ${tableName}\n`;
      schema += createTableResult.rows[0].create_statement + '\n';
    }
  }
  
  return schema;
}

// Run the cleanup
cleanupDeadTables();