import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
    TestTube, 
    Play, 
    RefreshCw, 
    TrendingUp, 
    TrendingDown,
    Clock,
    CheckCircle,
    XCircle,
    AlertTriangle,
    BarChart3,
    Activity,
    Download,
    Filter,
    Search
} from 'lucide-react';
import TestStatusCard from './TestStatusCard';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://jyotiflow-ai.onrender.com';

const TestResultsDashboard = () => {
    const [testSessions, setTestSessions] = useState([]);
    const [testMetrics, setTestMetrics] = useState({
        total_sessions: 0,
        success_rate: 0,
        avg_execution_time: 0,
        coverage_trend: 0,
        auto_fixes_applied: 0
    });
    const [selectedSession, setSelectedSession] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [filter, setFilter] = useState('all');
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        fetchTestData();
        const interval = setInterval(fetchTestData, 60000); // Refresh every minute
        return () => clearInterval(interval);
    }, []);

    const fetchTestData = async () => {
        try {
            setError(null);
            
            // Fetch test sessions
            const sessionsResponse = await fetch(`${API_BASE_URL}/api/monitoring/test-sessions`);
            if (sessionsResponse.ok) {
                const sessionsData = await sessionsResponse.json();
                setTestSessions(sessionsData.data || []);
            }
            
            // Fetch test metrics
            const metricsResponse = await fetch(`${API_BASE_URL}/api/monitoring/test-metrics`);
            if (metricsResponse.ok) {
                const metricsData = await metricsResponse.json();
                setTestMetrics(metricsData.data || testMetrics);
            }
            
        } catch (err) {
            setError('Failed to fetch test data');
        } finally {
            setLoading(false);
        }
    };

    const executeNewTest = async (testType) => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/monitoring/test-execute`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    test_type: testType,
                    environment: 'production',
                    triggered_by: 'manual'
                })
            });
            
            if (response.ok) {
                // Refresh data after starting test
                setTimeout(fetchTestData, 2000);
            }
        } catch (err) {
            setError('Failed to execute test');
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'passed': return 'bg-green-100 text-green-800';
            case 'failed': return 'bg-red-100 text-red-800';
            case 'running': return 'bg-blue-100 text-blue-800';
            case 'partial': return 'bg-yellow-100 text-yellow-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case 'passed': return <CheckCircle className="h-4 w-4" />;
            case 'failed': return <XCircle className="h-4 w-4" />;
            case 'running': return <Clock className="h-4 w-4" />;
            case 'partial': return <AlertTriangle className="h-4 w-4" />;
            default: return <TestTube className="h-4 w-4" />;
        }
    };

    const filteredSessions = testSessions.filter(session => {
        if (filter !== 'all' && session.status !== filter) return false;
        if (searchTerm && !session.test_type.toLowerCase().includes(searchTerm.toLowerCase())) return false;
        return true;
    });

    const TestExecutionHistory = () => (
        <Card>
            <CardHeader>
                <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2">
                        <Activity className="h-5 w-5" />
                        Test Execution History
                    </CardTitle>
                    <div className="flex items-center gap-2">
                        <select 
                            value={filter} 
                            onChange={(e) => setFilter(e.target.value)}
                            className="px-3 py-1 border rounded text-sm"
                        >
                            <option value="all">All Tests</option>
                            <option value="passed">Passed</option>
                            <option value="failed">Failed</option>
                            <option value="running">Running</option>
                        </select>
                        <Button size="sm" onClick={() => fetchTestData()}>
                            <RefreshCw className="h-4 w-4" />
                        </Button>
                    </div>
                </div>
            </CardHeader>
            <CardContent>
                <div className="space-y-3">
                    {filteredSessions.length === 0 ? (
                        <div className="text-center py-8 text-gray-500">
                            <TestTube className="h-12 w-12 mx-auto mb-4 opacity-50" />
                            <p>No test sessions found</p>
                            <p className="text-sm">Run your first test to see results here</p>
                        </div>
                    ) : (
                        filteredSessions.map((session) => (
                            <div 
                                key={session.session_id} 
                                className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 cursor-pointer"
                                onClick={() => setSelectedSession(session)}
                            >
                                <div className="flex items-center gap-3">
                                    {getStatusIcon(session.status)}
                                    <div>
                                        <div className="font-medium">{session.test_type}</div>
                                        <div className="text-sm text-gray-600">
                                            {new Date(session.started_at).toLocaleString()}
                                        </div>
                                    </div>
                                </div>
                                <div className="flex items-center gap-2">
                                    <Badge className={getStatusColor(session.status)}>
                                        {session.status}
                                    </Badge>
                                    {session.total_tests > 0 && (
                                        <span className="text-sm text-gray-600">
                                            {session.passed_tests}/{session.total_tests}
                                        </span>
                                    )}
                                    {session.execution_time_seconds && (
                                        <span className="text-sm text-gray-600">
                                            {session.execution_time_seconds}s
                                        </span>
                                    )}
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </CardContent>
        </Card>
    );

    const TestMetricsOverview = () => (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <Card>
                <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-600">Success Rate</p>
                            <p className="text-2xl font-bold">{testMetrics.success_rate}%</p>
                        </div>
                        <div className="p-2 bg-green-100 rounded">
                            <TrendingUp className="h-6 w-6 text-green-600" />
                        </div>
                    </div>
                </CardContent>
            </Card>
            
            <Card>
                <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-600">Total Sessions</p>
                            <p className="text-2xl font-bold">{testMetrics.total_sessions}</p>
                        </div>
                        <div className="p-2 bg-blue-100 rounded">
                            <BarChart3 className="h-6 w-6 text-blue-600" />
                        </div>
                    </div>
                </CardContent>
            </Card>
            
            <Card>
                <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-600">Avg Execution</p>
                            <p className="text-2xl font-bold">{testMetrics.avg_execution_time}s</p>
                        </div>
                        <div className="p-2 bg-yellow-100 rounded">
                            <Clock className="h-6 w-6 text-yellow-600" />
                        </div>
                    </div>
                </CardContent>
            </Card>
            
            <Card>
                <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-600">Auto-Fixes</p>
                            <p className="text-2xl font-bold">{testMetrics.auto_fixes_applied}</p>
                        </div>
                        <div className="p-2 bg-purple-100 rounded">
                            <RefreshCw className="h-6 w-6 text-purple-600" />
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );

    const TestExecutionPanel = () => (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <Play className="h-5 w-5" />
                    Test Execution
                </CardTitle>
            </CardHeader>
            <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                    <Button 
                        onClick={() => executeNewTest('unit')}
                        className="flex items-center gap-2"
                    >
                        <TestTube className="h-4 w-4" />
                        Unit Tests
                    </Button>
                    <Button 
                        onClick={() => executeNewTest('integration')}
                        variant="outline"
                        className="flex items-center gap-2"
                    >
                        <Activity className="h-4 w-4" />
                        Integration
                    </Button>
                    <Button 
                        onClick={() => executeNewTest('performance')}
                        variant="outline"
                        className="flex items-center gap-2"
                    >
                        <BarChart3 className="h-4 w-4" />
                        Performance
                    </Button>
                    <Button 
                        onClick={() => executeNewTest('security')}
                        variant="outline"
                        className="flex items-center gap-2"
                    >
                        <AlertTriangle className="h-4 w-4" />
                        Security
                    </Button>
                </div>
            </CardContent>
        </Card>
    );

    const SessionDetailModal = () => {
        if (!selectedSession) return null;
        
        return (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                <Card className="w-full max-w-2xl max-h-[80vh] overflow-y-auto">
                    <CardHeader>
                        <div className="flex items-center justify-between">
                            <CardTitle className="flex items-center gap-2">
                                {getStatusIcon(selectedSession.status)}
                                Test Session Details
                            </CardTitle>
                            <Button 
                                variant="outline" 
                                size="sm"
                                onClick={() => setSelectedSession(null)}
                            >
                                ✕
                            </Button>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="text-sm font-medium">Test Type</label>
                                    <p className="text-sm text-gray-600">{selectedSession.test_type}</p>
                                </div>
                                <div>
                                    <label className="text-sm font-medium">Status</label>
                                    <Badge className={getStatusColor(selectedSession.status)}>
                                        {selectedSession.status}
                                    </Badge>
                                </div>
                                <div>
                                    <label className="text-sm font-medium">Started</label>
                                    <p className="text-sm text-gray-600">
                                        {new Date(selectedSession.started_at).toLocaleString()}
                                    </p>
                                </div>
                                <div>
                                    <label className="text-sm font-medium">Duration</label>
                                    <p className="text-sm text-gray-600">
                                        {selectedSession.execution_time_seconds || 0}s
                                    </p>
                                </div>
                            </div>
                            
                            {selectedSession.total_tests > 0 && (
                                <div className="grid grid-cols-3 gap-4 p-4 bg-gray-50 rounded">
                                    <div className="text-center">
                                        <div className="text-lg font-bold text-green-600">
                                            {selectedSession.passed_tests}
                                        </div>
                                        <div className="text-sm text-gray-600">Passed</div>
                                    </div>
                                    <div className="text-center">
                                        <div className="text-lg font-bold text-red-600">
                                            {selectedSession.failed_tests}
                                        </div>
                                        <div className="text-sm text-gray-600">Failed</div>
                                    </div>
                                    <div className="text-center">
                                        <div className="text-lg font-bold">
                                            {selectedSession.total_tests}
                                        </div>
                                        <div className="text-sm text-gray-600">Total</div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </CardContent>
                </Card>
            </div>
        );
    };

    if (loading) {
        return (
            <div className="p-6">
                <div className="flex items-center space-x-2 mb-6">
                    <RefreshCw className="h-5 w-5 animate-spin" />
                    <span>Loading test results...</span>
                </div>
            </div>
        );
    }

    return (
        <div className="p-6 space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold flex items-center gap-2">
                    <TestTube className="h-6 w-6" />
                    Test Results Dashboard
                </h1>
                <Button onClick={() => fetchTestData()}>
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Refresh
                </Button>
            </div>

            {error && (
                <Alert>
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>{error}</AlertDescription>
                </Alert>
            )}

            <TestMetricsOverview />
            
            <TestExecutionPanel />

            <Tabs defaultValue="history" className="space-y-4">
                <TabsList>
                    <TabsTrigger value="history">Execution History</TabsTrigger>
                    <TabsTrigger value="coverage">Coverage Reports</TabsTrigger>
                    <TabsTrigger value="performance">Performance Metrics</TabsTrigger>
                    <TabsTrigger value="autofix">Auto-Fix Results</TabsTrigger>
                </TabsList>

                <TabsContent value="history">
                    <TestExecutionHistory />
                </TabsContent>

                <TabsContent value="coverage">
                    <Card>
                        <CardHeader>
                            <CardTitle>Test Coverage Reports</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="text-center py-8 text-gray-500">
                                <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
                                <p>Coverage reports will be displayed here</p>
                                <p className="text-sm">Run tests to generate coverage data</p>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="performance">
                    <Card>
                        <CardHeader>
                            <CardTitle>Performance Metrics</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="text-center py-8 text-gray-500">
                                <TrendingUp className="h-12 w-12 mx-auto mb-4 opacity-50" />
                                <p>Performance metrics will be displayed here</p>
                                <p className="text-sm">Run performance tests to see metrics</p>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="autofix">
                    <Card>
                        <CardHeader>
                            <CardTitle>Auto-Fix Test Results</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="text-center py-8 text-gray-500">
                                <RefreshCw className="h-12 w-12 mx-auto mb-4 opacity-50" />
                                <p>Auto-fix test results will be displayed here</p>
                                <p className="text-sm">Auto-fix actions will generate test validation data</p>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>

            <SessionDetailModal />
        </div>
    );
};

export default TestResultsDashboard;