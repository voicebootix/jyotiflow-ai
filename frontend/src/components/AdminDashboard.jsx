import { useState, useEffect } from 'react';
import { 
  ArrowLeft, Users, DollarSign, Calendar, TrendingUp, 
  BarChart3, Settings, Bell, Download, RefreshCw,
  Eye, MessageSquare, Video, Crown
} from 'lucide-react';
import spiritualAPI from '../lib/api';
import { Link, useNavigate } from 'react-router-dom';

const AdminDashboard = () => {
  const navigate = useNavigate();
  const [adminStats, setAdminStats] = useState({
    total_users: 0,
    active_users: 0,
    total_revenue: 0,
    daily_revenue: 0,
    total_sessions: 0,
    satsangs_completed: 0,
    avatar_generations: 0,
    live_chat_sessions: 0
  });
  const [monetizationInsights, setMonetizationInsights] = useState(null);
  const [productOptimization, setProductOptimization] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    checkAdminAuth();
  }, []);

  const checkAdminAuth = async () => {
    if (!spiritualAPI.isAuthenticated()) {
      navigate('/login?admin=true&redirect=admin');
      return;
    }

    // Check if user has admin privileges
    try {
      const adminData = await spiritualAPI.getAdminStats();
      if (adminData && adminData.success) {
        setIsAuthenticated(true);
        loadAdminData();
      } else {
        // Not an admin user
        alert('Access denied. Admin privileges required.');
        navigate('/');
      }
    } catch (error) {
      console.error('Admin authentication check failed:', error);
      navigate('/login?admin=true&redirect=/admin');
    }
  };

  const loadAdminData = async () => {
    try {
      // Load admin statistics
      const stats = await spiritualAPI.getAdminStats();
      if (stats && stats.success) {
        setAdminStats(stats.data);
      }

      // Load monetization insights
      const monetization = await spiritualAPI.getMonetizationInsights();
      if (monetization && monetization.success) {
        setMonetizationInsights(monetization.data);
      }

      // Load product optimization data
      const optimization = await spiritualAPI.getProductOptimization();
      if (optimization && optimization.success) {
        setProductOptimization(optimization.data);
      }

      // Track admin dashboard access
      await spiritualAPI.trackSpiritualEngagement('admin_dashboard_access');
    } catch (error) {
      console.log('Admin data loading blessed with patience:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const refreshData = async () => {
    setIsLoading(true);
    await loadAdminData();
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  if (!isAuthenticated || isLoading) {
    return (
      <div className="pt-16 min-h-screen flex items-center justify-center">
        <div className="consciousness-pulse text-center">
          <div className="om-symbol text-6xl">👑</div>
          <p className="text-white mt-4">
            {!isAuthenticated ? 'Verifying admin privileges...' : 'Loading divine administration...'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="pt-16 min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-800 to-indigo-800 py-8">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link 
                to="/" 
                className="inline-flex items-center text-white hover:text-gray-200 transition-colors"
              >
                <ArrowLeft size={20} className="mr-2" />
                Back to Site
              </Link>
              <div className="text-4xl">👑</div>
              <div>
                <h1 className="text-3xl font-bold text-white">Admin Dashboard</h1>
                <p className="text-purple-200">Divine Platform Management</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={refreshData}
                className="bg-white bg-opacity-20 text-white px-4 py-2 rounded-lg hover:bg-opacity-30 transition-all duration-300 flex items-center space-x-2"
              >
                <RefreshCw size={16} />
                <span>Refresh</span>
              </button>
              <button className="bg-yellow-400 text-black px-4 py-2 rounded-lg hover:bg-yellow-500 transition-colors flex items-center space-x-2">
                <Download size={16} />
                <span>Export</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-8 overflow-x-auto">
            {[
              { id: 'overview', label: 'Overview', icon: BarChart3 },
              { id: 'users', label: 'Users', icon: Users },
              { id: 'revenue', label: 'Revenue', icon: DollarSign },
              { id: 'content', label: 'Content', icon: MessageSquare },
              { id: 'insights', label: 'AI Insights', icon: TrendingUp },
              { id: 'settings', label: 'Settings', icon: Settings }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-4 py-4 border-b-2 transition-all duration-300 whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-purple-600 text-purple-600'
                    : 'border-transparent text-gray-600 hover:text-gray-800'
                }`}
              >
                <tab.icon size={16} />
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Total Users</p>
                    <p className="text-3xl font-bold text-gray-900">{formatNumber(adminStats.total_users)}</p>
                  </div>
                  <div className="bg-blue-100 p-3 rounded-full">
                    <Users className="text-blue-600" size={24} />
                  </div>
                </div>
                <div className="mt-4 flex items-center">
                  <TrendingUp className="text-green-500 mr-1" size={16} />
                  <span className="text-green-500 text-sm">+12% from last month</span>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Monthly Revenue</p>
                    <p className="text-3xl font-bold text-gray-900">{formatCurrency(adminStats.total_revenue)}</p>
                  </div>
                  <div className="bg-green-100 p-3 rounded-full">
                    <DollarSign className="text-green-600" size={24} />
                  </div>
                </div>
                <div className="mt-4 flex items-center">
                  <TrendingUp className="text-green-500 mr-1" size={16} />
                  <span className="text-green-500 text-sm">+8% from last month</span>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Active Sessions</p>
                    <p className="text-3xl font-bold text-gray-900">{formatNumber(adminStats.total_sessions)}</p>
                  </div>
                  <div className="bg-purple-100 p-3 rounded-full">
                    <Video className="text-purple-600" size={24} />
                  </div>
                </div>
                <div className="mt-4 flex items-center">
                  <TrendingUp className="text-green-500 mr-1" size={16} />
                  <span className="text-green-500 text-sm">+15% from last week</span>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Satsangs Held</p>
                    <p className="text-3xl font-bold text-gray-900">{adminStats.satsangs_completed}</p>
                  </div>
                  <div className="bg-orange-100 p-3 rounded-full">
                    <Calendar className="text-orange-600" size={24} />
                  </div>
                </div>
                <div className="mt-4 flex items-center">
                  <Calendar className="text-blue-500 mr-1" size={16} />
                  <span className="text-blue-500 text-sm">Next: This Sunday</span>
                </div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="grid lg:grid-cols-2 gap-8">
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent User Activity</h3>
                <div className="space-y-4">
                  {[
                    { action: 'New user registration', user: 'sarah@example.com', time: '2 minutes ago', type: 'user' },
                    { action: 'Avatar video generated', user: 'john@example.com', time: '5 minutes ago', type: 'avatar' },
                    { action: 'Live chat session started', user: 'priya@example.com', time: '8 minutes ago', type: 'chat' },
                    { action: 'Satsang registration', user: 'david@example.com', time: '12 minutes ago', type: 'satsang' }
                  ].map((activity, index) => (
                    <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                      <div className={`p-2 rounded-full ${
                        activity.type === 'user' ? 'bg-blue-100' :
                        activity.type === 'avatar' ? 'bg-purple-100' :
                        activity.type === 'chat' ? 'bg-green-100' : 'bg-orange-100'
                      }`}>
                        {activity.type === 'user' && <Users size={16} className="text-blue-600" />}
                        {activity.type === 'avatar' && <Crown size={16} className="text-purple-600" />}
                        {activity.type === 'chat' && <Video size={16} className="text-green-600" />}
                        {activity.type === 'satsang' && <Calendar size={16} className="text-orange-600" />}
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">{activity.action}</p>
                        <p className="text-xs text-gray-500">{activity.user} • {activity.time}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">System Health</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">API Response Time</span>
                    <span className="text-sm font-medium text-green-600">142ms</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-green-500 h-2 rounded-full" style={{ width: '85%' }}></div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Database Performance</span>
                    <span className="text-sm font-medium text-green-600">98%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-green-500 h-2 rounded-full" style={{ width: '98%' }}></div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Avatar Generation Queue</span>
                    <span className="text-sm font-medium text-yellow-600">3 pending</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '30%' }}></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'insights' && (
          <div className="space-y-8">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">AI-Powered Monetization Insights</h3>
              {monetizationInsights ? (
                <div className="space-y-4">
                  <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
                    <h4 className="font-semibold text-blue-800 mb-2">Revenue Optimization</h4>
                    <p className="text-blue-700">{monetizationInsights.revenue_recommendation || 'Analyzing revenue patterns...'}</p>
                  </div>
                  <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
                    <h4 className="font-semibold text-green-800 mb-2">User Engagement</h4>
                    <p className="text-green-700">{monetizationInsights.engagement_insight || 'Processing engagement data...'}</p>
                  </div>
                  <div className="bg-purple-50 border border-purple-200 p-4 rounded-lg">
                    <h4 className="font-semibold text-purple-800 mb-2">Product Recommendations</h4>
                    <p className="text-purple-700">{monetizationInsights.product_suggestion || 'Generating product insights...'}</p>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto mb-4"></div>
                  <p className="text-gray-600">AI is analyzing platform data for insights...</p>
                </div>
              )}
            </div>

            {productOptimization && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Product Optimization Recommendations</h3>
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-3">
                    <h4 className="font-medium text-gray-800">Feature Priorities</h4>
                    <ul className="space-y-2">
                      {(productOptimization.feature_priorities || []).map((feature, index) => (
                        <li key={index} className="flex items-center space-x-2">
                          <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                          <span className="text-sm text-gray-700">{feature}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div className="space-y-3">
                    <h4 className="font-medium text-gray-800">User Experience Improvements</h4>
                    <ul className="space-y-2">
                      {(productOptimization.ux_improvements || []).map((improvement, index) => (
                        <li key={index} className="flex items-center space-x-2">
                          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                          <span className="text-sm text-gray-700">{improvement}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Other tabs would be implemented similarly */}
        {activeTab !== 'overview' && activeTab !== 'insights' && (
          <div className="bg-white rounded-lg shadow-sm p-12 text-center">
            <div className="text-6xl mb-4">🚧</div>
            <h3 className="text-xl font-bold text-gray-800 mb-2">
              {activeTab.charAt(0).toUpperCase() + activeTab.slice(1)} Section
            </h3>
            <p className="text-gray-600 mb-6">
              This admin section is under divine construction. Advanced features coming soon.
            </p>
            <button className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition-colors">
              Request Feature
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;

