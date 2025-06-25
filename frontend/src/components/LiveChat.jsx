import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, Video, Clock, Users, Star } from 'lucide-react';
import spiritualAPI from '../lib/api';

const LiveChat = () => {
  const navigate = useNavigate(); 
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userProfile, setUserProfile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [chatSession, setChatSession] = useState(null);

  useEffect(() => {
    checkAuthAndSubscription();
    spiritualAPI.trackSpiritualEngagement('live_chat_visit');
  }, []);

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
    </div>
  );
};

export default LiveChat;

