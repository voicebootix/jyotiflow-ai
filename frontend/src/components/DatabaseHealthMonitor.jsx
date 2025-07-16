import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CheckCircle, XCircle, AlertTriangle, Loader2 } from 'lucide-react';

export default function DatabaseHealthMonitor() {
    const [status, setStatus] = useState({ status: 'stopped', last_check: null });
    const [issues, setIssues] = useState({ critical_issues: [], warnings: [] });
    const [checkInProgress, setCheckInProgress] = useState(false);

    const fetchStatus = async () => {
        try {
            const response = await fetch('/api/database-health/status');
            const data = await response.json();
            setStatus(data);
            setIssues(data.issues || { critical_issues: [], warnings: [] });
        } catch (error) {
            console.error('Failed to fetch status:', error);
        }
    };

    const runCheckNow = async () => {
        setCheckInProgress(true);
        try {
            const response = await fetch('/api/database-health/check', { method: 'POST' });
            await response.json();
            await fetchStatus();
        } catch (error) {
            console.error('Failed to run check:', error);
        } finally {
            setCheckInProgress(false);
        }
    };

    const toggleMonitoring = async () => {
        const endpoint = status.status === 'running' ? '/api/database-health/stop' : '/api/database-health/start';
        try {
            await fetch(endpoint, { method: 'POST' });
            await fetchStatus();
        } catch (error) {
            console.error('Failed to toggle monitoring:', error);
        }
    };

    const fixIssue = async (issue) => {
        try {
            const response = await fetch('/api/database-health/fix', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ issue })
            });
            await response.json();
            await fetchStatus();
        } catch (error) {
            console.error('Failed to fix issue:', error);
        }
    };

    useEffect(() => {
        fetchStatus();
        const interval = setInterval(fetchStatus, 30000); // Poll every 30 seconds
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="space-y-4">
            {/* Status Card */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                        Database Health Monitor
                        <span className={`text-sm px-2 py-1 rounded ${
                            status.status === 'running' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                            {status.status === 'running' ? 'Active' : 'Inactive'}
                        </span>
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-2">
                        <p className="text-sm text-muted-foreground">
                            Last check: {status.last_check ? new Date(status.last_check).toLocaleString() : 'Never'}
                        </p>
                        <p className="text-sm">
                            Critical Issues: {issues.critical_issues.length}
                        </p>
                        <p className="text-sm">
                            Warnings: {issues.warnings.length}
                        </p>
                    </div>
                    <div className="mt-4 flex gap-2">
                        <Button 
                            onClick={runCheckNow} 
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