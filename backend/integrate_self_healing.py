"""
Integration of Database Self-Healing System with JyotiFlow
This integrates the self-healing system into the existing application
"""

import os
import asyncio
from fastapi import FastAPI
from backend.database_self_healing_system import (
    router as health_router,
    startup_event as health_startup,
    orchestrator
)
from backend.startup_database_validator import run_startup_database_validation

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
    from backend.routers.admin import admin_router
    
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
REACT_COMPONENT = """
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';

export function DatabaseHealthMonitor() {
    const [status, setStatus] = useState(null);
    const [issues, setIssues] = useState({ critical_issues: [], warnings: [] });
    const [loading, setLoading] = useState(false);
    const [checkInProgress, setCheckInProgress] = useState(false);

    const loadStatus = async () => {
        try {
            const response = await fetch('/api/database-health/status');
            const data = await response.json();
            setStatus(data);
        } catch (error) {
            console.error('Failed to load status:', error);
        }
    };

    const loadIssues = async () => {
        try {
            const response = await fetch('/api/database-health/issues');
            const data = await response.json();
            setIssues(data);
        } catch (error) {
            console.error('Failed to load issues:', error);
        }
    };

    const triggerHealthCheck = async () => {
        setCheckInProgress(true);
        try {
            const response = await fetch('/api/database-health/check', { method: 'POST' });
            const results = await response.json();
            
            // Show results
            alert(`Health check complete!
Issues found: ${results.issues_found}
Issues fixed: ${results.issues_fixed}
Critical issues: ${results.critical_issues?.length || 0}`);
            
            // Reload data
            await loadStatus();
            await loadIssues();
        } catch (error) {
            alert('Health check failed: ' + error.message);
        } finally {
            setCheckInProgress(false);
        }
    };

    const toggleMonitoring = async () => {
        const endpoint = status?.status === 'running' ? 'stop' : 'start';
        try {
            await fetch(`/api/database-health/${endpoint}`, { method: 'POST' });
            await loadStatus();
        } catch (error) {
            alert('Failed to toggle monitoring: ' + error.message);
        }
    };

    const fixIssue = async (issue) => {
        if (!confirm('Are you sure you want to fix this issue?')) return;
        
        try {
            const response = await fetch('/api/database-health/fix', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    issue_type: issue.issue_type,
                    table: issue.table,
                    column: issue.column,
                    fix_sql: issue.fix_sql
                })
            });
            
            const result = await response.json();
            if (result.success) {
                alert('Issue fixed successfully!');
                await loadIssues();
            } else {
                alert('Fix failed: ' + result.errors.join(', '));
            }
        } catch (error) {
            alert('Failed to fix issue: ' + error.message);
        }
    };

    useEffect(() => {
        loadStatus();
        loadIssues();
        
        // Auto-refresh every 30 seconds
        const interval = setInterval(() => {
            loadStatus();
            loadIssues();
        }, 30000);
        
        return () => clearInterval(interval);
    }, []);

    if (!status) {
        return <div className="flex justify-center p-8"><Loader2 className="animate-spin" /></div>;
    }

    return (
        <div className="space-y-6">
            {/* Status Card */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                        Database Health Status
                        <Badge variant={status.status === 'running' ? 'success' : 'secondary'}>
                            {status.status}
                        </Badge>
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                            <p className="text-sm text-muted-foreground">Last Check</p>
                            <p className="font-medium">
                                {status.last_check ? new Date(status.last_check).toLocaleString() : 'Never'}
                            </p>
                        </div>
                        <div>
                            <p className="text-sm text-muted-foreground">Total Fixes</p>
                            <p className="font-medium">{status.total_fixes}</p>
                        </div>
                        <div>
                            <p className="text-sm text-muted-foreground">Critical Issues</p>
                            <p className="font-medium text-red-600">{status.active_critical_issues}</p>
                        </div>
                        <div>
                            <p className="text-sm text-muted-foreground">Next Check</p>
                            <p className="font-medium">
                                {status.next_check ? new Date(status.next_check).toLocaleString() : 'Not scheduled'}
                            </p>
                        </div>
                    </div>
                    
                    <div className="flex gap-2 mt-4">
                        <Button 
                            onClick={triggerHealthCheck} 
                            disabled={checkInProgress}
                        >
                            {checkInProgress ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Checking...
                                </>
                            ) : (
                                'Run Check Now'
                            )}
                        </Button>
                        <Button 
                            onClick={toggleMonitoring}
                            variant={status.status === 'running' ? 'destructive' : 'default'}
                        >
                            {status.status === 'running' ? 'Stop Monitoring' : 'Start Monitoring'}
                        </Button>
                    </div>
                </CardContent>
            </Card>

            {/* Critical Issues */}
            {issues.critical_issues.length > 0 && (
                <Card className="border-red-200">
                    <CardHeader>
                        <CardTitle className="flex items-center text-red-600">
                            <XCircle className="mr-2" />
                            Critical Issues ({issues.critical_issues.length})
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-3">
                            {issues.critical_issues.map((issue, idx) => (
                                <Alert key={idx} variant="destructive">
                                    <AlertDescription>
                                        <div className="flex justify-between items-start">
                                            <div>
                                                <p className="font-medium">{issue.issue_type}</p>
                                                <p className="text-sm">
                                                    Table: {issue.table}
                                                    {issue.column && `, Column: ${issue.column}`}
                                                </p>
                                                <p className="text-sm mt-1">
                                                    Current: {issue.current_state} → Expected: {issue.expected_state}
                                                </p>
                                            </div>
                                            <Button 
                                                size="sm" 
                                                onClick={() => fixIssue(issue)}
                                                disabled={!issue.fix_sql}
                                            >
                                                Fix Now
                                            </Button>
                                        </div>
                                    </AlertDescription>
                                </Alert>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Warnings */}
            {issues.warnings.length > 0 && (
                <Card className="border-yellow-200">
                    <CardHeader>
                        <CardTitle className="flex items-center text-yellow-600">
                            <AlertTriangle className="mr-2" />
                            Warnings ({issues.warnings.length})
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-2">
                            {issues.warnings.map((warning, idx) => (
                                <div key={idx} className="p-3 bg-yellow-50 rounded-md">
                                    <p className="font-medium text-sm">{warning.issue_type}</p>
                                    <p className="text-sm text-muted-foreground">
                                        {warning.table}
                                        {warning.column && `.${warning.column}`}: {warning.current_state}
                                    </p>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* All Clear */}
            {issues.critical_issues.length === 0 && issues.warnings.length === 0 && (
                <Alert className="border-green-200">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <AlertDescription className="text-green-600">
                        All systems healthy! No issues detected.
                    </AlertDescription>
                </Alert>
            )}
        </div>
    );
}
"""


# Migration plan for type mismatches
TYPE_MISMATCH_MIGRATION = """
-- Fix user_id type mismatches across all tables
-- This migration consolidates all user_id columns to INTEGER

BEGIN;

-- 1. Fix sessions table
ALTER TABLE sessions 
ALTER COLUMN user_id TYPE INTEGER 
USING user_id::INTEGER;

-- 2. Fix credit_transactions table
ALTER TABLE credit_transactions 
ALTER COLUMN user_id TYPE INTEGER 
USING user_id::INTEGER;

-- 3. Fix user_purchases table
ALTER TABLE user_purchases 
ALTER COLUMN user_id TYPE INTEGER 
USING user_id::INTEGER;

-- 4. Fix avatar_sessions table
ALTER TABLE avatar_sessions 
ALTER COLUMN user_id TYPE INTEGER 
USING user_id::INTEGER;

-- 5. Fix live_chat_sessions table
ALTER TABLE live_chat_sessions 
ALTER COLUMN user_id TYPE INTEGER 
USING user_id::INTEGER;

-- 6. Add missing foreign key constraints
ALTER TABLE sessions 
ADD CONSTRAINT fk_sessions_user_id 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE credit_transactions 
ADD CONSTRAINT fk_credit_transactions_user_id 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE user_purchases 
ADD CONSTRAINT fk_user_purchases_user_id 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- 7. Create indexes on foreign keys
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_user_id ON credit_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_purchases_user_id ON user_purchases(user_id);

COMMIT;
"""


# Command to run the self-healing system
if __name__ == "__main__":
    print("""
JyotiFlow Database Self-Healing System Integration

To integrate into your existing application:

1. Add to your main.py or app.py:
   ```python
   from backend.integrate_self_healing import integrate_self_healing
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