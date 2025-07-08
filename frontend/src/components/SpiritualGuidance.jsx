import { useState, useEffect, useCallback } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Send, Play, Mail, MessageSquare, Phone, RefreshCw } from 'lucide-react';

import spiritualAPI from '../lib/api';

const SpiritualGuidance = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [selectedService, setSelectedService] = useState('');
  const [formData, setFormData] = useState({
    birthDate: '',
    birthTime: '',
    birthLocation: '',
    question: ''
  });
  const [guidance, setGuidance] = useState(null);
  const [avatarVideo, setAvatarVideo] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [services, setServices] = useState([]);
  const [servicesLoading, setServicesLoading] = useState(true);
  const [credits, setCredits] = useState(0);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [creditPackages, setCreditPackages] = useState([]);
  const [packagesLoading, setPackagesLoading] = useState(true);
  const [selectedCreditPackage, setSelectedCreditPackage] = useState(null);
  const [donationOptions, setDonationOptions] = useState([]);
  const [donationsLoading, setDonationsLoading] = useState(true);
  const [selectedDonations, setSelectedDonations] = useState([]);
  const [donationTotal, setDonationTotal] = useState(0);
  
  // Follow-up options state
  const [showFollowUpOptions, setShowFollowUpOptions] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [followUpLoading, setFollowUpLoading] = useState(false);
  const [followUpStatus, setFollowUpStatus] = useState({});

  // Real-time refresh state
  const [lastRefresh, setLastRefresh] = useState(new Date());
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    const serviceFromUrl = searchParams.get('service');
    if (serviceFromUrl) {
      setSelectedService(serviceFromUrl);
    }
    
    loadData();
    spiritualAPI.trackSpiritualEngagement('spiritual_guidance_visit');

    // Set up real-time refresh every 30 seconds
    const refreshInterval = setInterval(() => {
      refreshData();
    }, 30000);

    return () => clearInterval(refreshInterval);
  }, [searchParams]);

  const loadData = async () => {
    try {
      // Load services
      const servicesData = await spiritualAPI.request('/api/services/types');
      if (servicesData && servicesData.success) {
        setServices(servicesData.data || []);
      } else {
        setServices([]);
      }
      setServicesLoading(false);

      // Load credit packages
      const packagesData = await spiritualAPI.request('/api/services/credit-packages');
      if (packagesData && packagesData.success) {
        setCreditPackages(packagesData.data || []);
      } else {
        setCreditPackages([]);
      }
      setPackagesLoading(false);

      // Load donation options
      const donationsData = await spiritualAPI.request('/api/admin/products/donations');
      setDonationOptions(Array.isArray(donationsData) ? donationsData : []);
      setDonationsLoading(false);

      // Load user credits if authenticated
      if (spiritualAPI.isAuthenticated()) {
        const creditsData = await spiritualAPI.getCreditBalance();
        if (creditsData && creditsData.success) {
          setCredits(creditsData.data.credits || 0);
        }
      }
    } catch (error) {
      console.log('Data loading blessed with patience:', error);
      setServicesLoading(false);
      setPackagesLoading(false);
      setDonationsLoading(false);
    }
  };

  // Real-time refresh function
  const refreshData = useCallback(async () => {
    try {
      setRefreshing(true);
      
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

      // Load donation options
      const donationsData = await spiritualAPI.request('/api/admin/products/donations');
      setDonationOptions(Array.isArray(donationsData) ? donationsData : []);

      // Load user credits if authenticated
      if (spiritualAPI.isAuthenticated()) {
        const creditsData = await spiritualAPI.getCreditBalance();
        if (creditsData && creditsData.success) {
          setCredits(creditsData.data.credits || 0);
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

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    setIsLoading(true);
    setGuidance(null);
    setAvatarVideo(null);

    try {
      // Track guidance request
      await spiritualAPI.trackSpiritualEngagement('guidance_requested', {
        service: selectedService,
        has_birth_details: !!(formData.birthDate && formData.birthTime && formData.birthLocation),
        question_length: formData.question.length
      });

      // Start session with credit deduction
      const sessionResult = await spiritualAPI.startSession({
        service_type: selectedService,
        question: formData.question,
        birth_details: {
          date: formData.birthDate,
          time: formData.birthTime,
          location: formData.birthLocation
        }
      });

      if (sessionResult && sessionResult.success) {
        // Update local credits after successful session
        setCredits(sessionResult.data.remaining_credits);
        
        setGuidance({
          guidance: sessionResult.data.guidance,
          astrology: sessionResult.data.astrology,
          session_id: sessionResult.data.session_id
        });

        // Set current session ID for follow-up options
        setCurrentSessionId(sessionResult.data.session_id);

        // For premium/elite users, generate avatar video
        if ((selectedService === 'premium' || selectedService === 'elite') && spiritualAPI.isAuthenticated()) {
          try {
            const avatarResult = await spiritualAPI.generateAvatarVideo(
              sessionResult.data.guidance,
              sessionResult.data.birth_details
            );
            
            if (avatarResult && avatarResult.success) {
              // Poll for video completion
              pollAvatarStatus(avatarResult.data.session_id);
            }
          } catch (error) {
            console.log('Avatar generation blessed with patience:', error);
          }
        }
      } else if (sessionResult && sessionResult.status === 402) {
        // Handle insufficient credits error
        alert(`⚠️ ${sessionResult.message || 'போதிய கிரெடிட்கள் இல்லை!'}\n\nதயவுசெய்து கிரெடிட்கள் வாங்கி மீண்டும் முயற்சிக்கவும்.`);
      } else {
        setGuidance({
          guidance: "Divine guidance is temporarily unavailable. Please try again in a few moments.",
          session_id: null
        });
      }
    } catch (error) {
      console.error('Guidance request encountered divine turbulence:', error);
      setGuidance({
        guidance: "The divine servers are currently in meditation. Please try again shortly.",
        session_id: null
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Follow-up functions
  const handleFollowUp = async (channel) => {
    if (!currentSessionId) return;

    setFollowUpLoading(true);
    try {
      let result;
      
      switch (channel) {
        case 'email':
          result = await spiritualAPI.request(`/api/followup/email/${currentSessionId}`, {
            method: 'POST'
          });
          break;
        case 'sms':
          result = await spiritualAPI.request(`/api/followup/sms/${currentSessionId}`, {
            method: 'POST'
          });
          break;
        case 'whatsapp':
          result = await spiritualAPI.request(`/api/followup/whatsapp/${currentSessionId}`, {
            method: 'POST'
          });
          break;
        default:
          return;
      }

      if (result && result.success) {
        // Update credits if charged
        if (result.credits_charged > 0) {
          setCredits(prevCredits => prevCredits - result.credits_charged);
        }
        
        // Update follow-up status
        setFollowUpStatus(prev => ({
          ...prev,
          [channel]: true
        }));

        alert(`${channel.toUpperCase()} follow-up sent successfully!`);
      } else {
        alert(result?.message || 'Failed to send follow-up');
      }
    } catch (error) {
      console.error('Follow-up error:', error);
      alert('Failed to send follow-up. Please try again.');
    } finally {
      setFollowUpLoading(false);
    }
  };

  const showFollowUpOptionsAfterSession = () => {
    setShowFollowUpOptions(true);
  };

  const pollAvatarStatus = async (sessionId) => {
    const maxAttempts = 30; // 5 minutes max
    let attempts = 0;

    const checkStatus = async () => {
      try {
        const status = await spiritualAPI.getAvatarGenerationStatus(sessionId);
        
        if (status && status.success && status.data.status === 'completed') {
          setAvatarVideo(status.data);
          return;
        }
        
        attempts++;
        if (attempts < maxAttempts) {
          setTimeout(checkStatus, 10000); // Check every 10 seconds
        }
      } catch (error) {
        console.log('Avatar status check blessed with patience:', error);
      }
    };

    checkStatus();
  };

  const handleDonationToggle = (donationId) => {
    setSelectedDonations(prev => {
      const newDonations = prev.includes(donationId) 
        ? prev.filter(id => id !== donationId)
        : [...prev, donationId];
      
      const total = newDonations.reduce((sum, id) => {
        const donation = donationOptions.find(d => d.id === id);
        return sum + (donation ? donation.price_usd : 0);
      }, 0);
      
      setDonationTotal(total);
      return newDonations;
    });
  };

  const handleDonationPayment = async () => {
    if (!spiritualAPI.isAuthenticated()) {
      navigate('/login');
      return;
    }

    if (selectedDonations.length === 0) {
      alert('தயவுசெய்து தானம் தேர்ந்தெடுக்கவும்');
      return;
    }

    try {
      // Process each selected donation
      for (const donationId of selectedDonations) {
        const donation = donationOptions.find(d => d.id === donationId);
        if (!donation) continue;

        // Process donation payment
        const paymentResult = await spiritualAPI.processDonation({
          donation_id: donationId,
          amount_usd: donation.price_usd,
          message: `தானம்: ${donation.tamil_name || donation.name}`,
          session_id: currentSessionId
        });

        if (paymentResult && paymentResult.success) {
          // Here you would integrate with Stripe for actual payment
          // For now, we'll simulate a successful payment
          await spiritualAPI.confirmDonation(paymentResult.payment_intent_id);
          
          alert(`தானம் வெற்றிகரமாக செய்யப்பட்டது: ${donation.tamil_name || donation.name}`);
        }
      }

      // Clear selected donations after successful payment
      setSelectedDonations([]);
      setDonationTotal(0);
      
    } catch (error) {
      console.error('Donation payment error:', error);
      alert('தானம் செய்யும் போது பிழை ஏற்பட்டது. மீண்டும் முயற்சிக்கவும்.');
    }
  };

  const currentService = services.find(s => s.name === selectedService) || { name: 'Clarity Plus', icon: '🔮' };
  const CATEGORY_LABELS = {
    '': 'அனைத்தும்',
    'guidance': 'வழிகாட்டுதல்',
    'consultation': 'ஆலோசனை',
    'premium': 'பிரீமியம்',
  };
  const CATEGORY_DESCRIPTIONS = {
    'guidance': 'Quick spiritual insights',
    'consultation': 'Live interaction with AI Swami',
    'premium': 'Comprehensive readings',
  };
  const categories = Array.from(new Set((services || []).map(s => s.service_category).filter(cat => ['guidance','consultation','premium'].includes(cat))));

  return (
    <div className="pt-16 min-h-screen">
      {/* Header */}
      <div className={`bg-gradient-to-r ${currentService.color} py-16`}>
        <div className="max-w-4xl mx-auto px-4 text-center">
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
          
          <div className="text-6xl mb-4">{currentService.icon}</div>
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            {currentService.name}
          </h1>
          <p className="text-xl text-white opacity-90 max-w-2xl mx-auto">
            {currentService.description}
          </p>
          
          {/* Last Updated Indicator */}
          <div className="mt-4 text-white opacity-75 text-sm">
            Last updated: {lastRefresh.toLocaleTimeString()}
          </div>
        </div>
      </div>

      {/* Credit Packages */}
      <div className="py-6 bg-black bg-opacity-20">
        <div className="max-w-4xl mx-auto px-4">
          <h3 className="text-xl font-bold text-white mb-4 text-center">கிரெடிட் தொகுப்புகள்</h3>
          {packagesLoading ? (
            <div className="text-white text-center">கிரெடிட் தொகுப்புகள் ஏற்றப்படுகிறது...</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {(Array.isArray(creditPackages) ? creditPackages : []).filter(pkg => pkg.enabled).map((creditPkg, index) => {
                // Determine most popular package (usually the middle one or highest value)
                const isMostPopular = index === 1 || creditPkg.is_popular;
                
                return (
                  <button
                    key={creditPkg.id}
                    onClick={() => setSelectedCreditPackage(creditPkg)}
                    className={`p-4 rounded-lg border-2 transition-all duration-300 relative ${
                      selectedCreditPackage?.id === creditPkg.id
                        ? 'border-blue-400 bg-blue-400 bg-opacity-20'
                        : isMostPopular
                          ? 'border-yellow-400 bg-yellow-400 bg-opacity-10'
                          : 'border-gray-600 bg-gray-800 hover:border-gray-400'
                    }`}
                  >
                    {/* Most Popular Badge */}
                    {isMostPopular && (
                      <div className="absolute -top-2 left-1/2 transform -translate-x-1/2 bg-yellow-400 text-black text-xs font-bold px-3 py-1 rounded-full">
                        சிறந்த மதிப்பு
                      </div>
                    )}
                    
                    <div className="text-2xl mb-2">🪙</div>
                    <div className="text-white font-semibold text-lg">{creditPkg.name}</div>
                    <div className="text-blue-300 font-bold text-xl">₹{creditPkg.price_usd}</div>
                    <div className="text-white text-sm">{creditPkg.credits_amount} கிரெடிட்ஸ்</div>
                    {creditPkg.bonus_credits > 0 && (
                      <div className="bg-green-500 text-white text-sm font-bold px-2 py-1 rounded-full mt-1">
                        +{creditPkg.bonus_credits} இலவசம்!
                      </div>
                    )}
                    <div className="text-gray-400 text-xs mt-2">{creditPkg.description}</div>
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Donation Options */}
      <div className="py-6 bg-black bg-opacity-30">
        <div className="max-w-4xl mx-auto px-4">
          <h3 className="text-xl font-bold text-white mb-4 text-center">தானம் செய்யுங்கள் (விருப்பமானது)</h3>
          {donationsLoading ? (
            <div className="text-white text-center">தானங்கள் ஏற்றப்படுகிறது...</div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {donationOptions.filter(donation => donation.enabled).map(donation => (
                <button
                  key={donation.id}
                  onClick={() => handleDonationToggle(donation.id)}
                  className={`p-3 rounded-lg border-2 transition-all duration-300 ${
                    selectedDonations.includes(donation.id)
                      ? 'border-green-400 bg-green-400 bg-opacity-20'
                      : 'border-gray-600 bg-gray-800 hover:border-gray-400'
                  }`}
                >
                  <div className="text-2xl mb-1">{donation.icon}</div>
                  <div className="text-white font-semibold text-xs">{donation.tamil_name || donation.name}</div>
                  <div className="text-green-300 font-bold text-sm">${donation.price_usd}</div>
                  <div className="text-gray-400 text-xs">{donation.description}</div>
                </button>
              ))}
            </div>
          )}
          {donationTotal > 0 && (
            <div className="text-center mt-4">
              <div className="text-white text-lg mb-3">
                மொத்த தானம்: <span className="text-green-400 font-bold">${donationTotal}</span>
              </div>
              <button
                onClick={handleDonationPayment}
                className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg font-semibold transition-colors"
              >
                💰 தானம் செய்யுங்கள்
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Credit Balance Display */}
      <div className="py-4 bg-black bg-opacity-40">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <div className="text-white text-lg">
            உங்கள் கிரெடிட் இருப்பு: <span className="text-yellow-400 font-bold text-xl">{credits}</span>
          </div>
          {!spiritualAPI.isAuthenticated() && (
            <div className="text-red-400 text-sm mt-2">
              சேவைகளைப் பயன்படுத்த <Link to="/login" className="text-blue-400 underline">உள்நுழையுங்கள்</Link>
            </div>
          )}
        </div>
      </div>

      {/* Category Filter */}
      <div className="mb-6 flex flex-col items-center">
        <div className="flex gap-2 mb-2">
          <button
            type="button"
            className={`px-4 py-2 rounded-full border text-sm font-medium transition-colors duration-200 ${selectedCategory === '' ? 'bg-yellow-400 text-black border-yellow-400' : 'bg-gray-100 text-gray-700 border-gray-300 hover:bg-yellow-100'}`}
            onClick={() => setSelectedCategory('')}
          >
            {CATEGORY_LABELS['']}
          </button>
          {categories.map(cat => (
            <button
              key={cat}
              type="button"
              className={`px-4 py-2 rounded-full border text-sm font-medium transition-colors duration-200 ${selectedCategory === cat ? 'bg-yellow-400 text-black border-yellow-400' : 'bg-gray-100 text-gray-700 border-gray-300 hover:bg-yellow-100'}`}
              onClick={() => setSelectedCategory(cat)}
            >
              {CATEGORY_LABELS[cat] || cat}
            </button>
          ))}
        </div>
        {selectedCategory && CATEGORY_DESCRIPTIONS[selectedCategory] && (
          <div className="text-sm text-gray-600 mt-1">{CATEGORY_DESCRIPTIONS[selectedCategory]}</div>
        )}
      </div>

      {/* Service Selection */}
      <div className="py-8 bg-black bg-opacity-50">
        <div className="max-w-4xl mx-auto px-4">
          <h2 className="text-2xl font-bold text-white mb-6 text-center">Choose Your Guidance Path</h2>
          {servicesLoading ? <div className="text-white">சேவைகள் ஏற்றப்படுகிறது...</div> : (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {(Array.isArray(services) ? services : [])
                .filter(s => s.enabled)
                .filter(s => !selectedCategory || s.service_category === selectedCategory)
                .map(service => (
                  <button
                    key={service.id}
                    onClick={() => setSelectedService(service.name)}
                    className={`p-4 rounded-lg border-2 transition-all duration-300 ${
                      selectedService === service.name
                        ? 'border-yellow-400 bg-yellow-400 bg-opacity-20'
                        : 'border-gray-600 bg-gray-800 hover:border-gray-400'
                    }`}
                  >
                    <div className="text-2xl mb-2">{service.icon || (service.is_video ? '🎥' : service.is_audio ? '🔊' : '🔮')}</div>
                    <div className="text-white font-semibold text-sm">{service.display_name || service.name}</div>
                    <div className="text-yellow-300 font-bold mt-2">₹{service.credits_required} கிரெடிட்ஸ்</div>
                    <div className="bg-blue-500 text-white text-xs px-2 py-1 rounded-full mt-1">{service.duration_minutes} நிமிடங்கள்</div>
                    <div className="text-gray-400 text-xs mt-1">{service.description}</div>
                  </button>
                ))}
            </div>
          )}
        </div>
      </div>

      {/* Guidance Form */}
      <div className="py-16 px-4">
        <div className="max-w-2xl mx-auto">
          <div className="sacred-card p-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">
              Share Your Sacred Details
            </h2>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Birth Details */}
              <div className="grid md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Birth Date
                  </label>
                  <input
                    type="date"
                    name="birthDate"
                    value={formData.birthDate}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-500"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Birth Time
                  </label>
                  <input
                    type="time"
                    name="birthTime"
                    value={formData.birthTime}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-500"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Birth Location
                  </label>
                  <input
                    type="text"
                    name="birthLocation"
                    value={formData.birthLocation}
                    onChange={handleInputChange}
                    placeholder="City, Country"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-500"
                    required
                  />
                </div>
              </div>

              {/* Question */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Your Sacred Question or Concern
                </label>
                <textarea
                  name="question"
                  value={formData.question}
                  onChange={handleInputChange}
                  rows={4}
                  placeholder="Share what guidance you seek from the divine wisdom..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-500"
                  required
                />
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full divine-button flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    <span>Receiving Divine Guidance...</span>
                  </>
                ) : (
                  <>
                    <Send size={20} />
                    <span>Begin Sacred Journey</span>
                  </>
                )}
              </button>
            </form>
          </div>
        </div>
      </div>

      {/* Guidance Results */}
      {guidance && (
        <div className="py-16 px-4 bg-gradient-to-br from-purple-900 to-blue-900">
          <div className="max-w-4xl mx-auto">
            <div className="sacred-card p-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">
                🕉️ Divine Guidance Received
              </h2>
              <div className="prose prose-lg max-w-none text-gray-700 mb-8">
                {guidance.guidance}
              </div>
              {guidance.astrology && (
                <div className="mb-8 p-4 bg-gray-100 rounded-lg">
                  <div><b>நட்சத்திரம்:</b> {guidance.astrology.data?.nakshatra?.name}</div>
                  <div><b>சந்திர ராசி:</b> {guidance.astrology.data?.chandra_rasi?.name}</div>
                </div>
              )}

              {/* Avatar Video */}
              {avatarVideo && (
                <div className="mt-8 text-center">
                  <h3 className="text-xl font-bold text-gray-800 mb-4">
                    🎥 Personal Message from Swami Jyotirananthan
                  </h3>
                  <div className="bg-gray-100 rounded-lg p-8">
                    {avatarVideo.video_url ? (
                      <video
                        controls
                        className="w-full max-w-md mx-auto rounded-lg"
                        poster="/swami-avatar-poster.jpg"
                      >
                        <source src={avatarVideo.video_url} type="video/mp4" />
                        Your browser does not support the video tag.
                      </video>
                    ) : (
                      <div className="text-center">
                        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-white mr-2"></div>
                        <p className="text-gray-600">Your personalized avatar video is being prepared...</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Follow-up Options */}
              {!showFollowUpOptions && (
                <div className="mt-8 text-center">
                  <button
                    onClick={showFollowUpOptionsAfterSession}
                    className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
                  >
                    📧 Get Follow-up Messages
                  </button>
                </div>
              )}

              {/* Follow-up Options Display */}
              {showFollowUpOptions && (
                <div className="mt-8 p-6 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border-2 border-green-200">
                  <h3 className="text-xl font-bold text-gray-800 mb-4 text-center">
                    📧 Follow-up Options
                  </h3>
                  <p className="text-gray-600 text-center mb-6">
                    Choose how you'd like to receive follow-up messages about your spiritual journey
                  </p>
                  
                  <div className="grid md:grid-cols-3 gap-4">
                    {/* Email Option - Free */}
                    <div className={`p-4 rounded-lg border-2 transition-all duration-300 ${
                      followUpStatus.email ? 'border-green-500 bg-green-100' : 'border-gray-300 bg-white hover:border-green-400'
                    }`}>
                      <div className="text-center">
                        <Mail className="mx-auto mb-2 text-green-600" size={32} />
                        <h4 className="font-semibold text-gray-800 mb-2">Email Follow-up</h4>
                        <p className="text-sm text-gray-600 mb-3">Receive insights via email</p>
                        <div className="text-green-600 font-bold mb-3">FREE</div>
                        <button
                          onClick={() => handleFollowUp('email')}
                          disabled={followUpLoading || followUpStatus.email}
                          className={`w-full px-4 py-2 rounded-lg font-semibold transition-colors ${
                            followUpStatus.email
                              ? 'bg-green-100 text-green-700 cursor-not-allowed'
                              : 'bg-green-600 hover:bg-green-700 text-white'
                          }`}
                        >
                          {followUpLoading ? (
                            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                          ) : followUpStatus.email ? (
                            '✅ Sent'
                          ) : (
                            'Send Email'
                          )}
                        </button>
                      </div>
                    </div>

                    {/* SMS Option - 1 Credit */}
                    <div className={`p-4 rounded-lg border-2 transition-all duration-300 ${
                      followUpStatus.sms ? 'border-blue-500 bg-blue-100' : 'border-gray-300 bg-white hover:border-blue-400'
                    }`}>
                      <div className="text-center">
                        <MessageSquare className="mx-auto mb-2 text-blue-600" size={32} />
                        <h4 className="font-semibold text-gray-800 mb-2">SMS Follow-up</h4>
                        <p className="text-sm text-gray-600 mb-3">Get guidance via SMS</p>
                        <div className="text-blue-600 font-bold mb-3">1 Credit</div>
                        <button
                          onClick={() => handleFollowUp('sms')}
                          disabled={followUpLoading || followUpStatus.sms || credits < 1}
                          className={`w-full px-4 py-2 rounded-lg font-semibold transition-colors ${
                            followUpStatus.sms
                              ? 'bg-blue-100 text-blue-700 cursor-not-allowed'
                              : credits < 1
                                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                : 'bg-blue-600 hover:bg-blue-700 text-white'
                          }`}
                        >
                          {followUpLoading ? (
                            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                          ) : followUpStatus.sms ? (
                            '✅ Sent'
                          ) : credits < 1 ? (
                            'Insufficient Credits'
                          ) : (
                            'Send SMS'
                          )}
                        </button>
                      </div>
                    </div>

                    {/* WhatsApp Option - 2 Credits */}
                    <div className={`p-4 rounded-lg border-2 transition-all duration-300 ${
                      followUpStatus.whatsapp ? 'border-green-500 bg-green-100' : 'border-gray-300 bg-white hover:border-green-400'
                    }`}>
                      <div className="text-center">
                        <Phone className="mx-auto mb-2 text-green-600" size={32} />
                        <h4 className="font-semibold text-gray-800 mb-2">WhatsApp Follow-up</h4>
                        <p className="text-sm text-gray-600 mb-3">Receive guidance on WhatsApp</p>
                        <div className="text-green-600 font-bold mb-3">2 Credits</div>
                        <button
                          onClick={() => handleFollowUp('whatsapp')}
                          disabled={followUpLoading || followUpStatus.whatsapp || credits < 2}
                          className={`w-full px-4 py-2 rounded-lg font-semibold transition-colors ${
                            followUpStatus.whatsapp
                              ? 'bg-green-100 text-green-700 cursor-not-allowed'
                              : credits < 2
                                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                : 'bg-green-600 hover:bg-green-700 text-white'
                          }`}
                        >
                          {followUpLoading ? (
                            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                          ) : followUpStatus.whatsapp ? (
                            '✅ Sent'
                          ) : credits < 2 ? (
                            'Insufficient Credits'
                          ) : (
                            'Send WhatsApp'
                          )}
                        </button>
                      </div>
                    </div>
                  </div>

                  <div className="text-center mt-4">
                    <p className="text-sm text-gray-500">
                      Available Credits: <span className="font-bold text-yellow-600">{credits}</span>
                    </p>
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  onClick={() => {
                    setGuidance(null);
                    setAvatarVideo(null);
                    setShowFollowUpOptions(false);
                    setFollowUpStatus({});
                    setFormData({
                      birthDate: '',
                      birthTime: '',
                      birthLocation: '',
                      question: ''
                    });
                  }}
                  className="divine-button"
                >
                  Ask Another Question
                </button>
                
                <Link
                  to="/satsang"
                  className="bg-transparent border-2 border-yellow-500 text-yellow-600 hover:bg-yellow-500 hover:text-white transition-all duration-300 px-6 py-3 rounded-lg font-semibold text-center"
                >
                  Join Sacred Community
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SpiritualGuidance;

