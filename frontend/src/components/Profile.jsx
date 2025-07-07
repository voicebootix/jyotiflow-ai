import { useState, useEffect, useCallback } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, User, Calendar, Star, Clock, Award, Settings, Play, LogOut, RefreshCw } from 'lucide-react';
import spiritualAPI from '../lib/api';

const Profile = () => {
  const [searchParams] = useSearchParams();
  const [userProfile, setUserProfile] = useState(null);
  const [sessionHistory, setSessionHistory] = useState([]);
  const [creditBalance, setCreditBalance] = useState(0);
  const [donationHistory, setDonationHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedService, setSelectedService] = useState(null);
  const [services, setServices] = useState([]);
  const [servicesLoading, setServicesLoading] = useState(true);
  const [creditPackages, setCreditPackages] = useState([]);
  const [packagesLoading, setPackagesLoading] = useState(true);
  const [purchasing, setPurchasing] = useState(false);
  const navigate = useNavigate();

  // Real-time refresh state
  const [lastRefresh, setLastRefresh] = useState(new Date());
  const [refreshing, setRefreshing] = useState(false);

  // Check if user came from service selection or tab parameter
  useEffect(() => {
    const serviceFromUrl = searchParams.get('service');
    const tabFromUrl = searchParams.get('tab');
    
    if (serviceFromUrl) {
      setSelectedService(serviceFromUrl);
      setActiveTab('services');
    }
    
    if (tabFromUrl && ['overview', 'services', 'sessions', 'credits', 'settings'].includes(tabFromUrl)) {
      setActiveTab(tabFromUrl);
    }
  }, [searchParams]);

  const loadCreditPackages = async () => {
    try {
      const result = await spiritualAPI.getCreditPackages();
      if (result && result.success) {
        setCreditPackages(result.packages || []);
      }
    } catch (error) {
      console.log('Credit packages loading blessed with patience:', error);
    }
  };

  const purchaseCredits = async (packageId) => {
    setPurchasing(true);
    try {
      const result = await spiritualAPI.purchaseCredits(packageId);
      if (result && result.success) {
        const { credits_purchased, bonus_credits, total_credits } = result.data;
        
        // Show success message with bonus details
        if (bonus_credits > 0) {
          alert(`✅ வெற்றிகரமாக ${total_credits} கிரெடிட்கள் வாங்கப்பட்டன!\n\n📦 ${credits_purchased} அடிப்படை + ${bonus_credits} போனஸ் = ${total_credits} மொத்தம்`);
        } else {
          alert(`✅ வெற்றிகரமாக ${total_credits} கிரெடிட்கள் வாங்கப்பட்டன!`);
        }
        
        // Immediately update user profile with new credits
        const profile = await spiritualAPI.getUserProfile();
        if (profile && profile.success) {
          setUserProfile(profile.data);
        }
        
        // Refresh credit packages to show updated pricing if needed
        loadCreditPackages();
        
        // Track purchase for analytics
        await spiritualAPI.trackSpiritualEngagement('credit_purchase', {
          package_id: packageId,
          credits_purchased: credits_purchased,
          bonus_credits: bonus_credits,
          total_credits: total_credits
        });
      } else {
        alert('கிரெடிட் வாங்குதல் தோல்வி. தயவுசெய்து மீண்டும் முயற்சிக்கவும்.');
      }
    } catch (error) {
      console.error('Credit purchase error:', error);
      alert('கிரெடிட் வாங்குதல் தோல்வி - தயவுசெய்து மீண்டும் முயற்சிக்கவும்.');
    } finally {
      setPurchasing(false);
    }
  };

  useEffect(() => {
    if (!spiritualAPI.isAuthenticated()) {
      navigate('/login', { replace: true });
    }
    
    loadProfileData();
    spiritualAPI.trackSpiritualEngagement('profile_visit');

    // Set up real-time refresh every 30 seconds
    const refreshInterval = setInterval(() => {
      refreshData();
    }, 30000);

    return () => clearInterval(refreshInterval);
  }, []);

  const loadProfileData = async () => {
    try {
      // Load user profile
      const profile = await spiritualAPI.getUserProfile();
      if (profile && profile.id) {
        setUserProfile(profile);
      }

      // Load session history
      const history = await spiritualAPI.getSessionHistory();
      if (history && Array.isArray(history)) {
        setSessionHistory(history);
      } else if (history && history.success && Array.isArray(history.data)) {
        setSessionHistory(history.data);
      }

      // Load credit balance
      const credits = await spiritualAPI.getCreditBalance();
      if (credits && credits.data && typeof credits.data.credits === 'number') {
        setCreditBalance(credits.data.credits);
      } else if (typeof credits === 'number') {
        setCreditBalance(credits);
      }

      // Load services
      const servicesData = await spiritualAPI.request('/api/services/types');
      if (servicesData && servicesData.success) {
        setServices(servicesData.data || []);
      } else {
        setServices([]);
      }
      setServicesLoading(false);

      // Load credit packages
      const packagesResult = await spiritualAPI.getCreditPackages();
      if (packagesResult && packagesResult.success) {
        setCreditPackages(packagesResult.packages || []);
      }
      setPackagesLoading(false);
    } catch (error) {
      console.log('Profile data loading blessed with patience:', error);
      setServicesLoading(false);
      setPackagesLoading(false);
    } finally {
      setIsLoading(false);
    }
  };

  // Real-time refresh function
  const refreshData = useCallback(async () => {
    try {
      setRefreshing(true);
      
      // Load credit balance
      const credits = await spiritualAPI.getCreditBalance();
      if (credits && credits.success) {
        setCreditBalance(credits.data.credits || 0);
      }

      // Load services
      const servicesData = await spiritualAPI.request('/api/services/types');
      if (servicesData && servicesData.success) {
        setServices(servicesData.data || []);
      } else {
        setServices([]);
      }

      // Load credit packages
      const packagesData = await spiritualAPI.request('/api/services/credit-packages');
      if (packagesData && packagesData.success) {
        setCreditPackages(packagesData.data || []);
      } else {
        setCreditPackages([]);
      }

      setLastRefresh(new Date());
    } catch (error) {
      console.log('Real-time refresh blessed with patience:', error);
    } finally {
      setRefreshing(false);
    }
  }, []);

  // Manual refresh function
  const handleManualRefresh = async () => {
    await refreshData();
  };

  const getSubscriptionBadge = (tier) => {
    const badges = {
      'basic': { color: 'bg-gray-100 text-gray-800', icon: '🌱', name: 'Basic' },
      'clarity': { color: 'bg-blue-100 text-blue-800', icon: '🔮', name: 'Clarity Plus' },
      'love': { color: 'bg-pink-100 text-pink-800', icon: '💕', name: 'AstroLove' },
      'premium': { color: 'bg-yellow-100 text-yellow-800', icon: '🌟', name: 'Premium' },
      'elite': { color: 'bg-purple-100 text-purple-800', icon: '👑', name: 'Elite' }
    };
    
    return badges[tier] || badges['basic'];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const handleLogout = () => {
    spiritualAPI.logout();
    navigate('/', { replace: true });
  };

  if (isLoading) {
    return (
      <div className="pt-16 min-h-screen flex items-center justify-center">
        <div className="consciousness-pulse text-center">
          <div className="om-symbol text-6xl">👤</div>
          <p className="text-white mt-4">Loading your spiritual profile...</p>
        </div>
      </div>
    );
  }

  if (!userProfile) {
    return (
      <div className="pt-16 min-h-screen flex items-center justify-center">
        <div className="text-center sacred-card p-12">
          <div className="text-6xl mb-6">🔐</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-4">
            Profile Access Unavailable
          </h2>
          <p className="text-gray-600 mb-6">
            Unable to load your spiritual profile. Please try signing in again.
          </p>
          <Link to="/login" className="divine-button">
            Sign In Again
          </Link>
        </div>
      </div>
    );
  }

  const subscriptionBadge = getSubscriptionBadge(userProfile.subscription_tier);

  return (
    <div className="pt-16 min-h-screen">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 py-16 relative">
        <div className="max-w-4xl mx-auto px-4">
          <div className="flex items-center justify-between mb-6">
            <Link 
              to="/" 
              className="inline-flex items-center text-white hover:text-gray-200 transition-colors"
            >
              <ArrowLeft size={20} className="mr-2" />
              Back to Home
            </Link>
            
            {/* Refresh Button */}
            <button
              onClick={handleManualRefresh}
              disabled={refreshing}
              className="inline-flex items-center text-white hover:text-gray-200 transition-colors disabled:opacity-50"
              title="Refresh prices and data"
            >
              <RefreshCw size={20} className={`mr-2 ${refreshing ? 'animate-spin' : ''}`} />
              {refreshing ? 'Refreshing...' : 'Refresh'}
            </button>
          </div>
          
          {/* Logout button top right */}
          <button
            onClick={handleLogout}
            className="absolute top-6 right-6 bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-full flex items-center shadow-lg z-10"
          >
            <LogOut size={18} className="mr-2" /> Logout
          </button>
          
          <div className="flex flex-col md:flex-row items-center md:items-start space-y-4 md:space-y-0 md:space-x-6">
            <div className="w-24 h-24 bg-white rounded-full flex items-center justify-center">
              <User size={40} className="text-gray-600" />
            </div>
            
            <div className="text-center md:text-left">
              <h1 className="text-3xl md:text-4xl font-bold text-white mb-2">
                {userProfile.name || 'Divine Soul'}
              </h1>
              <p className="text-white opacity-90 mb-3">{userProfile.email}</p>
              <div className="flex flex-col sm:flex-row items-center space-y-2 sm:space-y-0 sm:space-x-4">
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold ${subscriptionBadge.color}`}>
                  <span className="mr-1">{subscriptionBadge.icon}</span>
                  {subscriptionBadge.name}
                </span>
                <span className="text-white opacity-75 text-sm">
                  Member since {formatDate(userProfile.created_at || new Date())}
                </span>
              </div>
              
              {/* Last Updated Indicator */}
              <div className="text-white opacity-75 text-xs mt-2">
                Last updated: {lastRefresh.toLocaleTimeString()}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-black bg-opacity-50 py-4">
        <div className="max-w-4xl mx-auto px-4">
          <div className="flex space-x-6 overflow-x-auto">
            {[
              { id: 'overview', label: 'Overview', icon: User },
              { id: 'services', label: 'Services', icon: Play },
              { id: 'sessions', label: 'Sessions', icon: Calendar },
              { id: 'credits', label: 'Credits', icon: Star },
              { id: 'settings', label: 'Settings', icon: Settings }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-300 whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'bg-yellow-400 text-black'
                    : 'text-white hover:bg-gray-700'
                }`}
              >
                <tab.icon size={16} />
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Tab Content */}
      <div className="py-16 px-4">
        <div className="max-w-4xl mx-auto">
          {activeTab === 'overview' && (
            <div className="space-y-8">
              {/* Quick Stats */}
              <div className="grid md:grid-cols-3 gap-6">
                <div className="sacred-card p-6 text-center">
                  <div className="text-3xl mb-2">📊</div>
                  <div className="text-2xl font-bold text-gray-800">{sessionHistory.length}</div>
                  <div className="text-gray-600">Total Sessions</div>
                </div>
                <div className="sacred-card p-6 text-center">
                  <div className="text-3xl mb-2">⭐</div>
                  <div className="text-2xl font-bold text-gray-800">{creditBalance}</div>
                  <div className="text-gray-600">Available Credits</div>
                </div>
                <div className="sacred-card p-6 text-center">
                  <div className="text-3xl mb-2">🏆</div>
                  <div className="text-2xl font-bold text-gray-800">
                    {Math.floor((Date.now() - new Date(userProfile.created_at || Date.now())) / (1000 * 60 * 60 * 24))}
                  </div>
                  <div className="text-gray-600">Days on Journey</div>
                </div>
              </div>

              {/* Recent Activity */}
              <div className="sacred-card p-8">
                <h2 className="text-2xl font-bold text-gray-800 mb-6">Recent Spiritual Activity</h2>
                {sessionHistory.length > 0 ? (
                  <div className="space-y-4">
                    {sessionHistory.slice(0, 3).map((session, index) => (
                      <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <div className="text-2xl">🕉️</div>
                          <div>
                            <div className="font-semibold text-gray-800">
                              {session.service_type || 'Spiritual Guidance'}
                            </div>
                            <div className="text-sm text-gray-600">
                              {formatDate(session.created_at)}
                            </div>
                          </div>
                        </div>
                        <div className="text-sm text-gray-500">
                          {session.duration || '30 min'}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="text-4xl mb-4">🌱</div>
                    <p className="text-gray-600">Your spiritual journey is just beginning. Start your first session!</p>
                    <Link to="/spiritual-guidance" className="divine-button mt-4 inline-block">
                      Begin Sacred Journey
                    </Link>
                  </div>
                )}
              </div>
            </div>
          )}


          {activeTab === 'services' && (
            <div className="space-y-8">
              <div className="sacred-card p-8">
                <h2 className="text-2xl font-bold text-gray-800 mb-6">
                  🕉️ Your Spiritual Services
                </h2>
                
                {selectedService && (
                  <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <p className="text-yellow-800">
                      ✨ You selected: <strong>{selectedService.charAt(0).toUpperCase() + selectedService.slice(1)}</strong> service
                    </p>
                  </div>
                )}

                {servicesLoading ? (
                  <div className="text-center py-8">
                    <div className="text-4xl mb-4">🔄</div>
                    <p className="text-gray-600">சேவைகள் ஏற்றப்படுகிறது...</p>
                  </div>
                ) : (
                  <div className="grid md:grid-cols-2 gap-6">
                    {(Array.isArray(services) ? services : []).filter(s => s.enabled).map((service) => {
                      const hasEnoughCredits = creditBalance >= service.credits_required;
                      
                      return (
                        <div 
                          key={service.id}
                          className={`sacred-card p-6 border-2 ${
                            selectedService === service.name 
                              ? 'border-yellow-400 bg-yellow-50' 
                              : hasEnoughCredits
                                ? 'border-gray-200'
                                : 'border-red-200 bg-red-50'
                          }`}
                        >
                          <div className="text-center mb-4">
                            <div className="text-4xl mb-2">
                              {service.icon || (service.is_video ? '🎥' : service.is_audio ? '🔊' : '🔮')}
                            </div>
                            <h3 className="text-xl font-bold text-gray-800">{service.display_name || service.name}</h3>
                            <p className="text-gray-600 text-sm">{service.description}</p>
                            <div className="text-2xl font-bold text-gray-800 mt-2">₹{service.credits_required} கிரெடிட்ஸ்</div>
                            <div className="bg-blue-500 text-white text-xs px-2 py-1 rounded-full mt-1">{service.duration_minutes} நிமிடங்கள்</div>
                          </div>
                          
                          {hasEnoughCredits ? (
                            <Link 
                              to={`/spiritual-guidance?service=${service.name}`}
                              className="w-full divine-button block text-center"
                            >
                              Start {service.name} Session
                            </Link>
                          ) : (
                            <div className="text-center space-y-3">
                              <div className="bg-red-500 text-white text-sm px-3 py-1 rounded-full font-semibold">
                                ⚠️ போதுமான கிரெடிட்ஸ் இல்லை
                              </div>
                              <div className="text-red-600 text-xs">
                                தேவை: {service.credits_required} கிரெடிட்ஸ் | உள்ளது: {creditBalance} கிரெடிட்ஸ்
                              </div>
                              <Link 
                                to="/profile?tab=credits"
                                className="w-full bg-yellow-500 hover:bg-yellow-600 text-black font-bold px-4 py-2 rounded-lg transition-colors block text-center"
                              >
                                💰 கிரெடிட்ஸ் வாங்க
                              </Link>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          )}
          
          {activeTab === 'sessions' && (
            <div className="sacred-card p-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">Session History</h2>
              {sessionHistory.length > 0 ? (
                <div className="space-y-4">
                  {sessionHistory.map((session, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h3 className="font-semibold text-gray-800 text-lg">
                            {session.service_type || 'Spiritual Guidance Session'}
                          </h3>
                          <p className="text-gray-600">{formatDate(session.created_at)}</p>
                        </div>
                        <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">
                          Completed
                        </span>
                      </div>
                      
                      {session.question && (
                        <div className="mb-4">
                          <h4 className="font-medium text-gray-700 mb-2">Your Question:</h4>
                          <p className="text-gray-600 italic">"{session.question}"</p>
                        </div>
                      )}
                      
                      <div className="flex items-center justify-between text-sm text-gray-500">
                        <span>Duration: {session.duration || '30 minutes'}</span>
                        <button className="text-yellow-600 hover:text-yellow-800 transition-colors">
                          View Details
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="text-6xl mb-6">📚</div>
                  <h3 className="text-xl font-bold text-gray-800 mb-4">No Sessions Yet</h3>
                  <p className="text-gray-600 mb-6">
                    Your spiritual journey awaits. Begin with your first guidance session.
                  </p>
                  <Link to="/spiritual-guidance" className="divine-button">
                    Start First Session
                  </Link>
                </div>
              )}
            </div>
          )}

          {activeTab === 'credits' && (
            <div>
              <h2 className="text-2xl font-bold text-gray-800 mb-6">Credit Management</h2>
              
              {/* Current Credits */}
              <div className="bg-gradient-to-r from-yellow-400 to-orange-500 text-white rounded-lg p-6 mb-8">
                <div className="text-center">
                  <div className="text-4xl font-bold mb-2">{userProfile?.credits || 0}</div>
                  <div className="text-lg">Available Credits</div>
                </div>
              </div>

              {/* Credit Packages */}
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                {creditPackages.map((pkg) => (
                  <div key={pkg.id} className="bg-white rounded-lg shadow-lg p-6 border-2 border-gray-200 hover:border-yellow-400 transition-all">
                    <div className="text-center">
                      <h3 className="text-xl font-bold text-gray-800 mb-2">{pkg.name}</h3>
                      <div className="text-3xl font-bold text-green-600 mb-2">
                        {pkg.credits + (pkg.bonus_credits || 0)} Credits
                      </div>
                      <div className="text-sm text-gray-600 mb-2">
                        {pkg.credits} base + {pkg.bonus_credits || 0} bonus
                      </div>
                      <div className="text-2xl font-bold text-gray-800 mb-4">${pkg.price_usd}</div>
                      <p className="text-sm text-gray-600 mb-4">{pkg.description}</p>
                      <button
                        onClick={() => purchaseCredits(pkg.id)}
                        disabled={purchasing}
                        className="w-full bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-semibold transition-colors disabled:opacity-50"
                      >
                        {purchasing ? 'Processing...' : 'Purchase'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-8 text-center">
                <p className="text-gray-600">
                  💡 Larger packages include bonus credits for better value!
                </p>
              </div>
            </div>
          )}

          {activeTab === 'settings' && (
            <div className="sacred-card p-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">Account Settings</h2>
              
              <div className="space-y-6">
                {/* Profile Information */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">Profile Information</h3>
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Name</label>
                      <input
                        type="text"
                        value={userProfile.name || ''}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-500"
                        readOnly
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                      <input
                        type="email"
                        value={userProfile.email || ''}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-500"
                        readOnly
                      />
                    </div>
                  </div>
                </div>

                {/* Subscription */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">Subscription</h3>
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">{subscriptionBadge.icon}</span>
                      <div>
                        <div className="font-semibold text-gray-800">{subscriptionBadge.name}</div>
                        <div className="text-sm text-gray-600">Current plan</div>
                      </div>
                    </div>
                    <Link to="/spiritual-guidance" className="divine-button">
                      Upgrade Plan
                    </Link>
                  </div>
                </div>

                {/* Notifications */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">Notifications</h3>
                  <div className="space-y-3">
                    <label className="flex items-center">
                      <input type="checkbox" className="mr-3" defaultChecked />
                      <span className="text-gray-700">Satsang reminders</span>
                    </label>
                    <label className="flex items-center">
                      <input type="checkbox" className="mr-3" defaultChecked />
                      <span className="text-gray-700">Session confirmations</span>
                    </label>
                    <label className="flex items-center">
                      <input type="checkbox" className="mr-3" />
                      <span className="text-gray-700">Marketing updates</span>
                    </label>
                  </div>
                </div>

                {/* Danger Zone */}
                <div className="border-t pt-6">
                  <h3 className="text-lg font-semibold text-red-600 mb-4">Danger Zone</h3>
                  <button className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors">
                    Delete Account
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Profile;

