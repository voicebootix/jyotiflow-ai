import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, RefreshCw, Download } from 'lucide-react';
import Overview from './admin/Overview';
import Products from './admin/Products';
import RevenueAnalytics from './admin/RevenueAnalytics';
import Settings from './admin/Settings';
import UserManagement from './admin/UserManagement';
import Donations from './admin/Donations';
import ServiceTypes from './admin/ServiceTypes';
import spiritualAPI from '../lib/api';
import SocialContentManagement from './admin/SocialContentManagement';
import Notifications from './admin/Notifications';
import CreditPackages from './admin/CreditPackages';
import AdminPricingDashboard from './AdminPricingDashboard';
import SocialMediaMarketing from './admin/SocialMediaMarketing';
import FollowUpManagement from './admin/FollowUpManagement';
import SystemMonitoring from './admin/SystemMonitoring';

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [adminStats, setAdminStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [creditPackages, setCreditPackages] = useState([]);

  useEffect(() => {
    const fetchAdminData = async () => {
      try {
        setLoading(true);
        
        // Fetch admin statistics
        const stats = await spiritualAPI.request('/api/admin/analytics/overview');
        if (stats) setAdminStats(stats);
        
        // Fetch credit packages for price management
        const packages = await spiritualAPI.request('/api/admin/products/credit-packages');
        if (packages) setCreditPackages(Array.isArray(packages) ? packages : []);
        
      } catch (error) {
        console.error('Admin data fetch error:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchAdminData();
  }, []);

  const handlePriceChange = async (packageId, newPrice) => {
    try {
      const result = await spiritualAPI.request(`/api/admin/products/credit-packages/${packageId}`, {
        method: 'PUT',
        body: JSON.stringify({ price_usd: newPrice })
      });
      
      if (result && result.success) {
        // Immediately update local state to reflect price change
        setCreditPackages(prevPackages => 
          prevPackages.map(pkg => 
            pkg.id === packageId 
              ? { ...pkg, price_usd: newPrice }
              : pkg
          )
        );
        
        // Show success message
        alert(`✅ விலை வெற்றிகரமாக மாற்றப்பட்டது!\n\nபுதிய விலை: $${newPrice}`);
        
        // Track price change for analytics
        await spiritualAPI.trackSpiritualEngagement('admin_price_change', {
          package_id: packageId,
          old_price: creditPackages.find(p => p.id === packageId)?.price_usd,
          new_price: newPrice
        });
      } else {
        alert('விலை மாற்றம் தோல்வி. தயவுசெய்து மீண்டும் முயற்சிக்கவும்.');
      }
    } catch (error) {
      console.error('Price change error:', error);
      alert('விலை மாற்றம் தோல்வி - தயவுசெய்து மீண்டும் முயற்சிக்கவும்.');
    }
  };

  if (loading) {
    return <div>Loading divine administration...</div>;
  }

  // Tab labels and keys - Cleaned up structure
  const tabs = [
    { key: 'overview', label: 'Overview' },
    { key: 'socialMarketing', label: '📱 Social Media Marketing' },
    { key: 'products', label: 'Products' },
    { key: 'revenue', label: 'Revenue' },
    { key: 'content', label: 'Content' },
    { key: 'settings', label: 'Settings' },
    { key: 'users', label: 'Users' },
    { key: 'donations', label: 'Donations' },
    { key: 'serviceTypes', label: 'Service Types' },
    { key: 'pricing', label: 'Smart Pricing' },
    { key: 'notifications', label: 'Notifications' },
    { key: 'creditPackages', label: 'Credit Packages' },
    { key: 'followup', label: 'Follow-ups' },
    { key: 'monitoring', label: '🔍 System Monitor' },
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
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* Quick Stats */}
            <div className="grid md:grid-cols-4 gap-6">
              <div className="sacred-card p-6 text-center">
                <div className="text-3xl mb-2">👥</div>
                <div className="text-2xl font-bold text-gray-800">{adminStats.total_users || 0}</div>
                <div className="text-gray-600">Total Users</div>
              </div>
              <div className="sacred-card p-6 text-center">
                <div className="text-3xl mb-2">💰</div>
                <div className="text-2xl font-bold text-gray-800">${adminStats.total_revenue || 0}</div>
                <div className="text-gray-600">Total Revenue</div>
              </div>
              <div className="sacred-card p-6 text-center">
                <div className="text-3xl mb-2">🕉️</div>
                <div className="text-2xl font-bold text-gray-800">{adminStats.total_sessions || 0}</div>
                <div className="text-gray-600">Total Sessions</div>
              </div>
              <div className="sacred-card p-6 text-center">
                <div className="text-3xl mb-2">💝</div>
                <div className="text-2xl font-bold text-gray-800">${adminStats.total_donations || 0}</div>
                <div className="text-gray-600">Total Donations</div>
              </div>
            </div>

            {/* Credit Package Management */}
            <div className="sacred-card p-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">
                💰 கிரெடிட் பேக்கேஜ் விலை மேலாண்மை
              </h2>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {creditPackages.map((pkg) => (
                  <div key={pkg.id} className="border rounded-lg p-4 bg-gray-50">
                    <div className="flex justify-between items-center mb-3">
                      <h3 className="font-semibold text-gray-800">{pkg.name}</h3>
                      <span className="text-sm text-gray-500">ID: {pkg.id}</span>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-600">கிரெடிட்கள்:</span>
                        <span className="font-semibold">{pkg.credits}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">போனஸ்:</span>
                        <span className="font-semibold text-green-600">{pkg.bonus_credits || 0}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">தற்போதைய விலை:</span>
                        <span className="font-semibold text-blue-600">${pkg.price_usd}</span>
                      </div>
                      <div className="mt-3">
                        <input
                          type="number"
                          step="0.01"
                          min="0"
                          placeholder="புதிய விலை"
                          className="w-full px-3 py-2 border rounded-md text-sm"
                          onKeyPress={(e) => {
                            if (e.key === 'Enter') {
                              const newPrice = parseFloat(e.target.value);
                              if (newPrice >= 0) {
                                handlePriceChange(pkg.id, newPrice);
                                e.target.value = '';
                              }
                            }
                          }}
                        />
                        <button
                          onClick={() => {
                            const input = document.querySelector(`input[placeholder="புதிய விலை"]`);
                            const newPrice = parseFloat(input.value);
                            if (newPrice >= 0) {
                              handlePriceChange(pkg.id, newPrice);
                              input.value = '';
                            }
                          }}
                          className="w-full mt-2 bg-blue-500 hover:bg-blue-600 text-white px-3 py-2 rounded-md text-sm transition-colors"
                        >
                          விலை மாற்று
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
        {activeTab === 'products' && <Products />}
        {activeTab === 'revenue' && <RevenueAnalytics />}
        {activeTab === 'content' && <SocialContentManagement />}
        {activeTab === 'settings' && <Settings />}
        {activeTab === 'users' && <UserManagement />}
        {activeTab === 'donations' && <Donations />}
        {activeTab === 'serviceTypes' && <ServiceTypes />}
        {activeTab === 'pricing' && <AdminPricingDashboard />}
        {activeTab === 'notifications' && <Notifications />}
        {activeTab === 'creditPackages' && <CreditPackages />}
        {activeTab === 'socialMarketing' && <SocialMediaMarketing />}
        {activeTab === 'followup' && <FollowUpManagement />}
        {activeTab === 'monitoring' && <SystemMonitoring />}
      </div>
    </div>
  );
};

export default AdminDashboard;

