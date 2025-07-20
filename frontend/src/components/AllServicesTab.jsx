import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
    Play, 
    RefreshCw, 
    CheckCircle, 
    XCircle, 
    AlertTriangle,
    Activity,
    Target
} from 'lucide-react';
import ServiceStatusCard from './ServiceStatusCard';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://jyotiflow-ai.onrender.com';

const AllServicesTab = () => {
    const [globalStatus, setGlobalStatus] = useState('idle');
    const [loading, setLoading] = useState(false);
    const [testResults, setTestResults] = useState({});

    const allServices = [
        // Core Platform Services
        { 
            category: "Core Platform", 
            services: [
                { title: "Database Tests", testType: "database", icon: "🗄️", priority: "critical", description: "Core database operations and data integrity" },
                { title: "API Tests", testType: "api", icon: "🔌", priority: "critical", description: "REST API endpoint functionality" },
                { title: "Integration Tests", testType: "integration", icon: "🔗", priority: "high", description: "End-to-end workflow validation" },
                { title: "Performance Tests", testType: "performance", icon: "⚡", priority: "high", description: "Load and scalability testing" },
                { title: "Security Tests", testType: "security", icon: "🔒", priority: "critical", description: "Vulnerability protection validation" },
                { title: "Auto-Healing Tests", testType: "auto_healing", icon: "🔄", priority: "high", description: "Self-recovery mechanism testing" }
            ]
        },
        // Revenue-Critical Services
        {
            category: "Revenue Critical",
            services: [
                { title: "Credit & Payment Tests", testType: "credit_payment", icon: "💳", priority: "critical", description: "Revenue processing and transactions" },
                { title: "Spiritual Services Tests", testType: "spiritual_services", icon: "🕉️", priority: "critical", description: "Core business logic and AI services" },
                { title: "Avatar Generation Tests", testType: "avatar_generation", icon: "🎭", priority: "high", description: "Video creation and spiritual avatars" }
            ]
        },
        // Communication Services
        {
            category: "Communication",
            services: [
                { title: "Live Audio/Video Tests", testType: "live_audio_video", icon: "📹", priority: "critical", description: "Live consultation and WebRTC" },
                { title: "Social Media Tests", testType: "social_media", icon: "📱", priority: "high", description: "Marketing automation and content" }
            ]
        },
        // User Experience Services
        {
            category: "User Experience",
            services: [
                { title: "User Management Tests", testType: "user_management", icon: "👤", priority: "critical", description: "Authentication and profile management" },
                { title: "Community Services Tests", testType: "community_services", icon: "🤝", priority: "medium", description: "Follow-up systems and engagement" },
                { title: "Notification Services Tests", testType: "notification_services", icon: "🔔", priority: "medium", description: "Alerts and user communication" }
            ]
        },
        // Business Management Services
        {
            category: "Business Management",
            services: [
                { title: "Admin Services Tests", testType: "admin_services", icon: "⚙️", priority: "high", description: "Dashboard, settings, and management" },
                { title: "Analytics & Monitoring Tests", testType: "analytics_monitoring", icon: "📊", priority: "high", description: "Business intelligence and tracking" }
            ]
        }
    ];

    const runAllTests = async () => {
        setLoading(true);
        setGlobalStatus('running');
        const results = {};

        try {
            for (const category of allServices) {
                for (const service of category.services) {
                    try {
                        const response = await fetch(`${API_BASE_URL}/api/monitoring/test-execute`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ test_type: service.testType })
                        });

                        if (response.ok) {
                            const data = await response.json();
                            results[service.testType] = {
                                status: 'passed',
                                data: data.data || data
                            };
                        } else {
                            results[service.testType] = {
                                status: 'failed',
                                error: `HTTP ${response.status}`
                            };
                        }
                    } catch (err) {
                        results[service.testType] = {
                            status: 'failed',
                            error: err.message
                        };
                    }
                }
            }

            setTestResults(results);
            setGlobalStatus('completed');
        } catch (err) {
            setGlobalStatus('failed');
        } finally {
            setLoading(false);
        }
    };

    const getOverallStats = () => {
        const totalServices = allServices.reduce((sum, category) => sum + category.services.length, 0);
        const completedTests = Object.keys(testResults).length;
        const passedTests = Object.values(testResults).filter(result => result.status === 'passed').length;
        const failedTests = Object.values(testResults).filter(result => result.status === 'failed').length;

        return { totalServices, completedTests, passedTests, failedTests };
    };

    const stats = getOverallStats();

    return (
        <div className="space-y-6">
            {/* Overall Status Card */}
            <Card>
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <CardTitle className="flex items-center gap-2">
                            <Target className="h-5 w-5" />
                            All Services Test Suite
                        </CardTitle>
                        <Button 
                            onClick={runAllTests}
                            disabled={loading}
                            className="flex items-center gap-2"
                        >
                            {loading ? (
                                <RefreshCw className="h-4 w-4 animate-spin" />
                            ) : (
                                <Play className="h-4 w-4" />
                            )}
                            {loading ? 'Running All Tests...' : 'Run All Tests'}
                        </Button>
                    </div>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="text-center">
                            <div className="text-2xl font-bold text-blue-600">{stats.totalServices}</div>
                            <div className="text-sm text-gray-600">Total Services</div>
                        </div>
                        <div className="text-center">
                            <div className="text-2xl font-bold text-green-600">{stats.passedTests}</div>
                            <div className="text-sm text-gray-600">Passed Tests</div>
                        </div>
                        <div className="text-center">
                            <div className="text-2xl font-bold text-red-600">{stats.failedTests}</div>
                            <div className="text-sm text-gray-600">Failed Tests</div>
                        </div>
                        <div className="text-center">
                            <div className="text-2xl font-bold text-gray-600">{stats.completedTests}</div>
                            <div className="text-sm text-gray-600">Completed</div>
                        </div>
                    </div>
                    
                    {stats.completedTests > 0 && (
                        <div className="mt-4">
                            <div className="flex justify-between text-sm mb-2">
                                <span>Overall Success Rate</span>
                                <span className="font-medium">
                                    {stats.completedTests > 0 ? ((stats.passedTests / stats.completedTests) * 100).toFixed(1) : 0}%
                                </span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                                <div 
                                    className="bg-green-500 h-2 rounded-full transition-all duration-300" 
                                    style={{ 
                                        width: `${stats.completedTests > 0 ? (stats.passedTests / stats.completedTests) * 100 : 0}%` 
                                    }}
                                ></div>
                            </div>
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Service Categories */}
            {allServices.map((category, categoryIndex) => (
                <Card key={categoryIndex}>
                    <CardHeader>
                        <CardTitle className="text-lg">{category.category} Services</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {category.services.map((service, serviceIndex) => (
                                <ServiceStatusCard
                                    key={serviceIndex}
                                    title={service.title}
                                    description={service.description}
                                    endpoint="/api/monitoring/test-execute"
                                    testType={service.testType}
                                    icon={service.icon}
                                    priority={service.priority}
                                />
                            ))}
                        </div>
                    </CardContent>
                </Card>
            ))}
        </div>
    );
};

export default AllServicesTab;