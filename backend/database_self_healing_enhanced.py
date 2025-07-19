"""
Enhanced Database Self-Healing System - Concept for Full Auto-Creation
This shows what would be needed to auto-create ANY table/column from code analysis
"""

import re
import ast
from typing import Dict, List, Optional, Set, Tuple

class EnhancedSchemaInferrer:
    """Infers table schemas from SQL queries in code"""
    
    def infer_table_schema_from_queries(self, table_name: str, queries: List[Dict]) -> Optional[str]:
        """
        Analyze all queries for a table to infer its schema
        This is complex and error-prone but possible
        """
        columns = {}
        constraints = []
        
        for query_info in queries:
            query = query_info['query'].lower()
            
            # Extract from INSERT statements
            if 'insert into' in query and table_name in query:
                # Parse: INSERT INTO table (col1, col2) VALUES ...
                match = re.search(rf'insert\s+into\s+{table_name}\s*\(([^)]+)\)', query)
                if match:
                    cols = [c.strip() for c in match.group(1).split(',')]
                    for col in cols:
                        if col not in columns:
                            columns[col] = self._infer_column_type(col, query)
            
            # Extract from CREATE TABLE statements (if found in migrations)
            if f'create table {table_name}' in query:
                # This would parse the full CREATE TABLE statement
                return self._extract_create_table(query)
            
            # Extract from SELECT statements
            if 'select' in query and table_name in query:
                # Parse column references after SELECT
                select_match = re.search(r'select\s+(.+?)\s+from', query)
                if select_match:
                    select_clause = select_match.group(1)
                    # Handle *, specific columns, aliases, etc.
                    self._parse_select_columns(select_clause, columns)
            
            # Extract from WHERE clauses to infer types
            if 'where' in query:
                # Parse: WHERE user_id = $1 (implies integer if $1 is int)
                self._infer_types_from_where(query, columns)
        
        # Build CREATE TABLE statement
        if columns:
            return self._build_create_table(table_name, columns, constraints)
        
        return None
    
    def _infer_column_type(self, column_name: str, context: str) -> str:
        """Infer column type from name and usage context"""
        # Common patterns
        if column_name.endswith('_id') or column_name == 'id':
            return 'INTEGER'
        elif column_name.endswith('_at'):
            return 'TIMESTAMP'
        elif 'email' in column_name:
            return 'VARCHAR(255)'
        elif 'name' in column_name:
            return 'VARCHAR(255)'
        elif 'description' in column_name or 'content' in column_name:
            return 'TEXT'
        elif 'price' in column_name or 'amount' in column_name:
            return 'NUMERIC(10,2)'
        elif 'is_' in column_name or column_name.startswith('has_'):
            return 'BOOLEAN'
        elif 'json' in column_name or 'data' in column_name:
            return 'JSONB'
        else:
            return 'TEXT'  # Safe default
    
    def _build_create_table(self, table_name: str, columns: Dict[str, str], 
                           constraints: List[str]) -> str:
        """Build a CREATE TABLE statement"""
        col_defs = []
        
        # Always add an ID column if not present
        if 'id' not in columns:
            col_defs.append('id SERIAL PRIMARY KEY')
        
        for col, dtype in columns.items():
            if col == 'id':
                col_defs.append(f'{col} SERIAL PRIMARY KEY')
            else:
                col_defs.append(f'{col} {dtype}')
        
        # Add common columns if not present
        if 'created_at' not in columns:
            col_defs.append('created_at TIMESTAMP DEFAULT NOW()')
        
        # Add foreign key constraints for _id columns
        for col in columns:
            if col.endswith('_id') and col != 'id':
                ref_table = col[:-3] + 's'  # user_id -> users
                constraints.append(f'FOREIGN KEY ({col}) REFERENCES {ref_table}(id)')
        
        create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
        create_sql += ",\n".join(f"    {col}" for col in col_defs)
        if constraints:
            create_sql += ",\n" + ",\n".join(f"    {c}" for c in constraints)
        create_sql += "\n);"
        
        return create_sql


class EnhancedCodePatternAnalyzer:
    """Enhanced analyzer that detects missing columns too"""
    
    def analyze_missing_columns(self, queries: List[Dict], existing_columns: Set[str]) -> List[Tuple[str, str]]:
        """Detect columns referenced in queries but missing from table"""
        missing_columns = []
        
        for query_info in queries:
            query = query_info['query']
            
            # Extract column references from various query parts
            referenced_cols = self._extract_column_references(query)
            
            for col in referenced_cols:
                if col not in existing_columns and col not in ['*', 'count', 'sum', 'avg']:
                    # Infer type for missing column
                    col_type = self._infer_column_type(col, query)
                    missing_columns.append((col, col_type))
        
        return list(set(missing_columns))  # Remove duplicates
    
    def _extract_column_references(self, query: str) -> Set[str]:
        """Extract all column references from a query"""
        columns = set()
        
        # This would need sophisticated SQL parsing
        # For now, a simplified version:
        
        # Extract from SELECT clause
        if 'select' in query.lower():
            # Parse columns between SELECT and FROM
            pass
        
        # Extract from WHERE clause  
        if 'where' in query.lower():
            # Parse column = value patterns
            pass
            
        # Extract from INSERT
        if 'insert' in query.lower():
            # Parse column list
            pass
        
        return columns


# The enhanced detection would be integrated like this:
async def _detect_missing_tables_enhanced(self, schema: Dict, query_patterns: Dict[str, List[Dict]]) -> List[DatabaseIssue]:
    """Enhanced detection that can handle ANY table"""
    issues = []
    all_tables_in_schema = {t['tablename'] for t in schema['tables']}
    inferrer = EnhancedSchemaInferrer()
    
    for table_name, patterns in query_patterns.items():
        if table_name not in all_tables_in_schema:
            # Try to infer schema from queries
            inferred_sql = inferrer.infer_table_schema_from_queries(table_name, patterns)
            
            if inferred_sql:
                issues.append(DatabaseIssue(
                    issue_type='MISSING_TABLE',
                    severity='CRITICAL',
                    table=table_name,
                    current_state='Table not found in schema',
                    expected_state='Table must exist (schema inferred from code)',
                    fix_sql=inferred_sql,
                    affected_files=[p['file'] for p in patterns[:3]]
                ))
            else:
                # Can't infer - need manual intervention
                issues.append(DatabaseIssue(
                    issue_type='MISSING_TABLE',
                    severity='HIGH',
                    table=table_name,
                    current_state='Table not found in schema',
                    expected_state='Table must exist (manual schema definition needed)',
                    fix_sql=None,
                    affected_files=[p['file'] for p in patterns[:3]]
                ))
    
    return issues


async def _detect_missing_columns(self, schema: Dict, query_patterns: Dict[str, List[Dict]]) -> List[DatabaseIssue]:
    """Detect missing columns in existing tables"""
    issues = []
    analyzer = EnhancedCodePatternAnalyzer()
    
    for table_name, patterns in query_patterns.items():
        if table_name in schema['columns']:
            existing_cols = {col['column_name'] for col in schema['columns'][table_name]}
            missing_cols = analyzer.analyze_missing_columns(patterns, existing_cols)
            
            for col_name, col_type in missing_cols:
                issues.append(DatabaseIssue(
                    issue_type='MISSING_COLUMN',
                    severity='HIGH',
                    table=table_name,
                    column=col_name,
                    current_state='Column not found in table',
                    expected_state=f'Column {col_name} {col_type}',
                    fix_sql=f'ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}',
                    affected_files=[p['file'] for p in patterns if col_name in p['query']][:3]
                ))
    
    return issues