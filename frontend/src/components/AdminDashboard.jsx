import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, RefreshCw, Download } from 'lucide-react';
import Overview from './admin/Overview';
import Products from './admin/Products';
import RevenueAnalytics from './admin/RevenueAnalytics';
import ContentManagement from './admin/ContentManagement';
import BusinessIntelligence from './admin/BusinessIntelligence';
import Settings from './admin/Settings';
import UserManagement from './admin/UserManagement';
import Donations from './admin/Donations';
import ServiceTypes from './admin/ServiceTypes';
import PricingConfig from './admin/PricingConfig';
import spiritualAPI from '../lib/api';
import SocialContentManagement from './admin/SocialContentManagement';
import Notifications from './admin/Notifications';
import CreditPackages from './admin/CreditPackages';
import FollowUpManagement from './admin/FollowUpManagement';

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

  // Tab labels and keys
  const tabs = [
    { key: 'overview', label: 'Overview' },
    { key: 'products', label: 'Products' },
    { key: 'revenue', label: 'Revenue' },
    { key: 'content', label: 'Content' },
    { key: 'insights', label: 'Insights' },
    { key: 'settings', label: 'Settings' },
    { key: 'users', label: 'Users' },
    { key: 'donations', label: 'Donations' },
    { key: 'serviceTypes', label: 'Service Types' },
    { key: 'pricing', label: 'Pricing' },
    { key: 'notifications', label: 'Notifications' },
    { key: 'creditPackages', label: 'Credit Packages' },
    { key: 'followup', label: 'Follow-ups' },
  ];

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
      {/* Tab Navigation */}
      <div className="max-w-7xl mx-auto px-4 pt-6">
        <div className="flex space-x-2 border-b border-gray-200 mb-8 overflow-x-auto">
          {tabs.map(tab => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`px-4 py-2 font-medium rounded-t-lg focus:outline-none transition-colors duration-200 whitespace-nowrap ${activeTab === tab.key ? 'bg-white text-purple-800 border-x border-t border-gray-200 -mb-px' : 'text-gray-600 hover:text-purple-700'}`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>
      <div className="max-w-7xl mx-auto px-4 py-8">
        {activeTab === 'overview' && <Overview adminStats={adminStats} />}
        {activeTab === 'products' && <Products />}
        {activeTab === 'revenue' && <RevenueAnalytics />}
        {activeTab === 'content' && <SocialContentManagement />}
        {activeTab === 'insights' && <BusinessIntelligence />}
        {activeTab === 'settings' && <Settings />}
        {activeTab === 'users' && <UserManagement />}
        {activeTab === 'donations' && <Donations />}
        {activeTab === 'serviceTypes' && <ServiceTypes />}
        {activeTab === 'pricing' && <PricingConfig />}
        {activeTab === 'notifications' && <Notifications />}
        {activeTab === 'creditPackages' && <CreditPackages />}
        {activeTab === 'followup' && <FollowUpManagement />}
      </div>
    </div>
  );
};

export default AdminDashboard;

