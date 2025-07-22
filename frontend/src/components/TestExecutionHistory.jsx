import React from 'react';
import PropTypes from 'prop-types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Filter, Search } from 'lucide-react';
import { getStatusBadgeColor, getStatusIcon } from '../utils/testStatus.js';

const TestExecutionHistory = ({ 
    testSessions, 
    filter, 
    searchTerm, 
    onFilterChange, 
    onSearchChange, 
    onSessionSelect,
    filteredSessions 
}) => {
    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center justify-between">
                    <span>Test Execution History</span>
                    <div className="flex gap-2">
                        <div className="relative">
                            <Search className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" aria-hidden="true" />
                            <input
                                type="text"
                                placeholder="Search tests..."
                                value={searchTerm}
                                onChange={(e) => onSearchChange(e.target.value)}
                                className="pl-9 pr-4 py-2 border rounded-md text-sm"
                                aria-label="Search test execution history"
                            />
                        </div>
                        <select
                            value={filter}
                            onChange={(e) => onFilterChange(e.target.value)}
                            className="px-3 py-2 border rounded-md text-sm"
                            aria-label="Filter test results by status"
                        >
                            <option value="all">All Tests</option>
                            <option value="passed">Passed</option>
                            <option value="failed">Failed</option>
                            <option value="running">Running</option>
                        </select>
                    </div>
                </CardTitle>
            </CardHeader>
            <CardContent>
                <div className="space-y-3">
                    {filteredSessions.length === 0 ? (
                        <div className="text-center py-8 text-gray-500">
                            No test sessions found
                        </div>
                    ) : (
                        filteredSessions.map((session) => (
                            <button
                                key={session.session_id}
                                className="w-full flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 text-left"
                                onClick={() => onSessionSelect(session)}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter' || e.key === ' ') {
                                        e.preventDefault();
                                        onSessionSelect(session);
                                    }
                                }}
                                aria-label={`View details for ${session.test_type} test session from ${new Date(session.started_at).toLocaleString()}, status: ${session.status}`}
                                role="button"
                            >
                                <div className="flex items-center gap-3">
                                    {getStatusIcon(session.status)}
                                    <div>
                                        <div className="font-medium">{session.test_type}</div>
                                        <div className="text-sm text-gray-500">
                                            {new Date(session.started_at).toLocaleString()}
                                        </div>
                                    </div>
                                </div>
                                <div className="flex items-center gap-2">
                                    <Badge className={getStatusBadgeColor(session.status)}>
                                        {session.status}
                                    </Badge>
                                    {session.total_tests > 0 && (
                                        <span className="text-sm text-gray-600">
                                            {session.passed_tests}/{session.total_tests}
                                        </span>
                                    )}
                                </div>
                            </button>
                        ))
                    )}
                </div>
            </CardContent>
        </Card>
    );
};

TestExecutionHistory.propTypes = {
    testSessions: PropTypes.array.isRequired,
    filter: PropTypes.string.isRequired,
    searchTerm: PropTypes.string.isRequired,
    onFilterChange: PropTypes.func.isRequired,
    onSearchChange: PropTypes.func.isRequired,
    onSessionSelect: PropTypes.func.isRequired,
    filteredSessions: PropTypes.array.isRequired
};

export default TestExecutionHistory;