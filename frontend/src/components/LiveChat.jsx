import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, Video, Clock, Users, Star, X } from 'lucide-react';
import spiritualAPI from '../lib/api';

const LiveChat = () => {
  const navigate = useNavigate(); 
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userProfile, setUserProfile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [chatSession, setChatSession] = useState(null);
  const [showDonationPopup, setShowDonationPopup] = useState(false);
  const [donationOptions, setDonationOptions] = useState([]);
  const [donationsLoading, setDonationsLoading] = useState(false);
  const [selectedDonation, setSelectedDonation] = useState(null);
  const [donationPaying, setDonationPaying] = useState(false);
  const [showFlowerAnimation, setShowFlowerAnimation] = useState(false);
  const [sessionTotalDonations, setSessionTotalDonations] = useState(0);

  useEffect(() => {
    checkAuthAndSubscription();
    spiritualAPI.trackSpiritualEngagement('live_chat_visit');
  }, []);

  // Fetch donation options when chatSession becomes active
  useEffect(() => {
    if (chatSession) {
      setDonationsLoading(true);
      spiritualAPI.getDonations().then((data) => {
        setDonationOptions(Array.isArray(data) ? data.filter(d => d.enabled) : []);
        setDonationsLoading(false);
      });
    }
  }, [chatSession]);

  // Fetch total donations for session when chatSession is active
  useEffect(() => {
    if (chatSession && chatSession.session_id) {
      spiritualAPI.getSessionTotalDonations(chatSession.session_id).then((res) => {
        if (res && res.success) setSessionTotalDonations(res.total_donations || 0);
      });
    }
  }, [chatSession]);

  const checkAuthAndSubscription = async () => {
    if (spiritualAPI.isAuthenticated()) {
      setIsAuthenticated(true);
      try {
        const profile = await spiritualAPI.getUserProfile();
        if (profile && profile.success) {
          setUserProfile(profile.data);
        }
      } catch (error) {
        console.log('Profile loading blessed with patience:', error);
      }
    }
  };

  const initiateLiveChat = async () => {
    if (!isAuthenticated) {
      navigate('/register?service=live-chat');
      return;
    }

    setIsLoading(true);
    try {
      const sessionDetails = {
        user_id: userProfile?.id,
        session_type: 'live_video_chat',
        timestamp: new Date().toISOString()
      };

      const result = await spiritualAPI.initiateLiveChat(sessionDetails);
      
      if (result && result.success) {
        setChatSession(result.data);
        await spiritualAPI.trackSpiritualEngagement('live_chat_initiated', {
          session_id: result.data.session_id
        });
      } else {
        alert('Live chat session could not be initiated. Please try again.');
      }
    } catch (error) {
      console.error('Live chat initiation encountered divine turbulence:', error);
      alert('Connection to divine guidance temporarily unavailable.');
    } finally {
      setIsLoading(false);
    }
  };

  const hasRequiredSubscription = userProfile?.subscription_tier === 'premium' || userProfile?.subscription_tier === 'elite';

  // Donation payment handler
  const handleDonationPayment = async () => {
    if (!selectedDonation) return;
    setDonationPaying(true);
    try {
      const paymentResult = await spiritualAPI.processDonation({
        donation_id: selectedDonation.id,
        amount_usd: selectedDonation.price_usd,
        message: `LiveChat Donation: ${selectedDonation.tamil_name || selectedDonation.name}`,
        session_id: chatSession?.session_id
      });
      if (paymentResult && paymentResult.success) {
        await spiritualAPI.confirmDonation(paymentResult.payment_intent_id);
        // Show flower animation and thank you message
        setShowFlowerAnimation(true);
        setShowDonationPopup(false);
        setSelectedDonation(null);
        
        // Update session total donations without interrupting the session
        if (chatSession?.session_id) {
          spiritualAPI.getSessionTotalDonations(chatSession.session_id).then((res) => {
            if (res && res.success) setSessionTotalDonations(res.total_donations || 0);
          });
        }
        
        setTimeout(() => {
          setShowFlowerAnimation(false);
        }, 3500);
      }
    } catch (error) {
      alert('தானம் செய்யும் போது பிழை ஏற்பட்டது. மீண்டும் முயற்சிக்கவும்.');
    } finally {
      setDonationPaying(false);
    }
  };

  return (
    <div className="pt-16 min-h-screen">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 py-16">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <Link 
            to="/" 
            className="inline-flex items-center text-white hover:text-gray-200 mb-6 transition-colors"
          >
            <ArrowLeft size={20} className="mr-2" />
            Back to Home
          </Link>
          
          <div className="text-6xl mb-4">📹</div>
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Live Video Chat
          </h1>
          <p className="text-xl text-white opacity-90 max-w-2xl mx-auto">
            Real-time spiritual consultation with live video sessions for deeper guidance
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="py-16 px-4">
        <div className="max-w-4xl mx-auto">
          {!isAuthenticated ? (
            /* Not Authenticated */
            <div className="text-center sacred-card p-12">
              <div className="text-6xl mb-6">🔐</div>
              <h2 className="text-3xl font-bold text-gray-800 mb-4">
                Sacred Authentication Required
              </h2>
              <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
                To access live video guidance with Swami Jyotirananthan, please create your sacred account or sign in to your existing one.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link to="/register" className="divine-button">
                  Create Sacred Account
                </Link>
                <Link 
                  to="/login" 
                  className="bg-transparent border-2 border-yellow-500 text-yellow-600 hover:bg-yellow-500 hover:text-white transition-all duration-300 px-6 py-3 rounded-lg font-semibold"
                >
                  Sign In
                </Link>
              </div>
            </div>
          ) : !hasRequiredSubscription ? (
            /* Insufficient Subscription */
            <div className="text-center sacred-card p-12">
              <div className="text-6xl mb-6">⭐</div>
              <h2 className="text-3xl font-bold text-gray-800 mb-4">
                Premium Spiritual Investment Required
              </h2>
              <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
                Live video chat with Swami Jyotirananthan is available for Premium and Elite members. 
                Upgrade your spiritual journey to access this divine feature.
              </p>
              
              {/* Subscription Options */}
              <div className="grid md:grid-cols-2 gap-6 mb-8">
                <div className="border-2 border-yellow-400 rounded-lg p-6">
                  <div className="text-3xl mb-3">🌟</div>
                  <h3 className="text-xl font-bold text-gray-800 mb-2">Premium</h3>
                  <p className="text-gray-600 mb-4">Advanced spiritual guidance with avatar videos</p>
                  <ul className="text-sm text-gray-600 mb-6 space-y-2">
                    <li className="flex items-center">
                      <Star size={12} className="text-yellow-500 mr-2" />
                      Live video chat sessions
                    </li>
                    <li className="flex items-center">
                      <Star size={12} className="text-yellow-500 mr-2" />
                      Avatar video guidance
                    </li>
                    <li className="flex items-center">
                      <Star size={12} className="text-yellow-500 mr-2" />
                      Priority support
                    </li>
                  </ul>
                  <button className="divine-button w-full">
                    Upgrade to Premium
                  </button>
                </div>
                
                <div className="border-2 border-purple-400 rounded-lg p-6">
                  <div className="text-3xl mb-3">👑</div>
                  <h3 className="text-xl font-bold text-gray-800 mb-2">Elite</h3>
                  <p className="text-gray-600 mb-4">Complete spiritual transformation journey</p>
                  <ul className="text-sm text-gray-600 mb-6 space-y-2">
                    <li className="flex items-center">
                      <Star size={12} className="text-purple-500 mr-2" />
                      Unlimited live sessions
                    </li>
                    <li className="flex items-center">
                      <Star size={12} className="text-purple-500 mr-2" />
                      Personal mentorship
                    </li>
                    <li className="flex items-center">
                      <Star size={12} className="text-purple-500 mr-2" />
                      Exclusive satsangs
                    </li>
                  </ul>
                  <button className="bg-gradient-to-r from-purple-500 to-indigo-600 text-white px-6 py-3 rounded-lg font-semibold w-full hover:from-purple-600 hover:to-indigo-700 transition-all duration-300">
                    Upgrade to Elite
                  </button>
                </div>
              </div>
            </div>
          ) : chatSession ? (
            /* Active Chat Session */
            <div className="sacred-card p-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">
                🕉️ Live Session with Swami Jyotirananthan
              </h2>
              
              <div className="bg-gray-100 rounded-lg p-8 text-center mb-6">
                <div className="text-4xl mb-4">📹</div>
                <p className="text-gray-600 mb-4">
                  Session ID: {chatSession.session_id}
                </p>
                <p className="text-gray-600 mb-6">
                  Your live video session is ready. Click below to join the sacred conversation.
                </p>
                
                {chatSession.agora_channel && (
                  <div className="bg-white rounded-lg p-4 mb-6">
                    <p className="text-sm text-gray-500 mb-2">Channel:</p>
                    <p className="font-mono text-sm">{chatSession.agora_channel}</p>
                  </div>
                )}
                
                <button className="divine-button text-lg px-8 py-4">
                  <Video className="mr-2" size={20} />
                  Join Live Session
                </button>
              </div>
              
              <div className="text-center">
                <p className="text-sm text-gray-500 mb-4">
                  Session started at {new Date(chatSession.start_time).toLocaleTimeString()}
                </p>
                <button 
                  onClick={() => setChatSession(null)}
                  className="text-red-600 hover:text-red-800 transition-colors"
                >
                  End Session
                </button>
              </div>
            </div>
          ) : (
            /* Ready to Start */
            <div className="text-center sacred-card p-12">
              <div className="text-6xl mb-6">🙏</div>
              <h2 className="text-3xl font-bold text-gray-800 mb-4">
                Welcome, {userProfile?.name || 'Divine Soul'}
              </h2>
              <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
                You have access to live video guidance with Swami Jyotirananthan. 
                Start a session whenever you need divine wisdom and personal guidance.
              </p>
              
              {/* Session Info */}
              <div className="grid md:grid-cols-3 gap-6 mb-8">
                <div className="text-center">
                  <Clock className="mx-auto mb-2 text-yellow-500" size={32} />
                  <h3 className="font-semibold text-gray-800">Session Duration</h3>
                  <p className="text-sm text-gray-600">30-60 minutes</p>
                </div>
                <div className="text-center">
                  <Users className="mx-auto mb-2 text-blue-500" size={32} />
                  <h3 className="font-semibold text-gray-800">Private Session</h3>
                  <p className="text-sm text-gray-600">One-on-one guidance</p>
                </div>
                <div className="text-center">
                  <Video className="mx-auto mb-2 text-purple-500" size={32} />
                  <h3 className="font-semibold text-gray-800">HD Video</h3>
                  <p className="text-sm text-gray-600">Crystal clear connection</p>
                </div>
              </div>
              
              <button 
                onClick={initiateLiveChat}
                disabled={isLoading}
                className="divine-button text-lg px-8 py-4 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Connecting to Divine Guidance...
                  </>
                ) : (
                  <>
                    <Video className="mr-2" size={20} />
                    Start Live Session
                  </>
                )}
              </button>
              
              <p className="text-xs text-gray-500 mt-4">
                Sessions are recorded for quality and spiritual growth purposes
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Features Section */}
      <div className="py-16 bg-gradient-to-br from-purple-900 to-blue-900">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center text-white mb-12">
            <span className="divine-text">Live Chat Features</span>
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center sacred-card p-8">
              <div className="text-4xl mb-4">🎯</div>
              <h3 className="text-xl font-bold text-gray-800 mb-4">Personalized Guidance</h3>
              <p className="text-gray-600">
                Receive guidance tailored specifically to your life situation, birth chart, and spiritual journey
              </p>
            </div>
            
            <div className="text-center sacred-card p-8">
              <div className="text-4xl mb-4">⚡</div>
              <h3 className="text-xl font-bold text-gray-800 mb-4">Real-time Interaction</h3>
              <p className="text-gray-600">
                Ask questions and receive immediate responses in a live, interactive spiritual consultation
              </p>
            </div>
            
            <div className="text-center sacred-card p-8">
              <div className="text-4xl mb-4">🔒</div>
              <h3 className="text-xl font-bold text-gray-800 mb-4">Sacred Privacy</h3>
              <p className="text-gray-600">
                Your sessions are completely private and confidential, creating a safe space for spiritual growth
              </p>
            </div>
          </div>
        </div>
      </div>

      {chatSession && (
        <>
          {/* Floating Donation Button */}
          <button
            className="fixed bottom-8 right-8 z-50 bg-yellow-500 hover:bg-yellow-600 text-white px-6 py-3 rounded-full shadow-lg flex items-center text-lg font-bold animate-bounce"
            onClick={() => setShowDonationPopup(true)}
            style={{ boxShadow: '0 4px 24px rgba(0,0,0,0.15)' }}
          >
            <span className="text-2xl mr-2">🪔</span> தானம் செய்யுங்கள்
          </button>

          {/* Donation Popup Modal */}
          {showDonationPopup && (
            <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50">
              <div className="bg-white rounded-lg shadow-2xl p-8 w-full max-w-md relative">
                <button
                  className="absolute top-3 right-3 text-gray-500 hover:text-gray-800"
                  onClick={() => setShowDonationPopup(false)}
                >
                  <X size={24} />
                </button>
                <h3 className="text-xl font-bold mb-4 text-center">தானம் செய்யுங்கள்</h3>
                {donationsLoading ? (
                  <div className="text-center text-gray-600">தானங்கள் ஏற்றப்படுகிறது...</div>
                ) : (
                  <div className="space-y-4">
                    {donationOptions.length === 0 && (
                      <div className="text-center text-gray-500">தற்போது தானங்கள் இல்லை</div>
                    )}
                    {donationOptions.map((donation) => (
                      <button
                        key={donation.id}
                        onClick={() => setSelectedDonation(donation)}
                        className={`w-full flex items-center gap-3 p-3 rounded-lg border-2 transition-all duration-200 ${
                          selectedDonation?.id === donation.id
                            ? 'border-green-500 bg-green-50'
                            : 'border-gray-200 hover:border-yellow-400'
                        }`}
                        disabled={donationPaying}
                      >
                        <span className="text-2xl">{donation.icon}</span>
                        <span className="flex-1 text-left">
                          <span className="block font-semibold text-gray-800">{donation.tamil_name || donation.name}</span>
                          <span className="block text-xs text-gray-500">{donation.description}</span>
                        </span>
                        <span className="text-green-600 font-bold">${donation.price_usd}</span>
                      </button>
                    ))}
                  </div>
                )}
                {selectedDonation && (
                  <div className="mt-6 text-center">
                    <button
                      onClick={handleDonationPayment}
                      disabled={donationPaying}
                      className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg font-semibold transition-colors disabled:opacity-50"
                    >
                      {donationPaying ? 'தானம் செயல்படுகிறது...' : `🪔 ${selectedDonation.tamil_name || selectedDonation.name} - $${selectedDonation.price_usd} தானம் செய்யுங்கள்`}
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Flower Animation Overlay */}
          {showFlowerAnimation && (
            <div className="fixed inset-0 z-[100] flex items-center justify-center pointer-events-none">
              {/* Falling flowers */}
              {[...Array(12)].map((_, i) => (
                <span
                  key={i}
                  className={`flower-fall absolute text-4xl select-none pointer-events-none`}
                  style={{
                    left: `${8 + i * 7}%`,
                    animationDelay: `${i * 0.2}s`,
                  }}
                >🌸</span>
              ))}
              {/* Thank you message */}
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white bg-opacity-90 rounded-xl shadow-lg px-8 py-6 flex flex-col items-center">
                <div className="text-5xl mb-2">🌸</div>
                <div className="text-2xl font-bold text-pink-700 mb-1">நன்றி!</div>
                <div className="text-lg text-gray-700">உங்கள் அர்ப்பணிப்பு ஏற்றுக்கொள்ளப்பட்டது</div>
              </div>
              <style>{`
                .flower-fall {
                  animation: flower-fall 2.8s linear forwards;
                  top: -60px;
                }
                @keyframes flower-fall {
                  0% { transform: translateY(0) rotate(0deg) scale(1); opacity: 1; }
                  80% { opacity: 1; }
                  100% { transform: translateY(90vh) rotate(360deg) scale(1.2); opacity: 0.7; }
                }
              `}</style>
            </div>
          )}
          {/* Session Summary - Total Donations */}
          <div className="fixed bottom-8 left-8 z-40 bg-white bg-opacity-90 rounded-lg shadow-lg px-6 py-3 flex items-center gap-2 text-lg font-bold text-green-700 border-2 border-green-200">
            <span>🪔</span> மொத்த தானம்: <span className="text-green-800">${sessionTotalDonations.toFixed(2)}</span>
          </div>
        </>
      )}
    </div>
  );
};

export default LiveChat;

