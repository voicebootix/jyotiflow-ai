"""
JyotiFlow Database Self-Healing System
Production-grade automated database issue detection and repair
Built with PostgreSQL and asyncpg for Supabase

As CTO and co-founder, I'm building this to be bulletproof.
"""

import os
import ast
import glob
import json
import asyncio
import asyncpg
import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
import re

# Import timezone fixer to handle database datetime issues
try:
    from database_timezone_fixer import safe_utc_now, normalize_datetime_for_db
except ImportError:
    # Fallback definitions if file doesn't exist yet
    def safe_utc_now():
        return datetime.now(timezone.utc).replace(tzinfo=None)
    def normalize_datetime_for_db(dt):
        if isinstance(dt, datetime) and dt.tzinfo is not None:
            return dt.replace(tzinfo=None)
        return dt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL")
BACKUP_RETENTION_DAYS = 30
SCAN_INTERVAL_SECONDS = 300  # 5 minutes
MAX_FIX_ATTEMPTS = 3

# CRITICAL SPIRITUAL SERVICE TABLES - Enhanced for business context
CRITICAL_TABLES = {
    'users',                    # Customer accounts and credits
    'sessions',                # Spiritual guidance sessions
    'service_types',           # Available spiritual services
    'credit_transactions',     # Financial transactions
    'payments',                # Payment processing
    'rag_knowledge_base',      # Spiritual wisdom for AI responses
    'birth_chart_cache',       # Cached astrological calculations
    'followup_templates'       # Follow-up spiritual guidance
}

# SPIRITUAL SERVICE PRIORITIES - Business-critical vs non-critical
SPIRITUAL_SERVICE_PRIORITIES = {
    'CRITICAL': ['users', 'sessions', 'service_types', 'rag_knowledge_base'],
    'HIGH': ['credit_transactions', 'payments', 'birth_chart_cache'],
    'MEDIUM': ['followup_templates', 'health_check_results'],
    'LOW': ['database_backups', 'platform_settings']
}

# Allowed PostgreSQL data types for validation
ALLOWED_DATA_TYPES = {
    'INTEGER', 'BIGINT', 'SMALLINT', 'NUMERIC', 'DECIMAL', 'REAL', 'DOUBLE PRECISION',
    'TEXT', 'VARCHAR', 'CHAR', 'BOOLEAN', 'DATE', 'TIME', 'TIMESTAMP', 'TIMESTAMPTZ',
    'UUID', 'JSON', 'JSONB', 'ARRAY', 'BYTEA', 'INTERVAL', 'MONEY', 'INET', 'CIDR',
    'VARCHAR(255)', 'VARCHAR(50)', 'VARCHAR(100)', 'CHAR(1)', 'NUMERIC(10,2)'
}

def serialize_datetime(obj):
    """JSON serializer for datetime objects"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def quote_ident(identifier: str) -> str:
    """Safely quote a PostgreSQL identifier"""
    if not identifier:
        raise ValueError("Identifier cannot be empty")
    # Check for SQL injection attempts
    if any(char in identifier for char in [';', '--', '/*', '*/', '\x00']):
        raise ValueError(f"Invalid identifier: {identifier}")
    # Quote the identifier
    return '"' + identifier.replace('"', '""') + '"'


@dataclass
class DatabaseIssue:
    """Represents a detected database issue"""
    issue_type: str  # TYPE_MISMATCH, MISSING_TABLE, MISSING_COLUMN, ORPHANED_DATA, etc.
    severity: str    # CRITICAL, HIGH, MEDIUM, LOW
    table: str
    column: Optional[str] = None
    current_state: Optional[str] = None
    expected_state: Optional[str] = None
    affected_files: List[str] = None
    affected_queries: List[str] = None
    fix_sql: Optional[str] = None
    code_fixes: List[Dict[str, Any]] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = safe_utc_now()
        if self.affected_files is None:
            self.affected_files = []
        if self.affected_queries is None:
            self.affected_queries = []
        if self.code_fixes is None:
            self.code_fixes = []
    
    @property
    def issue_id(self) -> str:
        """Generate unique ID for this issue"""
        content = f"{self.issue_type}:{self.table}:{self.column}:{self.current_state}:{self.expected_state}"
        return hashlib.md5(content.encode()).hexdigest()[:12]


class PostgreSQLSchemaAnalyzer:
    """Analyzes PostgreSQL database schema and detects issues"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self._known_schemas = {}
        
    async def get_connection(self) -> asyncpg.Connection:
        """Get database connection"""
        return await asyncpg.connect(self.database_url)
    
    async def analyze_schema(self) -> Dict[str, Any]:
        """Analyze complete database schema"""
        conn = await self.get_connection()
        try:
            schema = {
                'tables': await self._get_all_tables(conn),
                'columns': await self._get_all_columns(conn),
                'constraints': await self._get_all_constraints(conn),
                'indexes': await self._get_all_indexes(conn),
                'functions': await self._get_all_functions(conn),
                'triggers': await self._get_all_triggers(conn)
            }
            
            # Cache the schema
            self._known_schemas = schema
            return schema
            
        finally:
            await conn.close()
    
    async def _get_all_tables(self, conn: asyncpg.Connection) -> List[Dict]:
        """Get all tables in database"""
        query = """
            SELECT 
                schemaname,
                tablename,
                tableowner,
                pg_relation_size(schemaname||'.'||tablename) as size_bytes,
                obj_description((schemaname||'.'||tablename)::regclass, 'pg_class') as comment
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename
        """
        rows = await conn.fetch(query)
        return [dict(row) for row in rows]
    
    async def _get_all_columns(self, conn: asyncpg.Connection) -> Dict[str, List[Dict]]:
        """Get all columns for all tables"""
        query = """
            SELECT 
                c.table_name,
                c.column_name,
                c.data_type,
                c.udt_name,
                c.is_nullable,
                c.column_default,
                c.character_maximum_length,
                c.numeric_precision,
                c.numeric_scale,
                col_description(pgc.oid, c.ordinal_position) as comment
            FROM information_schema.columns c
            JOIN pg_class pgc ON pgc.relname = c.table_name
            WHERE c.table_schema = 'public'
            ORDER BY c.table_name, c.ordinal_position
        """
        rows = await conn.fetch(query)
        
        columns_by_table = defaultdict(list)
        for row in rows:
            columns_by_table[row['table_name']].append(dict(row))
        
        return dict(columns_by_table)
    
    async def _get_all_constraints(self, conn: asyncpg.Connection) -> Dict[str, List[Dict]]:
        """Get all constraints"""
        query = """
            SELECT 
                tc.table_name,
                tc.constraint_name,
                tc.constraint_type,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name,
                rc.update_rule,
                rc.delete_rule
            FROM information_schema.table_constraints tc
            LEFT JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            LEFT JOIN information_schema.constraint_column_usage ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            LEFT JOIN information_schema.referential_constraints rc
                ON rc.constraint_name = tc.constraint_name
                AND rc.constraint_schema = tc.table_schema
            WHERE tc.table_schema = 'public'
            ORDER BY tc.table_name, tc.constraint_name
        """
        rows = await conn.fetch(query)
        
        constraints_by_table = defaultdict(list)
        for row in rows:
            constraints_by_table[row['table_name']].append(dict(row))
        
        return dict(constraints_by_table)
    
    async def _get_all_indexes(self, conn: asyncpg.Connection) -> Dict[str, List[Dict]]:
        """Get all indexes"""
        query = """
            SELECT 
                t.relname AS table_name,
                i.relname AS index_name,
                a.attname AS column_name,
                ix.indisprimary AS is_primary,
                ix.indisunique AS is_unique,
                pg_relation_size(i.oid) AS size_bytes
            FROM pg_class t
            JOIN pg_index ix ON t.oid = ix.indrelid
            JOIN pg_class i ON i.oid = ix.indexrelid
            JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
            WHERE t.relkind = 'r' AND t.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
            ORDER BY t.relname, i.relname
        """
        rows = await conn.fetch(query)
        
        indexes_by_table = defaultdict(list)
        for row in rows:
            indexes_by_table[row['table_name']].append(dict(row))
        
        return dict(indexes_by_table)
    
    async def _get_all_functions(self, conn: asyncpg.Connection) -> List[Dict]:
        """Get all user-defined functions"""
        query = """
            SELECT 
                proname AS function_name,
                pg_get_function_identity_arguments(oid) AS arguments,
                pg_get_functiondef(oid) AS definition
            FROM pg_proc
            WHERE pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
        """
        rows = await conn.fetch(query)
        return [dict(row) for row in rows]
    
    async def _get_all_triggers(self, conn: asyncpg.Connection) -> Dict[str, List[Dict]]:
        """Get all triggers"""
        query = """
            SELECT 
                event_object_table AS table_name,
                trigger_name,
                event_manipulation,
                action_timing,
                action_statement
            FROM information_schema.triggers
            WHERE trigger_schema = 'public'
            ORDER BY event_object_table, trigger_name
        """
        rows = await conn.fetch(query)
        
        triggers_by_table = defaultdict(list)
        for row in rows:
            triggers_by_table[row['table_name']].append(dict(row))
        
        return dict(triggers_by_table)


class CodePatternAnalyzer:
    """Analyzes Python code for database patterns and issues"""
    
    def __init__(self):
        self.issues = []
        self.query_patterns = defaultdict(list)
        
    def analyze_codebase(self) -> List[DatabaseIssue]:
        """Analyze entire codebase for database patterns"""
        self.issues = []
        self.query_patterns = defaultdict(list)
        
        # Find all Python files
        python_files = glob.glob("**/*.py", recursive=True)
        
        for file_path in python_files:
            if any(skip in file_path for skip in ['venv/', '__pycache__/', '.git/', 'node_modules/']):
                continue
                
            try:
                self._analyze_file(file_path)
            except Exception as e:
                logger.warning(f"Error analyzing {file_path}: {e}")
        
        return self.issues
    
    def _analyze_file(self, file_path: str):
        """Analyze single Python file for database patterns"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse AST
        try:
            tree = ast.parse(content)
            self._analyze_ast(tree, file_path, content)
        except SyntaxError:
            # Fall back to regex analysis
            self._analyze_with_regex(content, file_path)
    
    def _analyze_ast(self, tree: ast.AST, file_path: str, content: str):
        """Analyze AST for database patterns"""
        lines = content.split('\n')
        
        class DatabaseVisitor(ast.NodeVisitor):
            def __init__(self, analyzer, file_path, lines):
                self.analyzer = analyzer
                self.file_path = file_path
                self.lines = lines
                
            def visit_Call(self, node):
                # Look for database operations
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['execute', 'fetch', 'fetchrow', 'fetchval']:
                        self._analyze_db_call(node)
                self.generic_visit(node)
            
            def _analyze_db_call(self, node):
                """Analyze database call for issues"""
                if node.args:
                    query_arg = node.args[0]
                    if isinstance(query_arg, ast.Str):
                        query = query_arg.s
                        self._check_query_issues(query, node.lineno)
                    elif isinstance(query_arg, ast.JoinedStr):
                        # Handle f-strings
                        query_parts = []
                        for value in query_arg.values:
                            if isinstance(value, ast.Str):
                                query_parts.append(value.s)
                            else:
                                query_parts.append('{}')
                        query = ''.join(query_parts)
                        self._check_query_issues(query, node.lineno)
            
            def _check_query_issues(self, query: str, line_no: int):
                """Check query for potential issues"""
                query_lower = query.lower()
                
                # Check for type casting issues
                if 'user_id' in query_lower and '::integer' in query_lower:
                    self.analyzer.issues.append(DatabaseIssue(
                        issue_type='TYPE_CAST_IN_QUERY',
                        severity='HIGH',
                        table=self._extract_table_name(query),
                        column='user_id',
                        current_state='Explicit type cast in query',
                        expected_state='Consistent column types',
                        affected_files=[self.file_path],
                        affected_queries=[query],
                        code_fixes=[{
                            'file': self.file_path,
                            'line': line_no,
                            'original': self.lines[line_no - 1] if line_no <= len(self.lines) else '',
                            'suggestion': 'Remove type cast after fixing column type'
                        }]
                    ))
                
                # Store query pattern
                table = self._extract_table_name(query)
                if table:
                    self.analyzer.query_patterns[table].append({
                        'file': self.file_path,
                        'line': line_no,
                        'query': query,
                        'type': self._get_query_type(query)
                    })
            
            def _extract_table_name(self, query: str) -> Optional[str]:
                """Extract table name from query"""
                query_lower = query.lower()
                
                # Common patterns
                patterns = [
                    r'from\s+(\w+)',
                    r'into\s+(\w+)',
                    r'update\s+(\w+)',
                    r'table\s+(\w+)'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, query_lower)
                    if match:
                        return match.group(1)
                
                return None
            
            def _get_query_type(self, query: str) -> str:
                """Get query type (SELECT, INSERT, UPDATE, etc.)"""
                query_lower = query.lower().strip()
                for query_type in ['select', 'insert', 'update', 'delete', 'create', 'alter', 'drop']:
                    if query_lower.startswith(query_type):
                        return query_type.upper()
                return 'OTHER'
        
        visitor = DatabaseVisitor(self, file_path, lines)
        visitor.visit(tree)
    
    def _analyze_with_regex(self, content: str, file_path: str):
        """Fallback regex-based analysis"""
        lines = content.split('\n')
        
        # Pattern to find database queries
        patterns = [
            (r'await\s+conn\.execute\s*\(\s*["\']([^"\']+)', 'execute'),
            (r'await\s+conn\.fetch\s*\(\s*["\']([^"\']+)', 'fetch'),
            (r'\.query\s*\(\s*["\']([^"\']+)', 'query'),
        ]
        
        for line_no, line in enumerate(lines, 1):
            for pattern, method in patterns:
                match = re.search(pattern, line)
                if match:
                    query = match.group(1)
                    self._check_regex_query_issues(query, line_no, line, file_path)


class DatabaseIssueFixer:
    """Fixes detected database issues"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.fix_history = []
        
    async def fix_issue(self, issue: DatabaseIssue) -> Dict[str, Any]:
        """Fix a database issue"""
        result = {
            'issue_id': issue.issue_id,
            'success': False,
            'actions_taken': [],
            'errors': [],
            'rollback_available': False
        }
        
        conn = await asyncpg.connect(self.database_url)
        
        try:
            # Start transaction
            await conn.execute('BEGIN')
            
            # Create backup point
            backup_id = await self._create_backup_point(conn, issue)
            result['rollback_available'] = True
            
            # Fix based on issue type
            if issue.issue_type == 'TYPE_MISMATCH':
                await self._fix_type_mismatch(conn, issue, result)
            elif issue.issue_type == 'MISSING_TABLE':
                await self._fix_missing_table(conn, issue, result)
            elif issue.issue_type == 'MISSING_COLUMN':
                await self._fix_missing_column(conn, issue, result)
            elif issue.issue_type == 'MISSING_INDEX':
                await self._fix_missing_index(conn, issue, result)
            elif issue.issue_type == 'ORPHANED_DATA':
                await self._fix_orphaned_data(conn, issue, result)
            
            # Apply code fixes if any
            if issue.code_fixes:
                await self._apply_code_fixes(issue.code_fixes, result)
            
            # Commit transaction
            await conn.execute('COMMIT')
            result['success'] = True
            
            # Record fix in history
            self.fix_history.append({
                'timestamp': safe_utc_now(),
                'issue': asdict(issue),
                'result': result,
                'backup_id': backup_id
            })
            
        except Exception as e:
            # Rollback on error
            await conn.execute('ROLLBACK')
            result['errors'].append(str(e))
            logger.error(f"Error fixing issue {issue.issue_id}: {e}")
            
        finally:
            await conn.close()
        
        return result
    
    async def _create_backup_point(self, conn: asyncpg.Connection, issue: DatabaseIssue) -> str:
        """Create backup point for rollback"""
        backup_id = f"fix_{issue.issue_id}_{safe_utc_now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create backup table for affected data
        if issue.table and issue.column:
            # Validate table name
            if issue.table not in CRITICAL_TABLES and not await self._table_exists(conn, issue.table):
                raise ValueError(f"Invalid table name: {issue.table}")
            
            backup_table = f"backup_{issue.table}_{backup_id}"
            await conn.execute(f"""
                CREATE TABLE {quote_ident(backup_table)} AS 
                SELECT * FROM {quote_ident(issue.table)}
            """)
            
            # Record backup metadata
            await conn.execute("""
                INSERT INTO database_backups (backup_id, table_name, column_name, issue_type, created_at)
                VALUES ($1, $2, $3, $4, $5)
            """, backup_id, issue.table, issue.column, issue.issue_type, safe_utc_now())
        
        return backup_id
    
    async def _fix_type_mismatch(self, conn: asyncpg.Connection, issue: DatabaseIssue, result: Dict):
        """Fix column type mismatch"""
        table = issue.table
        column = issue.column
        new_type = issue.expected_state
        
        # Validate data type
        if new_type:
            # Extract base type (e.g., VARCHAR from VARCHAR(255))
            base_type = new_type.split('(')[0].upper()
            if base_type not in ALLOWED_DATA_TYPES and new_type.upper() not in ALLOWED_DATA_TYPES:
                result['errors'].append(f"Invalid data type: {new_type}")
                return
        
        logger.info(f"Fixing type mismatch: {table}.{column} -> {new_type}")
        
        # PostgreSQL supports ALTER COLUMN TYPE
        try:
            # First, check if data can be converted
            check_query = f"""
                SELECT COUNT(*) as invalid_count
                FROM {quote_ident(table)}
                WHERE {quote_ident(column)} IS NOT NULL
                AND {quote_ident(column)}::text !~ '^[0-9]+$'
            """
            
            if new_type.upper() == 'INTEGER':
                invalid_count = await conn.fetchval(check_query)
                if invalid_count > 0:
                    result['errors'].append(f"Cannot convert {column} to INTEGER: {invalid_count} non-numeric values")
                    return
            
            # Perform the conversion
            alter_query = f"""
                ALTER TABLE {quote_ident(table)} 
                ALTER COLUMN {quote_ident(column)} 
                TYPE {new_type} 
                USING {quote_ident(column)}::{new_type}
            """
            
            await conn.execute(alter_query)
            result['actions_taken'].append(f"Changed {table}.{column} type to {new_type}")
            
            # Update any related constraints
            if 'REFERENCES' in issue.expected_state:
                # Extract referenced table
                ref_match = re.search(r'REFERENCES\s+(\w+)\s*\((\w+)\)', issue.expected_state)
                if ref_match:
                    ref_table, ref_column = ref_match.groups()
                    constraint_name = f"fk_{table}_{column}_{ref_table}"
                    
                    await conn.execute(f"""
                        ALTER TABLE {quote_ident(table)}
                        ADD CONSTRAINT {quote_ident(constraint_name)}
                        FOREIGN KEY ({quote_ident(column)}) REFERENCES {quote_ident(ref_table)}({quote_ident(ref_column)})
                        ON DELETE CASCADE
                    """)
                    result['actions_taken'].append(f"Added foreign key constraint {constraint_name}")
            
        except Exception as e:
            result['errors'].append(f"Type conversion failed: {str(e)}")
            raise
    
    async def _fix_missing_table(self, conn: asyncpg.Connection, issue: DatabaseIssue, result: Dict):
        """Create missing table"""
        if issue.fix_sql:
            await conn.execute(issue.fix_sql)
            result['actions_taken'].append(f"Created table {issue.table}")
        else:
            result['errors'].append(f"No CREATE TABLE statement found for {issue.table}")
    
    async def _fix_missing_column(self, conn: asyncpg.Connection, issue: DatabaseIssue, result: Dict):
        """Add missing column"""
        table = issue.table
        column = issue.column
        column_def = issue.expected_state or 'TEXT'
        
        await conn.execute(f"ALTER TABLE {quote_ident(table)} ADD COLUMN {quote_ident(column)} {column_def}")
        result['actions_taken'].append(f"Added column {table}.{column}")
    
    async def _fix_missing_index(self, conn: asyncpg.Connection, issue: DatabaseIssue, result: Dict):
        """Create missing index"""
        table = issue.table
        column = issue.column
        index_name = f"idx_{table}_{column}"
        
        await conn.execute(f"CREATE INDEX {quote_ident(index_name)} ON {quote_ident(table)}({quote_ident(column)})")
        result['actions_taken'].append(f"Created index {index_name}")
    
    async def _fix_orphaned_data(self, conn: asyncpg.Connection, issue: DatabaseIssue, result: Dict):
        """Clean up orphaned data"""
        if issue.fix_sql:
            affected = await conn.execute(issue.fix_sql)
            result['actions_taken'].append(f"Cleaned up orphaned data: {affected} rows affected")
    
    async def _apply_code_fixes(self, code_fixes: List[Dict], result: Dict):
        """Apply code fixes"""
        for fix in code_fixes:
            try:
                file_path = fix['file']
                
                # Backup original file
                backup_path = f"{file_path}.backup.{safe_utc_now().strftime('%Y%m%d_%H%M%S')}"
                with open(file_path, 'r') as f:
                    original_content = f.read()
                with open(backup_path, 'w') as f:
                    f.write(original_content)
                
                # Apply fix (this is simplified - in production we'd use AST transformation)
                # For now, just log what should be done
                result['actions_taken'].append(f"Code fix suggested for {file_path}:{fix['line']}")
                
            except Exception as e:
                result['errors'].append(f"Code fix failed: {str(e)}")
    
    async def _table_exists(self, conn: asyncpg.Connection, table_name: str) -> bool:
        """Check if a table exists in the database"""
        result = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = $1
            )
        """, table_name)
        return result

    async def drop_dead_tables(self, dead_tables: List[str]):
        conn = await self.get_connection()
        try:
            await conn.execute('BEGIN')
            for table in dead_tables:
                await conn.execute(f'DROP TABLE IF EXISTS {quote_ident(table)} CASCADE')
            await conn.execute('COMMIT')
        except:
            await conn.execute('ROLLBACK')
            raise
        finally:
            await conn.close()

    async def prune_old_backups(self, retention_days: int = 30):
        conn = await self.get_connection()
        try:
            backups = await conn.fetch("SELECT backup_id, table_name FROM database_backups WHERE created_at < NOW() - INTERVAL '%s days'", retention_days)
            for backup in backups:
                await conn.execute(f'DROP TABLE IF EXISTS backup_{backup['table_name']}_{backup['backup_id']}')
                await conn.execute('DELETE FROM database_backups WHERE backup_id = $1', backup['backup_id'])
        finally:
            await conn.close()


class DatabaseHealthMonitor:
    """Monitors database health and triggers fixes"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.schema_analyzer = PostgreSQLSchemaAnalyzer(database_url)
        self.code_analyzer = CodePatternAnalyzer()
        self.issue_fixer = DatabaseIssueFixer(database_url)
        self.known_issues = {}
        self.fix_history = []
        
    async def run_health_check(self) -> Dict[str, Any]:
        """Run complete health check"""
        logger.info("Starting database health check...")
        
        results = {
            'timestamp': safe_utc_now(),
            'issues_found': 0,
            'issues_fixed': 0,
            'critical_issues': [],
            'warnings': [],
            'schema_analysis': {},
            'code_analysis': {},
            'performance_metrics': {}
        }
        
        try:
            # 1. Analyze database schema
            logger.info("Analyzing database schema...")
            try:
                schema = await self.schema_analyzer.analyze_schema()
                results['schema_analysis'] = {
                    'tables_count': len(schema['tables']),
                    'total_size': sum(t['size_bytes'] for t in schema['tables'] if t['size_bytes']),
                    'tables': schema['tables']
                }
            except Exception as e:
                logger.error(f"Schema analysis failed: {e}")
                results['schema_analysis'] = {
                    'tables_count': 0,
                    'total_size': 0,
                    'tables': [],
                    'error': str(e)
                }
            
            # 2. Analyze code patterns
            logger.info("Analyzing code patterns...")
            code_issues = self.code_analyzer.analyze_codebase()
            results['code_analysis'] = {
                'files_scanned': len(set(issue.affected_files[0] for issue in code_issues if issue.affected_files)),
                'issues_found': len(code_issues)
            }
            
            # 3. Detect schema issues
            logger.info("Detecting schema issues...")
            schema_issues = await self._detect_schema_issues(schema)
            
            # 4. Combine all issues
            all_issues = code_issues + schema_issues
            results['issues_found'] = len(all_issues)
            
            # 5. Categorize issues
            for issue in all_issues:
                if issue.severity == 'CRITICAL':
                    results['critical_issues'].append(asdict(issue))
                else:
                    results['warnings'].append(asdict(issue))
            
            # 6. Auto-fix critical issues
            if results['critical_issues']:
                logger.warning(f"Found {len(results['critical_issues'])} critical issues")
                for issue_dict in results['critical_issues']:
                    issue = DatabaseIssue(**issue_dict)
                    if self._should_auto_fix(issue):
                        fix_result = await self.issue_fixer.fix_issue(issue)
                        if fix_result['success']:
                            results['issues_fixed'] += 1
            
            # 7. Check performance
            try:
                results['performance_metrics'] = await self._check_performance()
            except Exception as e:
                logger.error(f"Performance check failed: {e}")
                results['performance_metrics'] = {'error': str(e)}
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            results['error'] = str(e)
            results['issues_found'] += 1  # Count the error as an issue
            results['critical_issues'].append({
                'issue_type': 'HEALTH_CHECK_ERROR',
                'severity': 'CRITICAL',
                'description': str(e)
            })
        
        return results
    
    async def _detect_schema_issues(self, schema: Dict) -> List[DatabaseIssue]:
        """Detect issues in database schema"""
        issues = []
        
        # Check for type mismatches in user_id columns
        for table, columns in schema['columns'].items():
            for col in columns:
                if col['column_name'] == 'user_id':
                    # Check if it matches users.id type
                    users_id_type = None
                    if 'users' in schema['columns']:
                        for users_col in schema['columns']['users']:
                            if users_col['column_name'] == 'id':
                                users_id_type = users_col['data_type']
                                break
                    
                    if users_id_type and col['data_type'] != users_id_type:
                        # Validate the users_id_type before using it
                        base_type = users_id_type.split('(')[0].upper()
                        if base_type in ALLOWED_DATA_TYPES or users_id_type.upper() in ALLOWED_DATA_TYPES:
                            issues.append(DatabaseIssue(
                                issue_type='TYPE_MISMATCH',
                                severity='CRITICAL',
                                table=table,
                                column='user_id',
                                current_state=col['data_type'],
                                expected_state=f"{users_id_type} REFERENCES users(id)",
                                fix_sql=f"ALTER TABLE {quote_ident(table)} ALTER COLUMN user_id TYPE {users_id_type} USING user_id::{users_id_type}"
                            ))
        
        # Check for missing indexes on foreign keys
        for table, constraints in schema['constraints'].items():
            for constraint in constraints:
                if constraint['constraint_type'] == 'FOREIGN KEY':
                    # Check if index exists
                    column = constraint['column_name']
                    has_index = False
                    
                    if table in schema['indexes']:
                        for index in schema['indexes'][table]:
                            if index['column_name'] == column:
                                has_index = True
                                break
                    
                    if not has_index and column:
                        issues.append(DatabaseIssue(
                            issue_type='MISSING_INDEX',
                            severity='MEDIUM',
                            table=table,
                            column=column,
                            current_state='No index',
                            expected_state='Index on foreign key',
                            fix_sql=f"CREATE INDEX {quote_ident(f'idx_{table}_{column}')} ON {quote_ident(table)}({quote_ident(column)})"
                        ))
        
        # Check for tables without primary keys
        for table in schema['tables']:
            table_name = table['tablename']
            has_primary = False
            
            if table_name in schema['constraints']:
                for constraint in schema['constraints'][table_name]:
                    if constraint['constraint_type'] == 'PRIMARY KEY':
                        has_primary = True
                        break
            
            if not has_primary:
                issues.append(DatabaseIssue(
                    issue_type='MISSING_PRIMARY_KEY',
                    severity='HIGH',
                    table=table_name,
                    current_state='No primary key',
                    expected_state='Primary key required'
                ))
        
        return issues
    
    async def _check_performance(self) -> Dict[str, Any]:
        """Check database performance metrics"""
        conn = await asyncpg.connect(self.database_url)
        try:
            metrics = {}
            
            # Table sizes
            try:
                size_query = """
                    SELECT 
                        relname AS table_name,
                        pg_size_pretty(pg_relation_size(relid)) AS size
                    FROM pg_stat_user_tables
                    ORDER BY pg_relation_size(relid) DESC
                    LIMIT 10
                """
                metrics['largest_tables'] = [dict(row) for row in await conn.fetch(size_query)]
            except Exception as e:
                logger.warning(f"Failed to get table sizes: {e}")
                metrics['largest_tables'] = []
            
            # Slow queries (if pg_stat_statements is available)
            try:
                # Check PostgreSQL version and adjust column names accordingly
                pg_version = await conn.fetchval("SELECT version()")
                
                # PostgreSQL 13+ uses different column names in pg_stat_statements
                if "PostgreSQL 13" in pg_version or "PostgreSQL 14" in pg_version or "PostgreSQL 15" in pg_version:
                    slow_query = """
                        SELECT 
                            query,
                            calls,
                            total_exec_time as total_time,
                            mean_exec_time as mean_time
                        FROM pg_stat_statements
                        WHERE query NOT LIKE '%pg_stat_statements%'
                        AND calls > 0
                        ORDER BY mean_exec_time DESC
                        LIMIT 5
                    """
                else:
                    # Older PostgreSQL versions
                    slow_query = """
                        SELECT 
                            query,
                            calls,
                            total_time,
                            mean_time
                        FROM pg_stat_statements
                        WHERE query NOT LIKE '%pg_stat_statements%'
                        AND calls > 0
                        ORDER BY mean_time DESC
                        LIMIT 5
                    """
                
                metrics['slow_queries'] = [dict(row) for row in await conn.fetch(slow_query)]
            except (asyncpg.UndefinedTableError, asyncpg.UndefinedColumnError, Exception) as e:
                logger.warning(f"pg_stat_statements not available or incompatible: {e}")
                metrics['slow_queries'] = []
            
            # Index usage
            try:
                index_query = """
                    SELECT 
                        schemaname,
                        tablename,
                        indexname,
                        idx_scan,
                        idx_tup_read,
                        idx_tup_fetch
                    FROM pg_stat_user_indexes
                    WHERE idx_scan = 0
                    AND schemaname = 'public'
                """
                unused_indexes = await conn.fetch(index_query)
                metrics['unused_indexes'] = [dict(row) for row in unused_indexes]
            except Exception as e:
                logger.warning(f"Failed to get index usage: {e}")
                metrics['unused_indexes'] = []
            
            return metrics
            
        finally:
            await conn.close()
    
    def _should_auto_fix(self, issue: DatabaseIssue) -> bool:
        """
        Determine if issue should be auto-fixed based on spiritual service business priorities.
        
        SPIRITUAL SERVICE LOGIC:
        - CRITICAL tables (users, sessions, rag_knowledge_base): Fix immediately
        - HIGH priority (payments, birth_chart_cache): Fix with caution  
        - MEDIUM/LOW priority: Manual approval required
        """
        # Get business priority for the affected table
        table_priority = None
        for priority, tables in SPIRITUAL_SERVICE_PRIORITIES.items():
            if issue.table in tables:
                table_priority = priority
                break
        
        # Unknown table defaults to MEDIUM priority
        if table_priority is None:
            table_priority = 'MEDIUM'
            logger.warning(f"🕉️ Unknown table {issue.table} for spiritual services, using MEDIUM priority")
        
        # Auto-fix logic based on spiritual service business requirements
        if issue.severity == 'CRITICAL':
            if table_priority == 'CRITICAL':
                # Critical spiritual service tables - fix immediately
                logger.info(f"🚨 CRITICAL spiritual service issue in {issue.table} - auto-fixing immediately")
                return self._check_fix_throttling(issue, max_attempts=1)
            elif table_priority == 'HIGH':
                # High priority - fix with throttling
                logger.info(f"⚠️ HIGH priority spiritual service issue in {issue.table} - auto-fixing with caution")
                return self._check_fix_throttling(issue, max_attempts=2)
            else:
                # Medium/Low priority - require manual approval for safety
                logger.warning(f"🤔 Spiritual service issue in {issue.table} requires manual approval")
                return False
        
        # Non-critical issues require manual review for spiritual services
        logger.info(f"💭 Non-critical issue in {issue.table} - manual review recommended")
        return False
    
    def _check_fix_throttling(self, issue: DatabaseIssue, max_attempts: int = 3) -> bool:
        """Enhanced throttling with spiritual service context"""
        issue_key = f"{issue.issue_type}:{issue.table}:{issue.column}"
        if issue_key in self.known_issues:
            last_attempt = self.known_issues[issue_key]
            if safe_utc_now() - last_attempt < timedelta(hours=1):
                logger.warning(f"🕉️ Spiritual service fix throttled for {issue.table} - waiting for cooldown")
                return False  # Don't retry within an hour
        
        self.known_issues[issue_key] = safe_utc_now()
        return True


class SelfHealingOrchestrator:
    """Main orchestrator for the self-healing system"""
    
    def __init__(self):
        self.database_url = DATABASE_URL
        self.monitor = DatabaseHealthMonitor(self.database_url)
        self.running = False
        self._task = None
        
    async def start(self):
        """Start the self-healing system"""
        if self.running:
            return
        
        logger.info("Starting Database Self-Healing System...")
        self.running = True
        
        # Run initial check
        await self.run_check()
        
        # Start periodic monitoring
        self._task = asyncio.create_task(self._periodic_monitor())
    
    async def stop(self):
        """Stop the self-healing system"""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    async def run_check(self) -> Dict[str, Any]:
        """Run a single health check"""
        try:
            results = await self.monitor.run_health_check()
            
            # Log summary
            logger.info(f"Health check complete: {results['issues_found']} issues found, {results['issues_fixed']} fixed")
            
            # Save results
            await self._save_results(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {'error': str(e)}
    
    async def _periodic_monitor(self):
        """Run periodic monitoring"""
        while self.running:
            try:
                await asyncio.sleep(SCAN_INTERVAL_SECONDS)
                await self.run_check()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Periodic check error: {e}")
                await asyncio.sleep(60)  # Wait a minute on error
    
    async def _save_results(self, results: Dict[str, Any]):
        """Save health check results"""
        conn = await asyncpg.connect(self.database_url)
        try:
            # Ensure health_check_results table exists
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS health_check_results (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT NOW(),
                    results JSONB,
                    issues_found INTEGER DEFAULT 0,
                    issues_fixed INTEGER DEFAULT 0,
                    critical_count INTEGER DEFAULT 0
                )
            """)
            
            # Insert results
            timestamp_naive = results['timestamp'].replace(tzinfo=None)
            await conn.execute("""
                INSERT INTO health_check_results (timestamp, results, issues_found, issues_fixed, critical_count)
                VALUES ($1, $2, $3, $4, $5)
            """, 
                timestamp_naive,  # Use naive timestamp
                json.dumps(results, default=serialize_datetime),
                results['issues_found'],
                results['issues_fixed'],
                len(results.get('critical_issues', []))
            )
            
        finally:
            await conn.close()
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        conn = await asyncpg.connect(self.database_url)
        try:
            # Get latest health check
            latest = await conn.fetchrow("""
                SELECT * FROM health_check_results
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            
            # Get fix history
            fix_count = await conn.fetchval("""
                SELECT COUNT(*) FROM health_check_results
                WHERE issues_fixed > 0
            """)
            
            # Get active issues
            if latest and latest['results']:
                results = json.loads(latest['results'])
                active_issues = len(results.get('critical_issues', []))
            else:
                active_issues = 0
            
            return {
                'status': 'running' if self.running else 'stopped',
                'last_check': latest['timestamp'] if latest else None,
                'total_fixes': fix_count or 0,
                'active_critical_issues': active_issues,
                'next_check': safe_utc_now() + timedelta(seconds=SCAN_INTERVAL_SECONDS) if self.running else None
            }
            
        finally:
            await conn.close()


# FastAPI Integration
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/database-health", tags=["database-health"])

# Global orchestrator instance
orchestrator = SelfHealingOrchestrator()


class HealthCheckResponse(BaseModel):
    status: str
    last_check: Optional[datetime]
    total_fixes: int
    active_critical_issues: int
    next_check: Optional[datetime]


class ManualFixRequest(BaseModel):
    issue_type: str
    table: str
    column: Optional[str]
    fix_sql: Optional[str]


@router.get("/status", response_model=HealthCheckResponse)
async def get_health_status():
    """Get current database health status"""
    try:
        # Ensure orchestrator is initialized and tables exist
        await _ensure_health_tables_exist()
        return await orchestrator.get_status()
    except Exception as e:
        logger.error(f"Health status endpoint error: {e}")
        # Return a default status when there's an error
        return {
            'status': 'error',
            'last_check': None,
            'total_fixes': 0,
            'active_critical_issues': 0,
            'next_check': None
        }


@router.post("/check")
async def trigger_health_check():
    """Manually trigger a health check"""
    try:
        # Ensure orchestrator is initialized and tables exist
        await _ensure_health_tables_exist()
        results = await orchestrator.run_check()
        return results
    except Exception as e:
        logger.error(f"Health check endpoint error: {e}")
        return {'error': str(e), 'issues_found': 0, 'issues_fixed': 0}


@router.post("/start")
async def start_monitoring():
    """Start automatic monitoring"""
    try:
        # Ensure orchestrator is initialized and tables exist
        await _ensure_health_tables_exist()
        await orchestrator.start()
        return {"message": "Monitoring started"}
    except Exception as e:
        logger.error(f"Start monitoring endpoint error: {e}")
        return {"error": str(e)}


@router.post("/stop")
async def stop_monitoring():
    """Stop automatic monitoring"""
    try:
        await orchestrator.stop()
        return {"message": "Monitoring stopped"}
    except Exception as e:
        logger.error(f"Stop monitoring endpoint error: {e}")
        return {"error": str(e)}


@router.get("/issues")
async def get_current_issues():
    """Get list of current issues"""
    try:
        # Ensure tables exist
        await _ensure_health_tables_exist()
        
        conn = await asyncpg.connect(DATABASE_URL)
        try:
            latest = await conn.fetchrow("""
                SELECT results FROM health_check_results
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            
            if latest and latest['results']:
                results = json.loads(latest['results'])
                return {
                    'critical_issues': results.get('critical_issues', []),
                    'warnings': results.get('warnings', [])
                }
            
            return {'critical_issues': [], 'warnings': []}
            
        finally:
            await conn.close()
    except Exception as e:
        logger.error(f"Get issues endpoint error: {e}")
        return {'critical_issues': [], 'warnings': [], 'error': str(e)}


async def _ensure_health_tables_exist():
    """Ensure all required health monitoring tables exist"""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable not set")
    
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # Create health_check_results table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS health_check_results (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT NOW(),
                results JSONB,
                issues_found INTEGER DEFAULT 0,
                issues_fixed INTEGER DEFAULT 0,
                critical_count INTEGER DEFAULT 0
            )
        """)
        
        # Create database_backups table (if not exists)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS database_backups (
                id SERIAL PRIMARY KEY,
                backup_id VARCHAR(255) UNIQUE,
                table_name VARCHAR(255),
                column_name VARCHAR(255),
                issue_type VARCHAR(100),
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        logger.info("✅ Health monitoring tables ensured")
        
    except Exception as e:
        logger.error(f"Failed to create health monitoring tables: {e}")
        raise
    finally:
        await conn.close()


@router.post("/fix")
async def manual_fix(request: ManualFixRequest):
    """Manually fix a specific issue"""
    issue = DatabaseIssue(
        issue_type=request.issue_type,
        severity='CRITICAL',
        table=request.table,
        column=request.column,
        fix_sql=request.fix_sql
    )
    
    fixer = DatabaseIssueFixer(DATABASE_URL)
    result = await fixer.fix_issue(issue)
    
    return result


# Startup integration
async def startup_event():
    """Initialize database self-healing on startup"""
    try:
        # Ensure required tables exist
        conn = await asyncpg.connect(DATABASE_URL)
        try:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS database_backups (
                    id SERIAL PRIMARY KEY,
                    backup_id VARCHAR(255) UNIQUE,
                    table_name VARCHAR(255),
                    column_name VARCHAR(255),
                    issue_type VARCHAR(100),
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
        finally:
            await conn.close()
        
        # Start monitoring
        await orchestrator.start()
        logger.info("✅ Database Self-Healing System initialized")
        return orchestrator
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize self-healing system: {e}")
        return None


# Admin UI Integration
admin_template = """
<div class="database-health-monitor">
    <h2>Database Health Monitor</h2>
    
    <div class="status-card">
        <h3>System Status</h3>
        <div id="health-status">Loading...</div>
    </div>
    
    <div class="controls">
        <button onclick="triggerHealthCheck()">Run Check Now</button>
        <button onclick="toggleMonitoring()">Toggle Monitoring</button>
    </div>
    
    <div class="issues-panel">
        <h3>Current Issues</h3>
        <div id="issues-list">Loading...</div>
    </div>
    
    <div class="history-panel">
        <h3>Fix History</h3>
        <div id="fix-history">Loading...</div>
    </div>
</div>

<script>
async function loadHealthStatus() {
    const response = await fetch('/api/database-health/status');
    const data = await response.json();
    document.getElementById('health-status').innerHTML = `
        <p>Status: ${data.status}</p>
        <p>Last Check: ${data.last_check || 'Never'}</p>
        <p>Total Fixes: ${data.total_fixes}</p>
        <p>Critical Issues: ${data.active_critical_issues}</p>
        <p>Next Check: ${data.next_check || 'Not scheduled'}</p>
    `;
}

async function triggerHealthCheck() {
    const response = await fetch('/api/database-health/check', {method: 'POST'});
    const results = await response.json();
    alert(`Check complete: ${results.issues_found} issues found, ${results.issues_fixed} fixed`);
    loadHealthStatus();
    loadIssues();
}

async function loadIssues() {
    const response = await fetch('/api/database-health/issues');
    const data = await response.json();
    // Render issues...
}

// Load on page load
loadHealthStatus();
loadIssues();
setInterval(loadHealthStatus, 10000);  // Refresh every 10 seconds
</script>
"""

if __name__ == "__main__":
    # Command-line interface
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "check":
            asyncio.run(orchestrator.run_check())
        elif command == "start":
            asyncio.run(orchestrator.start())
            # Keep running
            try:
                asyncio.run(asyncio.sleep(float('inf')))
            except KeyboardInterrupt:
                asyncio.run(orchestrator.stop())
        elif command == "analyze":
            analyzer = CodePatternAnalyzer()
            issues = analyzer.analyze_codebase()
            print(f"Found {len(issues)} issues")
            for issue in issues[:10]:  # Show first 10
                print(f"- {issue.issue_type} in {issue.table}.{issue.column}")
        else:
            print("Usage: python database_self_healing_system.py [check|start|analyze]")
    else:
        print("Database Self-Healing System ready. Use 'start' to begin monitoring.")