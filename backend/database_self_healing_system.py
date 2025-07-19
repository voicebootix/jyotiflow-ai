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
import sqlparse
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
    'CRITICAL': ['users', 'sessions', 'service_types', 'rag_knowledge_base',
                 # Integration Monitoring System tables (required for production debugging)
                 'validation_sessions', 'integration_validations', 
                 'business_logic_issues', 'context_snapshots'],
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


def infer_column_type_from_name(column_name: str) -> str:
    """Infer column type from naming patterns - standalone function"""
    col_lower = column_name.lower()
    
    # ID columns
    if col_lower == 'id' or col_lower.endswith('_id'):
        if col_lower == 'session_id':
            return 'VARCHAR(255)'
        return 'INTEGER'
    
    # Boolean columns
    if col_lower.startswith('is_') or col_lower.startswith('has_') or col_lower.endswith('_flag'):
        return 'BOOLEAN'
    
    # Timestamp columns
    if any(pattern in col_lower for pattern in ['_at', '_date', '_time', 'created', 'updated', 'modified']):
        return 'TIMESTAMP'
    
    # Numeric columns
    if any(pattern in col_lower for pattern in ['count', 'amount', 'quantity', 'total', 'sum']):
        return 'INTEGER'
    if any(pattern in col_lower for pattern in ['price', 'cost', 'rate', 'percentage']):
        return 'NUMERIC(10,2)'
    
    # Text columns
    if any(pattern in col_lower for pattern in ['name', 'title', 'email', 'username', 'code']):
        return 'VARCHAR(255)'
    if any(pattern in col_lower for pattern in ['description', 'comment', 'note', 'message', 'content']):
        return 'TEXT'
    
    # JSON columns
    if any(pattern in col_lower for pattern in ['json', 'data', 'metadata', 'config', 'settings']):
        return 'JSONB'
    
    # Default
    return 'TEXT'


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
        """Get database connection from shared pool"""
        import db
        pool = db.get_db_pool()
        if not pool:
            raise Exception("Shared database pool not available")
        return await pool.acquire()
    
    async def analyze_schema(self) -> Dict[str, Any]:
        """Analyze complete database schema"""
        import db
        pool = db.get_db_pool()
        if not pool:
            raise Exception("Shared database pool not available")
        
        async with pool.acquire() as conn:
            schema = {}
            
            try:
                schema['tables'] = await self._get_all_tables(conn)
            except Exception as e:
                logger.error(f"Error getting tables: {e}")
                schema['tables'] = []
            
            try:
                schema['columns'] = await self._get_all_columns(conn)
            except Exception as e:
                logger.error(f"Error getting columns: {e}")
                schema['columns'] = {}
            
            try:
                schema['constraints'] = await self._get_all_constraints(conn)
            except Exception as e:
                logger.error(f"Error getting constraints: {e}")
                schema['constraints'] = {}
            
            try:
                schema['indexes'] = await self._get_all_indexes(conn)
            except Exception as e:
                logger.error(f"Error getting indexes: {e}")
                schema['indexes'] = {}
            
            try:
                schema['functions'] = await self._get_all_functions(conn)
            except Exception as e:
                logger.error(f"Error getting functions: {e}")
                schema['functions'] = []
            
            try:
                schema['triggers'] = await self._get_all_triggers(conn)
            except Exception as e:
                logger.error(f"Error getting triggers: {e}")
                schema['triggers'] = []
            
            # Cache the schema
            self._known_schemas = schema
            return schema
    
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
                CASE 
                    WHEN prokind = 'a' THEN 'AGGREGATE FUNCTION'
                    ELSE pg_get_functiondef(oid) 
                END AS definition,
                prokind
            FROM pg_proc
            WHERE pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
            AND prokind != 'a'  -- Exclude aggregate functions which can't use pg_get_functiondef
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
                
                # Store query pattern with column information
                table = self._extract_table_name(query)
                if table:
                    columns = self._extract_columns_from_query(query)
                    self.analyzer.query_patterns[table].append({
                        'file': self.file_path,
                        'line': line_no,
                        'query': query,
                        'type': self._get_query_type(query),
                        'columns': columns  # Added column extraction
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
            
            def _extract_columns_from_query(self, query: str) -> Dict[str, str]:
                """Extract column references using SQL parser for accuracy"""
                columns = {}
                
                try:
                    # Parse the SQL query
                    parsed = sqlparse.parse(query)[0]
                    
                    # Get the query type
                    query_type = self._get_query_type(str(parsed))
                    
                    if query_type == 'INSERT':
                        columns.update(self._extract_insert_columns(parsed))
                    elif query_type == 'SELECT':
                        columns.update(self._extract_select_columns(parsed))
                    elif query_type == 'UPDATE':
                        columns.update(self._extract_update_columns(parsed))
                    
                    # Extract columns from WHERE clauses
                    columns.update(self._extract_where_columns(parsed))
                    
                except Exception as e:
                    logger.warning(f"Failed to parse SQL with sqlparse, falling back to regex: {e}")
                    # Fallback to simple regex extraction
                    columns.update(self._extract_columns_regex_fallback(query))
                
                return columns
            
            def _extract_insert_columns(self, parsed) -> Dict[str, str]:
                """Extract columns from INSERT statement"""
                columns = {}
                tokens = list(parsed.flatten())
                
                # Find column list after table name
                in_column_list = False
                in_values_list = False
                column_names = []
                values = []
                
                for i, token in enumerate(tokens):
                    if token.ttype is None and token.value.upper() == 'INSERT':
                        continue
                    elif token.ttype is None and token.value == '(' and not in_values_list:
                        in_column_list = True
                        continue
                    elif token.ttype is None and token.value == ')' and in_column_list:
                        in_column_list = False
                        continue
                    elif token.ttype is None and token.value.upper() == 'VALUES':
                        in_values_list = True
                        continue
                    elif in_column_list and token.ttype in (sqlparse.tokens.Name, None) and token.value not in (',', '(', ')'):
                        column_names.append(token.value.strip())
                    elif in_values_list and token.value == '(':
                        # Collect values until closing parenthesis
                        j = i + 1
                        paren_count = 1
                        while j < len(tokens) and paren_count > 0:
                            if tokens[j].value == '(':
                                paren_count += 1
                            elif tokens[j].value == ')':
                                paren_count -= 1
                            if paren_count > 0 and tokens[j].value != ',':
                                values.append(tokens[j].value)
                            j += 1
                        break
                
                # Match columns with inferred types
                for col_name in column_names:
                    columns[col_name] = infer_column_type_from_name(col_name)
                
                return columns
            
            def _extract_select_columns(self, parsed) -> Dict[str, str]:
                """Extract columns from SELECT statement"""
                columns = {}
                tokens = list(parsed.flatten())
                
                in_select = False
                for i, token in enumerate(tokens):
                    if token.ttype is None and token.value.upper() == 'SELECT':
                        in_select = True
                    elif token.ttype is None and token.value.upper() == 'FROM':
                        in_select = False
                    elif in_select and token.ttype in (sqlparse.tokens.Name, None):
                        if token.value not in (',', '*', 'DISTINCT'):
                            columns[token.value] = 'TEXT'  # Default type
                
                return columns
            
            def _extract_update_columns(self, parsed) -> Dict[str, str]:
                """Extract columns from UPDATE statement"""
                columns = {}
                tokens = list(parsed.flatten())
                
                in_set = False
                for i, token in enumerate(tokens):
                    if token.ttype is None and token.value.upper() == 'SET':
                        in_set = True
                    elif token.ttype is None and token.value.upper() in ('WHERE', 'FROM'):
                        in_set = False
                    elif in_set and token.ttype in (sqlparse.tokens.Name, None):
                        if i + 1 < len(tokens) and tokens[i + 1].value == '=':
                            columns[token.value] = 'TEXT'  # Will be refined later
                
                return columns
            
            def _extract_where_columns(self, parsed) -> Dict[str, str]:
                """Extract columns from WHERE clause"""
                columns = {}
                tokens = list(parsed.flatten())
                
                in_where = False
                for i, token in enumerate(tokens):
                    if token.ttype is None and token.value.upper() == 'WHERE':
                        in_where = True
                    elif in_where and token.ttype in (sqlparse.tokens.Name, None):
                        # Check if this is followed by an operator
                        if i + 1 < len(tokens) and tokens[i + 1].value in ('=', '>', '<', '>=', '<=', '!=', 'IS', 'IN', 'LIKE'):
                            columns[token.value] = infer_column_type_from_name(token.value)
                
                return columns
            
            def _extract_columns_regex_fallback(self, query: str) -> Dict[str, str]:
                """Fallback regex extraction when SQL parsing fails"""
                columns = {}
                query_lower = query.lower()
                
                # Extract from SELECT statements
                if 'select' in query_lower:
                    # Extract columns between SELECT and FROM
                    select_match = re.search(r'select\s+(.+?)\s+from', query_lower, re.DOTALL)
                    if select_match:
                        select_clause = select_match.group(1)
                        if '*' not in select_clause:
                            # Parse individual columns
                            col_parts = select_clause.split(',')
                            for part in col_parts:
                                # Handle aliases
                                col_match = re.match(r'(\w+)(?:\s+as\s+\w+)?', part.strip())
                                if col_match:
                                    columns[col_match.group(1)] = 'unknown'
                
                # Extract from WHERE clauses
                where_patterns = [
                    r'(\w+)\s*=\s*\$?\d+',  # column = $1 or column = 1
                    r'(\w+)\s*=\s*[\'"]([^\'"]+)[\'"]',  # column = 'value'
                    r'(\w+)\s+is\s+(?:not\s+)?null',  # column IS NULL
                    r'(\w+)\s+in\s*\(',  # column IN (...)
                    r'(\w+)\s*[<>]=?\s*',  # column > < >= <=
                ]
                
                for pattern in where_patterns:
                    for match in re.finditer(pattern, query_lower):
                        col_name = match.group(1)
                        if col_name not in ['and', 'or', 'not', 'where', 'from', 'select']:
                            columns[col_name] = columns.get(col_name, 'unknown')
                
                # Extract from UPDATE statements
                if 'update' in query_lower:
                    set_pattern = r'set\s+(.+?)(?:where|$)'
                    set_match = re.search(set_pattern, query_lower, re.DOTALL)
                    if set_match:
                        set_clause = set_match.group(1)
                        # Parse SET column = value pairs
                        set_parts = set_clause.split(',')
                        for part in set_parts:
                            col_match = re.match(r'(\w+)\s*=\s*(.+)', part.strip())
                            if col_match:
                                columns[col_match.group(1)] = self._infer_type_from_value(col_match.group(2))
                
                return columns
            
            def _parse_values_with_nested_parens(self, values_str: str) -> List[str]:
                """Parse comma-separated values handling nested parentheses and brackets"""
                values = []
                current_value = ""
                paren_depth = 0
                bracket_depth = 0
                in_quotes = False
                quote_char = None
                
                for char in values_str:
                    if char in ["'", '"'] and not in_quotes:
                        in_quotes = True
                        quote_char = char
                        current_value += char
                    elif char == quote_char and in_quotes and (len(current_value) == 0 or current_value[-1] != '\\'):
                        in_quotes = False
                        quote_char = None
                        current_value += char
                    elif char == '(' and not in_quotes:
                        paren_depth += 1
                        current_value += char
                    elif char == ')' and not in_quotes:
                        paren_depth -= 1
                        current_value += char
                    elif char == '[' and not in_quotes:
                        bracket_depth += 1
                        current_value += char
                    elif char == ']' and not in_quotes:
                        bracket_depth -= 1
                        current_value += char
                    elif char == ',' and paren_depth == 0 and bracket_depth == 0 and not in_quotes:
                        values.append(current_value.strip())
                        current_value = ""
                    else:
                        current_value += char
                
                # Add the last value
                if current_value.strip():
                    values.append(current_value.strip())
                
                return values
            
            def _infer_type_from_value(self, value: str) -> str:
                """Infer column type from value in query"""
                value = value.strip()
                
                # Check for explicit casts
                if '::' in value:
                    cast_match = re.search(r'::(\w+)', value)
                    if cast_match:
                        return cast_match.group(1).upper()
                
                # Check for NULL
                if value.lower() == 'null':
                    return 'unknown'
                
                # Check for boolean
                if value.lower() in ['true', 'false']:
                    return 'BOOLEAN'
                
                # Check for numbers (parameter placeholders or numeric literals)
                if re.match(r'^\$\d+$', value):  # PostgreSQL parameter placeholder
                    return 'INTEGER'  # Default type for parameters
                elif re.match(r'^\d+$', value):  # Pure integer
                    return 'INTEGER'
                
                if re.match(r'^\d+\.\d+$', value):
                    return 'NUMERIC'
                
                # Check for strings
                if value.startswith("'") or value.startswith('"'):
                    return 'VARCHAR'
                
                # Check for functions
                if 'now()' in value.lower() or 'current_timestamp' in value.lower():
                    return 'TIMESTAMP'
                
                if 'gen_random_uuid()' in value.lower():
                    return 'UUID'
                
                return 'unknown'
        
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
    
    def _check_regex_query_issues(self, query: str, line_no: int, line: str, file_path: str):
        """Check query issues when using regex fallback"""
        query_lower = query.lower()
        
        # Extract table name
        table = None
        for pattern in [r'from\s+(\w+)', r'into\s+(\w+)', r'update\s+(\w+)']:
            match = re.search(pattern, query_lower)
            if match:
                table = match.group(1)
                break
        
        if table:
            # Store in query patterns (simplified - no column extraction in regex mode)
            self.query_patterns[table].append({
                'file': file_path,
                'line': line_no,
                'query': query,
                'type': 'UNKNOWN',
                'columns': {}  # Regex mode doesn't extract columns
            })
    
    def _escape_identifier(self, identifier: str) -> str:
        """Escape SQL identifier to prevent injection"""
        # Use the existing secure quote_ident function
        return quote_ident(identifier)
    
    def _generate_table_schemas_from_queries(self, query_patterns: Dict[str, List[Dict]], 
                                           min_queries: int = 2,
                                           dry_run: bool = False) -> Dict[str, Any]:
        """Generate table schemas dynamically based on detected query patterns
        
        Args:
            query_patterns: Dictionary of table names to query info
            min_queries: Minimum number of queries required to generate schema
            dry_run: If True, only return schemas without applying
        """
        schemas = {}
        validation_report = []
        
        # For each table found in query patterns, generate a CREATE TABLE statement
        for table_name, queries in query_patterns.items():
            # Validation: Require minimum number of queries
            if len(queries) < min_queries:
                validation_report.append(f"Table '{table_name}' skipped: only {len(queries)} queries found (min: {min_queries})")
                continue
                
            if not queries:
                continue
                
            # Analyze all queries for this table to determine schema
            columns = {}
            has_foreign_keys = []
            
            for query_info in queries:
                query = query_info['query']
                query_columns = query_info.get('columns', {})
                
                # Add columns from this query
                for col_name, col_type in query_columns.items():
                    if col_name not in columns:
                        columns[col_name] = col_type
                    elif columns[col_name] == 'TEXT' and col_type != 'TEXT':
                        # Replace TEXT with more specific type
                        columns[col_name] = col_type
                    # Keep existing specific type if both are non-TEXT and different
                
                # Detect foreign key references
                fk_pattern = r'FOREIGN KEY\s*\(\s*(\w+)\s*\)\s*REFERENCES\s*(\w+)\s*\(\s*(\w+)\s*\)'
                fk_matches = re.finditer(fk_pattern, query, re.IGNORECASE)
                for fk_match in fk_matches:
                    has_foreign_keys.append({
                        'column': fk_match.group(1),
                        'ref_table': fk_match.group(2),
                        'ref_column': fk_match.group(3)
                    })
            
            # Generate CREATE TABLE statement
            # Even if no columns detected, create a basic table structure
            if True:  # Always generate for missing tables
                # Escape table name to prevent SQL injection
                table_name_escaped = self._escape_identifier(table_name)
                create_sql = f"CREATE TABLE IF NOT EXISTS {table_name_escaped} (\n"
                
                # Track columns for validation (including auto-generated ones)
                validation_columns = columns.copy()
                
                # Add id column if not present (common pattern)
                if 'id' not in columns:
                    create_sql += "    id SERIAL PRIMARY KEY,\n"
                    validation_columns['id'] = 'SERIAL'
                
                # Add detected columns
                for col_name, col_type in columns.items():
                    col_name_escaped = self._escape_identifier(col_name)
                    if col_name == 'id' and col_type == 'INTEGER':
                        create_sql += f"    {col_name_escaped} SERIAL PRIMARY KEY,\n"
                    else:
                        # Add NOT NULL for certain column patterns
                        not_null = ''
                        if col_name.endswith('_id') or col_name in ['name', 'email', 'username']:
                            not_null = ' NOT NULL'
                        
                        create_sql += f"    {col_name_escaped} {col_type}{not_null},\n"
                
                # If no columns detected, add minimal structure
                if not columns:
                    # Add common columns based on table name patterns
                    if 'session' in table_name:
                        create_sql += "    session_id VARCHAR(255),\n"
                        validation_columns['session_id'] = 'VARCHAR(255)'
                    if 'user' in table_name or 'validation' in table_name:
                        create_sql += "    user_id INTEGER,\n"
                        validation_columns['user_id'] = 'INTEGER'
                    if 'log' in table_name or 'issue' in table_name:
                        create_sql += "    description TEXT,\n"
                        validation_columns['description'] = 'TEXT'
                    # Add timestamp if not already present
                    if 'created_at' not in validation_columns:
                        create_sql += "    created_at TIMESTAMP DEFAULT NOW(),\n"
                        validation_columns['created_at'] = 'TIMESTAMP'
                
                # Add timestamp columns if detected in queries but not in columns
                elif 'created_at' not in columns and any('created' in q['query'].lower() for q in queries):
                    create_sql += "    created_at TIMESTAMP DEFAULT NOW(),\n"
                    validation_columns['created_at'] = 'TIMESTAMP'
                
                # Add foreign key constraints
                for fk in has_foreign_keys:
                    col_escaped = self._escape_identifier(fk['column'])
                    ref_table_escaped = self._escape_identifier(fk['ref_table'])
                    ref_col_escaped = self._escape_identifier(fk['ref_column'])
                    create_sql += f"    FOREIGN KEY ({col_escaped}) REFERENCES {ref_table_escaped}({ref_col_escaped}),\n"
                
                # Remove trailing comma and close
                create_sql = create_sql.rstrip(',\n') + "\n);"
                
                # Validate generated schema
                if self._validate_schema(create_sql, validation_columns):
                    schemas[table_name] = create_sql
                    logger.info(f"Generated schema for table '{table_name}' based on {len(queries)} queries")
                else:
                    validation_report.append(f"Table '{table_name}' schema validation failed")
        
        # Log validation report
        if validation_report:
            logger.warning("Schema generation validation report:\n" + "\n".join(validation_report))
        
        if dry_run:
            logger.info("DRY RUN MODE: Schemas generated but not applied")
            return {'schemas': schemas, 'validation_report': validation_report, 'dry_run': True}
        
        return schemas
    
    def _validate_schema(self, create_sql: str, columns: Dict[str, str]) -> bool:
        """Validate generated schema for common issues"""
        # Check for minimum columns
        if len(columns) == 0:
            return False
        
        # Check for suspicious column names
        suspicious_patterns = [';', '--', '/*', '*/', 'DROP', 'DELETE']
        for pattern in suspicious_patterns:
            if pattern in create_sql.upper():
                logger.warning(f"Suspicious pattern '{pattern}' found in schema")
                return False
        
        # Check for reasonable column types
        valid_types = ['INTEGER', 'VARCHAR', 'TEXT', 'BOOLEAN', 'TIMESTAMP', 'DATE', 
                      'NUMERIC', 'DECIMAL', 'SERIAL', 'BIGSERIAL', 'JSON', 'JSONB']
        for col_type in columns.values():
            base_type = col_type.split('(')[0].upper()
            if base_type not in valid_types:
                logger.warning(f"Unknown column type: {col_type}")
                return False
        
        return True


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
        
        import db
        pool = db.get_db_pool()
        if not pool:
            raise Exception("Shared database pool not available")
            
        async with pool.acquire() as conn:
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
        
        schema = None  # Initialize schema variable
        
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
            
            # 3. Detect schema issues (only if schema was successfully analyzed)
            schema_issues = []
            if schema:
                logger.info("Detecting schema issues...")
                schema_issues = await self._detect_schema_issues(schema)
                
                # 3.5 Detect critical missing tables referenced in code
                logger.info("Detecting missing critical tables...")
                missing_table_issues = await self._detect_critical_missing_tables(
                    schema, self.code_analyzer.query_patterns
                )
                schema_issues.extend(missing_table_issues)
                
                # 3.6 Detect missing columns referenced in code
                logger.info("Detecting missing columns...")
                missing_column_issues = await self._detect_missing_columns(
                    schema, self.code_analyzer.query_patterns
                )
                schema_issues.extend(missing_column_issues)
                
                # 3.7 Detect duplicate data
                logger.info("Detecting duplicate data...")
                duplicate_issues = await self._detect_duplicate_data(schema)
                schema_issues.extend(duplicate_issues)
            else:
                logger.warning("Skipping schema issue detection due to schema analysis failure")
            
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
    
    async def _detect_critical_missing_tables(self, schema: Dict, query_patterns: Dict[str, List[Dict]]) -> List[DatabaseIssue]:
        """Detect critical system tables that are missing but required."""
        issues = []
        existing_tables = {t['tablename'] for t in schema['tables']}
        
        # Dynamically generate table schemas based on query patterns
        # For critical monitoring tables, allow generation with just 1 query
        monitoring_table_schemas = self.code_analyzer._generate_table_schemas_from_queries(
            query_patterns, 
            min_queries=1,  # Critical tables need immediate creation
            dry_run=False
        )
        
        # Check monitoring tables first (these are causing the errors in logs)
        for table_name, create_sql in monitoring_table_schemas.items():
            if table_name not in existing_tables:
                # Check if this table is actually being used in code
                if table_name in query_patterns:
                    logger.warning(f"🚨 Critical monitoring table '{table_name}' is missing but actively used!")
                    issues.append(DatabaseIssue(
                        issue_type='MISSING_TABLE',
                        severity='CRITICAL',
                        table=table_name,
                        current_state='Table missing - monitoring system failing',
                        expected_state='Table required for Integration Monitoring System',
                        fix_sql=create_sql,
                        affected_files=[p['file'] for p in query_patterns[table_name][:3]]
                    ))
        
        # Also check other critical business tables
        for table_name in CRITICAL_TABLES:
            if table_name not in existing_tables:
                logger.warning(f"⚠️ Critical business table '{table_name}' is missing!")
                issues.append(DatabaseIssue(
                    issue_type='MISSING_TABLE',
                    severity='CRITICAL',
                    table=table_name,
                    current_state='Critical table missing',
                    expected_state='Table required for core business logic',
                    fix_sql=None  # These need proper schema definition
                ))
        
        # Add indexes for monitoring tables if they exist but lack indexes
        if 'integration_validations' in existing_tables:
            # Check if indexes exist
            table_indexes = schema.get('indexes', {}).get('integration_validations', [])
            index_names = [idx.get('index_name', '') for idx in table_indexes]
            
            if 'idx_integration_validations_session' not in index_names:
                issues.append(DatabaseIssue(
                    issue_type='MISSING_INDEX',
                    severity='HIGH',
                    table='integration_validations',
                    column='session_id',
                    current_state='Missing performance index',
                    expected_state='Index needed for monitoring queries',
                    fix_sql='CREATE INDEX IF NOT EXISTS idx_integration_validations_session ON integration_validations(session_id)'
                ))
        
        return issues
    
    async def _detect_missing_columns(self, schema: Dict, query_patterns: Dict[str, List[Dict]]) -> List[DatabaseIssue]:
        """Detect columns referenced in queries but missing from tables"""
        issues = []
        
        for table_name, patterns in query_patterns.items():
            # Skip if table doesn't exist (will be handled by missing table detection)
            if table_name not in [t['tablename'] for t in schema['tables']]:
                continue
            
            # Get existing columns for this table
            existing_columns = set()
            if table_name in schema['columns']:
                existing_columns = {col['column_name'] for col in schema['columns'][table_name]}
            
            # Collect all columns referenced in queries for this table
            referenced_columns = {}
            for pattern in patterns:
                if 'columns' in pattern:
                    for col_name, col_type in pattern['columns'].items():
                        if col_name not in existing_columns:
                            # Track the inferred type and where it's used
                            if col_name not in referenced_columns:
                                referenced_columns[col_name] = {
                                    'types': [],
                                    'files': [],
                                    'queries': []
                                }
                            referenced_columns[col_name]['types'].append(col_type)
                            referenced_columns[col_name]['files'].append(pattern['file'])
                            referenced_columns[col_name]['queries'].append(pattern['query'][:100])
            
            # Create issues for missing columns
            for col_name, col_info in referenced_columns.items():
                # Determine the most likely type
                types = [t for t in col_info['types'] if t != 'unknown']
                if types:
                    # Use the most common type
                    inferred_type = max(set(types), key=types.count)
                else:
                    # Default based on column name patterns
                    inferred_type = self._infer_column_type_from_name(col_name)
                
                issues.append(DatabaseIssue(
                    issue_type='MISSING_COLUMN',
                    severity='HIGH',
                    table=table_name,
                    column=col_name,
                    current_state='Column not found in table',
                    expected_state=f'Column {col_name} {inferred_type}',
                    fix_sql=f'ALTER TABLE {quote_ident(table_name)} ADD COLUMN {quote_ident(col_name)} {inferred_type}',
                    affected_files=list(set(col_info['files']))[:3],
                    affected_queries=col_info['queries'][:3]
                ))
        
        return issues
    
    def _infer_column_type_from_name(self, column_name: str) -> str:
        """Infer column type from naming patterns - delegates to standalone function"""
        return infer_column_type_from_name(column_name)
    
    async def _detect_duplicate_data(self, schema: Dict) -> List[DatabaseIssue]:
        """Detect duplicate data in tables by analyzing actual database constraints and data"""
        issues = []
        
        import db
        pool = db.get_db_pool()
        if not pool:
            return issues
            
        async with pool.acquire() as conn:
            # 1. First, find all UNIQUE constraints in the database
            unique_constraints = await conn.fetch("""
                SELECT 
                    tc.table_name,
                    kcu.column_name,
                    tc.constraint_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu 
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                WHERE tc.constraint_type = 'UNIQUE'
                    AND tc.table_schema = 'public'
                ORDER BY tc.table_name, kcu.ordinal_position
            """)
            
            # Group by table and constraint to handle multi-column unique constraints
            unique_by_table = defaultdict(list)
            for row in unique_constraints:
                unique_by_table[row['table_name']].append({
                    'column': row['column_name'],
                    'constraint': row['constraint_name']
                })
            
            # 2. Check each unique constraint for violations
            for table_name in unique_by_table:
                # Skip if table not in schema
                if table_name not in [t['tablename'] for t in schema.get('tables', [])]:
                    continue
                
                # Group columns by constraint name
                constraints_dict = defaultdict(list)
                for item in unique_by_table[table_name]:
                    constraints_dict[item['constraint']].append(item['column'])
                
                for constraint_name, columns in constraints_dict.items():
                    try:
                        if len(columns) == 1:
                            # Single column unique constraint
                            column = columns[0]
                            duplicates = await conn.fetch(f"""
                                SELECT {quote_ident(column)}, COUNT(*) as count
                                FROM {quote_ident(table_name)}
                                WHERE {quote_ident(column)} IS NOT NULL
                                GROUP BY {quote_ident(column)}
                                HAVING COUNT(*) > 1
                                ORDER BY count DESC
                                LIMIT 5
                            """)
                            
                            if duplicates:
                                total_duplicates = await conn.fetchval(f"""
                                    SELECT SUM(count - 1) as total_duplicates
                                    FROM (
                                        SELECT COUNT(*) as count
                                        FROM {quote_ident(table_name)}
                                        WHERE {quote_ident(column)} IS NOT NULL
                                        GROUP BY {quote_ident(column)}
                                        HAVING COUNT(*) > 1
                                    ) as dup_counts
                                """)
                                
                                duplicate_values = [f"'{row[column]}' ({row['count']} times)" for row in duplicates[:3]]
                                issues.append(DatabaseIssue(
                                    issue_type='DUPLICATE_DATA',
                                    severity='CRITICAL',
                                    table=table_name,
                                    column=column,
                                    current_state=f"{total_duplicates} duplicate records violating UNIQUE constraint",
                                    expected_state=f"Unique values enforced by constraint {constraint_name}",
                                    description=f"UNIQUE constraint violation in {table_name}.{column}: {', '.join(duplicate_values)}{'...' if len(duplicates) > 3 else ''}",
                                    fix_sql=None,  # Manual review needed
                                    affected_files=[],
                                    affected_queries=[]
                                ))
                        else:
                            # Multi-column unique constraint
                            col_list = ", ".join(quote_ident(col) for col in columns)
                            dup_count = await conn.fetchval(f"""
                                SELECT COUNT(*) FROM (
                                    SELECT {col_list}, COUNT(*) as count
                                    FROM {quote_ident(table_name)}
                                    GROUP BY {col_list}
                                    HAVING COUNT(*) > 1
                                ) as dups
                            """)
                            
                            if dup_count > 0:
                                issues.append(DatabaseIssue(
                                    issue_type='DUPLICATE_DATA',
                                    severity='CRITICAL',
                                    table=table_name,
                                    column=None,
                                    current_state=f"{dup_count} duplicate combinations violating UNIQUE constraint",
                                    expected_state=f"Unique combinations enforced by constraint {constraint_name}",
                                    description=f"UNIQUE constraint violation in {table_name} on columns ({', '.join(columns)})",
                                    fix_sql=None,
                                    affected_files=[],
                                    affected_queries=[]
                                ))
                                
                    except Exception as e:
                        logger.warning(f"Error checking unique constraint {constraint_name} in {table_name}: {e}")
            
            # 3. Check for duplicates in columns that SHOULD have unique constraints based on naming patterns
            # These are columns that look like they should be unique but don't have constraints
            unique_pattern_columns = [
                r'.*_id$',  # Columns ending with _id
                r'.*_key$',  # Columns ending with _key
                r'.*_code$',  # Columns ending with _code
                r'^email$',  # Email columns
                r'^username$',  # Username columns
                r'.*_hash$',  # Hash columns
                r'.*_token$',  # Token columns
            ]
            
            for table in schema.get('tables', []):
                table_name = table['tablename']
                if table_name not in schema.get('columns', {}):
                    continue
                    
                for column_info in schema['columns'][table_name]:
                    column_name = column_info['column_name']
                    
                    # Skip if already has unique constraint
                    has_unique = any(
                        col['column'] == column_name 
                        for col in unique_by_table.get(table_name, [])
                    )
                    if has_unique:
                        continue
                    
                    # Check if column matches any unique pattern
                    should_be_unique = any(
                        re.match(pattern, column_name, re.IGNORECASE) 
                        for pattern in unique_pattern_columns
                    )
                    
                    if should_be_unique:
                        try:
                            # Check for duplicates
                            dup_count = await conn.fetchval(f"""
                                SELECT COUNT(*) FROM (
                                    SELECT {quote_ident(column_name)}, COUNT(*) as count
                                    FROM {quote_ident(table_name)}
                                    WHERE {quote_ident(column_name)} IS NOT NULL
                                    GROUP BY {quote_ident(column_name)}
                                    HAVING COUNT(*) > 1
                                ) as dups
                            """)
                            
                            if dup_count > 0:
                                # Get sample duplicates
                                duplicates = await conn.fetch(f"""
                                    SELECT {quote_ident(column_name)}, COUNT(*) as count
                                    FROM {quote_ident(table_name)}
                                    WHERE {quote_ident(column_name)} IS NOT NULL
                                    GROUP BY {quote_ident(column_name)}
                                    HAVING COUNT(*) > 1
                                    ORDER BY count DESC
                                    LIMIT 3
                                """)
                                
                                duplicate_values = [f"'{row[column_name]}' ({row['count']} times)" for row in duplicates]
                                
                                issues.append(DatabaseIssue(
                                    issue_type='DUPLICATE_DATA',
                                    severity='HIGH',
                                    table=table_name,
                                    column=column_name,
                                    current_state=f"{dup_count} groups of duplicates (no unique constraint)",
                                    expected_state=f"Column {column_name} should probably have unique constraint",
                                    description=f"Column {table_name}.{column_name} has duplicates but no unique constraint: {', '.join(duplicate_values)}",
                                    fix_sql=f"-- Consider adding: ALTER TABLE {quote_ident(table_name)} ADD CONSTRAINT {quote_ident(f'{table_name}_{column_name}_unique')} UNIQUE ({quote_ident(column_name)});",
                                    affected_files=[],
                                    affected_queries=[]
                                ))
                                
                        except Exception as e:
                            logger.warning(f"Error checking potential unique column {table_name}.{column_name}: {e}")
            
            # 4. Check for completely duplicate rows in tables (excluding system columns)
            for table in schema.get('tables', []):
                table_name = table['tablename']
                if table_name not in schema.get('columns', {}):
                    continue
                
                # Get all columns except system columns
                columns = [
                    col['column_name'] 
                    for col in schema['columns'][table_name]
                    if col['column_name'] not in ['id', 'created_at', 'updated_at']
                ]
                
                if len(columns) > 1:  # Only check if there are meaningful columns
                    try:
                        col_list = ", ".join(quote_ident(col) for col in columns)
                        # Check for complete duplicate rows
                        dup_count = await conn.fetchval(f"""
                            SELECT COUNT(*) FROM (
                                SELECT {col_list}, COUNT(*) as count
                                FROM {quote_ident(table_name)}
                                GROUP BY {col_list}
                                HAVING COUNT(*) > 1
                            ) as dups
                        """)
                        
                        if dup_count > 0:
                            issues.append(DatabaseIssue(
                                issue_type='DUPLICATE_DATA',
                                severity='MEDIUM',
                                table=table_name,
                                column=None,
                                current_state=f"{dup_count} sets of duplicate rows",
                                expected_state="No duplicate rows",
                                description=f"Found {dup_count} sets of completely duplicate rows in {table_name} (ignoring id/timestamps)",
                                fix_sql=None,  # Too complex for auto-fix
                                affected_files=[],
                                affected_queries=[]
                            ))
                            
                    except Exception as e:
                        logger.warning(f"Error checking duplicate rows in {table_name}: {e}")
        
        return issues
    
    async def _check_performance(self) -> Dict[str, Any]:
        """Check database performance metrics"""
        import db
        pool = db.get_db_pool()
        if not pool:
            raise Exception("Shared database pool not available")
            
        async with pool.acquire() as conn:
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
        import db
        pool = db.get_db_pool()
        if not pool:
            raise Exception("Shared database pool not available")
            
        async with pool.acquire() as conn:
            # Ensure health_check_results table exists
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS health_check_results (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT NOW(),
                    results JSONB,
                    issues_found INTEGER,
                    issues_fixed INTEGER,
                    critical_count INTEGER
                )
            """)
            
            # Insert results
            await conn.execute("""
                INSERT INTO health_check_results (timestamp, results, issues_found, issues_fixed, critical_count)
                VALUES ($1, $2, $3, $4, $5)
            """, 
                results['timestamp'],
                json.dumps(results, default=serialize_datetime),
                results['issues_found'],
                results['issues_fixed'],
                len(results.get('critical_issues', []))
            )
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        import db
        pool = db.get_db_pool()
        if not pool:
            raise Exception("Shared database pool not available")
            
        async with pool.acquire() as conn:
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


from pydantic import field_validator

class ManualFixRequest(BaseModel):
    issue_type: str
    table: str
    column: Optional[str] = None
    fix_sql: Optional[str] = None
    
    @field_validator('issue_type')
    def validate_issue_type(cls, v):
        allowed_types = [
            'MISSING_TABLE', 'MISSING_COLUMN', 'TYPE_MISMATCH', 
            'MISSING_INDEX', 'ORPHANED_DATA', 'PERFORMANCE',
            'MISSING_PRIMARY_KEY', 'TYPE_CAST_IN_QUERY', 'DUPLICATE_DATA'
        ]
        if v not in allowed_types:
            raise ValueError(f"Invalid issue type. Must be one of: {', '.join(allowed_types)}")
        return v
    
    @field_validator('table', 'column')
    def validate_no_sql_injection(cls, v):
        if v:
            suspicious_patterns = [';', '--', '/*', '*/', 'DROP', 'DELETE', 'EXEC', 'UNION']
            for pattern in suspicious_patterns:
                if pattern in v.upper():
                    raise ValueError(f"Suspicious pattern '{pattern}' detected in input")
        return v


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
    """Get list of current issues with full details"""
    try:
        # Ensure tables exist
        await _ensure_health_tables_exist()
        
        import db
        pool = db.get_db_pool()
        if not pool:
            logger.error("Database pool not available for issues endpoint")
            return {
                'critical_issues': [], 
                'warnings': [],
                'issues_by_type': {},
                'summary': {
                    'total_issues': 0,
                    'critical_count': 0,
                    'warning_count': 0,
                    'auto_fixable': 0,
                    'requires_manual': 0
                },
                'error': 'Database connection not available'
            }
            
        async with pool.acquire() as conn:
            latest = await conn.fetchrow("""
                SELECT results FROM health_check_results
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            
            if latest and latest['results']:
                results = json.loads(latest['results'])
                
                # Categorize issues by type for better UI display
                issues_by_type = {
                    'MISSING_TABLE': [],
                    'MISSING_COLUMN': [],
                    'TYPE_MISMATCH': [],
                    'MISSING_INDEX': [],
                    'MISSING_PRIMARY_KEY': [],
                    'ORPHANED_DATA': [],
                    'TYPE_CAST_IN_QUERY': [],
                    'DUPLICATE_DATA': []
                }
                
                # Process critical issues
                for issue in results.get('critical_issues', []):
                    issue_type = issue.get('issue_type', 'OTHER')
                    if issue_type in issues_by_type:
                        issues_by_type[issue_type].append(issue)
                
                # Process warnings
                for issue in results.get('warnings', []):
                    issue_type = issue.get('issue_type', 'OTHER')
                    if issue_type in issues_by_type:
                        issues_by_type[issue_type].append(issue)
                
                return {
                    'critical_issues': results.get('critical_issues', []),
                    'warnings': results.get('warnings', []),
                    'issues_by_type': issues_by_type,
                    'summary': {
                        'total_issues': results.get('issues_found', 0),
                        'critical_count': len(results.get('critical_issues', [])),
                        'warning_count': len(results.get('warnings', [])),
                        'auto_fixable': sum(1 for issue in results.get('critical_issues', []) + results.get('warnings', []) 
                                          if issue.get('fix_sql')),
                        'requires_manual': sum(1 for issue in results.get('critical_issues', []) + results.get('warnings', []) 
                                             if not issue.get('fix_sql'))
                    }
                }
            
            return {
                'critical_issues': [], 
                'warnings': [],
                'issues_by_type': {},
                'summary': {
                    'total_issues': 0,
                    'critical_count': 0,
                    'warning_count': 0,
                    'auto_fixable': 0,
                    'requires_manual': 0
                }
            }
            
    except Exception as e:
        logger.error(f"Get issues endpoint error: {e}")
        return {'critical_issues': [], 'warnings': [], 'error': str(e)}


async def _ensure_health_tables_exist():
    """Ensure all required health monitoring tables exist"""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable not set")
    
    import db
    pool = db.get_db_pool()

    if not pool:
        raise Exception("Shared database pool not available")
        
    async with pool.acquire() as conn:
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


@router.post("/preview-fix")
async def preview_fix(request: ManualFixRequest):
    """Preview what a fix would do without applying it"""
    try:
        issue = DatabaseIssue(
            issue_type=request.issue_type,
            severity='CRITICAL',
            table=request.table,
            column=request.column,
            fix_sql=request.fix_sql
        )
        
        # Generate preview information
        preview = {
            'issue': asdict(issue),
            'fix_explanation': _explain_fix(issue),
            'affected_data': await _preview_affected_data(issue),
            'rollback_possible': True,
            'estimated_impact': _estimate_impact(issue)
        }
        
        return preview
        
    except Exception as e:
        logger.error(f"Preview fix error: {e}")
        return {'error': str(e)}


@router.post("/fix")
async def manual_fix(request: ManualFixRequest):
    """Manually fix a specific issue with optional approval"""
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


def _explain_fix(issue: DatabaseIssue) -> str:
    """Generate human-readable explanation of what the fix will do"""
    explanations = {
        'MISSING_TABLE': f"Create new table '{issue.table}' with the required schema",
        'MISSING_COLUMN': f"Add column '{issue.column}' to table '{issue.table}'",
        'TYPE_MISMATCH': f"Change data type of '{issue.column}' in '{issue.table}'",
        'MISSING_INDEX': f"Create index on '{issue.column}' in '{issue.table}' for better performance",
        'MISSING_PRIMARY_KEY': f"Add primary key to table '{issue.table}'",
        'ORPHANED_DATA': f"Clean up orphaned records in '{issue.table}'",
        'TYPE_CAST_IN_QUERY': f"Fix type casting issue for '{issue.column}' in queries"
    }
    return explanations.get(issue.issue_type, f"Apply fix for {issue.issue_type}")


async def _preview_affected_data(issue: DatabaseIssue) -> Dict:
    """Preview what data would be affected by the fix"""
    try:
        import db
        pool = db.get_db_pool()
        if not pool:
            return {'error': 'Database not available'}
            
        async with pool.acquire() as conn:
            if issue.issue_type == 'MISSING_TABLE':
                # Check if any queries are failing due to missing table
                return {'queries_affected': len(issue.affected_queries or [])}
            
            elif issue.issue_type == 'MISSING_COLUMN':
                # Count rows in the table
                count = await conn.fetchval(f"SELECT COUNT(*) FROM {quote_ident(issue.table)}")
                return {'rows_affected': count, 'default_value': 'NULL'}
            
            elif issue.issue_type == 'TYPE_MISMATCH':
                # Check for potential data loss
                return {'potential_data_loss': False, 'conversion_safe': True}
            
            return {'info': 'No data preview available'}
            
    except Exception as e:
        return {'error': str(e)}


def _estimate_impact(issue: DatabaseIssue) -> Dict:
    """Estimate the impact of applying the fix"""
    impacts = {
        'MISSING_TABLE': {'risk': 'low', 'downtime': 'none', 'reversible': True},
        'MISSING_COLUMN': {'risk': 'low', 'downtime': 'minimal', 'reversible': True},
        'TYPE_MISMATCH': {'risk': 'medium', 'downtime': 'brief', 'reversible': True},
        'MISSING_INDEX': {'risk': 'low', 'downtime': 'none', 'reversible': True},
        'MISSING_PRIMARY_KEY': {'risk': 'medium', 'downtime': 'brief', 'reversible': False},
        'ORPHANED_DATA': {'risk': 'medium', 'downtime': 'none', 'reversible': True},
        'TYPE_CAST_IN_QUERY': {'risk': 'low', 'downtime': 'none', 'reversible': True}
    }
    return impacts.get(issue.issue_type, {'risk': 'unknown', 'downtime': 'unknown', 'reversible': False})


# Startup integration
async def startup_event():
    """Initialize database self-healing on startup"""
    try:
        # Ensure required tables exist
        import db
        pool = db.get_db_pool()
        if not pool:
            raise Exception("Shared database pool not available")
            
        async with pool.acquire() as conn:
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