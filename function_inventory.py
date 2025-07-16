#!/usr/bin/env python3
"""
Function Inventory for Startup System Unification
Analyzes and documents all functions from the 4 systems to be unified
"""

import ast
import os
from typing import Dict, List, Any

class FunctionInventory:
    """Analyzes Python files to extract function signatures and purposes"""
    
    def __init__(self):
        self.inventory = {}
    
    def analyze_file(self, filepath: str) -> Dict[str, Any]:
        """Analyze a Python file and extract all functions"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        'name': node.name,
                        'line_number': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                        'is_async': isinstance(node, ast.AsyncFunctionDef),
                        'docstring': ast.get_docstring(node),
                        'decorators': [self._get_decorator_name(d) for d in node.decorator_list]
                    }
                    functions.append(func_info)
            
            return {
                'filepath': filepath,
                'functions': functions,
                'total_functions': len(functions)
            }
        except Exception as e:
            return {
                'filepath': filepath,
                'error': str(e),
                'functions': [],
                'total_functions': 0
            }
    
    def _get_decorator_name(self, decorator):
        """Extract decorator name from AST node"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            # Safely extract the full decorator name by recursively traversing the attribute chain
            return self._get_full_attribute_name(decorator)
        else:
            return str(decorator)
    
    def _get_full_attribute_name(self, node):
        """Recursively extract full attribute name from AST node"""
        try:
            if isinstance(node, ast.Name):
                return node.id
            elif isinstance(node, ast.Attribute):
                base = self._get_full_attribute_name(node.value)
                return f"{base}.{node.attr}"
            else:
                return str(node)
        except (AttributeError, Exception):
            # Fallback for complex or unsupported decorator patterns
            return "complex_decorator"
    
    def generate_inventory(self) -> Dict[str, Any]:
        """Generate complete function inventory for all startup systems"""
        systems_to_analyze = [
            'backend/integrate_self_healing.py',
            'backend/enhanced_startup_integration.py', 
            'backend/fix_startup_issues.py',
            'backend/startup_database_validator.py',
            'backend/unified_startup_system.py'  # Current unified system
        ]
        
        inventory = {}
        
        for system in systems_to_analyze:
            if os.path.exists(system):
                analysis = self.analyze_file(system)
                system_name = os.path.basename(system).replace('.py', '')
                inventory[system_name] = analysis
        
        return inventory
    
    def categorize_functions(self, inventory: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """Categorize functions by their purpose"""
        categories = {
            'database_connection': [],
            'health_monitoring': [],
            'knowledge_seeding': [],
            'schema_validation': [],
            'error_handling': [],
            'initialization': [],
            'cleanup': [],
            'other': []
        }
        
        # Keywords to identify function purposes
        keywords = {
            'database_connection': ['connect', 'pool', 'database', 'db_', 'connection'],
            'health_monitoring': ['health', 'monitor', 'check', 'status', 'healing'],
            'knowledge_seeding': ['knowledge', 'seed', 'rag', 'embedding', 'ai'],
            'schema_validation': ['validate', 'schema', 'table', 'column', 'fix'],
            'error_handling': ['error', 'exception', 'retry', 'fallback', 'handle'],
            'initialization': ['init', 'setup', 'start', 'create', 'ensure'],
            'cleanup': ['cleanup', 'close', 'shutdown', 'stop', 'clear']
        }
        
        for system_name, system_data in inventory.items():
            if 'functions' in system_data:
                for func in system_data['functions']:
                    categorized = False
                    func_name_lower = func['name'].lower()
                    
                    for category, category_keywords in keywords.items():
                        if any(keyword in func_name_lower for keyword in category_keywords):
                            categories[category].append({
                                'system': system_name,
                                'function': func,
                                'filepath': system_data['filepath']
                            })
                            categorized = True
                            break
                    
                    if not categorized:
                        categories['other'].append({
                            'system': system_name,
                            'function': func,
                            'filepath': system_data['filepath']
                        })
        
        return categories

if __name__ == "__main__":
    # Generate the inventory
    analyzer = FunctionInventory()
    inventory = analyzer.generate_inventory()
    categories = analyzer.categorize_functions(inventory)
    
    print("🔍 STARTUP SYSTEMS FUNCTION INVENTORY")
    print("=" * 50)
    
    # Print summary
    total_functions = sum(data.get('total_functions', 0) for data in inventory.values())
    print(f"📊 Total Functions Analyzed: {total_functions}")
    print(f"📁 Systems Analyzed: {len(inventory)}")
    print()
    
    # Print by system
    for system_name, data in inventory.items():
        if 'error' in data:
            print(f"❌ {system_name}: ERROR - {data['error']}")
        else:
            print(f"✅ {system_name}: {data['total_functions']} functions")
    print()
    
    # Print by category
    print("📋 FUNCTIONS BY CATEGORY:")
    for category, functions in categories.items():
        if functions:
            print(f"\n🎯 {category.upper()}: {len(functions)} functions")
            for item in functions:
                func = item['function']
                async_marker = "async " if func['is_async'] else ""
                print(f"  • {async_marker}{func['name']}() - {item['system']}")