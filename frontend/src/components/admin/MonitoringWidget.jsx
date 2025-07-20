import React, { useState, useEffect } from 'react';
import { Activity, AlertCircle, CheckCircle } from 'lucide-react';
import spiritualAPI from '../../lib/api';

const MonitoringWidget = () => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 60000); // Update every minute
    return () => clearInterval(interval);
  }, []);

  const fetchStatus = async () => {
    try {
      const response = await spiritualAPI.request('/api/monitoring/dashboard');
      
      // Handle StandardResponse format - extract data and normalize structure
      if (response && response.success && response.data) {
        const normalizedData = {
          ...response.data,
          status: response.data.system_health?.system_status || 'unknown',
          integrations: response.data.system_health?.integration_points || {}
        };
        setStatus(normalizedData);
      } else {
        // Fallback for direct response format
        setStatus(response);
      }
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch monitoring status:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Activity className="text-purple-600" size={20} />
            <h3 className="text-lg font-semibold">System Health</h3>
          </div>
        </div>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': return 'text-green-600';
      case 'degraded': return 'text-yellow-600';
      case 'critical': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy': return <CheckCircle className="text-green-600" size={24} />;
      case 'degraded': return <AlertCircle className="text-yellow-600" size={24} />;
      case 'critical': return <AlertCircle className="text-red-600" size={24} />;
      default: return <Activity className="text-gray-600" size={24} />;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Activity className="text-purple-600" size={20} />
          <h3 className="text-lg font-semibold">System Health</h3>
        </div>
        <a href="#" onClick={(e) => { e.preventDefault(); window.location.hash = '#monitoring'; }} className="text-sm text-purple-600 hover:underline">
          View Details →
        </a>
      </div>

      {status ? (
        <>
          <div className="flex items-center space-x-3 mb-4">
            {getStatusIcon(status.status)}
            <span className={`text-lg font-medium ${getStatusColor(status.status)}`}>
              {status.status?.toUpperCase() || 'UNKNOWN'}
            </span>
          </div>

          <div className="space-y-2">
            {/* Integration Status Summary */}
            <div className="grid grid-cols-2 gap-2 text-sm">
              {Object.entries(status.integrations || {}).map(([key, data]) => {
                // Safety check for data structure
                if (!data || typeof data !== 'object') {
                  console.warn(`Invalid integration data for ${key}:`, data);
                  return null;
                }
                
                return (
                  <div key={key} className="flex items-center justify-between">
                    <span className="text-gray-600 capitalize">{key.replace('_', ' ')}:</span>
                    <span className={`font-medium ${data.status === 'healthy' ? 'text-green-600' : 'text-red-600'}`}>
                      {data.status === 'healthy' ? '✓' : '✗'}
                    </span>
                  </div>
                );
              })}
            </div>

            {/* Recent Issues Count */}
            {status.recent_issues?.length > 0 && (
              <div className="mt-3 pt-3 border-t">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Recent Issues:</span>
                  <span className="text-sm font-medium text-red-600">
                    {status.recent_issues.length} issues
                  </span>
                </div>
              </div>
            )}
          </div>
        </>
      ) : (
        <div className="text-center py-4 text-gray-500">
          <p>Unable to fetch system status</p>
        </div>
      )}
    </div>
  );
};

export default MonitoringWidget;