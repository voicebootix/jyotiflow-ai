import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, RefreshCw, Download } from 'lucide-react';
import Overview from './admin/Overview';
import Products from './admin/Products';
import RevenueAnalytics from './admin/RevenueAnalytics';
import ContentManagement from './admin/ContentManagement';
import BusinessIntelligence from './admin/BusinessIntelligence';
import Settings from './admin/Settings';
import spiritualAPI from '../lib/api';

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [adminStats, setAdminStats] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAdminData = async () => {
      setLoading(true);
      const stats = await spiritualAPI.getAdminStats();
      setAdminStats(stats.data || {});
      setLoading(false);
    };
    fetchAdminData();
  }, []);

  if (loading) {
    return <div>Loading divine administration...</div>;
  }

  return (
    <div className="pt-16 min-h-screen bg-gray-50">
      <div className="bg-gradient-to-r from-purple-800 to-indigo-800 py-8">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link to="/" className="inline-flex items-center text-white hover:text-gray-200 transition-colors">
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
              <button className="bg-white bg-opacity-20 text-white px-4 py-2 rounded-lg hover:bg-opacity-30 transition-all duration-300 flex items-center space-x-2">
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
      <div className="max-w-7xl mx-auto px-4 py-8">
        {activeTab === 'overview' && <Overview adminStats={adminStats} />}
        {activeTab === 'products' && <Products />}
        {activeTab === 'revenue' && <RevenueAnalytics />}
        {activeTab === 'content' && <ContentManagement />}
        {activeTab === 'insights' && <BusinessIntelligence />}
        {activeTab === 'settings' && <Settings />}
      </div>
    </div>
  );
};

export default AdminDashboard;

