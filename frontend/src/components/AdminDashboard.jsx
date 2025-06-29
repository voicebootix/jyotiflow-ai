import { useState, useEffect } from 'react';
import { 
  ArrowLeft, Users, DollarSign, Calendar, TrendingUp, 
  BarChart3, Settings, Bell, Download, RefreshCw,
  Eye, MessageSquare, Video, Crown
} from 'lucide-react';
import spiritualAPI from '../lib/api';
import { Link, useNavigate } from 'react-router-dom';
import Overview from './admin/Overview';
import Products from './admin/Products';
import RevenueAnalytics from './admin/RevenueAnalytics';
import ContentManagement from './admin/ContentManagement';
import BusinessIntelligence from './admin/BusinessIntelligence';
import Settings from './admin/Settings';

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
  const [users, setUsers] = useState([]);
  const [content, setContent] = useState([]);

  useEffect(() => {
    checkAdminAuth();
  }, []);

  const checkAdminAuth = async () => {
    if (!spiritualAPI.isAuthenticated()) {
      console.log('Not authenticated, redirecting to login');
      navigate('/login?admin=true&redirect=admin');
      return;
    }

    // Pre-check: fetch user profile and verify admin role before calling admin endpoints
    try {
      const profile = await spiritualAPI.getUserProfile();
      console.log('Admin pre-check profile:', profile);
      if (!profile || !profile.success || !profile.data || profile.data.role !== 'admin') {
        alert('Access denied. Admin privileges required. (Role check failed)');
        navigate('/');
        return;
      }
    } catch (err) {
      console.error('Admin pre-check failed:', err);
      alert('Failed to verify admin privileges. Please try again.');
      navigate('/');
      return;
    }

    // Check if user has admin privileges via backend endpoint
    try {
      console.log('Checking admin privileges...');
      const adminData = await spiritualAPI.getAdminStats();
      console.log('Admin stats response:', adminData);
      if (adminData && adminData.success) {
        console.log('Admin authentication successful');
        setIsAuthenticated(true);
        loadAdminData();
      } else {
        console.log('Admin authentication failed:', adminData);
        alert('Access denied. Admin privileges required. (Backend check failed)\n' + (adminData && adminData.message ? adminData.message : ''));
        navigate('/');
      }
    } catch (error) {
      console.error('Admin authentication check failed:', error);
      alert(`Admin authentication failed: ${error.message || 'Unknown error'}`);
      navigate('/login?admin=true&redirect=/admin');
    }
  };

  const loadAdminData = async () => {
    try {
      console.log('Loading admin data...');
      
      // Load admin statistics
      const stats = await spiritualAPI.getAdminStats();
      console.log('Admin stats loaded:', stats);
      if (stats && stats.success) {
        setAdminStats(stats.data);
      } else {
        console.error('Failed to load admin stats:', stats);
      }

      // Load monetization insights
      const monetization = await spiritualAPI.getMonetizationInsights();
      console.log('Monetization insights loaded:', monetization);
      if (monetization && monetization.success) {
        setMonetizationInsights(monetization.data);
      } else {
        console.error('Failed to load monetization insights:', monetization);
      }

      // Load product optimization data
      const optimization = await spiritualAPI.getProductOptimization();
      console.log('Product optimization loaded:', optimization);
      if (optimization && optimization.success) {
        setProductOptimization(optimization.data);
      } else {
        console.error('Failed to load product optimization:', optimization);
      }

      // Load users
      const usersRes = await spiritualAPI.getAdminUsers();
      if (usersRes && usersRes.success) {
        setUsers(usersRes.data);
      } else {
        setUsers([]);
      }

      // Load content
      const contentRes = await spiritualAPI.getAdminContent();
      if (contentRes && contentRes.success) {
        setContent(contentRes.data);
      } else {
        setContent([]);
      }

      // Track admin dashboard access
      await spiritualAPI.trackSpiritualEngagement('admin_dashboard_access');
    } catch (error) {
      console.error('Admin data loading failed:', error);
      alert(`Failed to load admin data: ${error.message || 'Unknown error'}`);
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
          {isLoading && (
            <div className="mt-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto"></div>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Add error boundary for the main content
  try {
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
                { id: 'products', label: 'Products', icon: Crown },
                { id: 'revenue', label: 'Revenue', icon: DollarSign },
                { id: 'credits', label: 'Credits', icon: DollarSign },
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
          {activeTab === 'overview' && <Overview adminStats={adminStats} />}
          {activeTab === 'products' && <Products />}
          {activeTab === 'revenue' && <RevenueAnalytics />}
          {activeTab === 'content' && <ContentManagement />}
          {activeTab === 'insights' && <BusinessIntelligence />}
          {activeTab === 'settings' && <Settings />}
          {activeTab === 'credits' && (
            <div className="bg-white rounded-lg shadow-sm p-12 text-center">
              <div className="text-6xl mb-4">💳</div>
              <h3 className="text-xl font-bold text-gray-800 mb-2">Credits Section</h3>
              <p className="text-gray-600 mb-6">
                Credits management and analytics coming soon. (Please add Credits.jsx for full functionality)
              </p>
            </div>
          )}
        </div>
      </div>
    );
  } catch (error) {
    console.error('AdminDashboard render error:', error);
    return (
      <div className="pt-16 min-h-screen flex items-center justify-center bg-red-50">
        <div className="text-center">
          <div className="text-6xl mb-4">⚠️</div>
          <h1 className="text-2xl font-bold text-red-800 mb-4">Dashboard Error</h1>
          <p className="text-red-600 mb-4">Something went wrong while rendering the admin dashboard.</p>
          <p className="text-sm text-gray-600 mb-6">Error: {error.message}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700 transition-colors"
          >
            Reload Page
          </button>
        </div>
      </div>
    );
  }
};

export default AdminDashboard;

