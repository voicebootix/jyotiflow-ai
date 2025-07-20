import React, { useState } from 'react';
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
    Clock
} from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://jyotiflow-ai.onrender.com';

const ServiceStatusCard = ({ 
    title, 
    description, 
    endpoint, 
    testType, 
    icon, 
    priority = 'medium' 
}) => {
    const [status, setStatus] = useState('idle');
    const [loading, setLoading] = useState(false);
    const [lastResult, setLastResult] = useState(null);
    const [error, setError] = useState(null);

    const triggerTest = async () => {
        setLoading(true);
        setError(null);
        setStatus('running');

        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ test_type: testType })
            });

            if (response.ok) {
                const data = await response.json();
                setLastResult(data.data || data);
                setStatus('completed');
            } else {
                setError(`Test failed with status ${response.status}`);
                setStatus('failed');
            }
        } catch (err) {
            setError(`Test execution failed: ${err.message}`);
            setStatus('failed');
        } finally {
            setLoading(false);
        }
    };

    const getStatusIcon = () => {
        switch (status) {
            case 'running':
                return <RefreshCw className="h-4 w-4 animate-spin text-blue-500" />;
            case 'completed':
                return <CheckCircle className="h-4 w-4 text-green-500" />;
            case 'failed':
                return <XCircle className="h-4 w-4 text-red-500" />;
            default:
                return <Clock className="h-4 w-4 text-gray-400" />;
        }
    };

    const getStatusBadge = () => {
        const priorityColor = {
            critical: 'bg-red-100 text-red-800',
            high: 'bg-orange-100 text-orange-800',
            medium: 'bg-yellow-100 text-yellow-800',
            low: 'bg-gray-100 text-gray-800'
        };

        return (
            <Badge className={priorityColor[priority]}>
                {priority.toUpperCase()}
            </Badge>
        );
    };

    return (
        <Card className="h-full">
            <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <span className="text-lg">{icon}</span>
                        <CardTitle className="text-sm font-medium">{title}</CardTitle>
                    </div>
                    <div className="flex items-center gap-2">
                        {getStatusIcon()}
                        {getStatusBadge()}
                    </div>
                </div>
            </CardHeader>
            <CardContent className="space-y-3">
                <p className="text-xs text-gray-600">{description}</p>
                
                {lastResult && (
                    <div className="text-xs space-y-1">
                        <div className="flex justify-between">
                            <span>Status:</span>
                            <Badge className={lastResult.status === 'passed' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                                {lastResult.status}
                            </Badge>
                        </div>
                        {lastResult.success_rate && (
                            <div className="flex justify-between">
                                <span>Success Rate:</span>
                                <span className="font-medium">{lastResult.success_rate.toFixed(1)}%</span>
                            </div>
                        )}
                        {lastResult.accessible_endpoints && (
                            <div className="flex justify-between">
                                <span>Endpoints:</span>
                                <span className="font-medium">{lastResult.accessible_endpoints}/{lastResult.total_endpoints}</span>
                            </div>
                        )}
                    </div>
                )}

                {error && (
                    <Alert className="py-2">
                        <AlertTriangle className="h-3 w-3" />
                        <AlertDescription className="text-xs">{error}</AlertDescription>
                    </Alert>
                )}

                <Button
                    size="sm"
                    onClick={triggerTest}
                    disabled={loading}
                    className="w-full text-xs"
                >
                    {loading ? (
                        <RefreshCw className="h-3 w-3 animate-spin mr-1" />
                    ) : (
                        <Play className="h-3 w-3 mr-1" />
                    )}
                    {loading ? 'Testing...' : 'Run Test'}
                </Button>
            </CardContent>
        </Card>
    );
};

export default ServiceStatusCard;