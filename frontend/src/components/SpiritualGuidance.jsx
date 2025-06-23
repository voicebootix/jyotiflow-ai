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

  useEffect(() => {
    // Track page visit
    spiritualAPI.trackSpiritualEngagement('spiritual_guidance_visit', {
      service: selectedService
    });
  }, [selectedService]);

// Authentication check
  useEffect(() => {
    if (!spiritualAPI.isAuthenticated()) {
      // Redirect to login with current service
      navigate(`/login?service=${selectedService}&redirect=spiritual-guidance`);
      return;
    }
  }, [navigate, selectedService]);
  
  const services = {
    clarity: {
      name: 'Clarity Plus',
      description: 'Essential spiritual guidance for life\'s questions',
      icon: '🔮',
      color: 'from-blue-500 to-purple-600'
    },
    love: {
      name: 'AstroLove',
      description: 'Divine guidance for relationships and love',
      icon: '💕',
      color: 'from-pink-500 to-red-500'
    },
    premium: {
      name: 'Premium',
      description: 'Advanced spiritual guidance with avatar videos',
      icon: '🌟',
      color: 'from-yellow-500 to-orange-500'
    },
    elite: {
      name: 'Elite',
      description: 'Complete spiritual transformation journey',
      icon: '👑',
      color: 'from-purple-500 to-indigo-600'
    }
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

      // Start session with backend
      const sessionData = {
        service_type: selectedService,
        birth_details: {
          date: formData.birthDate,
          time: formData.birthTime,
          location: formData.birthLocation
        },
        question: formData.question
      };

      const sessionResult = await spiritualAPI.startSession(sessionData);
      
      if (sessionResult && sessionResult.success) {
        setGuidance(sessionResult.data);

        // For premium/elite users, generate avatar video
        if ((selectedService === 'premium' || selectedService === 'elite') && spiritualAPI.isAuthenticated()) {
          try {
            const avatarResult = await spiritualAPI.generateAvatarVideo(
              sessionResult.data.guidance_text,
              sessionData.birth_details
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
          guidance_text: "Divine guidance is temporarily unavailable. Please try again in a few moments.",
          session_id: null
        });
      }
    } catch (error) {
      console.error('Guidance request encountered divine turbulence:', error);
      setGuidance({
        guidance_text: "The divine servers are currently in meditation. Please try again shortly.",
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

  const currentService = services[selectedService];

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

      {/* Service Selection */}
      <div className="py-8 bg-black bg-opacity-50">
        <div className="max-w-4xl mx-auto px-4">
          <h2 className="text-2xl font-bold text-white mb-6 text-center">Choose Your Guidance Path</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(services).map(([key, service]) => (
              <button
                key={key}
                onClick={() => setSelectedService(key)}
                className={`p-4 rounded-lg border-2 transition-all duration-300 ${
                  selectedService === key
                    ? 'border-yellow-400 bg-yellow-400 bg-opacity-20'
                    : 'border-gray-600 bg-gray-800 hover:border-gray-400'
                }`}
              >
                <div className="text-2xl mb-2">{service.icon}</div>
                <div className="text-white font-semibold text-sm">{service.name}</div>
              </button>
            ))}
          </div>
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
                {guidance.guidance_text}
              </div>

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

