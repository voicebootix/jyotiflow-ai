#!/usr/bin/env node

const { Client } = require('pg');
const fs = require('fs').promises;
const path = require('path');
const { execSync } = require('child_process');

// Load environment variables
require('dotenv').config();

const DATABASE_URL = process.env.DATABASE_URL || 'postgresql://user:password@localhost:5432/yourdb';

const client = new Client({
  connectionString: DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
});

// Tables we expect based on code analysis
const EXPECTED_TABLES = [
  'users', 'sessions', 'service_types', 'credit_packages', 'donations',
  'pricing_config', 'platform_settings', 'ai_recommendations', 'monetization_experiments',
  'followup_templates', 'avatar_sessions', 'rag_knowledge_base', 'cache_analytics',
  'payments', 'user_purchases', 'user_subscriptions', 'satsang_events',
  'satsang_attendees', 'social_content', 'ai_pricing_recommendations',
  'ai_insights_cache', 'service_configuration_cache', 'birth_chart_cache',
  'prokerala_tokens', 'schema_migrations', 'session_donations'
];

async function analyzeDatabase() {
  try {
    await client.connect();
    console.log('🔍 Starting comprehensive database analysis...\n');
    
    // Get all tables in database
    const tablesResult = await client.query(`
      SELECT tablename 
      FROM pg_tables 
      WHERE schemaname = 'public'
      ORDER BY tablename
    `);
    
    const dbTables = tablesResult.rows.map(r => r.tablename);
    console.log(`📊 Found ${dbTables.length} tables in database\n`);
    
    // Analyze each expected table
    const tableAnalysis = [];
    
    for (const table of EXPECTED_TABLES) {
      const analysis = {
        table,
        exists: dbTables.includes(table),
        usedInCode: false,
        filesFound: [],
        issues: [],
        columns: {}
      };
      
      // Check if table is used in code
      try {
        const codeSearch = execSync(
          `grep -r "FROM ${table}\\|INTO ${table}\\|TABLE ${table}" --include="*.py" backend/ 2>/dev/null | head -5`,
          { encoding: 'utf8' }
        );
        
        if (codeSearch) {
          analysis.usedInCode = true;
          const files = codeSearch.split('\n')
            .filter(line => line.trim())
            .map(line => line.split(':')[0].replace('backend/', ''));
          analysis.filesFound = [...new Set(files)];
        }
      } catch (e) {
        // Grep returns error if no matches
      }
      
      // If table exists, analyze columns
      if (analysis.exists) {
        const columnsResult = await client.query(`
          SELECT 
            column_name,
            data_type,
            character_maximum_length,
            is_nullable,
            column_default
          FROM information_schema.columns
          WHERE table_name = $1
          ORDER BY ordinal_position
        `, [table]);
        
        columnsResult.rows.forEach(col => {
          analysis.columns[col.column_name] = {
            type: col.data_type,
            maxLength: col.character_maximum_length,
            nullable: col.is_nullable === 'YES',
            default: col.column_default
          };
        });
      }
      
      // Check for known issues
      if (table === 'sessions' && analysis.columns.user_id?.type === 'text') {
        analysis.issues.push('user_id should be INTEGER, not TEXT');
      }
      
      if (table === 'service_types' && !analysis.columns.credits_required) {
        analysis.issues.push('Missing credits_required column');
      }
      
      if (!analysis.exists && analysis.usedInCode) {
        analysis.issues.push('Table missing but referenced in code');
      }
      
      tableAnalysis.push(analysis);
    }
    
    // Find tables in DB but not expected
    const unexpectedTables = dbTables.filter(t => !EXPECTED_TABLES.includes(t));
    
    // Generate report
    const reportPath = path.join(__dirname, '..', 'database-analysis-report.md');
    const report = generateReport(tableAnalysis, unexpectedTables, dbTables);
    
    await fs.writeFile(reportPath, report);
    console.log(`✅ Analysis complete! Report saved to: ${reportPath}`);
    
    // Print summary
    console.log('\n📊 Summary:');
    console.log(`   Tables in code: ${EXPECTED_TABLES.length}`);
    console.log(`   Tables in DB: ${dbTables.length}`);
    console.log(`   Missing tables: ${tableAnalysis.filter(t => !t.exists && t.usedInCode).length}`);
    console.log(`   Unused tables: ${unexpectedTables.length}`);
    console.log(`   Type mismatches: ${tableAnalysis.filter(t => t.issues.length > 0).length}`);
    
    const missingTables = tableAnalysis.filter(t => !t.exists && t.usedInCode);
    if (missingTables.length > 0) {
      console.log('\n❌ Missing tables that need to be created:');
      missingTables.forEach(t => {
        console.log(`   - ${t.table} (used in: ${t.filesFound.join(', ')})`);
      });
    }
    
    const criticalIssues = tableAnalysis.filter(t => t.issues.length > 0);
    if (criticalIssues.length > 0) {
      console.log('\n🚨 Critical issues found:');
      criticalIssues.forEach(t => {
        t.issues.forEach(issue => {
          console.log(`   - ${t.table}: ${issue}`);
        });
      });
    }
    
    console.log('\n💡 Next steps:');
    console.log('   1. Review the generated report: database-analysis-report.md');
    console.log('   2. Run "npm run db:fix" to apply automatic fixes');
    console.log('   3. Run "npm run db:clean-migrations" to clean up migration files');
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  } finally {
    await client.end();
  }
}

function generateReport(tableAnalysis, unexpectedTables, dbTables) {
  const now = new Date().toISOString().split('T')[0];
  
  let report = `# Database Analysis Report
Generated: ${now}

## 🔍 Code Analysis Results

### Tables Referenced in Code:
| Table Name | Status | Found In Files | Issues |
|------------|--------|----------------|---------|
`;

  tableAnalysis.forEach(t => {
    const status = t.exists ? '✅ Exists' : '❌ Missing';
    const files = t.filesFound.slice(0, 3).join(', ') + (t.filesFound.length > 3 ? '...' : '');
    const issues = t.issues.join('; ') || 'No issues';
    report += `| ${t.table} | ${status} | ${files || 'Not found'} | ${issues} |\n`;
  });
  
  // Add type mismatches section
  report += `
### Type Mismatches:
| Table | Column | Code Type | DB Type | Files | Severity |
|-------|--------|-----------|---------|-------|----------|
`;

  tableAnalysis.forEach(t => {
    if (t.exists) {
      // Check for known type mismatches
      if (t.table === 'sessions' && t.columns.user_id?.type === 'text') {
        report += `| sessions | user_id | int expected | TEXT | followup.py, follow_up_service.py | High |\n`;
      }
      if (t.table === 'users' && t.columns.id) {
        report += `| users | id | int/str mixed | ${t.columns.id.type.toUpperCase()} | auth.py (str conversion), ai.py (int) | High |\n`;
      }
    }
  });
  
  // Add migration files analysis
  report += `
### Migration Files Analysis:
See migration-analyzer.js output for detailed migration analysis.

### 🚨 Critical Issues (Broken Features):
`;

  let issueNum = 1;
  tableAnalysis.forEach(t => {
    if (!t.exists && t.usedInCode) {
      report += `${issueNum}. **Feature: ${t.table.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}**
   - Missing table: ${t.table}
   - Files affected: ${t.filesFound.join(', ')}
   - Impact: Feature broken

`;
      issueNum++;
    }
  });
  
  // Cleanup opportunities
  report += `### 🧹 Cleanup Opportunities:
- **Unused tables in database**: ${unexpectedTables.length} tables
  ${unexpectedTables.slice(0, 5).map(t => `- ${t}`).join('\n  ')}${unexpectedTables.length > 5 ? '\n  - ...' : ''}
  
### 📊 Summary:
- Tables in code: ${EXPECTED_TABLES.length}
- Tables in DB: ${dbTables.length}
- Missing tables: ${tableAnalysis.filter(t => !t.exists && t.usedInCode).length}
- Unused tables: ${unexpectedTables.length}
- Type mismatches: ${tableAnalysis.filter(t => t.issues.length > 0).length}
- Critical issues: ${tableAnalysis.filter(t => !t.exists && t.usedInCode).length}

### 🔧 Recommended Actions:
1. **Immediate**: Fix user ID type consistency (int vs string)
2. **High Priority**: Create missing tables for broken features
3. **Medium Priority**: Fix session user_id column type mismatch
4. **Low Priority**: Clean up unused tables and migrations
5. **Maintenance**: Archive old migration files after verification
`;

  return report;
}

// Run the analysis
analyzeDatabase();