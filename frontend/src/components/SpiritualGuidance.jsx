import { useState, useEffect } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Send, Loader, Play } from 'lucide-react';
import spiritualAPI from '../lib/api';

const SpiritualGuidance = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [selectedService, setSelectedService] = useState(searchParams.get('service') || 'clarity');
  const [isLoading, setIsLoading] = useState(false);
  const [guidance, setGuidance] = useState(null);
  const [avatarVideo, setAvatarVideo] = useState(null);
  const [formData, setFormData] = useState({
    birthDate: '',
    birthTime: '',
    birthLocation: '',
    question: ''
  });
  const [credits, setCredits] = useState(0);
  const [loadingCredits, setLoadingCredits] = useState(true);
  const [services, setServices] = useState([]);
  const [servicesLoading, setServicesLoading] = useState(true);
  const [selectedDonations, setSelectedDonations] = useState([]);
  const [donationTotal, setDonationTotal] = useState(0);
  const [creditPackages, setCreditPackages] = useState([]);
  const [selectedCreditPackage, setSelectedCreditPackage] = useState(null);
  const [packagesLoading, setPackagesLoading] = useState(true);

  const donationOptions = [
    { id: 'flowers', name: 'மலர்கள்', tamilName: 'மலர்கள்', price: 5, icon: '🌸', description: 'புனித மலர்கள் சமர்ப்பிப்பு' },
    { id: 'lamp', name: 'விளக்கு', tamilName: 'விளக்கு', price: 10, icon: '🕯️', description: 'தீபாராதனை' },
    { id: 'prasadam', name: 'பிரசாதம்', tamilName: 'பிரசாதம்', price: 15, icon: '🍯', description: 'புனித பிரசாதம்' },
    { id: 'temple', name: 'கோவில்', tamilName: 'கோவில்', price: 25, icon: '🕉️', description: 'கோவில் பராமரிப்பு' },
    { id: 'superchat', name: 'சூப்பர் சாட்', tamilName: 'சூப்பர் சாட்', price: 50, icon: '💬', description: 'முன்னுரிமை செய்தி' }
  ];

  useEffect(() => {
    // Track page visit
    spiritualAPI.trackSpiritualEngagement('spiritual_guidance_visit', {
      service: selectedService
    });
  }, [selectedService]);

  useEffect(() => {
    if (spiritualAPI.isAuthenticated()) {
      spiritualAPI.getCreditBalance().then(res => {
        if (res.success) setCredits(res.data.credits);
        setLoadingCredits(false);
      });
    } else {
      setLoadingCredits(false);
    }
  }, []);

  useEffect(() => {
    spiritualAPI.request('/api/admin/products/service-types').then(data => {
      setServices(Array.isArray(data) ? data : []);
      setServicesLoading(false);
    });
    
    // Fetch credit packages
    spiritualAPI.request('/api/admin/products/credit-packages').then(data => {
      setCreditPackages(Array.isArray(data) ? data : []);
      setPackagesLoading(false);
    });
  }, []);

  // Authentication check
  useEffect(() => {
   // if (!spiritualAPI.isAuthenticated()) {
      // Redirect to login with current service
     // navigate(`/login?service=${selectedService}&redirect=spiritual-guidance`);
     // return;
   // }
  }, [navigate, selectedService]);
  
  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!spiritualAPI.isAuthenticated()) {
      navigate('/login');
      return;
    }
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

      // Change here: use submitSpiritualQuestion instead of startSession
      const sessionResult = await spiritualAPI.submitSpiritualQuestion({
        question: formData.question,
        birth_details: {
          date: formData.birthDate,
          time: formData.birthTime,
          location: formData.birthLocation
        }
      });

      if (sessionResult && sessionResult.success) {
        setGuidance({
          guidance: sessionResult.guidance,
          astrology: sessionResult.astrology
        });

        // For premium/elite users, generate avatar video
        if ((selectedService === 'premium' || selectedService === 'elite') && spiritualAPI.isAuthenticated()) {
          try {
            const avatarResult = await spiritualAPI.generateAvatarVideo(
              sessionResult.data.guidance_text,
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
        return sum + (donation ? donation.price : 0);
      }, 0);
      
      setDonationTotal(total);
      return newDonations;
    });
  };

  const currentService = services.find(s => s.name === selectedService) || { name: 'Clarity Plus', icon: '🔮' };

  return (
    <div className="pt-16 min-h-screen">
      {/* Header */}
      <div className={`bg-gradient-to-r ${currentService.color} py-16`}>
        <div className="max-w-4xl mx-auto px-4 text-center">
          <Link 
            to="/" 
            className="inline-flex items-center text-white hover:text-gray-200 mb-6 transition-colors"
          >
            <ArrowLeft size={20} className="mr-2" />
            Back to Home
          </Link>
          
          <div className="text-6xl mb-4">{currentService.icon}</div>
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            {currentService.name}
          </h1>
          <p className="text-xl text-white opacity-90 max-w-2xl mx-auto">
            {currentService.description}
          </p>
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
                              {(Array.isArray(creditPackages) ? creditPackages : []).filter(pkg => pkg.enabled).map(creditPkg => (
                  <button
                    key={creditPkg.id}
                    onClick={() => setSelectedCreditPackage(creditPkg)}
                    className={`p-4 rounded-lg border-2 transition-all duration-300 ${
                      selectedCreditPackage?.id === creditPkg.id
                        ? 'border-blue-400 bg-blue-400 bg-opacity-20'
                        : 'border-gray-600 bg-gray-800 hover:border-gray-400'
                    }`}
                  >
                    <div className="text-2xl mb-2">🪙</div>
                    <div className="text-white font-semibold text-lg">{creditPkg.name}</div>
                    <div className="text-blue-300 font-bold text-xl">${creditPkg.price_usd}</div>
                    <div className="text-white text-sm">{creditPkg.credits_amount} கிரெடிட்ஸ்</div>
                    {creditPkg.bonus_credits > 0 && (
                      <div className="text-green-400 text-sm">+{creditPkg.bonus_credits} போனஸ்!</div>
                    )}
                    <div className="text-gray-400 text-xs mt-2">{creditPkg.description}</div>
                  </button>
                ))}
            </div>
          )}
        </div>
      </div>

      {/* Donation Options */}
      <div className="py-6 bg-black bg-opacity-30">
        <div className="max-w-4xl mx-auto px-4">
          <h3 className="text-xl font-bold text-white mb-4 text-center">தானம் செய்யுங்கள் (விருப்பமானது)</h3>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {donationOptions.map(donation => (
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
                <div className="text-white font-semibold text-xs">{donation.tamilName}</div>
                <div className="text-green-300 font-bold text-sm">${donation.price}</div>
                <div className="text-gray-400 text-xs">{donation.description}</div>
              </button>
            ))}
          </div>
          {donationTotal > 0 && (
            <div className="text-center mt-4">
              <div className="text-white text-lg">
                மொத்த தானம்: <span className="text-green-400 font-bold">${donationTotal}</span>
              </div>
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

      {/* Service Selection */}
      <div className="py-8 bg-black bg-opacity-50">
        <div className="max-w-4xl mx-auto px-4">
          <h2 className="text-2xl font-bold text-white mb-6 text-center">Choose Your Guidance Path</h2>
          {servicesLoading ? <div className="text-white">சேவைகள் ஏற்றப்படுகிறது...</div> : (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {(Array.isArray(services) ? services : []).filter(s => s.enabled).map(service => {
                const hasEnoughCredits = spiritualAPI.isAuthenticated() && credits >= service.credits_required;
                const canSelect = spiritualAPI.isAuthenticated() && hasEnoughCredits;
                
                return (
                  <button
                    key={service.id}
                    onClick={() => canSelect ? setSelectedService(service.name) : null}
                    disabled={!canSelect}
                    className={`p-4 rounded-lg border-2 transition-all duration-300 ${
                      selectedService === service.name
                        ? 'border-yellow-400 bg-yellow-400 bg-opacity-20'
                        : canSelect
                          ? 'border-gray-600 bg-gray-800 hover:border-gray-400'
                          : 'border-red-600 bg-red-900 bg-opacity-50 cursor-not-allowed'
                    }`}
                    title={!spiritualAPI.isAuthenticated() ? 'உள்நுழைய வேண்டும்' : !hasEnoughCredits ? 'போதுமான கிரெடிட்ஸ் இல்லை' : ''}
                  >
                    <div className="text-2xl mb-2">{service.is_video ? '🎥' : service.is_audio ? '🔊' : '🔮'}</div>
                    <div className="text-white font-semibold text-sm">{service.name}</div>
                    <div className="text-yellow-300 font-bold mt-2">${service.price_usd}</div>
                    <div className="text-gray-400 text-xs">{service.credits_required} கிரெடிட்ஸ்</div>
                    <div className="text-gray-400 text-xs">{service.duration_minutes} நிமிடம்</div>
                    <div className="text-gray-500 text-xs mt-1">{service.description}</div>
                    
                    {!spiritualAPI.isAuthenticated() && (
                      <div className="text-red-400 text-xs mt-2">உள்நுழைய வேண்டும்</div>
                    )}
                    {spiritualAPI.isAuthenticated() && !hasEnoughCredits && (
                      <div className="text-red-400 text-xs mt-2">போதுமான கிரெடிட்ஸ் இல்லை</div>
                    )}
                  </button>
                );
              })}
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
                    <Loader className="animate-spin" size={20} />
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
                        <Loader className="animate-spin mx-auto mb-4" size={40} />
                        <p className="text-gray-600">Your personalized avatar video is being prepared...</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  onClick={() => {
                    setGuidance(null);
                    setAvatarVideo(null);
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

