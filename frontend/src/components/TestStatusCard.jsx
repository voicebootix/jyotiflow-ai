import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
    TestTube, 
    Activity,
    TrendingUp,
    TrendingDown,
    Play,
    RefreshCw,
    Video
} from 'lucide-react';
import { getStatusColor, getStatusIcon, getStatusBadgeColor } from '../utils/testStatus.jsx';

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
    const [businessLogicStatus, setBusinessLogicStatus] = useState({
        success_rate: 0,
        total_validations: 0,
        avg_quality_score: 0
    });
    const [spiritualServicesStatus, setSpiritualServicesStatus] = useState({
        spiritual_avatar_engine: { available: false },
        monetization_optimizer: { available: false },
        recent_metrics: { sessions_24h: 0, successful_validations_24h: 0 }
    });
    const [socialMediaStatus, setSocialMediaStatus] = useState({
        social_media_engine: { available: false },
        social_media_validator: { available: false },
        metrics: { campaigns_7d: 0, posts_24h: 0, active_campaigns: 0 },
        automation_health: { overall_status: 'unknown' }
    });
    const [liveAudioVideoStatus, setLiveAudioVideoStatus] = useState({
        overall_status: 'unknown',
        system_health_score: 0,
        agora_service: { available: false },
        livechat_router: { available: false },
        database: { available: false, tables: {} },
        frontend_components: { available: false, components: {} },
        session_metrics: {
            active_sessions: 0,
            sessions_24h: 0,
            total_revenue_24h: 0.0
        }
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [executingTest, setExecutingTest] = useState(false);

    useEffect(() => {
        fetchAllStatus();
        // Refresh every 30 seconds
        const interval = setInterval(fetchAllStatus, 30000);
        return () => clearInterval(interval);
    }, []);

    const fetchAllStatus = async () => {
        await Promise.all([
            fetchTestStatus(),
            fetchBusinessLogicStatus(),
            fetchSpiritualServicesStatus(),
            fetchSocialMediaStatus(),
            fetchLiveAudioVideoStatus()
        ]);
    };

    const fetchTestStatus = async () => {
        try {
            setError(null);
            const response = await fetch(`${API_BASE_URL}/api/monitoring/test-status`);
            if (response.ok) {
                const data = await response.json();
                setTestStatus(prevStatus => data.data || prevStatus);
            } else if (response.status === 404) {
                setError('Testing infrastructure not yet deployed');
            } else {
                setError(`Failed to fetch test status: ${response.status}`);
            }
        } catch (err) {
            setError(`Connection error: ${err.message}`);
        } finally {
            setLoading(false);
        }
    };

    const fetchBusinessLogicStatus = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/monitoring/business-logic-validation`);
            if (response.ok) {
                const data = await response.json();
                setBusinessLogicStatus(prevStatus => data.data?.summary || prevStatus);
            }
        } catch (err) {
            console.warn('Business logic status not available:', err.message);
        }
    };

    const fetchSpiritualServicesStatus = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/monitoring/spiritual-services-status`);
            if (response.ok) {
                const data = await response.json();
                setSpiritualServicesStatus(prevStatus => data.data || prevStatus);
            }
        } catch (err) {
            console.warn('Spiritual services status not available:', err.message);
        }
    };

    const fetchSocialMediaStatus = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/monitoring/social-media-status`);
            if (response.ok) {
                const data = await response.json();
                setSocialMediaStatus(prevStatus => data.data || prevStatus);
            }
        } catch (err) {
            console.warn('Social media status not available:', err.message);
        }
    };

    const fetchLiveAudioVideoStatus = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/monitoring/live-audio-video-status`);
            if (response.ok) {
                const data = await response.json();
                setLiveAudioVideoStatus(prevStatus => data.data || prevStatus);
            }
        } catch (err) {
            console.warn('Live audio/video status not available:', err.message);
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
                setTimeout(fetchAllStatus, 2000);
            }
        } catch (err) {
            setError('Failed to execute tests');
        } finally {
            setExecutingTest(false);
        }
    };

    // Status functions now imported from shared utility

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
                                <Badge className={`text-xs ${getStatusBadgeColor(testStatus.status)}`}>
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
                    
                    {/* Business Logic Validation Status */}
                    {businessLogicStatus.total_validations > 0 && (
                        <div className="mt-4 pt-4 border-t border-gray-200">
                            <div className="flex items-center justify-between mb-2">
                                <div className="flex items-center gap-1">
                                    <Activity className="h-3 w-3" />
                                    <span className="text-xs font-medium">Spiritual Content Quality</span>
                                </div>
                                <Badge className={`text-xs ${businessLogicStatus.success_rate > 80 ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                                    {Math.round(businessLogicStatus.success_rate)}%
                                </Badge>
                            </div>
                            <div className="grid grid-cols-2 gap-2 text-xs text-gray-600">
                                <div>Quality Score: {businessLogicStatus.avg_quality_score.toFixed(1)}</div>
                                <div>Validations: {businessLogicStatus.total_validations}</div>
                            </div>
                        </div>
                    )}
                    
                    {/* Spiritual Services Status */}
                    {(spiritualServicesStatus.spiritual_avatar_engine.available || spiritualServicesStatus.monetization_optimizer.available) && (
                        <div className="mt-4 pt-4 border-t border-gray-200">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-xs font-medium">Spiritual Services</span>
                                <div className="flex gap-1">
                                    {spiritualServicesStatus.spiritual_avatar_engine.available && (
                                        <div className="h-2 w-2 bg-green-500 rounded-full" title="Avatar Engine Online" />
                                    )}
                                    {spiritualServicesStatus.monetization_optimizer.available && (
                                        <div className="h-2 w-2 bg-blue-500 rounded-full" title="Monetization Online" />
                                    )}
                                </div>
                            </div>
                            <div className="grid grid-cols-2 gap-2 text-xs text-gray-600">
                                <div>Sessions: {spiritualServicesStatus.recent_metrics.sessions_24h}</div>
                                <div>Validations: {spiritualServicesStatus.recent_metrics.successful_validations_24h}</div>
                            </div>
                        </div>
                    )}
                    
                    {/* Social Media Automation Status - BUSINESS CRITICAL */}
                    {(socialMediaStatus.social_media_engine.available || socialMediaStatus.metrics.campaigns_7d > 0) && (
                        <div className="mt-4 pt-4 border-t border-gray-200">
                            <div className="flex items-center justify-between mb-2">
                                <div className="flex items-center gap-1">
                                    <Activity className="h-3 w-3" />
                                    <span className="text-xs font-medium">Social Media Automation</span>
                                    <Badge className={`text-xs ml-1 ${socialMediaStatus.automation_health.overall_status === 'healthy' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                        {socialMediaStatus.automation_health.overall_status?.toUpperCase() || 'UNKNOWN'}
                                    </Badge>
                                </div>
                                <div className="flex gap-1">
                                    {socialMediaStatus.social_media_engine.available && (
                                        <div className="h-2 w-2 bg-green-500 rounded-full" title="Marketing Engine Online" />
                                    )}
                                    {socialMediaStatus.social_media_validator.available && (
                                        <div className="h-2 w-2 bg-blue-500 rounded-full" title="Content Validator Online" />
                                    )}
                                </div>
                            </div>
                            <div className="grid grid-cols-3 gap-2 text-xs text-gray-600">
                                <div>Campaigns: {socialMediaStatus.metrics.campaigns_7d}</div>
                                <div>Posts: {socialMediaStatus.metrics.posts_24h}</div>
                                <div>Active: {socialMediaStatus.metrics.active_campaigns}</div>
                            </div>
                        </div>
                    )}
                    
                    {/* Live Audio/Video Status - REVENUE CRITICAL */}
                    {(liveAudioVideoStatus.agora_service.available || liveAudioVideoStatus.session_metrics.active_sessions > 0) && (
                        <div className="mt-4 pt-4 border-t border-gray-200">
                            <div className="flex items-center justify-between mb-2">
                                <div className="flex items-center gap-1">
                                    <Video className="h-3 w-3" />
                                    <span className="text-xs font-medium">Live Audio/Video</span>
                                    <Badge className={`text-xs ml-1 ${liveAudioVideoStatus.overall_status === 'healthy' ? 'bg-green-100 text-green-800' : liveAudioVideoStatus.overall_status === 'degraded' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'}`}>
                                        {liveAudioVideoStatus.overall_status?.toUpperCase() || 'UNKNOWN'}
                                    </Badge>
                                </div>
                                <div className="flex gap-1">
                                    {liveAudioVideoStatus.agora_service.available && (
                                        <div className="h-2 w-2 bg-green-500 rounded-full" title="Agora Service Online" />
                                    )}
                                    {liveAudioVideoStatus.livechat_router.available && (
                                        <div className="h-2 w-2 bg-blue-500 rounded-full" title="Live Chat Router Online" />
                                    )}
                                    {liveAudioVideoStatus.database.available && (
                                        <div className="h-2 w-2 bg-purple-500 rounded-full" title="Database Ready" />
                                    )}
                                </div>
                            </div>
                            <div className="grid grid-cols-3 gap-2 text-xs text-gray-600">
                                <div>Active: {liveAudioVideoStatus.session_metrics.active_sessions}</div>
                                <div>24h Sessions: {liveAudioVideoStatus.session_metrics.sessions_24h}</div>
                                <div>Revenue: ${liveAudioVideoStatus.session_metrics.total_revenue_24h.toFixed(0)}</div>
                            </div>
                        </div>
                    )}
                    
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
                            <Badge className={getStatusBadgeColor(testStatus.status)}>
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
            <Badge className={`text-xs ${getStatusBadgeColor(testStatus.status)}`}>
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