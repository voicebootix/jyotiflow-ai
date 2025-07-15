import { useState, useEffect, useCallback } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, User, Calendar, Star, Clock, Award, Settings, Play, LogOut, RefreshCw, Mail, MessageSquare, Phone, CheckCircle, AlertCircle } from 'lucide-react';
import spiritualAPI from '../lib/api';
import userDashboardAPI from '../services/userDashboardAPI';
import SessionAnalytics from './dashboard/SessionAnalytics';
import CommunityHub from './dashboard/CommunityHub';

const Profile = () => {
  const [searchParams] = useSearchParams();
  const [userProfile, setUserProfile] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);
  const [sessionHistory, setSessionHistory] = useState([]);
  const [followUpData, setFollowUpData] = useState({});
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
  const [recommendations, setRecommendations] = useState([]);
  const [sessionAnalytics, setSessionAnalytics] = useState(null);
  const [spiritualProgress, setSpiritualProgress] = useState(null);
  const navigate = useNavigate();

  // Real-time refresh state
  const [lastRefresh, setLastRefresh] = useState(new Date());
  const [refreshing, setRefreshing] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(null);

  // Birth chart generation state
  const [birthChartGenerating, setBirthChartGenerating] = useState(false);

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
      setIsLoading(true);
      
      // Load comprehensive dashboard data
      const dashboardResponse = await userDashboardAPI.getDashboardData();
      
      if (dashboardResponse && dashboardResponse.success) {
        const { data } = dashboardResponse;
        
        // Set all dashboard data
        setDashboardData(data);
        setUserProfile(data.profile);
        setSessionHistory(data.sessions || []);
        setCreditBalance(data.credits?.current_balance || 0);
        setCreditPackages(data.credits?.available_packages || []);
        setServices(data.services || []);
        setRecommendations(data.recommendations || []);
        setSpiritualProgress(data.profile?.spiritual_progress || null);
        
        // Process follow-up data
        const followUpMap = {};
        if (data.followups && Array.isArray(data.followups)) {
          for (const followup of data.followups) {
            const sessionId = followup.session_id;
            if (!followUpMap[sessionId]) {
              followUpMap[sessionId] = [];
            }
            followUpMap[sessionId].push(followup);
          }
        }
        setFollowUpData(followUpMap);
        
        // Load session analytics
        const analytics = await userDashboardAPI.getSessionAnalytics();
        setSessionAnalytics(analytics);
        
        // Load community participation
        const community = await userDashboardAPI.getCommunityParticipation();
        setDashboardData(prev => ({ ...prev, community }));
        
      } else {
        // Fallback to individual API calls
        console.log('Dashboard API unavailable, using fallback...');
        
        // Load user profile
        const profile = await spiritualAPI.getUserProfile();
        if (profile && profile.id) {
          setUserProfile(profile);
        }

        // Load session history
        const history = await spiritualAPI.getSessionHistory();
        let sessions = [];
        if (history && Array.isArray(history)) {
          sessions = history;
          setSessionHistory(history);
        } else if (history && history.success && Array.isArray(history.data)) {
          sessions = history.data;
          setSessionHistory(history.data);
        }

        // Load follow-up data for each session
        const followUpMap = {};
        for (const session of sessions) {
          if (session.session_id || session.id) {
            try {
              const sessionId = session.session_id || session.id;
              const followUps = await spiritualAPI.request(`/api/followup/session/${sessionId}`);
              if (followUps && followUps.success && Array.isArray(followUps.data)) {
                followUpMap[sessionId] = followUps.data;
              }
            } catch (error) {
              console.log(`Follow-up loading for session ${session.session_id || session.id} blessed with patience:`, error);
            }
          }
        }
        setFollowUpData(followUpMap);

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

        // Load credit packages
        const packagesResult = await spiritualAPI.getCreditPackages();
        if (packagesResult && packagesResult.success) {
          setCreditPackages(packagesResult.packages || []);
        }
      }
      
      setServicesLoading(false);
      setPackagesLoading(false);
    } catch (error) {
      console.log('Profile data loading blessed with patience:', error);
      setServicesLoading(false);
      setPackagesLoading(false);
    } finally {
      setIsLoading(false);
    }
  };

  // Enhanced real-time refresh function
  const refreshData = useCallback(async () => {
    try {
      setRefreshing(true);
      
      // Comprehensive dashboard refresh
      const dashboardResponse = await userDashboardAPI.refreshDashboard();
      
      if (dashboardResponse && dashboardResponse.success) {
        const { data } = dashboardResponse;
        
        // Update all dashboard data
        setDashboardData(data);
        setUserProfile(data.profile);
        setSessionHistory(data.sessions || []);
        setCreditBalance(data.credits?.current_balance || 0);
        setCreditPackages(data.credits?.available_packages || []);
        setServices(data.services || []);
        setRecommendations(data.recommendations || []);
        setSpiritualProgress(data.profile?.spiritual_progress || null);
        
        // Update follow-up data
        const followUpMap = {};
        if (data.followups && Array.isArray(data.followups)) {
          for (const followup of data.followups) {
            const sessionId = followup.session_id;
            if (!followUpMap[sessionId]) {
              followUpMap[sessionId] = [];
            }
            followUpMap[sessionId].push(followup);
          }
        }
        setFollowUpData(followUpMap);
        
        // Update session analytics
        const analytics = await userDashboardAPI.getSessionAnalytics();
        setSessionAnalytics(analytics);
        
        // Update community data
        const community = await userDashboardAPI.getCommunityParticipation();
        setDashboardData(prev => ({ ...prev, community }));
        
        console.log('🔄 Dashboard refreshed successfully');
      } else {
        // Fallback refresh of individual components
        const [credits, servicesData, packagesData] = await Promise.all([
          spiritualAPI.getCreditBalance(),
          spiritualAPI.request('/api/services/types'),
          spiritualAPI.request('/api/services/credit-packages')
        ]);
        
        if (credits && credits.success) {
          setCreditBalance(credits.data.credits || 0);
        }
        
        if (servicesData && servicesData.success) {
          setServices(servicesData.data || []);
        }
        
        if (packagesData && packagesData.success) {
          setCreditPackages(packagesData.data || []);
        }
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
    navigate('/login', { replace: true });
  };

  // Birth chart generation functions - Refactored to eliminate duplication
  const handleBirthChartAction = async (action = 'generate', successMessage = '') => {
    setBirthChartGenerating(true);
    try {
      const result = await userDashboardAPI.generateUserBirthChart();
      if (result) {
        // Update dashboard data with new birth chart
        setDashboardData(prev => ({
          ...prev,
          birthChart: result
        }));
        
        // Show success message using toast notification
        showToast('success', successMessage || '✅ Birth chart operation completed successfully!');
      } else {
        showToast('error', '❌ Failed to complete birth chart operation. Please try again.');
      }
    } catch (error) {
      console.error('Birth chart operation error:', error);
      // Provide specific error messages based on error type
      let errorMessage = '❌ Error completing birth chart operation. Please try again.';
      if (error.message?.includes('network')) {
        errorMessage = '❌ Network error. Please check your connection and try again.';
      } else if (error.message?.includes('unauthorized')) {
        errorMessage = '❌ Session expired. Please sign in again.';
      } else if (error.message?.includes('birth details')) {
        errorMessage = '❌ Please complete your birth details in your profile first.';
      }
      showToast('error', errorMessage);
    } finally {
      setBirthChartGenerating(false);
    }
  };

  const handleGenerateBirthChart = () => {
    handleBirthChartAction('generate', '✅ Your complete birth chart with Swamiji\'s insights has been generated successfully!');
  };

  const handleRefreshBirthChart = () => {
    handleBirthChartAction('refresh', '✅ Your birth chart has been refreshed with the latest insights!');
  };

  // Toast notification function
  const showToast = (type, message) => {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 z-50 px-6 py-4 rounded-lg shadow-lg transform transition-all duration-300 ${
      type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
    }`;
    toast.textContent = message;
    
    // Add to DOM
    document.body.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
      toast.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after 5 seconds
    setTimeout(() => {
      toast.style.transform = 'translateX(100%)';
      setTimeout(() => {
        if (document.body.contains(toast)) {
          document.body.removeChild(toast);
        }
      }, 300);
    }, 5000);
  };

  // Auto-load birth chart for registered users
  const loadBirthChartForRegisteredUser = async () => {
    if (userProfile && userProfile.birth_date && !dashboardData?.birthChart) {
      setBirthChartGenerating(true);
      try {
        const result = await userDashboardAPI.getUserBirthChart();
        if (result) {
          setDashboardData(prev => ({
            ...prev,
            birthChart: result
          }));
        } else {
          // Auto-generate if not available
          const generatedResult = await userDashboardAPI.generateUserBirthChart();
          if (generatedResult) {
            setDashboardData(prev => ({
              ...prev,
              birthChart: generatedResult
            }));
          }
        }
      } catch (error) {
        console.error('Auto-load birth chart error:', error);
      } finally {
        setBirthChartGenerating(false);
      }
    }
  };

  // Auto-load birth chart when profile data is loaded
  useEffect(() => {
    if (userProfile && userProfile.birth_date && !dashboardData?.birthChart) {
      loadBirthChartForRegisteredUser();
    }
  }, [userProfile, dashboardData?.birthChart]);

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
              
              {/* Last Updated Indicator & Auto-refresh Toggle */}
              <div className="flex items-center space-x-4 text-white opacity-75 text-xs mt-2">
                <span>Last updated: {lastRefresh.toLocaleTimeString()}</span>
                <label className="flex items-center space-x-1 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={autoRefresh}
                    onChange={(e) => setAutoRefresh(e.target.checked)}
                    className="rounded border-gray-300 text-purple-600 focus:ring-purple-500 h-3 w-3"
                  />
                  <span className="text-xs">Auto-refresh</span>
                </label>
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
              { id: 'analytics', label: 'Analytics', icon: Award },
              { id: 'community', label: 'Community', icon: MessageSquare },
              { id: 'messages', label: 'Follow-ups', icon: Mail },
              { id: 'birthchart', label: 'Birth Chart', icon: Star },
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
              {/* Spiritual Progress Header */}
              {spiritualProgress && (
                <div className="sacred-card p-8 bg-gradient-to-r from-purple-50 to-indigo-50">
                  <div className="text-center">
                    <div className="text-5xl mb-4">🧘</div>
                    <h2 className="text-3xl font-bold text-gray-800 mb-2">
                      {spiritualProgress.spiritual_level || 'Spiritual Seeker'}
                    </h2>
                    <p className="text-gray-600 mb-4">
                      Your spiritual journey progress: {spiritualProgress.progress_percentage || 0}%
                    </p>
                    <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
                      <div 
                        className="bg-gradient-to-r from-purple-500 to-indigo-500 h-3 rounded-full transition-all duration-300"
                        style={{ width: `${spiritualProgress.progress_percentage || 0}%` }}
                      ></div>
                    </div>
                    <div className="text-sm text-gray-500">
                      Next milestone: {spiritualProgress.next_milestone || 5} sessions
                    </div>
                  </div>
                </div>
              )}

              {/* Enhanced Stats Grid */}
              <div className="grid md:grid-cols-4 gap-6">
                <div className="sacred-card p-6 text-center">
                  <div className="text-3xl mb-2">📊</div>
                  <div className="text-2xl font-bold text-gray-800">
                    {spiritualProgress?.total_sessions || sessionHistory.length}
                  </div>
                  <div className="text-gray-600">Total Sessions</div>
                  <div className="text-xs text-gray-500 mt-1">
                    {spiritualProgress?.completion_rate || 0}% completion rate
                  </div>
                </div>
                <div className="sacred-card p-6 text-center">
                  <div className="text-3xl mb-2">⭐</div>
                  <div className="text-2xl font-bold text-gray-800">{creditBalance}</div>
                  <div className="text-gray-600">Available Credits</div>
                  <div className="text-xs text-gray-500 mt-1">
                    {dashboardData?.credits?.spending_analysis?.total_spent || 0} total spent
                  </div>
                </div>
                <div className="sacred-card p-6 text-center">
                  <div className="text-3xl mb-2">🏆</div>
                  <div className="text-2xl font-bold text-gray-800">
                    {spiritualProgress?.milestones_achieved || 0}
                  </div>
                  <div className="text-gray-600">Milestones Achieved</div>
                  <div className="text-xs text-gray-500 mt-1">
                    {Math.floor((Date.now() - new Date(userProfile.created_at || Date.now())) / (1000 * 60 * 60 * 24))} days on journey
                  </div>
                </div>
                <div className="sacred-card p-6 text-center">
                  <div className="text-3xl mb-2">🤝</div>
                  <div className="text-2xl font-bold text-gray-800">
                    {dashboardData?.community?.satsang_attended || 0}
                  </div>
                  <div className="text-gray-600">Satsang Attended</div>
                  <div className="text-xs text-gray-500 mt-1">
                    {dashboardData?.community?.community_rank || 'New Member'}
                  </div>
                </div>
              </div>

              {/* AI Recommendations */}
              {recommendations && recommendations.length > 0 && (
                <div className="sacred-card p-8">
                  <h2 className="text-2xl font-bold text-gray-800 mb-6">
                    🤖 Personalized Recommendations
                  </h2>
                  <div className="space-y-4">
                    {recommendations.slice(0, 3).map((recommendation, index) => (
                      <div key={index} className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
                        <div className="flex items-start space-x-3">
                          <div className="text-2xl">
                            {recommendation.type === 'birth_chart' ? '🌟' : 
                             recommendation.type === 'first_session' ? '🚀' : '💡'}
                          </div>
                          <div className="flex-1">
                            <h3 className="font-semibold text-gray-800 mb-1">
                              {recommendation.title}
                            </h3>
                            <p className="text-gray-600 text-sm mb-2">
                              {recommendation.description}
                            </p>
                            <div className="flex items-center space-x-2">
                              <span className={`text-xs px-2 py-1 rounded ${
                                recommendation.priority === 'high' ? 'bg-red-100 text-red-700' :
                                recommendation.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                                'bg-green-100 text-green-700'
                              }`}>
                                {recommendation.priority} priority
                              </span>
                              {recommendation.action && (
                                <button 
                                  onClick={() => {
                                    if (recommendation.action === 'view_birth_chart') {
                                      navigate('/birth-chart');
                                    } else if (recommendation.action === 'book_session') {
                                      navigate('/spiritual-guidance');
                                    }
                                  }}
                                  className="text-xs bg-purple-600 text-white px-3 py-1 rounded hover:bg-purple-700 transition-colors"
                                >
                                  Take Action
                                </button>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Journey Insights */}
              {spiritualProgress?.journey_insights && (
                <div className="sacred-card p-8">
                  <h2 className="text-2xl font-bold text-gray-800 mb-6">
                    ✨ Your Spiritual Journey Insights
                  </h2>
                  <div className="space-y-3">
                    {spiritualProgress.journey_insights.map((insight, index) => (
                      <div key={index} className="p-4 bg-gradient-to-r from-green-50 to-teal-50 rounded-lg border border-green-200">
                        <div className="flex items-start space-x-3">
                          <div className="text-xl">🌟</div>
                          <p className="text-gray-700">{insight}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Session Analytics */}
              {sessionAnalytics && (
                <div className="sacred-card p-8">
                  <h2 className="text-2xl font-bold text-gray-800 mb-6">
                    📈 Session Analytics
                  </h2>
                  <div className="grid md:grid-cols-3 gap-6">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-purple-600">
                        {sessionAnalytics.average_duration || 0} min
                      </div>
                      <div className="text-sm text-gray-600">Average Duration</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">
                        {sessionAnalytics.average_effectiveness || 0}%
                      </div>
                      <div className="text-sm text-gray-600">Effectiveness Score</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {sessionAnalytics.most_active_day || 'Monday'}
                      </div>
                      <div className="text-sm text-gray-600">Most Active Day</div>
                    </div>
                  </div>
                </div>
              )}

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
                          {session.duration ? `${session.duration} min` : 'Completed'}
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

          {activeTab === 'analytics' && (
            <div className="space-y-8">
              <div className="sacred-card p-6">
                <h2 className="text-2xl font-bold text-gray-800 mb-4">
                  📊 Your Spiritual Journey Analytics
                </h2>
                <p className="text-gray-600 mb-6">
                  Discover patterns, track progress, and gain insights into your spiritual growth journey.
                </p>
              </div>
              
              {sessionHistory.length > 0 ? (
                <SessionAnalytics 
                  sessionData={sessionHistory}
                  spiritualProgress={spiritualProgress}
                  userProfile={userProfile}
                />
              ) : (
                <div className="sacred-card p-12 text-center">
                  <div className="text-6xl mb-6">📈</div>
                  <h3 className="text-2xl font-bold text-gray-800 mb-4">
                    No Analytics Data Yet
                  </h3>
                  <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
                    Start your spiritual journey to unlock detailed analytics and insights. 
                    Your first session will begin generating personalized data to track your progress.
                  </p>
                  <div className="space-y-4">
                    <Link 
                      to="/spiritual-guidance" 
                      className="inline-block bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-8 py-3 rounded-lg hover:from-purple-700 hover:to-indigo-700 transition-all duration-300"
                    >
                      Start Your First Session
                    </Link>
                    <div className="text-sm text-gray-500">
                      Or explore the{' '}
                      <button 
                        onClick={() => setActiveTab('birthchart')}
                        className="text-purple-600 hover:text-purple-700 underline"
                      >
                        Birth Chart
                      </button>
                      {' '}feature to begin your spiritual profile
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'community' && (
            <div className="space-y-8">
              <div className="sacred-card p-6">
                <h2 className="text-2xl font-bold text-gray-800 mb-4">
                  🤝 Spiritual Community
                </h2>
                <p className="text-gray-600 mb-6">
                  Connect with fellow seekers, join satsang events, and grow together on the spiritual path.
                </p>
              </div>
              
              <CommunityHub 
                userProfile={userProfile}
                communityData={dashboardData?.community}
              />
            </div>
          )}

          {activeTab === 'messages' && (
            <div className="space-y-8">
              <div className="sacred-card p-6">
                <h2 className="text-2xl font-bold text-gray-800 mb-4">
                  💌 Spiritual Follow-ups & Messages
                </h2>
                <p className="text-gray-600 mb-6">
                  Your personalized spiritual guidance messages and session follow-ups from Swamiji.
                </p>
              </div>

              {/* Follow-up Stats */}
              <div className="grid md:grid-cols-3 gap-6">
                <div className="sacred-card p-6 text-center bg-gradient-to-br from-blue-50 to-indigo-50">
                  <div className="text-3xl mb-2">📧</div>
                  <div className="text-2xl font-bold text-blue-700">
                    {Object.keys(followUpData).length}
                  </div>
                  <div className="text-gray-600">Follow-up Sessions</div>
                  <div className="text-xs text-blue-600 mt-1">
                    Total messages received
                  </div>
                </div>

                <div className="sacred-card p-6 text-center bg-gradient-to-br from-green-50 to-teal-50">
                  <div className="text-3xl mb-2">📱</div>
                  <div className="text-2xl font-bold text-green-700">
                    {Object.values(followUpData).flat().filter(f => f.delivery_status === 'delivered').length}
                  </div>
                  <div className="text-gray-600">Delivered</div>
                  <div className="text-xs text-green-600 mt-1">
                    WhatsApp & SMS
                  </div>
                </div>

                <div className="sacred-card p-6 text-center bg-gradient-to-br from-purple-50 to-pink-50">
                  <div className="text-3xl mb-2">🎯</div>
                  <div className="text-2xl font-bold text-purple-700">
                    {Object.values(followUpData).flat().filter(f => f.status === 'read').length}
                  </div>
                  <div className="text-gray-600">Read</div>
                  <div className="text-xs text-purple-600 mt-1">
                    Engagement rate
                  </div>
                </div>
              </div>

              {/* Follow-up Messages */}
              <div className="sacred-card p-8">
                <h3 className="text-xl font-bold text-gray-800 mb-6">📋 Your Follow-up Messages</h3>
                
                {Object.keys(followUpData).length > 0 ? (
                  <div className="space-y-6">
                    {sessionHistory.slice(0, 5).map((session, index) => {
                      const sessionFollowUps = followUpData[session.id] || [];
                      return (
                        <div key={index} className="border border-gray-200 rounded-lg p-6">
                          <div className="flex items-center justify-between mb-4">
                            <div>
                              <h4 className="font-semibold text-gray-800">
                                Session: {session.service_type || 'Spiritual Guidance'}
                              </h4>
                              <p className="text-sm text-gray-600">
                                {formatDate(session.created_at)}
                              </p>
                            </div>
                            <span className="text-sm text-gray-500">
                              {sessionFollowUps.length} follow-ups
                            </span>
                          </div>

                          {sessionFollowUps.length > 0 ? (
                            <div className="space-y-3">
                              {sessionFollowUps.map((followUp, fIndex) => {
                                const getChannelIcon = (channel) => {
                                  switch (channel) {
                                    case 'whatsapp': return '📱';
                                    case 'sms': return '💬';
                                    case 'email': return '📧';
                                    default: return '📝';
                                  }
                                };

                                const getStatusIcon = (status) => {
                                  switch (status) {
                                    case 'delivered': return '✅';
                                    case 'pending': return '⏳';
                                    case 'failed': return '❌';
                                    case 'read': return '👁️';
                                    default: return '📋';
                                  }
                                };

                                const getStatusColor = (status) => {
                                  switch (status) {
                                    case 'delivered': return 'text-green-600';
                                    case 'pending': return 'text-yellow-600';
                                    case 'failed': return 'text-red-600';
                                    case 'read': return 'text-blue-600';
                                    default: return 'text-gray-600';
                                  }
                                };

                                return (
                                  <div key={fIndex} className="p-4 bg-gray-50 rounded-lg">
                                    <div className="flex items-start justify-between mb-2">
                                      <div className="flex items-center space-x-2">
                                        <span className="text-lg">
                                          {getChannelIcon(followUp.channel)}
                                        </span>
                                        <span className="font-medium text-gray-800">
                                          {followUp.channel?.charAt(0).toUpperCase() + followUp.channel?.slice(1) || 'Message'}
                                        </span>
                                      </div>
                                      <span className={`text-sm ${getStatusColor(followUp.status || followUp.delivery_status)}`}>
                                        {getStatusIcon(followUp.status || followUp.delivery_status)}{' '}
                                        {(followUp.status || followUp.delivery_status || 'sent').charAt(0).toUpperCase() + 
                                         (followUp.status || followUp.delivery_status || 'sent').slice(1)}
                                      </span>
                                    </div>
                                    <p className="text-gray-700 text-sm mb-2">
                                      {followUp.message || followUp.content || 'Personalized spiritual guidance message'}
                                    </p>
                                    <div className="text-xs text-gray-500">
                                      Sent: {formatDate(followUp.created_at || followUp.sent_at || session.created_at)}
                                    </div>
                                  </div>
                                );
                              })}
                            </div>
                          ) : (
                            <div className="text-center py-4 text-gray-500">
                              <div className="text-2xl mb-2">💌</div>
                              <p className="text-sm">
                                Follow-up messages will be sent after this session
                              </p>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <div className="text-6xl mb-6">📬</div>
                    <h3 className="text-2xl font-bold text-gray-800 mb-4">
                      No Follow-up Messages Yet
                    </h3>
                    <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
                      Once you complete spiritual guidance sessions, you'll receive personalized follow-up 
                      messages with continued guidance and spiritual insights.
                    </p>
                    <Link 
                      to="/spiritual-guidance" 
                      className="inline-block bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-8 py-3 rounded-lg hover:from-purple-700 hover:to-indigo-700 transition-all duration-300"
                    >
                      Start Your First Session
                    </Link>
                  </div>
                )}
              </div>

              {/* Message Preferences */}
              <div className="sacred-card p-6">
                <h3 className="text-lg font-bold text-gray-800 mb-4">⚙️ Message Preferences</h3>
                <div className="grid md:grid-cols-3 gap-4">
                  <div className="p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center space-x-3 mb-2">
                      <span className="text-xl">📱</span>
                      <span className="font-medium">WhatsApp</span>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">
                      Instant spiritual guidance messages
                    </p>
                    <label className="flex items-center">
                      <input type="checkbox" defaultChecked className="mr-2" />
                      <span className="text-sm">Enable WhatsApp</span>
                    </label>
                  </div>
                  
                  <div className="p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center space-x-3 mb-2">
                      <span className="text-xl">💬</span>
                      <span className="font-medium">SMS</span>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">
                      Text message reminders
                    </p>
                    <label className="flex items-center">
                      <input type="checkbox" defaultChecked className="mr-2" />
                      <span className="text-sm">Enable SMS</span>
                    </label>
                  </div>
                  
                  <div className="p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center space-x-3 mb-2">
                      <span className="text-xl">📧</span>
                      <span className="font-medium">Email</span>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">
                      Detailed spiritual reports
                    </p>
                    <label className="flex items-center">
                      <input type="checkbox" defaultChecked className="mr-2" />
                      <span className="text-sm">Enable Email</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'birthchart' && (
            <div className="space-y-8">
              <div className="sacred-card p-8">
                <h2 className="text-2xl font-bold text-gray-800 mb-6">
                  🌟 Your Birth Chart & Spiritual Profile
                </h2>
                
                {dashboardData?.birthChart ? (
                  <div className="space-y-6">
                    {/* Birth Chart Status */}
                    <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className="text-2xl">✅</div>
                        <div>
                          <h3 className="font-semibold text-green-800">
                            Complete Spiritual Profile Available
                          </h3>
                          <p className="text-green-600 text-sm">
                            Your birth chart with Swamiji's personalized insights is ready
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Birth Chart Key Insights */}
                    <div className="grid md:grid-cols-2 gap-6">
                      <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
                        <h3 className="font-semibold text-purple-800 mb-2">
                          🌙 Moon Sign (Rashi)
                        </h3>
                        <p className="text-purple-600">
                          {dashboardData?.birthChart?.birth_chart?.moon_sign || 'Available in your chart'}
                        </p>
                      </div>
                      <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                        <h3 className="font-semibold text-yellow-800 mb-2">
                          ⭐ Nakshatra
                        </h3>
                        <p className="text-yellow-600">
                          {dashboardData?.birthChart?.birth_chart?.nakshatra || 'Available in your chart'}
                        </p>
                      </div>
                      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                        <h3 className="font-semibold text-blue-800 mb-2">
                          ☀️ Sun Sign
                        </h3>
                        <p className="text-blue-600">
                          {dashboardData?.birthChart?.birth_chart?.sun_sign || 'Available in your chart'}
                        </p>
                      </div>
                      <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                        <h3 className="font-semibold text-green-800 mb-2">
                          🔮 Ascendant (Lagna)
                        </h3>
                        <p className="text-green-600">
                          {dashboardData?.birthChart?.birth_chart?.ascendant || 'Available in your chart'}
                        </p>
                      </div>
                    </div>

                    {/* Swamiji's Reading Preview */}
                    {dashboardData?.birthChart?.swamiji_reading && (
                      <div className="p-6 bg-gradient-to-r from-orange-50 to-yellow-50 rounded-lg border border-orange-200">
                        <h3 className="text-xl font-semibold text-orange-800 mb-4">
                          🕉️ Swamiji's Spiritual Guidance
                        </h3>
                        <div className="text-orange-700 mb-4">
                          <p className="italic">
                            "{dashboardData?.birthChart?.swamiji_reading?.summary || 
                              (dashboardData?.birthChart?.swamiji_reading?.full_reading ? 
                                dashboardData.birthChart.swamiji_reading.full_reading.substring(0, 200) + '...' : 
                                'Swamiji\'s personalized reading is being prepared...')}"
                          </p>
                        </div>
                        <div className="grid md:grid-cols-3 gap-4">
                          {dashboardData?.birthChart?.swamiji_reading?.personality_insights && (
                            <div>
                              <h4 className="font-medium text-orange-700 mb-2">Personality Insights:</h4>
                              <ul className="text-sm text-orange-600 space-y-1">
                                {dashboardData.birthChart.swamiji_reading.personality_insights.slice(0, 2).map((insight, index) => (
                                  <li key={index}>• {insight}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {dashboardData?.birthChart?.swamiji_reading?.spiritual_guidance && (
                            <div>
                              <h4 className="font-medium text-orange-700 mb-2">Spiritual Guidance:</h4>
                              <ul className="text-sm text-orange-600 space-y-1">
                                {dashboardData.birthChart.swamiji_reading.spiritual_guidance.slice(0, 2).map((guidance, index) => (
                                  <li key={index}>• {guidance}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {dashboardData?.birthChart?.swamiji_reading?.practical_advice && (
                            <div>
                              <h4 className="font-medium text-orange-700 mb-2">Practical Advice:</h4>
                              <ul className="text-sm text-orange-600 space-y-1">
                                {dashboardData.birthChart.swamiji_reading.practical_advice.slice(0, 2).map((advice, index) => (
                                  <li key={index}>• {advice}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Current Period Analysis */}
                    <div className="p-6 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg border border-indigo-200">
                      <h3 className="text-xl font-semibold text-indigo-800 mb-4">
                        📅 Current Spiritual Period
                      </h3>
                      <p className="text-indigo-600 mb-4">
                        Based on your birth chart, this is a significant time for spiritual growth and introspection.
                      </p>
                      <div className="grid md:grid-cols-2 gap-4">
                        <div>
                          <h4 className="font-medium text-indigo-700 mb-2">Focus Areas:</h4>
                          <ul className="text-sm text-indigo-600 space-y-1">
                            <li>• Meditation and inner reflection</li>
                            <li>• Karmic healing and understanding</li>
                            <li>• Spiritual community connection</li>
                          </ul>
                        </div>
                        <div>
                          <h4 className="font-medium text-indigo-700 mb-2">Recommended Practices:</h4>
                          <ul className="text-sm text-indigo-600 space-y-1">
                            <li>• Daily spiritual guidance sessions</li>
                            <li>• Mantra chanting and prayer</li>
                            <li>• Service to others (seva)</li>
                          </ul>
                        </div>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex flex-wrap gap-4">
                      <Link 
                        to="/birth-chart" 
                        className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition-colors"
                      >
                        View Complete Birth Chart
                      </Link>
                      <Link 
                        to="/spiritual-guidance" 
                        className="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition-colors"
                      >
                        Get Personalized Guidance
                      </Link>
                      <button 
                        onClick={handleRefreshBirthChart}
                        className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors"
                      >
                        🔄 Refresh Chart
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="text-6xl mb-4">🌟</div>
                    <h3 className="text-xl font-semibold text-gray-800 mb-2">
                      {userProfile?.birth_date ? 'Loading Your Complete Birth Chart' : 'Complete Your Profile'}
                    </h3>
                    <p className="text-gray-600 mb-6">
                      {userProfile?.birth_date 
                        ? 'Swamiji is preparing your personalized spiritual insights and birth chart analysis...'
                        : 'Please complete your birth details in your profile to generate your birth chart.'
                      }
                    </p>
                    
                    {userProfile?.birth_date ? (
                      <div className="space-y-4">
                        <div className="flex items-center justify-center space-x-2">
                          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-purple-600"></div>
                          <span className="text-purple-600">Generating your complete birth chart...</span>
                        </div>
                        <p className="text-sm text-gray-500">
                          This includes your birth chart, Swamiji's AI reading, and detailed astrological reports
                        </p>
                        <button 
                          onClick={handleGenerateBirthChart}
                          disabled={birthChartGenerating}
                          className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-8 py-3 rounded-lg hover:from-purple-700 hover:to-indigo-700 transition-all duration-300 disabled:opacity-50"
                        >
                          {birthChartGenerating ? 'Generating...' : 'Generate Now'}
                        </button>
                      </div>
                    ) : (
                      <Link 
                        to="/profile?tab=settings" 
                        className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-8 py-3 rounded-lg hover:from-purple-700 hover:to-indigo-700 transition-all duration-300"
                      >
                        Complete Profile
                      </Link>
                    )}
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
              <h2 className="text-2xl font-bold text-gray-800 mb-6">Session History & Follow-ups</h2>
              {sessionHistory.length > 0 ? (
                <div className="space-y-6">
                  {sessionHistory.map((session, index) => {
                    const sessionId = session.session_id || session.id;
                    const sessionFollowUps = followUpData[sessionId] || [];
                    
                    return (
                      <div key={index} className="border border-gray-200 rounded-lg p-6 bg-gradient-to-r from-white to-gray-50">
                        <div className="flex items-start justify-between mb-4">
                          <div>
                            <h3 className="font-semibold text-gray-800 text-lg flex items-center">
                              <span className="text-2xl mr-2">🕉️</span>
                              {session.service_type || 'Spiritual Guidance Session'}
                            </h3>
                            <p className="text-gray-600">{formatDate(session.created_at)}</p>
                            {sessionId && (
                              <p className="text-xs text-gray-500">Session ID: {sessionId}</p>
                            )}
                          </div>
                          <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">
                            Completed
                          </span>
                        </div>
                        
                        {session.question && (
                          <div className="mb-4 p-3 bg-blue-50 rounded-lg border-l-4 border-blue-400">
                            <h4 className="font-medium text-gray-700 mb-2">Your Question:</h4>
                            <p className="text-gray-600 italic">"{session.question}"</p>
                          </div>
                        )}

                        {/* Session Content */}
                        {(session.guidance || session.audio_url || session.video_url) && (
                          <div className="mb-4 p-3 bg-yellow-50 rounded-lg border-l-4 border-yellow-400">
                            <h4 className="font-medium text-gray-700 mb-2">🎯 Guidance Received:</h4>
                            {session.guidance && (
                              <p className="text-gray-600 text-sm mb-2 line-clamp-3">{session.guidance}</p>
                            )}
                            <div className="flex gap-2">
                              {session.audio_url && (
                                <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded text-xs">🔊 Audio</span>
                              )}
                              {session.video_url && (
                                <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">🎥 Video</span>
                              )}
                            </div>
                          </div>
                        )}
                        
                        {/* Follow-up Status */}
                        <div className="mb-4">
                          <h4 className="font-medium text-gray-700 mb-3 flex items-center">
                            <span className="mr-2">📧</span>
                            Follow-up Communications
                          </h4>
                          {sessionFollowUps.length > 0 ? (
                            <div className="grid md:grid-cols-3 gap-3">
                              {sessionFollowUps.map((followUp, fIndex) => {
                                const getChannelIcon = (channel) => {
                                  const icons = {
                                    email: <Mail size={16} className="text-green-600" />,
                                    sms: <MessageSquare size={16} className="text-blue-600" />,
                                    whatsapp: <Phone size={16} className="text-green-600" />
                                  };
                                  return icons[channel] || <Mail size={16} className="text-gray-600" />;
                                };

                                const getStatusIcon = (status) => {
                                  const icons = {
                                    sent: <CheckCircle size={14} className="text-green-600" />,
                                    delivered: <CheckCircle size={14} className="text-green-600" />,
                                    read: <CheckCircle size={14} className="text-green-600" />,
                                    pending: <AlertCircle size={14} className="text-yellow-600" />,
                                    failed: <AlertCircle size={14} className="text-red-600" />
                                  };
                                  return icons[status] || <AlertCircle size={14} className="text-gray-600" />;
                                };

                                const getStatusColor = (status) => {
                                  const colors = {
                                    sent: 'bg-green-100 text-green-800 border-green-200',
                                    delivered: 'bg-green-100 text-green-800 border-green-200',
                                    read: 'bg-green-100 text-green-800 border-green-200',
                                    pending: 'bg-yellow-100 text-yellow-800 border-yellow-200',
                                    failed: 'bg-red-100 text-red-800 border-red-200'
                                  };
                                  return colors[status] || 'bg-gray-100 text-gray-800 border-gray-200';
                                };

                                return (
                                  <div key={fIndex} className={`p-3 rounded-lg border ${getStatusColor(followUp.status)}`}>
                                    <div className="flex items-center justify-between mb-2">
                                      <div className="flex items-center space-x-2">
                                        {getChannelIcon(followUp.channel)}
                                        <span className="text-sm font-medium capitalize">{followUp.channel}</span>
                                      </div>
                                      {getStatusIcon(followUp.status)}
                                    </div>
                                    <div className="text-xs">
                                      <div className="font-medium">{followUp.template_name || followUp.subject}</div>
                                      <div className="text-gray-600">
                                        {followUp.status === 'pending' 
                                          ? `Scheduled: ${new Date(followUp.scheduled_at).toLocaleDateString()}`
                                          : `Sent: ${new Date(followUp.sent_at || followUp.created_at).toLocaleDateString()}`
                                        }
                                      </div>
                                      {followUp.credits_charged > 0 && (
                                        <div className="text-yellow-600 font-medium">{followUp.credits_charged} credits</div>
                                      )}
                                    </div>
                                  </div>
                                );
                              })}
                            </div>
                          ) : (
                            <div className="text-center py-4 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                              <p className="text-gray-500 text-sm">No follow-up communications for this session</p>
                              <p className="text-xs text-gray-400 mt-1">Follow-ups can be requested during or after your session</p>
                            </div>
                          )}
                        </div>
                        
                        <div className="flex items-center justify-between text-sm text-gray-500 border-t pt-3">
                          <span>Duration: {session.duration || '30 minutes'}</span>
                          <div className="flex space-x-3">
                            {sessionFollowUps.length > 0 && (
                              <span className="text-green-600 font-medium">
                                {sessionFollowUps.filter(f => ['sent', 'delivered', 'read'].includes(f.status)).length} follow-ups delivered
                              </span>
                            )}
                            <button className="text-yellow-600 hover:text-yellow-800 transition-colors font-medium">
                              View Full Details
                            </button>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="text-6xl mb-6">📚</div>
                  <h3 className="text-xl font-bold text-gray-800 mb-4">No Sessions Yet</h3>
                  <p className="text-gray-600 mb-6">
                    Your spiritual journey awaits. Begin with your first guidance session to start building your session history.
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

