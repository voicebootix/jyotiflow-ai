import React from 'react';
import PropTypes from 'prop-types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, TrendingDown, BarChart3, Activity } from 'lucide-react';

const TestMetricsOverview = ({ testMetrics, loading }) => {
    if (loading) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle>Test Metrics Overview</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-center py-4">Loading metrics...</div>
                </CardContent>
            </Card>
        );
    }

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <Card>
                <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-600">Total Sessions</p>
                            <p className="text-2xl font-bold">
                                {testMetrics.total_sessions != null ? testMetrics.total_sessions.toLocaleString() : '-'}
                            </p>
                        </div>
                        <BarChart3 className="h-8 w-8 text-blue-600" />
                    </div>
                </CardContent>
            </Card>

            <Card>
                <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-600">Success Rate</p>
                            <p className="text-2xl font-bold">
                                {testMetrics.success_rate != null ? `${Number(testMetrics.success_rate).toFixed(1)}%` : '-'}
                            </p>
                        </div>
                        <div className="flex items-center">
                            {testMetrics.success_rate != null && testMetrics.success_rate >= 80 ? (
                                <TrendingUp className="h-8 w-8 text-green-600" />
                            ) : testMetrics.success_rate != null ? (
                                <TrendingDown className="h-8 w-8 text-red-600" />
                            ) : (
                                <Activity className="h-8 w-8 text-gray-600" />
                            )}
                        </div>
                    </div>
                </CardContent>
            </Card>

            <Card>
                <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-600">Avg Execution Time</p>
                            <p className="text-2xl font-bold">
                                {testMetrics.avg_execution_time != null ? `${Number(testMetrics.avg_execution_time).toFixed(1)}s` : '-'}
                            </p>
                        </div>
                        <Activity className="h-8 w-8 text-yellow-600" />
                    </div>
                </CardContent>
            </Card>

            <Card>
                <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-600">Auto-Fixes Applied</p>
                            <p className="text-2xl font-bold">
                                {testMetrics.auto_fixes_applied != null ? testMetrics.auto_fixes_applied.toLocaleString() : '-'}
                            </p>
                        </div>
                        <div className="flex items-center">
                            {(() => {
                                const trend = testMetrics.coverage_trend;
                                if (trend === 'improving') {
                                    return <TrendingUp className="h-8 w-8 text-green-600" />;
                                } else if (trend === 'declining') {
                                    return <TrendingDown className="h-8 w-8 text-red-600" />;
                                } else if (trend === 'stable') {
                                    return <Activity className="h-8 w-8 text-blue-600" />;
                                } else {
                                    // Default for unexpected or null values
                                    return <Activity className="h-8 w-8 text-gray-600" />;
                                }
                            })()}
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};

TestMetricsOverview.propTypes = {
    testMetrics: PropTypes.shape({
        total_sessions: PropTypes.number,
        success_rate: PropTypes.number,
        avg_execution_time: PropTypes.number,
        coverage_trend: PropTypes.oneOf(['improving', 'declining', 'stable', null, undefined]),
        auto_fixes_applied: PropTypes.number
    }).isRequired,
    loading: PropTypes.bool
};

TestMetricsOverview.defaultProps = {
    loading: false
};

export default TestMetricsOverview;