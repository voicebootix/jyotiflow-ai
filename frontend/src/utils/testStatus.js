import { 
    CheckCircle, 
    XCircle, 
    Clock, 
    AlertTriangle,
    RefreshCw
} from 'lucide-react';

/**
 * Gets the appropriate status color based on test status
 * @param {string} status - The test status ('passed', 'failed', 'running', 'idle', etc.)
 * @returns {string} CSS color class
 */
export const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
        case 'passed':
        case 'success':
        case 'completed':
            return 'text-green-500';
        case 'failed':
        case 'error':
            return 'text-red-500';
        case 'running':
        case 'in_progress':
            return 'text-blue-500';
        case 'warning':
            return 'text-yellow-500';
        default:
            return 'text-gray-400';
    }
};

/**
 * Gets the appropriate status icon based on test status
 * @param {string} status - The test status ('passed', 'failed', 'running', 'idle', etc.)
 * @param {string} className - Additional CSS classes for the icon
 * @param {Object} props - Additional props for the icon component
 * @returns {JSX.Element} Status icon component
 */
export const getStatusIcon = (status, className = 'h-4 w-4', props = {}) => {
    const iconProps = { className, ...props };
    
    switch (status?.toLowerCase()) {
        case 'passed':
        case 'success':
        case 'completed':
            return <CheckCircle {...iconProps} />;
        case 'failed':
        case 'error':
            return <XCircle {...iconProps} />;
        case 'running':
        case 'in_progress':
            return <RefreshCw {...iconProps} className={`${className} animate-spin`} />;
        case 'warning':
            return <AlertTriangle {...iconProps} />;
        default:
            return <Clock {...iconProps} />;
    }
};

/**
 * Gets a human-readable status message
 * @param {string} status - The test status
 * @returns {string} Human-readable status message
 */
export const getStatusMessage = (status) => {
    switch (status?.toLowerCase()) {
        case 'passed':
            return 'All tests passed';
        case 'failed':
            return 'Tests failed';
        case 'running':
            return 'Tests running...';
        case 'completed':
            return 'Tests completed';
        case 'warning':
            return 'Tests completed with warnings';
        case 'idle':
            return 'Ready to run tests';
        default:
            return 'Unknown status';
    }
};

/**
 * Gets the appropriate badge color for priority levels
 * @param {string} priority - Priority level ('critical', 'high', 'medium', 'low')
 * @returns {string} CSS classes for badge styling
 */
export const getPriorityBadgeColor = (priority) => {
    switch (priority?.toLowerCase()) {
        case 'critical':
            return 'bg-red-100 text-red-800';
        case 'high':
            return 'bg-orange-100 text-orange-800';
        case 'medium':
            return 'bg-yellow-100 text-yellow-800';
        case 'low':
            return 'bg-gray-100 text-gray-800';
        default:
            return 'bg-gray-100 text-gray-800';
    }
};