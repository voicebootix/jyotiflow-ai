import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
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
    Search,
    Database,
    DollarSign,
    Users
} from 'lucide-react';
import TestStatusCard from './TestStatusCard';
import ServiceStatusCard from './ServiceStatusCard';
import AllServicesTab from './AllServicesTab';

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
                setTestMetrics(prevMetrics => metricsData.data || prevMetrics);
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

    const BusinessLogicValidationTab = () => {
        const [businessLogicData, setBusinessLogicData] = useState({
            summary: {
                total_validations: 0,
                passed_validations: 0,
                success_rate: 0,
                avg_quality_score: 0
            },
            recent_validations: []
        });
        const [spiritualServices, setSpiritualServices] = useState({
            spiritual_avatar_engine: { available: false },
            monetization_optimizer: { available: false },
            recent_metrics: { sessions_24h: 0, successful_validations_24h: 0 }
        });
        const [validationLoading, setValidationLoading] = useState(false);

        useEffect(() => {
            fetchBusinessLogicData();
            fetchSpiritualServicesData();
        }, []);

        const fetchBusinessLogicData = async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/api/monitoring/business-logic-validation`);
                if (response.ok) {
                    const data = await response.json();
                    setBusinessLogicData(prevData => data.data || prevData);
                }
            } catch (err) {
                console.warn('Business logic data not available:', err.message);
            }
        };

        const fetchSpiritualServicesData = async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/api/monitoring/spiritual-services-status`);
                if (response.ok) {
                    const data = await response.json();
                    setSpiritualServices(prevData => data.data || prevData);
                }
            } catch (err) {
                console.warn('Spiritual services data not available:', err.message);
            }
        };

        const triggerValidation = async () => {
            setValidationLoading(true);
            try {
                const response = await fetch(`${API_BASE_URL}/api/monitoring/business-logic-validate`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ validation_type: 'test' })
                });
                
                if (response.ok) {
                    setTimeout(() => {
                        fetchBusinessLogicData();
                        fetchSpiritualServicesData();
                    }, 2000);
                }
            } catch (err) {
                console.error('Validation trigger failed:', err);
            } finally {
                setValidationLoading(false);
            }
        };

        return (
            <div className="space-y-6">
                {/* Spiritual Services Health */}
                <Card>
                    <CardHeader>
                        <div className="flex items-center justify-between">
                            <CardTitle className="flex items-center gap-2">
                                <Activity className="h-5 w-5" />
                                Spiritual Services Health
                            </CardTitle>
                            <Button 
                                size="sm" 
                                onClick={triggerValidation}
                                disabled={validationLoading}
                            >
                                {validationLoading ? (
                                    <RefreshCw className="h-4 w-4 animate-spin" />
                                ) : (
                                    <Play className="h-4 w-4" />
                                )}
                                Test Validation
                            </Button>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-3">
                                <div className="flex items-center justify-between p-3 border rounded">
                                    <div>
                                        <p className="font-medium">Spiritual Avatar Engine</p>
                                        <p className="text-sm text-gray-600">Personalized guidance generation</p>
                                    </div>
                                    <Badge className={spiritualServices.spiritual_avatar_engine.available ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                                        {spiritualServices.spiritual_avatar_engine.available ? 'Online' : 'Offline'}
                                    </Badge>
                                </div>
                                
                                <div className="flex items-center justify-between p-3 border rounded">
                                    <div>
                                        <p className="font-medium">Monetization Optimizer</p>
                                        <p className="text-sm text-gray-600">AI-powered pricing recommendations</p>
                                    </div>
                                    <Badge className={spiritualServices.monetization_optimizer.available ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                                        {spiritualServices.monetization_optimizer.available ? 'Online' : 'Offline'}
                                    </Badge>
                                </div>
                            </div>
                            
                            <div className="space-y-3">
                                <div className="p-3 bg-blue-50 rounded">
                                    <p className="text-sm font-medium text-blue-800">24h Spiritual Sessions</p>
                                    <p className="text-2xl font-bold text-blue-600">{spiritualServices.recent_metrics.sessions_24h}</p>
                                </div>
                                
                                <div className="p-3 bg-green-50 rounded">
                                    <p className="text-sm font-medium text-green-800">Successful Validations</p>
                                    <p className="text-2xl font-bold text-green-600">{spiritualServices.recent_metrics.successful_validations_24h}</p>
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Business Logic Validation Results */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <CheckCircle className="h-5 w-5" />
                            Spiritual Content Quality Validation
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        {businessLogicData.summary.total_validations > 0 ? (
                            <div className="space-y-4">
                                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                                    <div className="text-center p-3 bg-gray-50 rounded">
                                        <p className="text-sm font-medium">Total Validations</p>
                                        <p className="text-xl font-bold">{businessLogicData.summary.total_validations}</p>
                                    </div>
                                    <div className="text-center p-3 bg-green-50 rounded">
                                        <p className="text-sm font-medium">Success Rate</p>
                                        <p className="text-xl font-bold text-green-600">{Math.round(businessLogicData.summary.success_rate)}%</p>
                                    </div>
                                    <div className="text-center p-3 bg-blue-50 rounded">
                                        <p className="text-sm font-medium">Quality Score</p>
                                        <p className="text-xl font-bold text-blue-600">{businessLogicData.summary.avg_quality_score.toFixed(1)}</p>
                                    </div>
                                    <div className="text-center p-3 bg-purple-50 rounded">
                                        <p className="text-sm font-medium">Passed</p>
                                        <p className="text-xl font-bold text-purple-600">{businessLogicData.summary.passed_validations}</p>
                                    </div>
                                </div>
                                
                                {businessLogicData.recent_validations.length > 0 && (
                                    <div>
                                        <h4 className="font-medium mb-3">Recent Validation Results</h4>
                                        <div className="space-y-2">
                                            {businessLogicData.recent_validations.slice(0, 5).map((validation, index) => (
                                                <div key={index} className="flex items-center justify-between p-3 border rounded">
                                                    <div>
                                                        <p className="font-medium">{validation.validation_type}</p>
                                                        <p className="text-sm text-gray-600">
                                                            {new Date(validation.created_at).toLocaleString()}
                                                        </p>
                                                    </div>
                                                    <div className="text-right">
                                                        <Badge className={validation.validation_result === 'passed' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                                                            {validation.validation_result}
                                                        </Badge>
                                                        {validation.quality_score && (
                                                            <p className="text-sm text-gray-600 mt-1">
                                                                Score: {validation.quality_score.toFixed(2)}
                                                            </p>
                                                        )}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className="text-center py-8 text-gray-500">
                                <Activity className="h-12 w-12 mx-auto mb-4 opacity-50" />
                                <p>No business logic validation data available</p>
                                <p className="text-sm">Trigger a validation test to see results</p>
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        );
    };

    const SocialMediaAutomationTab = () => {
        const [socialMediaData, setSocialMediaData] = useState({
            summary: {
                total_posts: 0,
                total_engagements: 0,
                total_followers: 0,
                avg_engagement_rate: 0
            },
            recent_posts: []
        });
        const [automationLoading, setAutomationLoading] = useState(false);

        useEffect(() => {
            fetchSocialMediaData();
        }, []);

        const fetchSocialMediaData = async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/api/monitoring/social-media-automation`);
                if (response.ok) {
                    const data = await response.json();
                    setSocialMediaData(prevData => data.data || prevData);
                }
            } catch (err) {
                console.warn('Social media data not available:', err.message);
            }
        };

        const triggerAutomation = async () => {
            setAutomationLoading(true);
            try {
                const response = await fetch(`${API_BASE_URL}/api/monitoring/social-media-automate`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ automation_type: 'test' })
                });
                
                if (response.ok) {
                    setTimeout(() => {
                        fetchSocialMediaData();
                    }, 2000);
                }
            } catch (err) {
                console.error('Automation trigger failed:', err);
            } finally {
                setAutomationLoading(false);
            }
        };

        return (
            <div className="space-y-6">
                {/* Social Media Automation Health */}
                <Card>
                    <CardHeader>
                        <div className="flex items-center justify-between">
                            <CardTitle className="flex items-center gap-2">
                                <Activity className="h-5 w-5" />
                                Social Media Automation
                            </CardTitle>
                            <Button 
                                size="sm" 
                                onClick={triggerAutomation}
                                disabled={automationLoading}
                            >
                                {automationLoading ? (
                                    <RefreshCw className="h-4 w-4 animate-spin" />
                                ) : (
                                    <Play className="h-4 w-4" />
                                )}
                                Test Automation
                            </Button>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-3">
                                <div className="flex items-center justify-between p-3 border rounded">
                                    <div>
                                        <p className="font-medium">Total Posts</p>
                                        <p className="text-sm text-gray-600">Automated posts across platforms</p>
                                    </div>
                                    <Badge className="bg-blue-100 text-blue-800">{socialMediaData.summary.total_posts}</Badge>
                                </div>
                                
                                <div className="flex items-center justify-between p-3 border rounded">
                                    <div>
                                        <p className="font-medium">Total Engagements</p>
                                        <p className="text-sm text-gray-600">Total interactions on posts</p>
                                    </div>
                                    <Badge className="bg-purple-100 text-purple-800">{socialMediaData.summary.total_engagements}</Badge>
                                </div>
                            </div>
                            
                            <div className="space-y-3">
                                <div className="p-3 bg-green-50 rounded">
                                    <p className="text-sm font-medium text-green-800">Total Followers</p>
                                    <p className="text-2xl font-bold text-green-600">{socialMediaData.summary.total_followers}</p>
                                </div>
                                
                                <div className="p-3 bg-yellow-50 rounded">
                                    <p className="text-sm font-medium text-yellow-800">Avg. Engagement Rate</p>
                                    <p className="text-2xl font-bold text-yellow-600">{socialMediaData.summary.avg_engagement_rate.toFixed(2)}%</p>
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Recent Social Media Posts */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Download className="h-5 w-5" />
                            Recent Social Media Posts
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        {socialMediaData.recent_posts.length > 0 ? (
                            <div className="space-y-3">
                                {socialMediaData.recent_posts.map((post, index) => (
                                    <div key={index} className="p-3 border rounded-lg bg-gray-50">
                                        <p className="font-medium">{post.platform}</p>
                                        <p className="text-sm text-gray-600">{post.content}</p>
                                        <p className="text-sm text-gray-600">Engagements: {post.engagements}</p>
                                        <p className="text-sm text-gray-600">Date: {new Date(post.posted_at).toLocaleString()}</p>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-8 text-gray-500">
                                <Download className="h-12 w-12 mx-auto mb-4 opacity-50" />
                                <p>No recent social media posts available</p>
                                <p className="text-sm">Trigger an automation test to see posts</p>
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        );
    };

    const LiveAudioVideoTab = () => {
        const [liveAudioVideoData, setLiveAudioVideoData] = useState({
            summary: {
                total_sessions: 0,
                active_sessions: 0,
                avg_latency: 0,
                success_rate: 0
            },
            recent_sessions: []
        });
        const [loading, setLoading] = useState(true);
        const [error, setError] = useState(null);

        useEffect(() => {
            fetchLiveAudioVideoData();
            const interval = setInterval(fetchLiveAudioVideoData, 30000); // Refresh every 30 seconds
            return () => clearInterval(interval);
        }, []);

        const fetchLiveAudioVideoData = async () => {
            try {
                setError(null);
                const response = await fetch(`${API_BASE_URL}/api/monitoring/live-audio-video-status`);
                if (response.ok) {
                    const data = await response.json();
                    setLiveAudioVideoData(data.data || liveAudioVideoData);
                } else {
                    setError('Failed to fetch live audio/video status');
                }
            } catch (err) {
                setError('Failed to fetch live audio/video status');
            } finally {
                setLoading(false);
            }
        };

        return (
            <div className="space-y-6">
                {loading ? (
                    <div className="text-center py-8 text-gray-500">
                        <Activity className="h-12 w-12 mx-auto mb-4 opacity-50" />
                        <p>Loading live audio/video status...</p>
                    </div>
                ) : error ? (
                    <Alert>
                        <AlertTriangle className="h-4 w-4" />
                        <AlertDescription>{error}</AlertDescription>
                    </Alert>
                ) : (
                    <>
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Activity className="h-5 w-5" />
                                    Live Audio/Video Overview
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div className="space-y-3">
                                        <div className="flex items-center justify-between p-3 border rounded">
                                            <div>
                                                <p className="font-medium">Total Sessions</p>
                                                <p className="text-sm text-gray-600">Total live audio/video sessions</p>
                                            </div>
                                            <Badge className="bg-blue-100 text-blue-800">{liveAudioVideoData.summary.total_sessions}</Badge>
                                        </div>
                                        <div className="flex items-center justify-between p-3 border rounded">
                                            <div>
                                                <p className="font-medium">Active Sessions</p>
                                                <p className="text-sm text-gray-600">Currently active audio/video streams</p>
                                            </div>
                                            <Badge className="bg-green-100 text-green-800">{liveAudioVideoData.summary.active_sessions}</Badge>
                                        </div>
                                    </div>
                                    <div className="space-y-3">
                                        <div className="p-3 bg-purple-50 rounded">
                                            <p className="text-sm font-medium text-purple-800">Avg. Latency</p>
                                            <p className="text-2xl font-bold text-purple-600">{liveAudioVideoData.summary.avg_latency.toFixed(2)}ms</p>
                                        </div>
                                        <div className="p-3 bg-yellow-50 rounded">
                                            <p className="text-sm font-medium text-yellow-800">Success Rate</p>
                                            <p className="text-2xl font-bold text-yellow-600">{liveAudioVideoData.summary.success_rate}%</p>
                                        </div>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Activity className="h-5 w-5" />
                                    Recent Live Audio/Video Sessions
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                {liveAudioVideoData.recent_sessions.length > 0 ? (
                                    <div className="space-y-3">
                                        {liveAudioVideoData.recent_sessions.map((session, index) => (
                                            <div key={index} className="p-3 border rounded-lg bg-gray-50">
                                                <p className="font-medium">Session {index + 1}</p>
                                                <p className="text-sm text-gray-600">Type: {session.session_type}</p>
                                                <p className="text-sm text-gray-600">Started: {new Date(session.started_at).toLocaleString()}</p>
                                                <p className="text-sm text-gray-600">Duration: {session.duration_seconds}s</p>
                                                <p className="text-sm text-gray-600">Status: {session.status}</p>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="text-center py-8 text-gray-500">
                                        <Activity className="h-12 w-12 mx-auto mb-4 opacity-50" />
                                        <p>No recent live audio/video sessions available</p>
                                        <p className="text-sm">Trigger a live audio/video test to see sessions</p>
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </>
                )}
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

            <Tabs defaultValue="overview" className="space-y-4">
                <TabsList className="grid w-full grid-cols-8 gap-1 text-xs">
                    <TabsTrigger value="overview">Overview</TabsTrigger>
                    <TabsTrigger value="core-services">Core Services</TabsTrigger>
                    <TabsTrigger value="revenue-critical">Revenue Critical</TabsTrigger>
                    <TabsTrigger value="user-experience">User Experience</TabsTrigger>
                    <TabsTrigger value="business-mgmt">Business Mgmt</TabsTrigger>
                    <TabsTrigger value="social-media">Social Media</TabsTrigger>
                    <TabsTrigger value="live-audio-video">Live Audio/Video</TabsTrigger>
                    <TabsTrigger value="all-services">All Services</TabsTrigger>
                </TabsList>

                <TabsContent value="overview" className="space-y-6">
                    <TestStatusCard variant="detailed" className="w-full" />
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <Card>
                            <CardContent className="p-4">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm font-medium">Total Sessions</p>
                                        <p className="text-2xl font-bold">{testMetrics.total_sessions}</p>
                                    </div>
                                    <TestTube className="h-8 w-8 text-blue-500" />
                                </div>
                            </CardContent>
                        </Card>
                        
                        <Card>
                            <CardContent className="p-4">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm font-medium">Success Rate</p>
                                        <p className="text-2xl font-bold">{testMetrics.success_rate}%</p>
                                    </div>
                                    {testMetrics.success_rate > 80 ? 
                                        <TrendingUp className="h-8 w-8 text-green-500" /> : 
                                        <TrendingDown className="h-8 w-8 text-red-500" />
                                    }
                                </div>
                            </CardContent>
                        </Card>
                        
                        <Card>
                            <CardContent className="p-4">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm font-medium">Avg. Execution Time</p>
                                        <p className="text-2xl font-bold">{testMetrics.avg_execution_time}s</p>
                                    </div>
                                    <Clock className="h-8 w-8 text-orange-500" />
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                <TabsContent value="history">
                    <TestExecutionHistory />
                </TabsContent>

                <TabsContent value="coverage">
                    <Card>
                        <CardHeader>
                            <CardTitle>Test Coverage Report</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                <div className="text-center py-8 text-gray-500">
                                    <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
                                    <p>Coverage reports will be available after test execution</p>
                                </div>
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
                            <div className="space-y-4">
                                <div className="text-center py-8 text-gray-500">
                                    <Activity className="h-12 w-12 mx-auto mb-4 opacity-50" />
                                    <p>Performance metrics will be displayed here</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="business-logic">
                    <BusinessLogicValidationTab />
                </TabsContent>

                <TabsContent value="social-media">
                    <SocialMediaAutomationTab />
                </TabsContent>

                <TabsContent value="live-audio-video">
                    <LiveAudioVideoTab />
                </TabsContent>

                <TabsContent value="core-services">
                    <div className="space-y-6">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Database className="h-5 w-5" />
                                    Core Platform Services
                                </CardTitle>
                                <CardDescription>
                                    Database, API, Integration, Security, Performance, and Auto-Healing Services
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                    <ServiceStatusCard 
                                        title="Database Tests"
                                        description="Core database operations and integrity"
                                        endpoint="/api/monitoring/test-execute"
                                        testType="database"
                                        icon="🗄️"
                                    />
                                    <ServiceStatusCard 
                                        title="API Tests"
                                        description="REST API endpoint functionality"
                                        endpoint="/api/monitoring/test-execute"
                                        testType="api"
                                        icon="🔌"
                                    />
                                    <ServiceStatusCard 
                                        title="Integration Tests"
                                        description="End-to-end workflow validation"
                                        endpoint="/api/monitoring/test-execute"
                                        testType="integration"
                                        icon="🔗"
                                    />
                                    <ServiceStatusCard 
                                        title="Performance Tests"
                                        description="Load and scalability testing"
                                        endpoint="/api/monitoring/test-execute"
                                        testType="performance"
                                        icon="⚡"
                                    />
                                    <ServiceStatusCard 
                                        title="Security Tests"
                                        description="Vulnerability protection validation"
                                        endpoint="/api/monitoring/test-execute"
                                        testType="security"
                                        icon="🔒"
                                    />
                                    <ServiceStatusCard 
                                        title="Auto-Healing Tests"
                                        description="Self-recovery mechanism testing"
                                        endpoint="/api/monitoring/test-execute"
                                        testType="auto_healing"
                                        icon="🔄"
                                    />
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                <TabsContent value="revenue-critical">
                    <div className="space-y-6">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <DollarSign className="h-5 w-5" />
                                    Revenue-Critical Services
                                </CardTitle>
                                <CardDescription>
                                    Credit & Payment Systems, Avatar Generation, and Spiritual Services
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                    <ServiceStatusCard 
                                        title="Credit & Payment Tests"
                                        description="Revenue processing and transactions"
                                        endpoint="/api/monitoring/test-execute"
                                        testType="credit_payment"
                                        icon="💳"
                                        priority="critical"
                                    />
                                    <ServiceStatusCard 
                                        title="Spiritual Services Tests"
                                        description="Core business logic and AI services"
                                        endpoint="/api/monitoring/test-execute"
                                        testType="spiritual_services"
                                        icon="🕉️"
                                        priority="critical"
                                    />
                                    <ServiceStatusCard 
                                        title="Avatar Generation Tests"
                                        description="Video creation and spiritual avatars"
                                        endpoint="/api/monitoring/test-execute"
                                        testType="avatar_generation"
                                        icon="🎭"
                                        priority="high"
                                    />
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                <TabsContent value="user-experience">
                    <div className="space-y-6">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Users className="h-5 w-5" />
                                    User Experience Services
                                </CardTitle>
                                <CardDescription>
                                    User Management, Community, and Notification Services
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                    <ServiceStatusCard 
                                        title="User Management Tests"
                                        description="Authentication and profile management"
                                        endpoint="/api/monitoring/test-execute"
                                        testType="user_management"
                                        icon="👤"
                                        priority="critical"
                                    />
                                    <ServiceStatusCard 
                                        title="Community Services Tests"
                                        description="Follow-up systems and user engagement"
                                        endpoint="/api/monitoring/test-execute"
                                        testType="community_services"
                                        icon="🤝"
                                        priority="medium"
                                    />
                                    <ServiceStatusCard 
                                        title="Notification Services Tests"
                                        description="Alerts and user communication"
                                        endpoint="/api/monitoring/test-execute"
                                        testType="notification_services"
                                        icon="🔔"
                                        priority="medium"
                                    />
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                <TabsContent value="business-mgmt">
                    <div className="space-y-6">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <BarChart3 className="h-5 w-5" />
                                    Business Management Services
                                </CardTitle>
                                <CardDescription>
                                    Admin Services and Analytics & Monitoring
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <ServiceStatusCard 
                                        title="Admin Services Tests"
                                        description="Dashboard, settings, and management"
                                        endpoint="/api/monitoring/test-execute"
                                        testType="admin_services"
                                        icon="⚙️"
                                        priority="high"
                                    />
                                    <ServiceStatusCard 
                                        title="Analytics & Monitoring Tests"
                                        description="Business intelligence and session tracking"
                                        endpoint="/api/monitoring/test-execute"
                                        testType="analytics_monitoring"
                                        icon="📊"
                                        priority="high"
                                    />
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                <TabsContent value="all-services">
                    <AllServicesTab />
                </TabsContent>
            </Tabs>

            <SessionDetailModal />
        </div>
    );
};

export default TestResultsDashboard;