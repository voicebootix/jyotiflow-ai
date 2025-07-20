import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
    TestTube, 
    CheckCircle, 
    XCircle, 
    Clock, 
    Activity,
    TrendingUp,
    TrendingDown,
    AlertTriangle,
    Play,
    RefreshCw
} from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://jyotiflow-ai.onrender.com';

const TestStatusCard = ({ variant = 'summary', className = '' }) => {
    const [testStatus, setTestStatus] = useState({
        last_execution: null,
        total_tests: 0,
        passed_tests: 0,
        failed_tests: 0,
        test_coverage: 0,
        execution_time: 0,
        status: 'unknown',
        auto_fixes_applied: 0
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [executingTest, setExecutingTest] = useState(false);

    useEffect(() => {
        fetchTestStatus();
        // Refresh every 30 seconds
        const interval = setInterval(fetchTestStatus, 30000);
        return () => clearInterval(interval);
    }, []);

    const fetchTestStatus = async () => {
        try {
            setError(null);
            const response = await fetch(`${API_BASE_URL}/api/monitoring/test-status`);
            if (response.ok) {
                const data = await response.json();
                setTestStatus(data.data || testStatus);
            } else if (response.status === 404) {
                // Test status endpoint not yet available
                setTestStatus({
                    ...testStatus,
                    status: 'not_available'
                });
            }
        } catch (err) {
            setError('Failed to fetch test status');
            setTestStatus({
                ...testStatus,
                status: 'error'
            });
        } finally {
            setLoading(false);
        }
    };

    const executeTests = async (testType = 'quick') => {
        setExecutingTest(true);
        try {
            const response = await fetch(`${API_BASE_URL}/api/monitoring/test-execute`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ test_type: testType })
            });
            
            if (response.ok) {
                // Refresh status after execution
                setTimeout(fetchTestStatus, 2000);
            }
        } catch (err) {
            setError('Failed to execute tests');
        } finally {
            setExecutingTest(false);
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'passed': return 'text-green-600 bg-green-100';
            case 'failed': return 'text-red-600 bg-red-100';
            case 'running': return 'text-blue-600 bg-blue-100';
            case 'partial': return 'text-yellow-600 bg-yellow-100';
            case 'not_available': return 'text-gray-600 bg-gray-100';
            case 'error': return 'text-red-600 bg-red-100';
            default: return 'text-gray-600 bg-gray-100';
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

    const calculateSuccessRate = () => {
        if (testStatus.total_tests === 0) return 0;
        return Math.round((testStatus.passed_tests / testStatus.total_tests) * 100);
    };

    if (loading) {
        return (
            <Card className={className}>
                <CardContent className="p-4">
                    <div className="flex items-center space-x-2">
                        <RefreshCw className="h-4 w-4 animate-spin" />
                        <span className="text-sm text-gray-600">Loading test status...</span>
                    </div>
                </CardContent>
            </Card>
        );
    }

    if (variant === 'summary') {
        return (
            <Card className={className}>
                <CardHeader className="pb-2">
                    <CardTitle className="flex items-center gap-2 text-sm font-medium">
                        <TestTube className="h-4 w-4" />
                        Test Status
                    </CardTitle>
                </CardHeader>
                <CardContent className="p-4 pt-0">
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <div className="flex items-center gap-1 mb-1">
                                {getStatusIcon(testStatus.status)}
                                <Badge className={`text-xs ${getStatusColor(testStatus.status)}`}>
                                    {testStatus.status.replace('_', ' ').toUpperCase()}
                                </Badge>
                            </div>
                            <p className="text-xs text-gray-600">
                                {testStatus.total_tests > 0 
                                    ? `${testStatus.passed_tests}/${testStatus.total_tests} passed`
                                    : 'No tests run yet'
                                }
                            </p>
                        </div>
                        <div>
                            <div className="text-right">
                                <div className="text-lg font-bold">
                                    {testStatus.test_coverage > 0 ? `${testStatus.test_coverage}%` : 'N/A'}
                                </div>
                                <p className="text-xs text-gray-600">Coverage</p>
                            </div>
                        </div>
                    </div>
                    
                    {error && (
                        <Alert className="mt-2">
                            <AlertTriangle className="h-4 w-4" />
                            <AlertDescription className="text-xs">{error}</AlertDescription>
                        </Alert>
                    )}
                </CardContent>
            </Card>
        );
    }

    if (variant === 'detailed') {
        return (
            <Card className={className}>
                <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                        <span className="flex items-center gap-2">
                            <TestTube className="h-5 w-5" />
                            Test Execution Status
                        </span>
                        <Button 
                            size="sm" 
                            onClick={() => executeTests('quick')}
                            disabled={executingTest}
                        >
                            {executingTest ? (
                                <RefreshCw className="h-4 w-4 animate-spin mr-1" />
                            ) : (
                                <Play className="h-4 w-4 mr-1" />
                            )}
                            Run Tests
                        </Button>
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                        <div className="text-center p-3 bg-gray-50 rounded-lg">
                            <div className="text-2xl font-bold text-gray-900">
                                {calculateSuccessRate()}%
                            </div>
                            <p className="text-sm text-gray-600">Success Rate</p>
                        </div>
                        <div className="text-center p-3 bg-gray-50 rounded-lg">
                            <div className="text-2xl font-bold text-gray-900">
                                {testStatus.test_coverage || 0}%
                            </div>
                            <p className="text-sm text-gray-600">Coverage</p>
                        </div>
                        <div className="text-center p-3 bg-gray-50 rounded-lg">
                            <div className="text-2xl font-bold text-gray-900">
                                {testStatus.auto_fixes_applied || 0}
                            </div>
                            <p className="text-sm text-gray-600">Auto-Fixes</p>
                        </div>
                    </div>

                    <div className="space-y-3">
                        <div className="flex justify-between items-center">
                            <span className="text-sm font-medium">Status:</span>
                            <Badge className={getStatusColor(testStatus.status)}>
                                {getStatusIcon(testStatus.status)}
                                <span className="ml-1">{testStatus.status.replace('_', ' ').toUpperCase()}</span>
                            </Badge>
                        </div>
                        
                        <div className="flex justify-between items-center">
                            <span className="text-sm font-medium">Total Tests:</span>
                            <span className="text-sm">{testStatus.total_tests}</span>
                        </div>
                        
                        <div className="flex justify-between items-center">
                            <span className="text-sm font-medium">Passed:</span>
                            <span className="text-sm text-green-600">{testStatus.passed_tests}</span>
                        </div>
                        
                        <div className="flex justify-between items-center">
                            <span className="text-sm font-medium">Failed:</span>
                            <span className="text-sm text-red-600">{testStatus.failed_tests}</span>
                        </div>
                        
                        {testStatus.execution_time > 0 && (
                            <div className="flex justify-between items-center">
                                <span className="text-sm font-medium">Last Execution:</span>
                                <span className="text-sm">{testStatus.execution_time}s</span>
                            </div>
                        )}
                        
                        {testStatus.last_execution && (
                            <div className="flex justify-between items-center">
                                <span className="text-sm font-medium">Last Run:</span>
                                <span className="text-xs text-gray-600">
                                    {new Date(testStatus.last_execution).toLocaleString()}
                                </span>
                            </div>
                        )}
                    </div>

                    {error && (
                        <Alert className="mt-4">
                            <AlertTriangle className="h-4 w-4" />
                            <AlertDescription>{error}</AlertDescription>
                        </Alert>
                    )}
                </CardContent>
            </Card>
        );
    }

    // Default compact variant
    return (
        <div className={`flex items-center space-x-2 ${className}`}>
            {getStatusIcon(testStatus.status)}
            <span className="text-sm font-medium">Tests:</span>
            <Badge className={`text-xs ${getStatusColor(testStatus.status)}`}>
                {testStatus.total_tests > 0 
                    ? `${testStatus.passed_tests}/${testStatus.total_tests}`
                    : 'N/A'
                }
            </Badge>
            {testStatus.test_coverage > 0 && (
                <span className="text-xs text-gray-600">
                    {testStatus.test_coverage}% coverage
                </span>
            )}
        </div>
    );
};

export default TestStatusCard;