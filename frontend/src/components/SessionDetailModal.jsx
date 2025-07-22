import React, { useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { X } from 'lucide-react';
import { getStatusBadgeColor, getStatusIcon } from '../utils/testStatus.js';

const SessionDetailModal = ({ session, onClose, isOpen }) => {
    const modalRef = useRef(null);
    const firstFocusableRef = useRef(null);
    const lastFocusableRef = useRef(null);

    // Focus trap and escape key handling
    useEffect(() => {
        if (!isOpen) return;

        const handleEscape = (event) => {
            if (event.key === 'Escape') {
                onClose();
            }
        };

        const handleTabKey = (event) => {
            if (event.key !== 'Tab') return;

            if (event.shiftKey) {
                // Shift + Tab
                if (document.activeElement === firstFocusableRef.current) {
                    event.preventDefault();
                    lastFocusableRef.current?.focus();
                }
            } else {
                // Tab
                if (document.activeElement === lastFocusableRef.current) {
                    event.preventDefault();
                    firstFocusableRef.current?.focus();
                }
            }
        };

        document.addEventListener('keydown', handleEscape);
        document.addEventListener('keydown', handleTabKey);

        // Focus the first focusable element when modal opens
        setTimeout(() => {
            firstFocusableRef.current?.focus();
        }, 100);

        return () => {
            document.removeEventListener('keydown', handleEscape);
            document.removeEventListener('keydown', handleTabKey);
        };
    }, [isOpen, onClose]);

    if (!isOpen || !session) return null;

    return (
        <div 
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
            role="dialog"
            aria-modal="true"
            aria-labelledby="modal-title"
        >
            <Card 
                ref={modalRef}
                className="max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto"
            >
                <CardHeader className="flex flex-row items-center justify-between">
                    <CardTitle id="modal-title">Test Session Details</CardTitle>
                    <Button
                        ref={firstFocusableRef}
                        variant="ghost"
                        size="sm"
                        onClick={onClose}
                        aria-label="Close session details modal"
                    >
                        <X className="h-4 w-4" />
                    </Button>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="text-sm font-medium">Session ID</label>
                            <p className="text-sm text-gray-600 font-mono">{session.session_id}</p>
                        </div>
                        <div>
                            <label className="text-sm font-medium">Test Type</label>
                            <p className="text-sm text-gray-600">{session.test_type}</p>
                        </div>
                        <div>
                            <label className="text-sm font-medium">Started At</label>
                            <p className="text-sm text-gray-600">
                                {new Date(session.started_at).toLocaleString()}
                            </p>
                        </div>
                        <div>
                            <label className="text-sm font-medium">Status</label>
                            <Badge className={getStatusBadgeColor(session.status)}>
                                {session.status}
                            </Badge>
                        </div>
                        <div>
                            <label className="text-sm font-medium">Total Tests</label>
                            <p className="text-sm text-gray-600">{session.total_tests || 0}</p>
                        </div>
                        <div>
                            <label className="text-sm font-medium">Passed Tests</label>
                            <p className="text-sm text-green-600">{session.passed_tests || 0}</p>
                        </div>
                        <div>
                            <label className="text-sm font-medium">Failed Tests</label>
                            <p className="text-sm text-red-600">{session.failed_tests || 0}</p>
                        </div>
                        <div>
                            <label className="text-sm font-medium">Execution Time</label>
                            <p className="text-sm text-gray-600">
                                {session.execution_time_seconds ? `${session.execution_time_seconds}s` : 'N/A'}
                            </p>
                        </div>
                    </div>
                    
                    {session.coverage_percentage != null && (
                        <div>
                            <label className="text-sm font-medium">Test Coverage</label>
                            <div className="flex items-center gap-2 mt-1">
                                <div className="flex-1 bg-gray-200 rounded-full h-2">
                                    <div
                                        className="bg-blue-600 h-2 rounded-full"
                                        style={{ width: `${session.coverage_percentage}%` }}
                                        role="progressbar"
                                        aria-valuenow={session.coverage_percentage}
                                        aria-valuemin="0"
                                        aria-valuemax="100"
                                        aria-label={`Test coverage: ${session.coverage_percentage}%`}
                                    ></div>
                                </div>
                                <span className="text-sm text-gray-600">
                                    {typeof session.coverage_percentage === 'number' 
                                        ? session.coverage_percentage.toFixed(1) 
                                        : session.coverage_percentage}%
                                </span>
                            </div>
                        </div>
                    )}
                    
                    {session.environment && (
                        <div>
                            <label className="text-sm font-medium">Environment</label>
                            <p className="text-sm text-gray-600">{session.environment}</p>
                        </div>
                    )}
                    
                    {session.triggered_by && (
                        <div>
                            <label className="text-sm font-medium">Triggered By</label>
                            <p className="text-sm text-gray-600">{session.triggered_by}</p>
                        </div>
                    )}
                    
                    {session.test_category && (
                        <div>
                            <label className="text-sm font-medium">Category</label>
                            <p className="text-sm text-gray-600">{session.test_category}</p>
                        </div>
                    )}

                    <div className="flex justify-end pt-4">
                        <Button ref={lastFocusableRef} onClick={onClose}>Close</Button>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};

SessionDetailModal.propTypes = {
    session: PropTypes.shape({
        session_id: PropTypes.string,
        test_type: PropTypes.string,
        started_at: PropTypes.string,
        status: PropTypes.string,
        total_tests: PropTypes.number,
        passed_tests: PropTypes.number,
        failed_tests: PropTypes.number,
        execution_time_seconds: PropTypes.number,
        coverage_percentage: PropTypes.number,
        environment: PropTypes.string,
        triggered_by: PropTypes.string,
        test_category: PropTypes.string
    }),
    onClose: PropTypes.func.isRequired,
    isOpen: PropTypes.bool.isRequired
};

SessionDetailModal.defaultProps = {
    session: null
};

export default SessionDetailModal;