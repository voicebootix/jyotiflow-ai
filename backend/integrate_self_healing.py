"""
Integration of Database Self-Healing System with JyotiFlow
This integrates the self-healing system into the existing application
"""

import asyncio
from fastapi import FastAPI
from .database_self_healing_system import (
    router as health_router,
    startup_event as health_startup,
    orchestrator
)
from .startup_database_validator import run_startup_database_validation

# Add to your existing FastAPI app
def integrate_self_healing(app: FastAPI):
    """Integrate self-healing system into existing FastAPI app"""
    
    # Add health monitoring routes
    app.include_router(health_router)
    
    # Add startup event
    @app.on_event("startup")
    async def combined_startup():
        """Combined startup with existing validation and new self-healing"""
        
        # Run existing validation first
        validation_results = await run_startup_database_validation()
        
        if validation_results['validation_passed']:
            # Initialize self-healing system
            await health_startup()
            
            # Start continuous monitoring
            await orchestrator.start()
        else:
            print("⚠️ Skipping self-healing initialization due to validation failures")
    
    # Add shutdown event
    @app.on_event("shutdown")
    async def shutdown_self_healing():
        """Stop self-healing on shutdown"""
        await orchestrator.stop()
    
    # Add admin panel integration
    from .routers.admin import admin_router
    
    @admin_router.get("/database-health")
    async def database_health_page():
        """Database health monitoring page"""
        return {
            "title": "Database Health Monitor",
            "component": "DatabaseHealthMonitor",
            "api_endpoints": {
                "status": "/api/database-health/status",
                "check": "/api/database-health/check",
                "issues": "/api/database-health/issues",
                "fix": "/api/database-health/fix"
            }
        }


# React component for admin panel
# Component moved to: frontend/src/components/DatabaseHealthMonitor.jsx
# This provides better maintainability, IDE support, and type checking
REACT_COMPONENT_PATH = "frontend/src/components/DatabaseHealthMonitor.jsx"

# To use in your app:
# import DatabaseHealthMonitor from './components/DatabaseHealthMonitor';


# Path to migration file for type mismatches
# Migration moved to: backend/migrations/005_fix_user_id_types.sql
TYPE_MISMATCH_MIGRATION_FILE = "backend/migrations/005_fix_user_id_types.sql"

# Read migration content when needed
def get_type_mismatch_migration():
    with open(TYPE_MISMATCH_MIGRATION_FILE, 'r') as f:
        return f.read()


# Command to run the self-healing system
if __name__ == "__main__":
    print("""
JyotiFlow Database Self-Healing System Integration

To integrate into your existing application:

1. Add to your main.py or app.py:
   ```python
   from .integrate_self_healing import integrate_self_healing
   integrate_self_healing(app)
   ```

2. Add the React component to your admin panel

3. Run the type mismatch migration:
   ```bash
   psql $DATABASE_URL < type_mismatch_migration.sql
   ```

4. Start your application normally - self-healing will initialize automatically

The system will:
- Run health checks every 5 minutes
- Auto-fix critical issues in core tables
- Provide manual fix options for other issues
- Keep full audit trail and backups
- Integrate with your existing admin panel
""")

    # If running directly, start the orchestrator
    asyncio.run(orchestrator.start())
    try:
        asyncio.run(asyncio.sleep(float('inf')))
    except KeyboardInterrupt:
        asyncio.run(orchestrator.stop())