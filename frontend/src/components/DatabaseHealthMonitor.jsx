import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
    CheckCircle, XCircle, AlertTriangle, Loader2, 
    Play, Pause, RefreshCw, Shield, Zap, Eye,
    Database, Columns, Key, Link, Trash2, Code
} from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://jyotiflow-ai.onrender.com';

// Issue type icons and colors
const ISSUE_CONFIG = {
    MISSING_TABLE: { icon: Database, color: 'text-red-500', bgColor: 'bg-red-50' },
    MISSING_COLUMN: { icon: Columns, color: 'text-orange-500', bgColor: 'bg-orange-50' },
    TYPE_MISMATCH: { icon: AlertTriangle, color: 'text-yellow-500', bgColor: 'bg-yellow-50' },
    MISSING_INDEX: { icon: Link, color: 'text-blue-500', bgColor: 'bg-blue-50' },
    MISSING_PRIMARY_KEY: { icon: Key, color: 'text-purple-500', bgColor: 'bg-purple-50' },
    ORPHANED_DATA: { icon: Trash2, color: 'text-gray-500', bgColor: 'bg-gray-50' },
    TYPE_CAST_IN_QUERY: { icon: Code, color: 'text-indigo-500', bgColor: 'bg-indigo-50' }
};

export default function DatabaseHealthMonitor() {
    const [status, setStatus] = useState({ status: 'stopped', last_check: null });
    const [issues, setIssues] = useState({ 
        critical_issues: [], 
        warnings: [], 
        issues_by_type: {},
        summary: {
            total_issues: 0,
            critical_count: 0,
            warning_count: 0,
            auto_fixable: 0,
            requires_manual: 0
        }
    });
    const [checkInProgress, setCheckInProgress] = useState(false);
    const [error, setError] = useState(null);
    const [selectedIssue, setSelectedIssue] = useState(null);
    const [fixPreview, setFixPreview] = useState(null);
    const [autoMode, setAutoMode] = useState(false);
    const [fixingIssue, setFixingIssue] = useState(false);
    
    // Track attempted fixes to prevent infinite loops - moved up before fetchIssues
    const [attemptedFixes, setAttemptedFixes] = useState(new Set());
    const [lastAutoFixTime, setLastAutoFixTime] = useState(0);

    const fetchStatus = async () => {
        try {
            setError(null);
            const response = await fetch(`${API_BASE_URL}/api/database-health/status`);
            if (!response.ok) throw new Error(`API Error: ${response.status}`);
            const data = await response.json();
            setStatus(data);
        } catch (error) {
            console.error('Failed to fetch status:', error);
            setError('Failed to fetch database health status');
        }
    };

    const fetchIssues = async () => {
        try {
            setError(null);
            const response = await fetch(`${API_BASE_URL}/api/database-health/issues`);
            if (!response.ok) throw new Error(`Failed to fetch issues: ${response.status}`);
            const data = await response.json();
            setIssues(data);
            
            // Don't clear attempted fixes here to prevent infinite loops
            // Only clear when user manually triggers a refresh
        } catch (error) {
            console.error('Failed to fetch issues:', error);
            setError('Failed to fetch database issues');
        }
    };

    const runCheckNow = async () => {
        setCheckInProgress(true);
        try {
            setError(null);
            const response = await fetch(`${API_BASE_URL}/api/database-health/check`, { method: 'POST' });
            if (!response.ok) throw new Error(`Health check failed: ${response.status}`);
            
            // Clear attempted fixes on manual check to allow retrying
            setAttemptedFixes(new Set());
            
            await fetchStatus();
            await fetchIssues();
        } catch (error) {
            console.error('Failed to run check:', error);
            setError('Failed to run health check');
        } finally {
            setCheckInProgress(false);
        }
    };

    const toggleMonitoring = async () => {
        const endpoint = status.status === 'running' 
            ? `${API_BASE_URL}/api/database-health/stop` 
            : `${API_BASE_URL}/api/database-health/start`;
        
        try {
            setError(null);
            const response = await fetch(endpoint, { method: 'POST' });
            if (!response.ok) throw new Error(`Failed to toggle monitoring: ${response.status}`);
            await fetchStatus();
        } catch (error) {
            console.error('Failed to toggle monitoring:', error);
            setError('Failed to toggle monitoring');
        }
    };

    const previewFix = async (issue) => {
        try {
            setError(null);
            const response = await fetch(`${API_BASE_URL}/api/database-health/preview-fix`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    issue_type: issue.issue_type,
                    table: issue.table,
                    column: issue.column,
                    fix_sql: issue.fix_sql
                })
            });
            if (!response.ok) throw new Error('Failed to preview fix');
            const preview = await response.json();
            setFixPreview(preview);
            setSelectedIssue(issue);
        } catch (error) {
            console.error('Failed to preview fix:', error);
            setError('Failed to preview fix');
        }
    };

    const applyFix = async (issue) => {
        // Prevent multiple concurrent executions
        if (fixingIssue) return;
        
        setFixingIssue(true);
        setError(null);
        
        try {
            const response = await fetch(`${API_BASE_URL}/api/database-health/fix`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    issue_type: issue.issue_type,
                    table: issue.table,
                    column: issue.column,
                    fix_sql: issue.fix_sql
                })
            });
            if (!response.ok) throw new Error('Failed to apply fix');
            
            // Clear modal state first
            setSelectedIssue(null);
            setFixPreview(null);
            
            // Then refresh data by calling fetch functions directly
            try {
                await fetchStatus();
                await fetchIssues();
            } catch (refreshError) {
                // Log but don't fail - the fix was already applied
                console.error('Failed to refresh after fix:', refreshError);
            }
        } catch (error) {
            console.error('Failed to apply fix:', error);
            setError('Failed to apply fix');
        } finally {
            setFixingIssue(false);
        }
    };

    // Auto-fix logic with loop prevention
    useEffect(() => {
        if (autoMode && issues.critical_issues?.length > 0 && !fixingIssue) {
            const now = Date.now();
            const cooldownMs = 5000; // 5 second cooldown between auto-fixes
            
            if (now - lastAutoFixTime < cooldownMs) {
                return; // Still in cooldown period
            }
            
            const autoFixableIssues = issues.critical_issues.filter(issue => 
                issue.fix_sql && 
                issue.severity === 'CRITICAL' &&
                !attemptedFixes.has(issue.issue_id || `${issue.table}-${issue.issue_type}`)
            );
            
            if (autoFixableIssues.length > 0) {
                // Auto-fix the first critical issue not yet attempted
                const issueToFix = autoFixableIssues[0];
                const issueKey = issueToFix.issue_id || `${issueToFix.table}-${issueToFix.issue_type}`;
                
                console.log('Auto-fixing issue:', issueToFix);
                setAttemptedFixes(prev => new Set([...prev, issueKey]));
                setLastAutoFixTime(now);
                applyFix(issueToFix);
            }
        }
    }, [autoMode, issues.critical_issues, fixingIssue, attemptedFixes, lastAutoFixTime]);
    // Note: applyFix is intentionally excluded to prevent infinite loops

    // Modal accessibility - Escape key handling
    useEffect(() => {
        const handleEscape = (e) => {
            if (e.key === 'Escape' && selectedIssue) {
                setSelectedIssue(null);
                setFixPreview(null);
            }
        };
        
        if (selectedIssue) {
            document.addEventListener('keydown', handleEscape);
            // Focus trap would go here in production
            return () => document.removeEventListener('keydown', handleEscape);
        }
    }, [selectedIssue]);

    useEffect(() => {
        fetchStatus();
        fetchIssues();
        const interval = setInterval(() => {
            fetchStatus();
            fetchIssues();
        }, 10000);
        return () => clearInterval(interval);
    }, []);

    const renderIssueCard = (issue, index) => {
        const config = ISSUE_CONFIG[issue.issue_type] || { icon: AlertTriangle, color: 'text-gray-500', bgColor: 'bg-gray-50' };
        const Icon = config.icon;

        return (
            <Card key={index} className={`mb-4 ${config.bgColor} border-l-4 ${config.color.replace('text-', 'border-')}`}>
                <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                        <div className="flex-1">
                            <div className="flex items-center mb-2">
                                <Icon className={`h-5 w-5 ${config.color} mr-2`} />
                                <h4 className="font-semibold">{issue.issue_type.replace(/_/g, ' ')}</h4>
                                <Badge className="ml-2" variant={issue.severity === 'CRITICAL' ? 'destructive' : 'secondary'}>
                                    {issue.severity}
                                </Badge>
                            </div>
                            <p className="text-sm text-gray-600 mb-1">
                                Table: <code className="bg-gray-100 px-1 rounded">{issue.table}</code>
                                {issue.column && (
                                    <> • Column: <code className="bg-gray-100 px-1 rounded">{issue.column}</code></>
                                )}
                            </p>
                            <p className="text-sm mb-2">{issue.current_state} → {issue.expected_state}</p>
                            {issue.affected_files && issue.affected_files.length > 0 && (
                                <p className="text-xs text-gray-500">
                                    Affected files: {issue.affected_files.join(', ')}
                                </p>
                            )}
                        </div>
                        <div className="flex flex-col gap-2 ml-4">
                            <Button
                                size="sm"
                                variant="outline"
                                onClick={() => previewFix(issue)}
                                disabled={!issue.fix_sql}
                            >
                                <Eye className="h-4 w-4 mr-1" />
                                Preview
                            </Button>
                            {autoMode && issue.fix_sql && (
                                <Badge variant="success" className="text-xs">
                                    <Zap className="h-3 w-3 mr-1" />
                                    Auto-fix
                                </Badge>
                            )}
                        </div>
                    </div>
                </CardContent>
            </Card>
        );
    };

    return (
        <div className="p-6 max-w-7xl mx-auto">
            <div className="mb-6">
                <h2 className="text-2xl font-bold mb-4">🏥 Database Health Monitor</h2>
                
                {/* Status Bar */}
                <Card className="mb-6">
                    <CardContent className="p-6">
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                            <div>
                                <p className="text-sm text-gray-600">Status</p>
                                <div className="flex items-center mt-1">
                                    {status.status === 'running' ? (
                                        <>
                                            <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                                            <span className="font-semibold text-green-600">Running</span>
                                        </>
                                    ) : (
                                        <>
                                            <XCircle className="h-5 w-5 text-gray-400 mr-2" />
                                            <span className="font-semibold text-gray-600">Stopped</span>
                                        </>
                                    )}
                                </div>
                            </div>
                            <div>
                                <p className="text-sm text-gray-600">Total Issues</p>
                                <p className="text-2xl font-bold">{issues.summary.total_issues}</p>
                            </div>
                            <div>
                                <p className="text-sm text-gray-600">Critical Issues</p>
                                <p className="text-2xl font-bold text-red-600">{issues.summary.critical_count}</p>
                            </div>
                            <div>
                                <p className="text-sm text-gray-600">Auto-fixable</p>
                                <p className="text-2xl font-bold text-green-600">{issues.summary.auto_fixable}</p>
                            </div>
                        </div>
                        
                        {/* Control Buttons */}
                        <div className="flex gap-3 mt-6">
                            <Button onClick={toggleMonitoring} variant="outline">
                                {status.status === 'running' ? (
                                    <>
                                        <Pause className="h-4 w-4 mr-2" />
                                        Stop Monitoring
                                    </>
                                ) : (
                                    <>
                                        <Play className="h-4 w-4 mr-2" />
                                        Start Monitoring
                                    </>
                                )}
                            </Button>
                            <Button onClick={runCheckNow} disabled={checkInProgress}>
                                {checkInProgress ? (
                                    <>
                                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                        Checking...
                                    </>
                                ) : (
                                    <>
                                        <RefreshCw className="h-4 w-4 mr-2" />
                                        Run Check Now
                                    </>
                                )}
                            </Button>
                            <div className="ml-auto flex items-center gap-2">
                                <span className="text-sm text-gray-600">Mode:</span>
                                <Button
                                    size="sm"
                                    variant={autoMode ? 'default' : 'outline'}
                                    onClick={() => setAutoMode(!autoMode)}
                                >
                                    {autoMode ? (
                                        <>
                                            <Zap className="h-4 w-4 mr-1" />
                                            Auto Mode
                                        </>
                                    ) : (
                                        <>
                                            <Shield className="h-4 w-4 mr-1" />
                                            Manual Mode
                                        </>
                                    )}
                                </Button>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {error && (
                    <Alert variant="destructive" className="mb-4">
                        <AlertDescription>{error}</AlertDescription>
                    </Alert>
                )}

                {/* Issues Tabs */}
                <Tabs defaultValue="by-severity" className="mt-6">
                    <TabsList>
                        <TabsTrigger value="by-severity">By Severity</TabsTrigger>
                        <TabsTrigger value="by-type">By Type</TabsTrigger>
                        <TabsTrigger value="all">All Issues</TabsTrigger>
                    </TabsList>
                    
                    <TabsContent value="by-severity">
                        {issues.critical_issues.length > 0 && (
                            <div className="mb-6">
                                <h3 className="text-lg font-semibold mb-3 text-red-600">Critical Issues</h3>
                                {issues.critical_issues.map((issue, idx) => renderIssueCard(issue, `critical-${idx}`))}
                            </div>
                        )}
                        {issues.warnings.length > 0 && (
                            <div>
                                <h3 className="text-lg font-semibold mb-3 text-yellow-600">Warnings</h3>
                                {issues.warnings.map((issue, idx) => renderIssueCard(issue, `warning-${idx}`))}
                            </div>
                        )}
                    </TabsContent>
                    
                    <TabsContent value="by-type">
                        {Object.entries(issues.issues_by_type || {}).map(([type, typeIssues]) => (
                            typeIssues.length > 0 && (
                                <div key={type} className="mb-6">
                                    <h3 className="text-lg font-semibold mb-3">{type.replace(/_/g, ' ')}</h3>
                                    {typeIssues.map((issue, idx) => renderIssueCard(issue, `${type}-${idx}`))}
                                </div>
                            )
                        ))}
                    </TabsContent>
                    
                    <TabsContent value="all">
                        {[...issues.critical_issues, ...issues.warnings].map((issue, idx) => 
                            renderIssueCard(issue, `all-${idx}`)
                        )}
                    </TabsContent>
                </Tabs>
            </div>

            {/* Fix Preview Modal */}
            {selectedIssue && fixPreview && (
                <div 
                    className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
                    role="dialog"
                    aria-modal="true"
                    aria-labelledby="modal-title"
                    onClick={(e) => {
                        if (e.target === e.currentTarget) {
                            setSelectedIssue(null);
                            setFixPreview(null);
                        }
                    }}
                >
                    <Card className="max-w-2xl w-full max-h-[80vh] overflow-y-auto">
                        <CardHeader>
                            <CardTitle id="modal-title">Fix Preview</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                <div>
                                    <h4 className="font-semibold mb-2">What will happen:</h4>
                                    <p className="text-sm">{fixPreview.fix_explanation}</p>
                                </div>
                                
                                <div>
                                    <h4 className="font-semibold mb-2">SQL to execute:</h4>
                                    <pre className="bg-gray-100 p-3 rounded text-xs overflow-x-auto">
                                        {selectedIssue.fix_sql}
                                    </pre>
                                </div>
                                
                                <div>
                                    <h4 className="font-semibold mb-2">Impact Assessment:</h4>
                                    <div className="grid grid-cols-3 gap-2 text-sm">
                                        <div>
                                            <span className="text-gray-600">Risk:</span>
                                            <Badge variant={fixPreview.estimated_impact?.risk === 'low' ? 'success' : 'warning'}>
                                                {fixPreview.estimated_impact?.risk || 'unknown'}
                                            </Badge>
                                        </div>
                                        <div>
                                            <span className="text-gray-600">Downtime:</span>
                                            <Badge>{fixPreview.estimated_impact?.downtime || 'unknown'}</Badge>
                                        </div>
                                        <div>
                                            <span className="text-gray-600">Reversible:</span>
                                            <Badge variant={fixPreview.estimated_impact?.reversible ? 'success' : 'destructive'}>
                                                {fixPreview.estimated_impact?.reversible ? 'Yes' : 'No'}
                                            </Badge>
                                        </div>
                                    </div>
                                </div>
                                
                                {fixPreview.affected_data && (
                                    <div>
                                        <h4 className="font-semibold mb-2">Affected Data:</h4>
                                        <pre className="bg-gray-100 p-3 rounded text-xs">
                                            {JSON.stringify(fixPreview.affected_data, null, 2)}
                                        </pre>
                                    </div>
                                )}
                                
                                <div className="flex justify-end gap-3 mt-6">
                                    <Button variant="outline" onClick={() => {
                                        setSelectedIssue(null);
                                        setFixPreview(null);
                                    }}>
                                        Cancel
                                    </Button>
                                    <Button 
                                        variant="destructive" 
                                        onClick={() => applyFix(selectedIssue)}
                                        disabled={fixingIssue}
                                    >
                                        {fixingIssue ? (
                                            <>
                                                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                                Applying Fix...
                                            </>
                                        ) : (
                                            'Apply Fix'
                                        )}
                                    </Button>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            )}
        </div>
    );
}