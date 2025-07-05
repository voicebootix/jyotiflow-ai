import { useState, useEffect } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, User, Calendar, Star, Clock, Award, Settings, Play, LogOut } from 'lucide-react';
import spiritualAPI from '../lib/api';

const Profile = () => {
  const [searchParams] = useSearchParams();
  const [userProfile, setUserProfile] = useState(null);
  const [sessionHistory, setSessionHistory] = useState([]);
  const [creditBalance, setCreditBalance] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedService, setSelectedService] = useState(null);
  const [services, setServices] = useState([]);
  const [servicesLoading, setServicesLoading] = useState(true);
  const [creditPackages, setCreditPackages] = useState([]);
  const [packagesLoading, setPackagesLoading] = useState(true);
  const navigate = useNavigate();

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

  useEffect(() => {
    if (!spiritualAPI.isAuthenticated()) {
      navigate('/login', { replace: true });
    }
    
    loadProfileData();
    spiritualAPI.trackSpiritualEngagement('profile_visit');
  }, []);

  const loadProfileData = async () => {
    try {
      // Load user profile
      const profile = await spiritualAPI.getUserProfile();
      if (profile && profile.success) {
        setUserProfile(profile.data);
      }

      // Load session history
      const history = await spiritualAPI.getSessionHistory();
      if (history && history.success) {
        setSessionHistory(history.data || []);
      }

      // Load credit balance
      const credits = await spiritualAPI.getCreditBalance();
      if (credits && credits.success) {
        setCreditBalance(credits.data.credits || 0);
      }

      // Load services
      const servicesData = await spiritualAPI.request('/api/admin/products/service-types');
      setServices(Array.isArray(servicesData) ? servicesData : []);
      setServicesLoading(false);

      // Load credit packages
      const packagesData = await spiritualAPI.request('/api/admin/products/credit-packages');
      setCreditPackages(Array.isArray(packagesData) ? packagesData : []);
      setPackagesLoading(false);
    } catch (error) {
      console.log('Profile data loading blessed with patience:', error);
      setServicesLoading(false);
      setPackagesLoading(false);
    } finally {
      setIsLoading(false);
    }
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
          <Link 
            to="/" 
            className="inline-flex items-center text-white hover:text-gray-200 mb-6 transition-colors"
          >
            <ArrowLeft size={20} className="mr-2" />
            Back to Home
          </Link>
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
                              {service.is_video ? '🎥' : service.is_audio ? '🔊' : '🔮'}
                            </div>
                            <h3 className="text-xl font-bold text-gray-800">{service.name}</h3>
                            <p className="text-gray-600 text-sm">{service.description}</p>
                            <div className="text-2xl font-bold text-gray-800 mt-2">${service.price_usd}</div>
                            <div className="text-sm text-gray-500">{service.credits_required} கிரெடிட்ஸ்</div>
                            <div className="text-sm text-gray-500">{service.duration_minutes} நிமிடம்</div>
                          </div>
                          
                          {hasEnoughCredits ? (
                            <Link 
                              to={`/spiritual-guidance?service=${service.name}`}
                              className="w-full divine-button block text-center"
                            >
                              Start {service.name} Session
                            </Link>
                          ) : (
                            <div className="text-center">
                              <div className="text-red-600 text-sm mb-2">போதுமான கிரெடிட்ஸ் இல்லை</div>
                              <Link 
                                to="/profile?tab=credits"
                                className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors block text-center"
                              >
                                Buy Credits
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
            <div className="space-y-8">
              {/* Credit Balance */}
              <div className="sacred-card p-8 text-center">
                <div className="text-6xl mb-4">⭐</div>
                <h2 className="text-3xl font-bold text-gray-800 mb-2">
                  {creditBalance} Credits Available
                </h2>
                <p className="text-gray-600 mb-6">
                  Use credits for premium guidance sessions and special features
                </p>
                <button 
                  onClick={() => spiritualAPI.purchaseCredits(100)}
                  className="divine-button"
                >
                  Purchase More Credits
                </button>
              </div>

              {/* Credit Packages */}
              {packagesLoading ? (
                <div className="text-center py-8">
                  <div className="text-4xl mb-4">🔄</div>
                  <p className="text-gray-600">கிரெடிட் தொகுப்புகள் ஏற்றப்படுகிறது...</p>
                </div>
              ) : (
                <div className="grid md:grid-cols-3 gap-6">
                  {(Array.isArray(creditPackages) ? creditPackages : []).filter(pkg => pkg.enabled).map((creditPkg, index) => (
                    <div 
                      key={creditPkg.id}
                      className={`sacred-card p-6 text-center ${
                        index === 1 ? 'ring-2 ring-yellow-400' : ''
                      }`}
                    >
                      {index === 1 && (
                        <div className="bg-yellow-400 text-black text-xs font-bold px-2 py-1 rounded-full inline-block mb-3">
                          BEST VALUE
                        </div>
                      )}
                      <div className="text-3xl mb-3">💎</div>
                      <div className="text-2xl font-bold text-gray-800 mb-2">
                        {creditPkg.name}
                      </div>
                      <div className="text-gray-600 mb-2">
                        {creditPkg.credits_amount + creditPkg.bonus_credits} கிரெடிட்ஸ்
                      </div>
                      <div className="text-gray-600 mb-4">${creditPkg.price_usd}</div>
                      {creditPkg.bonus_credits > 0 && (
                        <div className="text-green-600 text-sm mb-4">
                          +{creditPkg.bonus_credits} போனஸ் கிரெடிட்ஸ்
                        </div>
                      )}
                      <div className="text-gray-500 text-xs mb-4">{creditPkg.description}</div>
                      <button 
                        onClick={() => spiritualAPI.purchaseCredits(creditPkg.credits_amount)}
                        className="divine-button w-full"
                      >
                        வாங்கு
                      </button>
                    </div>
                  ))}
                </div>
              )}
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

