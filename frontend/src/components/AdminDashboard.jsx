import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, RefreshCw, Download, Database, Shield, Globe, Zap, TrendingUp, Users, Settings as SettingsIcon, Bell, CreditCard, MessageCircle, BarChart3, DollarSign, Heart, Video, Brain, Cpu, Activity, AlertTriangle } from 'lucide-react';

// Import the custom notification hook
import { useNotification } from '../hooks/useNotification';

// Import existing components
import Overview from './admin/Overview';
import Products from './admin/Products';
import RevenueAnalytics from './admin/RevenueAnalytics';
import Settings from './admin/Settings';
import UserManagement from './admin/UserManagement';
import Donations from './admin/Donations';
import ServiceTypes from './admin/ServiceTypes';
import Notifications from './admin/Notifications';
import CreditPackages from './admin/CreditPackages';
import SocialMediaMarketing from './admin/SocialMediaMarketing';
import SocialContentManagement from './admin/SocialContentManagement';
import FollowUpManagement from './admin/FollowUpManagement';

// Import the comprehensive pricing dashboard (most advanced)
import AdminPricingDashboard from './AdminPricingDashboard';

// Import API
import spiritualAPI from '../lib/api';

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [adminStats, setAdminStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [systemHealth, setSystemHealth] = useState({});
  const [knowledgeStats, setKnowledgeStats] = useState({});
  const [sessionMonitoring, setSessionMonitoring] = useState({});
  const [apiIntegrations, setApiIntegrations] = useState({});
  
  // Use the custom notification hook
  const { notification, showNotification, clearNotification } = useNotification();

  // Reusable data fetching function
  const fetchComprehensiveAdminData = async (showRefreshIndicator = false) => {
    try {
      if (showRefreshIndicator) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      
      // Parallel fetch all admin data
      const [
        stats,
        health,
        knowledge,
        sessions,
        integrations
      ] = await Promise.all([
        // Basic admin stats
        spiritualAPI.request('/api/admin/analytics/overview').catch(() => ({})),
        
        // System health check
        spiritualAPI.request('/api/health').catch(() => ({})),
        
        // Knowledge base stats (if available)
        spiritualAPI.request('/api/spiritual/enhanced/knowledge-domains').catch(() => ({})),
        
        // Session monitoring
        spiritualAPI.request('/api/admin/analytics/sessions').catch(() => ({})),
        
        // API integrations status
        spiritualAPI.request('/api/admin/integrations/status').catch(() => ({}))
      ]);
      
      setAdminStats(stats);
      setSystemHealth(health);
      setKnowledgeStats(knowledge);
      setSessionMonitoring(sessions);
      setApiIntegrations(integrations);
      
      if (showRefreshIndicator) {
        showNotification('Dashboard data refreshed successfully!', 'success');
      }
      
    } catch (error) {
      console.error('Admin data fetch error:', error);
      if (showRefreshIndicator) {
        showNotification('Failed to refresh dashboard data. Please try again.', 'error');
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  // Notification helper function is now provided by the useNotification hook

  useEffect(() => {
    fetchComprehensiveAdminData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(() => fetchComprehensiveAdminData(), 30000);
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = () => {
    fetchComprehensiveAdminData(true);
  };

  const handleExport = async () => {
    try {
      const exportData = {
        timestamp: new Date().toISOString(),
        stats: adminStats,
        health: systemHealth,
        knowledge: knowledgeStats,
        sessions: sessionMonitoring,
        integrations: apiIntegrations
      };
      
      // Convert to JSON string to check size
      const jsonString = JSON.stringify(exportData, null, 2);
      const sizeInBytes = new Blob([jsonString]).size;
      const sizeInMB = sizeInBytes / (1024 * 1024);
      
      // Check if data exceeds reasonable size threshold (50MB)
      const MAX_SIZE_MB = 50;
      if (sizeInMB > MAX_SIZE_MB) {
        showNotification(
          `Export data too large (${sizeInMB.toFixed(2)}MB). Maximum allowed size is ${MAX_SIZE_MB}MB. Please contact support for assistance.`,
          'error'
        );
        console.warn('Export aborted - data size exceeds limit:', { sizeInMB, maxSizeMB: MAX_SIZE_MB });
        return;
      }
      
      // Create and download the file
      const blob = new Blob([jsonString], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `jyotiflow-admin-export-${new Date().toISOString().split('T')[0]}.json`;
      
      // Ensure the download element is properly handled
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      showNotification(
        `Export completed successfully! File size: ${sizeInMB.toFixed(2)}MB`,
        'success'
      );
      
    } catch (error) {
      console.error('Export error:', error);
      showNotification(
        'Export failed. Please try again or contact support if the issue persists.',
        'error'
      );
    }
  };

  if (loading) {
    return (
      <div className="pt-16 min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading comprehensive admin dashboard...</p>
        </div>
      </div>
    );
  }

  // Enhanced tab configuration with all features
  const tabs = [
    { key: 'overview', label: 'Overview', icon: BarChart3, description: 'Platform statistics and quick actions' },
    { key: 'users', label: 'Users', icon: Users, description: 'User management and analytics' },
    { key: 'products', label: 'Products & Services', icon: CreditCard, description: 'Service types and credit packages' },
    { key: 'pricing', label: 'Smart Pricing', icon: DollarSign, description: 'AI-powered dynamic pricing system' },
    { key: 'revenue', label: 'Revenue Analytics', icon: TrendingUp, description: 'Financial performance and insights' },
    { key: 'content', label: 'Content Management', icon: MessageCircle, description: 'Social media content and scheduling' },
    { key: 'marketing', label: 'Marketing Automation', icon: Globe, description: 'Social media marketing campaigns' },
    { key: 'followups', label: 'Follow-up System', icon: Bell, description: 'Email, SMS, and WhatsApp follow-ups' },
    { key: 'knowledge', label: 'Knowledge Base', icon: Brain, description: 'RAG system and spiritual knowledge' },
    { key: 'sessions', label: 'Session Monitoring', icon: Video, description: 'Live sessions and recordings' },
    { key: 'integrations', label: 'API Integrations', icon: Zap, description: 'Third-party service monitoring' },
    { key: 'system', label: 'System Health', icon: Activity, description: 'Database, migrations, and maintenance' },
    { key: 'settings', label: 'Platform Settings', icon: SettingsIcon, description: 'Configuration and preferences' }
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return <Overview />;
      case 'users':
        return <UserManagement />;
      case 'products':
        return <Products />;
      case 'pricing':
        return <AdminPricingDashboard />;
      case 'revenue':
        return <RevenueAnalytics />;
      case 'content':
        return <SocialContentManagement />;
      case 'marketing':
        return <SocialMediaMarketing />;
      case 'followups':
        return <FollowUpManagement />;
      case 'knowledge':
        return <KnowledgeBaseManagement 
          notification={notification} 
          showNotification={showNotification} 
          clearNotification={clearNotification} 
        />;
      case 'sessions':
        return <SessionMonitoring />;
      case 'integrations':
        return <APIIntegrations />;
      case 'system':
        return <SystemHealth 
          notification={notification} 
          showNotification={showNotification} 
          clearNotification={clearNotification} 
        />;
      case 'settings':
        return <Settings />;
      default:
        return <Overview />;
    }
  };

  return (
    <div className="pt-16 min-h-screen bg-gray-50">
      {/* Notification Component */}
      {notification && (
        <div className={`fixed top-20 right-4 z-50 p-4 rounded-lg shadow-lg max-w-md ${
          notification.type === 'success' ? 'bg-green-500 text-white' :
          notification.type === 'error' ? 'bg-red-500 text-white' :
          'bg-blue-500 text-white'
        }`}>
          <div className="flex items-center justify-between">
            <span>{notification.message}</span>
            <button 
              onClick={clearNotification}
              aria-label="Dismiss notification"
              className={`ml-4 p-1 rounded-full transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-white focus:ring-opacity-50 ${
                notification.type === 'success' ? 'text-green-100 hover:text-white hover:bg-green-600' :
                notification.type === 'error' ? 'text-red-100 hover:text-white hover:bg-red-600' :
                'text-blue-100 hover:text-white hover:bg-blue-600'
              }`}
            >
              ×
            </button>
          </div>
        </div>
      )}
      
      {/* Enhanced Header */}
      <div className="bg-gradient-to-r from-purple-800 via-indigo-800 to-blue-800 py-8 shadow-lg">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link to="/" className="inline-flex items-center text-white hover:text-gray-200 transition-colors">
                <ArrowLeft size={20} className="mr-2" />
                Back to Site
              </Link>
              <div className="text-4xl">🕉️</div>
              <div>
                <h1 className="text-3xl font-bold text-white">JyotiFlow Admin Dashboard</h1>
                <p className="text-purple-200">Comprehensive Platform Administration</p>
              </div>
            </div>
            
            {/* System Status Indicators */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 bg-white bg-opacity-20 rounded-lg px-3 py-2">
                <div className={`w-2 h-2 rounded-full ${systemHealth.status === 'healthy' ? 'bg-green-400' : 'bg-red-400'}`}></div>
                <span className="text-white text-sm">System {systemHealth.status || 'Unknown'}</span>
              </div>
              
              <button 
                onClick={handleRefresh}
                disabled={refreshing}
                className={`bg-white bg-opacity-20 text-white px-4 py-2 rounded-lg hover:bg-opacity-30 transition-all duration-300 flex items-center space-x-2 ${refreshing ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <RefreshCw size={16} className={refreshing ? 'animate-spin' : ''} />
                <span>{refreshing ? 'Refreshing...' : 'Refresh'}</span>
              </button>
              
              <button 
                onClick={handleExport}
                className="bg-yellow-400 text-black px-4 py-2 rounded-lg hover:bg-yellow-500 transition-colors flex items-center space-x-2"
              >
                <Download size={16} />
                <span>Export Data</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Enhanced Tab Navigation */}
      <div className="max-w-7xl mx-auto px-4 pt-6">
        <div 
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 gap-3 mb-8"
          role="tablist"
          aria-label="Admin dashboard navigation"
        >
          {tabs.map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.key;
            return (
              <button
                key={tab.key}
                id={`tab-${tab.key}`}
                role="tab"
                aria-selected={isActive}
                aria-controls={`tabpanel-${tab.key}`}
                tabIndex={isActive ? 0 : -1}
                onClick={() => setActiveTab(tab.key)}
                className={`p-4 rounded-lg border-2 transition-all duration-200 text-left ${
                  isActive 
                    ? 'bg-purple-600 text-white border-purple-600 shadow-lg' 
                    : 'bg-white text-gray-700 border-gray-200 hover:border-purple-300 hover:shadow-md'
                }`}
              >
                <div className="flex items-center space-x-2 mb-2">
                  <Icon size={20} />
                  <span className="font-medium">{tab.label}</span>
                </div>
                <p className={`text-xs ${isActive ? 'text-purple-100' : 'text-gray-500'}`}>
                  {tab.description}
                </p>
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab Content */}
      <div className="max-w-7xl mx-auto px-4 pb-8">
        <div 
          className="bg-white rounded-lg shadow-sm border border-gray-200 min-h-96"
          role="tabpanel"
          id={`tabpanel-${activeTab}`}
          aria-labelledby={`tab-${activeTab}`}
        >
          {renderTabContent()}
        </div>
      </div>
    </div>
  );
};

// New Components for Missing Features

const KnowledgeBaseManagement = ({ notification, showNotification, clearNotification }) => {
  const [knowledgeDomains, setKnowledgeDomains] = useState([]);
  const [seedingStatus, setSeedingStatus] = useState({});
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);

  const fetchKnowledgeData = async () => {
    try {
      const [domains, status] = await Promise.all([
        spiritualAPI.request('/api/spiritual/enhanced/knowledge-domains').catch(() => []),
        spiritualAPI.request('/api/admin/knowledge/seeding-status').catch(() => ({}))
      ]);
      
      setKnowledgeDomains(domains);
      setSeedingStatus(status);
    } catch (error) {
      console.error('Knowledge data fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchKnowledgeData();
  }, []);

  const handleSeedKnowledge = async () => {
    try {
      setSeeding(true);
      const result = await spiritualAPI.request('/api/admin/knowledge/seed', { method: 'POST' });
      if (result.success) {
        showNotification('Knowledge seeding completed successfully!', 'success');
        // Refresh the data instead of reloading the page
        await fetchKnowledgeData();
      } else {
        showNotification('Knowledge seeding failed. Please check the logs.', 'error');
      }
    } catch (error) {
      console.error('Knowledge seeding error:', error);
      showNotification('Knowledge seeding failed. Please check the logs.', 'error');
    } finally {
      setSeeding(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center">Loading knowledge base data...</div>;
  }

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-800">Knowledge Base Management</h2>
        <button
          onClick={handleSeedKnowledge}
          disabled={seeding}
          className={`bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors flex items-center space-x-2 ${seeding ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <Database size={16} className={seeding ? 'animate-spin' : ''} />
          <span>{seeding ? 'Seeding...' : 'Seed Knowledge Base'}</span>
        </button>
      </div>

      {/* Knowledge Domains */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {knowledgeDomains.map((domain, index) => (
          <div key={index} className="bg-gray-50 rounded-lg p-6">
            <h3 className="font-semibold text-gray-800 mb-2">{domain.name}</h3>
            <p className="text-gray-600 text-sm mb-4">{domain.description}</p>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Knowledge Pieces:</span>
                <span className="font-medium">{domain.count || 0}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Authority Level:</span>
                <span className="font-medium">{domain.authority_level || 'N/A'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Last Updated:</span>
                <span className="font-medium">{domain.last_updated || 'Never'}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Seeding Status */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h3 className="font-semibold text-blue-800 mb-4">Seeding Status</h3>
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-blue-600">Total Knowledge Pieces: <span className="font-medium">{seedingStatus.total_pieces || 0}</span></p>
            <p className="text-sm text-blue-600">Last Seeding: <span className="font-medium">{seedingStatus.last_seeding || 'Never'}</span></p>
          </div>
          <div>
            <p className="text-sm text-blue-600">Seeding Status: <span className="font-medium">{seedingStatus.status || 'Unknown'}</span></p>
            <p className="text-sm text-blue-600">OpenAI Available: <span className="font-medium">{seedingStatus.openai_available ? 'Yes' : 'No'}</span></p>
          </div>
        </div>
      </div>
    </div>
  );
};

const SessionMonitoring = () => {
  const [activeSessions, setActiveSessions] = useState([]);
  const [sessionStats, setSessionStats] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSessionData = async () => {
      try {
        const [sessions, stats] = await Promise.all([
          spiritualAPI.request('/api/admin/sessions/active').catch(() => []),
          spiritualAPI.request('/api/admin/sessions/stats').catch(() => ({}))
        ]);
        
        setActiveSessions(sessions);
        setSessionStats(stats);
      } catch (error) {
        console.error('Session data fetch error:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchSessionData();
    
    // Auto-refresh every 10 seconds
    const interval = setInterval(fetchSessionData, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="p-8 text-center">Loading session monitoring data...</div>;
  }

  return (
    <div className="p-8 space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Session Monitoring</h2>

      {/* Session Stats */}
      <div className="grid md:grid-cols-4 gap-6">
        <div className="bg-green-50 rounded-lg p-6 text-center">
          <div className="text-3xl mb-2">🟢</div>
          <div className="text-2xl font-bold text-green-800">{sessionStats.active_sessions || 0}</div>
          <div className="text-green-600">Active Sessions</div>
        </div>
        <div className="bg-blue-50 rounded-lg p-6 text-center">
          <div className="text-3xl mb-2">📊</div>
          <div className="text-2xl font-bold text-blue-800">{sessionStats.total_today || 0}</div>
          <div className="text-blue-600">Sessions Today</div>
        </div>
        <div className="bg-purple-50 rounded-lg p-6 text-center">
          <div className="text-3xl mb-2">⏱️</div>
          <div className="text-2xl font-bold text-purple-800">{sessionStats.avg_duration || '0m'}</div>
          <div className="text-purple-600">Avg Duration</div>
        </div>
        <div className="bg-yellow-50 rounded-lg p-6 text-center">
          <div className="text-3xl mb-2">🎥</div>
          <div className="text-2xl font-bold text-yellow-800">{sessionStats.video_sessions || 0}</div>
          <div className="text-yellow-600">Video Sessions</div>
        </div>
      </div>

      {/* Active Sessions */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-800">Active Sessions</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Service</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Duration</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {activeSessions.length === 0 ? (
                <tr>
                  <td colSpan="5" className="px-6 py-4 text-center text-gray-500">No active sessions</td>
                </tr>
              ) : (
                activeSessions.map((session) => (
                  <tr key={session.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{session.user_name}</div>
                      <div className="text-sm text-gray-500">{session.user_email}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{session.service_type}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{session.duration}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        session.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                      }`}>
                        {session.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <button className="text-blue-600 hover:text-blue-900">View Details</button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

const APIIntegrations = () => {
  const [integrations, setIntegrations] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchIntegrationData = async () => {
      try {
        const data = await spiritualAPI.request('/api/admin/integrations/status').catch(() => ({}));
        setIntegrations(data);
      } catch (error) {
        console.error('Integration data fetch error:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchIntegrationData();
  }, []);

  if (loading) {
    return <div className="p-8 text-center">Loading API integration status...</div>;
  }

  const integrationList = [
    { name: 'OpenAI', status: integrations.openai_available, description: 'AI-powered spiritual guidance' },
    { name: 'ProKerala', status: integrations.prokerala_available, description: 'Birth chart calculations' },
    { name: 'ElevenLabs', status: integrations.elevenlabs_available, description: 'Voice synthesis' },
    { name: 'D-ID', status: integrations.did_available, description: 'Avatar video generation' },
    { name: 'Agora', status: integrations.agora_available, description: 'Live video sessions' },
    { name: 'WhatsApp', status: integrations.whatsapp_available, description: 'WhatsApp notifications' },
    { name: 'SMS', status: integrations.sms_available, description: 'SMS notifications' },
    { name: 'Email', status: integrations.email_available, description: 'Email notifications' }
  ];

  return (
    <div className="p-8 space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">API Integrations</h2>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {integrationList.map((integration, index) => (
          <div key={index} className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-800">{integration.name}</h3>
              <div className={`w-3 h-3 rounded-full ${integration.status ? 'bg-green-500' : 'bg-red-500'}`}></div>
            </div>
            <p className="text-gray-600 text-sm mb-4">{integration.description}</p>
            <div className="flex items-center space-x-2">
              <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                integration.status ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {integration.status ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const SystemHealth = ({ notification, showNotification, clearNotification }) => {
  const [healthData, setHealthData] = useState({});
  const [dbStats, setDbStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [migrating, setMigrating] = useState(false);

  const fetchHealthData = async () => {
    try {
      const [health, db] = await Promise.all([
        spiritualAPI.request('/api/health').catch(() => ({})),
        spiritualAPI.request('/api/admin/database/stats').catch(() => ({}))
      ]);
      
      setHealthData(health);
      setDbStats(db);
    } catch (error) {
      console.error('Health data fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealthData();
  }, []);

  const runMigrations = async () => {
    // Show confirmation dialog before proceeding
    const confirmed = window.confirm(
      'Are you sure you want to run database migrations?\n\n' +
      'This operation will:\n' +
      '• Apply pending database schema changes\n' +
      '• Modify database structure\n' +
      '• Cannot be easily undone\n\n' +
      'Make sure you have a database backup before proceeding.\n\n' +
      'Click OK to continue or Cancel to abort.'
    );
    
    if (!confirmed) {
      showNotification('Database migration cancelled by user.', 'info');
      return;
    }
    
    try {
      setMigrating(true);
      const result = await spiritualAPI.request('/api/admin/database/migrate', { method: 'POST' });
      if (result.success) {
        showNotification('Database migrations completed successfully!', 'success');
        // Refresh the data instead of reloading the page
        await fetchHealthData();
      } else {
        showNotification('Migration failed. Please check the logs.', 'error');
      }
    } catch (error) {
      console.error('Migration error:', error);
      showNotification('Migration failed. Please check the logs.', 'error');
    } finally {
      setMigrating(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center">Loading system health data...</div>;
  }

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-800">System Health</h2>
        <button
          onClick={runMigrations}
          disabled={migrating}
          className={`bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2 ${migrating ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <Database size={16} className={migrating ? 'animate-spin' : ''} />
          <span>{migrating ? 'Running Migrations...' : 'Run Migrations'}</span>
        </button>
      </div>

      {/* System Status */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-green-50 rounded-lg p-6 text-center">
          <div className="text-3xl mb-2">💚</div>
          <div className="text-lg font-semibold text-green-800">Database</div>
          <div className="text-green-600">{healthData.database || 'Unknown'}</div>
        </div>
        <div className="bg-blue-50 rounded-lg p-6 text-center">
          <div className="text-3xl mb-2">🧠</div>
          <div className="text-lg font-semibold text-blue-800">Enhanced System</div>
          <div className="text-blue-600">{healthData.enhanced_features?.enhanced_system_active ? 'Active' : 'Inactive'}</div>
        </div>
        <div className="bg-purple-50 rounded-lg p-6 text-center">
          <div className="text-3xl mb-2">📚</div>
          <div className="text-lg font-semibold text-purple-800">Knowledge Base</div>
          <div className="text-purple-600">{healthData.enhanced_features?.knowledge_base_seeded ? 'Seeded' : 'Not Seeded'}</div>
        </div>
        <div className="bg-yellow-50 rounded-lg p-6 text-center">
          <div className="text-3xl mb-2">🔧</div>
          <div className="text-lg font-semibold text-yellow-800">System Status</div>
          <div className="text-yellow-600">{healthData.status || 'Unknown'}</div>
        </div>
      </div>

      {/* Database Statistics */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Database Statistics</h3>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-800">{dbStats.total_users || 0}</div>
            <div className="text-gray-600">Total Users</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-800">{dbStats.total_sessions || 0}</div>
            <div className="text-gray-600">Total Sessions</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-800">{dbStats.knowledge_pieces || 0}</div>
            <div className="text-gray-600">Knowledge Pieces</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-800">{dbStats.service_types || 0}</div>
            <div className="text-gray-600">Service Types</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;

