#!/usr/bin/env python3
"""
Critical Functions Analysis for Startup System Unification
Identifies and analyzes the essential functions that must be integrated
"""

import os
from typing import Dict, Any

class CriticalFunctionsAnalyzer:
    """Analyzes critical functions that must be preserved in unification"""
    
    def __init__(self):
        self.critical_functions = {}
    
    def analyze_integrate_self_healing(self) -> Dict[str, Any]:
        """Analyze integrate_self_healing.py for critical functions"""
        filepath = "backend/integrate_self_healing.py"
        if not os.path.exists(filepath):
            return {"error": "File not found"}
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        critical_features = {
            "health_router_integration": {
                "purpose": "Adds health monitoring API endpoints",
                "code_pattern": "app.include_router(health_router)",
                "found": "app.include_router(health_router)" in content,
                "integration_needed": True
            },
            "startup_event_handler": {
                "purpose": "Initializes self-healing system on startup",
                "code_pattern": "@app.on_event(\"startup\")",
                "found": "@app.on_event(\"startup\")" in content,
                "integration_needed": True
            },
            "database_validation": {
                "purpose": "Runs startup database validation",
                "code_pattern": "run_startup_database_validation",
                "found": "run_startup_database_validation" in content,
                "integration_needed": True
            },
            "orchestrator_startup": {
                "purpose": "Starts database health monitoring orchestrator",
                "code_pattern": "await health_startup()",
                "found": "await health_startup()" in content,
                "integration_needed": True
            }
        }
        
        return {
            "filepath": filepath,
            "critical_features": critical_features,
            "integration_priority": "HIGH",
            "reason": "Health monitoring is essential for production stability"
        }
    
    def analyze_enhanced_startup_integration(self) -> Dict[str, Any]:
        """Analyze enhanced_startup_integration.py for critical functions"""
        filepath = "backend/enhanced_startup_integration.py"
        if not os.path.exists(filepath):
            return {"error": "File not found"}
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        critical_features = {
            "rag_knowledge_base_creation": {
                "purpose": "Creates rag_knowledge_base table for AI features",
                "code_pattern": "CREATE TABLE.*rag_knowledge_base",
                "found": "rag_knowledge_base" in content,
                "integration_needed": True
            },
            "service_configuration_cache": {
                "purpose": "Creates service_configuration_cache for AI personas",
                "code_pattern": "CREATE TABLE.*service_configuration_cache",
                "found": "service_configuration_cache" in content,
                "integration_needed": True
            },
            "knowledge_seeding": {
                "purpose": "Seeds spiritual knowledge base with AI embeddings",
                "code_pattern": "KnowledgeSeeder",
                "found": "KnowledgeSeeder" in content,
                "integration_needed": True
            },
            "robust_connection_handling": {
                "purpose": "Enhanced connection management with retries",
                "code_pattern": "_create_robust_connection",
                "found": "_create_robust_connection" in content,
                "integration_needed": False  # Already have this in unified
            }
        }
        
        return {
            "filepath": filepath,
            "critical_features": critical_features,
            "integration_priority": "HIGH",
            "reason": "RAG and AI features require knowledge base seeding"
        }
    
    def analyze_fix_startup_issues(self) -> Dict[str, Any]:
        """Analyze fix_startup_issues.py for critical functions"""
        filepath = "backend/fix_startup_issues.py"
        if not os.path.exists(filepath):
            return {"error": "File not found"}
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        critical_features = {
            "sentry_configuration": {
                "purpose": "Configures Sentry for error monitoring",
                "code_pattern": "sentry_sdk",
                "found": "sentry_sdk" in content,
                "integration_needed": True
            },
            "knowledge_base_validation": {
                "purpose": "Validates knowledge base exists and is populated",
                "code_pattern": "rag_knowledge_base",
                "found": "rag_knowledge_base" in content,
                "integration_needed": True
            },
            "service_cache_setup": {
                "purpose": "Sets up service configuration cache",
                "code_pattern": "service_configuration_cache",
                "found": "service_configuration_cache" in content,
                "integration_needed": True
            }
        }
        
        return {
            "filepath": filepath,
            "critical_features": critical_features,
            "integration_priority": "MEDIUM",
            "reason": "Error monitoring and cache setup are important for stability"
        }
    
    def analyze_startup_database_validator(self) -> Dict[str, Any]:
        """Analyze startup_database_validator.py for critical functions"""
        filepath = "backend/startup_database_validator.py"
        if not os.path.exists(filepath):
            return {"error": "File not found"}
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        critical_features = {
            "table_structure_validation": {
                "purpose": "Validates that required tables exist",
                "code_pattern": "validate_table_structures",
                "found": "validate_table_structures" in content,
                "integration_needed": True
            },
            "missing_columns_fix": {
                "purpose": "Fixes missing columns in critical tables",
                "code_pattern": "fix_missing_columns",
                "found": "fix_missing_columns" in content,
                "integration_needed": True
            },
            "constraints_validation": {
                "purpose": "Validates database constraints",
                "code_pattern": "validate_constraints",
                "found": "validate_constraints" in content,
                "integration_needed": True
            },
            "required_data_check": {
                "purpose": "Ensures required reference data exists",
                "code_pattern": "ensure_required_data",
                "found": "ensure_required_data" in content,
                "integration_needed": True
            }
        }
        
        return {
            "filepath": filepath,
            "critical_features": critical_features,
            "integration_priority": "HIGH",
            "reason": "Database validation prevents startup failures"
        }
    
    def generate_integration_plan(self) -> Dict[str, Any]:
        """Generate complete integration plan based on analysis"""
        analyses = {
            "self_healing": self.analyze_integrate_self_healing(),
            "enhanced_startup": self.analyze_enhanced_startup_integration(),
            "startup_fixer": self.analyze_fix_startup_issues(),
            "database_validator": self.analyze_startup_database_validator()
        }
        
        # Categorize features by priority
        high_priority = []
        medium_priority = []
        low_priority = []
        
        for system_name, analysis in analyses.items():
            if "error" in analysis:
                continue
                
            priority = analysis.get("integration_priority", "LOW")
            features = analysis.get("critical_features", {})
            
            for feature_name, feature_data in features.items():
                if feature_data.get("integration_needed", False):
                    feature_info = {
                        "system": system_name,
                        "feature": feature_name,
                        "purpose": feature_data.get("purpose", ""),
                        "filepath": analysis.get("filepath", "")
                    }
                    
                    if priority == "HIGH":
                        high_priority.append(feature_info)
                    elif priority == "MEDIUM":
                        medium_priority.append(feature_info)
                    else:
                        low_priority.append(feature_info)
        
        return {
            "high_priority_features": high_priority,
            "medium_priority_features": medium_priority,
            "low_priority_features": low_priority,
            "total_features_to_integrate": len(high_priority) + len(medium_priority) + len(low_priority)
        }

if __name__ == "__main__":
    analyzer = CriticalFunctionsAnalyzer()
    plan = analyzer.generate_integration_plan()
    
    print("🎯 CRITICAL FUNCTIONS INTEGRATION PLAN")
    print("=" * 50)
    
    print(f"📊 Total Features to Integrate: {plan['total_features_to_integrate']}")
    print()
    
    print("🚨 HIGH PRIORITY FEATURES:")
    for feature in plan['high_priority_features']:
        print(f"  • {feature['feature']} ({feature['system']})")
        print(f"    Purpose: {feature['purpose']}")
    print()
    
    print("⚠️ MEDIUM PRIORITY FEATURES:")
    for feature in plan['medium_priority_features']:
        print(f"  • {feature['feature']} ({feature['system']})")
        print(f"    Purpose: {feature['purpose']}")
    print()
    
    if plan['low_priority_features']:
        print("💡 LOW PRIORITY FEATURES:")
        for feature in plan['low_priority_features']:
            print(f"  • {feature['feature']} ({feature['system']})")
            print(f"    Purpose: {feature['purpose']}")