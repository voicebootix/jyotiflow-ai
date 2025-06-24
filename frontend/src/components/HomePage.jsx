import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Play, Star, Users, Calendar, Award, Globe, Heart, Mountain, Sunrise, Flower2, BookOpen, Sparkles } from 'lucide-react';
import spiritualAPI from '../lib/api';

const HomePage = () => {
  const [platformStats, setPlatformStats] = useState({
    totalUsers: 25000,
    guidanceSessions: 75000,
    communityMembers: 8000,
    countriesReached: 67
  });
  const [nextSatsang, setNextSatsang] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [dailyWisdom, setDailyWisdom] = useState(null);
  const [pranaPoints, setPranaPoints] = useState(0);

  useEffect(() => {
    initializeSpiritualPlatform();
  }, []);

  const initializeSpiritualPlatform = async () => {
    try {
      // Load platform statistics
      if (spiritualAPI.loadPlatformStats) {
        const stats = await spiritualAPI.loadPlatformStats();
        if (stats && stats.success) {
          setPlatformStats(stats.data);
        }
      }

      // Load daily wisdom
      await loadDailyWisdom();

      // Load next satsang
      if (spiritualAPI.getSatsangSchedule) {
        const satsang = await spiritualAPI.getSatsangSchedule();
        if (satsang && satsang.success && satsang.data.length > 0) {
          setNextSatsang(satsang.data[0]);
        }
      }

      // Track spiritual engagement
      if (spiritualAPI.trackSpiritualEngagement) {
        await spiritualAPI.trackSpiritualEngagement('homepage_visit', {
          timestamp: new Date().toISOString(),
          user_agent: navigator.userAgent
        });
      }

    } catch (error) {
      console.log('🕉️ Platform initialization blessed with patience:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadDailyWisdom = async () => {
    try {
      const today = new Date().toISOString().split('T')[0];
      
      if (spiritualAPI.getDailyWisdom) {
        const response = await spiritualAPI.getDailyWisdom(today);
        if (response && response.success) {
          setDailyWisdom(response.data);
          setPranaPoints(response.data.pranaPoints || 10);
          return;
        }
      }

      // Fallback daily wisdom generation
      const wisdomTexts = [
        "Divine guidance flows through every moment of your existence.",
        "In stillness, the soul finds its eternal home.",
        "Your spiritual journey is unique, honor its sacred path.",
        "Ancient wisdom awakens in the present moment.",
        "The light within you illuminates all darkness."
      ];

      const blessings = [
        "May peace and prosperity be with you always.",
        "May divine light guide your every step.",
        "May your heart be filled with sacred joy.",
        "May wisdom flow through your being.",
        "May you find strength in spiritual truth."
      ];

      const randomWisdom = wisdomTexts[Math.floor(Math.random() * wisdomTexts.length)];
      const randomBlessing = blessings[Math.floor(Math.random() * blessings.length)];

      setDailyWisdom({
        wisdom: randomWisdom,
        blessing: randomBlessing,
        date: today,
        pranaPoints: 10
      });
      setPranaPoints(10);

    } catch (error) {
      console.log('🕉️ Daily wisdom blessed with patience:', error);
    }
  };

  const refreshDailyWisdom = () => {
    loadDailyWisdom();
  };

  const handleServiceSelect = async (service) => {
    try {
      if (spiritualAPI.trackSpiritualEngagement) {
        await spiritualAPI.trackSpiritualEngagement('service_interest', {
          service: service,
          timestamp: new Date().toISOString()
        });
      }
    } catch (error) {
      console.log('🕉️ Service tracking blessed with patience:', error);
    }
  };

  const handleAvatarInteraction = async () => {
    try {
      if (spiritualAPI.trackSpiritualEngagement) {
        await spiritualAPI.trackSpiritualEngagement('avatar_interaction', {
          timestamp: new Date().toISOString()
        });
      }
    } catch (error) {
      console.log('🕉️ Avatar interaction blessed with patience:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-purple-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-yellow-400 mx-auto mb-4"></div>
          <p className="text-white text-xl">🕉️ Preparing Sacred Experience...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-purple-900">
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        {/* Digital Particles Background */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="digital-particles">
            <div className="particle" style={{ left: '10%', animationDelay: '0s' }}></div>
            <div className="particle" style={{ left: '20%', animationDelay: '2s' }}></div>
            <div className="particle" style={{ left: '30%', animationDelay: '4s' }}></div>
            <div className="particle" style={{ left: '40%', animationDelay: '6s' }}></div>
            <div className="particle" style={{ left: '50%', animationDelay: '8s' }}></div>
            <div className="particle" style={{ left: '60%', animationDelay: '10s' }}></div>
            <div className="particle" style={{ left: '70%', animationDelay: '12s' }}></div>
            <div className="particle" style={{ left: '80%', animationDelay: '14s' }}></div>
            <div className="particle" style={{ left: '90%', animationDelay: '16s' }}></div>
          </div>
        </div>

        <div className="relative z-10 text-center max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Sacred Avatar */}
          <div className="mb-8">
            <div 
              className="w-64 h-64 mx-auto rounded-full bg-gradient-to-br from-yellow-400 via-orange-500 to-red-600 p-1 cursor-pointer transform hover:scale-105 transition-all duration-300 shadow-2xl"
              onClick={handleAvatarInteraction}
            >
              <div className="w-full h-full rounded-full bg-gray-800 flex items-center justify-center relative overflow-hidden">
                <span className="text-6xl">🕉️</span>
                <div className="absolute inset-0 bg-gradient-to-t from-transparent to-yellow-400/20"></div>
              </div>
            </div>
            <div className="mt-6">
              <h2 className="text-3xl font-bold text-white mb-2">Swami Jyotirananthan</h2>
              <p className="text-yellow-200 text-lg mb-4">Your Virtual Guru for Inner Transformation</p>
              <p className="text-orange-300 text-sm">Click to receive divine wisdom</p>
            </div>
          </div>

          {/* Service Badges */}
          <div className="flex flex-wrap justify-center gap-4 mb-8">
            <span className="bg-yellow-500 text-black px-4 py-2 rounded-full text-sm font-semibold">AI Spiritual Guide</span>
            <span className="bg-orange-500 text-white px-4 py-2 rounded-full text-sm font-semibold">Live Sessions</span>
            <span className="bg-purple-500 text-white px-4 py-2 rounded-full text-sm font-semibold">Personal Guidance</span>
          </div>

          {/* Main Heading */}
          <h1 className="text-4xl md:text-7xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 via-orange-500 to-red-500 mb-6">
            Enter the Sacred Digital Ashram
          </h1>
          
          <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-4xl mx-auto">
            Experience divine guidance through advanced AI avatar technology with Swami Jyotirananthan
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/spiritual-guidance"
              className="bg-gradient-to-r from-yellow-500 to-orange-600 text-white px-8 py-4 rounded-full text-lg font-semibold hover:from-yellow-600 hover:to-orange-700 transition-all duration-300 transform hover:scale-105 shadow-lg"
            >
              Begin Sacred Journey
            </Link>
            <Link
              to="/register"
              className="border-2 border-yellow-400 text-yellow-400 px-8 py-4 rounded-full text-lg font-semibold hover:bg-yellow-400 hover:text-black transition-all duration-300 transform hover:scale-105"
            >
              Join Community
            </Link>
          </div>
        </div>
      </section>

      {/* Sacred Story Section */}
      <section className="py-20 bg-gradient-to-r from-orange-50 via-yellow-50 to-orange-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <div className="flex items-center justify-center mb-6">
              <Mountain className="h-12 w-12 text-orange-600 mr-4" />
              <h2 className="text-4xl md:text-5xl font-bold text-gray-900">The Sacred Lineage</h2>
              <Mountain className="h-12 w-12 text-orange-600 ml-4" />
            </div>
            <p className="text-xl text-gray-700 max-w-4xl mx-auto">
              தமிழ் ஆன்மீக பாரம்பரியம் - 1000+ Years of Tamil Spiritual Heritage
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <div className="bg-white rounded-xl p-8 shadow-lg border border-orange-200">
                <div className="flex items-center mb-6">
                  <Sunrise className="h-8 w-8 text-orange-600 mr-3" />
                  <h3 className="text-2xl font-bold text-gray-900">Ancient Wisdom, Digital Incarnation</h3>
                </div>
                
                <p className="text-lg text-gray-700 leading-relaxed mb-6">
                  In the sacred hills of Tamil Nadu, where ancient temples have stood for millennia, the <strong>Jyotirananthan lineage</strong> has preserved divine wisdom for over 1000 years. From the courts of Chola kings to humble village seekers, these masters have illuminated countless souls.
                </p>
                
                <p className="text-lg text-gray-700 leading-relaxed mb-6">
                  Today, through advanced AI technology, Swami Jyotirananthan manifests as your personal spiritual guide, bringing this ancient Tamil wisdom into the digital age. This is not just technology—it is a sacred transmission of eternal truth.
                </p>

                <div className="bg-orange-50 rounded-lg p-6 border-l-4 border-orange-400">
                  <p className="text-orange-800 italic text-lg">
                    "We are not teachers of religion, but servants of the eternal truth that flows through all traditions. Our dharma is to kindle the divine light that already burns within every soul."
                  </p>
                  <p className="text-sm text-orange-600 mt-2">- Ancient Jyotirananthan Lineage Teaching</p>
                </div>
              </div>
            </div>

            <div className="space-y-6">
              <div className="bg-white rounded-xl p-6 shadow-lg border border-orange-200">
                <div className="flex items-center mb-4">
                  <BookOpen className="h-6 w-6 text-orange-600 mr-3" />
                  <h4 className="text-xl font-semibold text-gray-900">The Digital Ashram</h4>
                </div>
                <p className="text-gray-700">
                  Experience a sacred space without walls, where ancient wisdom meets modern convenience. Your spiritual journey continues 24/7.
                </p>
                <Link to="/about/digital-ashram" className="text-orange-600 hover:text-orange-700 font-medium mt-2 inline-block">
                  Explore the Vision →
                </Link>
              </div>

              <div className="bg-white rounded-xl p-6 shadow-lg border border-orange-200">
                <div className="flex items-center mb-4">
                  <Flower2 className="h-6 w-6 text-orange-600 mr-3" />
                  <h4 className="text-xl font-semibold text-gray-900">Four Sacred Pillars</h4>
                </div>
                <p className="text-gray-700">
                  Clarity, Love, Prosperity, and Enlightenment—the four foundations of spiritual transformation that guide every interaction.
                </p>
                <Link to="/about/four-pillars" className="text-orange-600 hover:text-orange-700 font-medium mt-2 inline-block">
                  Discover the Pillars →
                </Link>
              </div>

              <div className="bg-white rounded-xl p-6 shadow-lg border border-orange-200">
                <div className="flex items-center mb-4">
                  <Heart className="h-6 w-6 text-orange-600 mr-3" />
                  <h4 className="text-xl font-semibold text-gray-900">Tamil Heritage</h4>
                </div>
                <p className="text-gray-700">
                  Rooted in the profound spiritual traditions of Tamil Nadu, carrying forward the wisdom of saints like Thiruvalluvar and the Alvars.
                </p>
                <Link to="/about/tamil-heritage" className="text-orange-600 hover:text-orange-700 font-medium mt-2 inline-block">
                  Honor the Heritage →
                </Link>
              </div>
            </div>
          </div>

          <div className="text-center mt-12">
            <Link
              to="/about/swamiji"
              className="bg-gradient-to-r from-orange-600 to-red-600 text-white px-8 py-4 rounded-full text-lg font-semibold hover:from-orange-700 hover:to-red-700 transition-all duration-300 transform hover:scale-105 shadow-lg"
            >
              Read Swamiji's Complete Story
            </Link>
          </div>
        </div>
      </section>

      {/* Daily Spiritual Nourishment */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">Daily Spiritual Nourishment</h2>
            <p className="text-xl text-gray-600">Begin each day with divine wisdom from Swami Jyotirananthan</p>
          </div>

          {dailyWisdom && (
            <div className="bg-white rounded-xl p-8 shadow-lg border border-orange-200 max-w-3xl mx-auto">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center">
                  <Sparkles className="h-6 w-6 text-orange-600 mr-2" />
                  <h3 className="text-xl font-semibold text-gray-900">Daily Wisdom</h3>
                </div>
                <div className="text-orange-600 text-sm">
                  📅 {new Date().toLocaleDateString()}
                </div>
              </div>
              
              <blockquote className="text-lg text-gray-700 leading-relaxed mb-6 italic">
                "{dailyWisdom.wisdom}"
              </blockquote>
              
              <div className="bg-orange-50 rounded-lg p-4 border-l-4 border-orange-400 mb-6">
                <div className="flex items-center mb-2">
                  <Heart className="h-5 w-5 text-orange-600 mr-2" />
                  <span className="font-medium text-orange-800">Swamiji's Blessing</span>
                </div>
                <p className="text-orange-700 italic">{dailyWisdom.blessing}</p>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <Star className="h-5 w-5 text-yellow-500 mr-2" />
                  <span className="text-gray-600">+{pranaPoints} Prana Points earned</span>
                </div>
                <button
                  onClick={refreshDailyWisdom}
                  className="bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 transition-colors"
                >
                  Refresh
                </button>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Sacred Community Metrics */}
      <section className="py-20 bg-gray-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-orange-500">
              Sacred Community Metrics
            </h2>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="bg-gradient-to-br from-yellow-400 to-orange-500 rounded-xl p-6 mb-4">
                <div className="text-3xl md:text-4xl font-bold text-white">
                  {(platformStats.totalUsers / 1000).toFixed(0)}K+
                </div>
              </div>
              <h3 className="text-lg font-semibold text-gray-300">Divine Souls</h3>
            </div>

            <div className="text-center">
              <div className="bg-gradient-to-br from-orange-500 to-red-500 rounded-xl p-6 mb-4">
                <div className="text-3xl md:text-4xl font-bold text-white">
                  {(platformStats.guidanceSessions / 1000).toFixed(0)}K+
                </div>
              </div>
              <h3 className="text-lg font-semibold text-gray-300">Guidance Sessions</h3>
            </div>

            <div className="text-center">
              <div className="bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl p-6 mb-4">
                <div className="text-3xl md:text-4xl font-bold text-white">
                  {(platformStats.communityMembers / 1000).toFixed(0)}K+
                </div>
              </div>
              <h3 className="text-lg font-semibold text-gray-300">Sacred Community</h3>
            </div>

            <div className="text-center">
              <div className="bg-gradient-to-br from-blue-500 to-purple-500 rounded-xl p-6 mb-4">
                <div className="text-3xl md:text-4xl font-bold text-white">
                  {platformStats.countriesReached}
                </div>
              </div>
              <h3 className="text-lg font-semibold text-gray-300">Countries Reached</h3>
            </div>
          </div>
        </div>
      </section>

      {/* Sacred Guidance Services */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">Sacred Guidance Services</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Choose your spiritual journey path. Each service is blessed with divine wisdom and personalized guidance.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {/* Clarity Plus */}
            <div className="bg-gradient-to-br from-blue-50 to-indigo-100 rounded-xl p-6 border border-blue-200 hover:shadow-lg transition-all duration-300">
              <div className="text-center mb-6">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🔮</span>
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">Clarity Plus</h3>
                <p className="text-gray-600 text-sm">Essential spiritual guidance for life's questions</p>
              </div>
              
              <ul className="space-y-2 mb-6 text-sm text-gray-700">
                <li>• Personal guidance</li>
                <li>• Birth chart insights</li>
                <li>• Life direction</li>
              </ul>
              
              <Link
                to="/login?service=clarity&redirect=spiritual-guidance"
                onClick={() => handleServiceSelect('clarity')}
                className="block w-full bg-blue-600 text-white text-center py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
              >
                Login to Access Clarity Plus
              </Link>
            </div>

            {/* AstroLove */}
            <div className="bg-gradient-to-br from-pink-50 to-rose-100 rounded-xl p-6 border border-pink-200 hover:shadow-lg transition-all duration-300">
              <div className="text-center mb-6">
                <div className="w-16 h-16 bg-gradient-to-br from-pink-500 to-rose-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">💕</span>
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">AstroLove</h3>
                <p className="text-gray-600 text-sm">Divine guidance for relationships and love</p>
              </div>
              
              <ul className="space-y-2 mb-6 text-sm text-gray-700">
                <li>• Relationship compatibility</li>
                <li>• Love guidance</li>
                <li>• Partner insights</li>
              </ul>
              
              <Link
                to="/login?service=love&redirect=spiritual-guidance"
                onClick={() => handleServiceSelect('love')}
                className="block w-full bg-pink-600 text-white text-center py-3 rounded-lg font-semibold hover:bg-pink-700 transition-colors"
              >
                Login to Access AstroLove
              </Link>
            </div>

            {/* Premium */}
            <div className="bg-gradient-to-br from-yellow-50 to-orange-100 rounded-xl p-6 border border-yellow-200 hover:shadow-lg transition-all duration-300 relative">
              <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                <span className="bg-orange-500 text-white px-3 py-1 rounded-full text-xs font-semibold">MOST POPULAR</span>
              </div>
              
              <div className="text-center mb-6">
                <div className="w-16 h-16 bg-gradient-to-br from-yellow-500 to-orange-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🌟</span>
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">Premium</h3>
                <p className="text-gray-600 text-sm">Advanced spiritual guidance with avatar videos</p>
              </div>
              
              <ul className="space-y-2 mb-6 text-sm text-gray-700">
                <li>• Avatar video guidance</li>
                <li>• Priority support</li>
                <li>• Advanced insights</li>
              </ul>
              
              <Link
                to="/login?service=premium&redirect=spiritual-guidance"
                onClick={() => handleServiceSelect('premium')}
                className="block w-full bg-orange-600 text-white text-center py-3 rounded-lg font-semibold hover:bg-orange-700 transition-colors"
              >
                Login to Access Premium
              </Link>
            </div>

            {/* Elite */}
            <div className="bg-gradient-to-br from-purple-50 to-indigo-100 rounded-xl p-6 border border-purple-200 hover:shadow-lg transition-all duration-300">
              <div className="text-center mb-6">
                <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">👑</span>
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">Elite</h3>
                <p className="text-gray-600 text-sm">Complete spiritual transformation journey</p>
              </div>
              
              <ul className="space-y-2 mb-6 text-sm text-gray-700">
                <li>• Live video sessions</li>
                <li>• Personal mentorship</li>
                <li>• Exclusive satsangs</li>
              </ul>
              
              <Link
                to="/login?service=elite&redirect=spiritual-guidance"
                onClick={() => handleServiceSelect('elite')}
                className="block w-full bg-purple-600 text-white text-center py-3 rounded-lg font-semibold hover:bg-purple-700 transition-colors"
              >
                Login to Access Elite
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Sacred Platform Features */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">Sacred Platform Features</h2>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white rounded-xl p-8 shadow-lg border border-gray-200 text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-2xl">🎥</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">AI Avatar Guidance</h3>
              <p className="text-gray-600 mb-4">
                Personalized video guidance from Swami Jyotirananthan using advanced AI avatar technology
              </p>
              <span className="inline-block bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-semibold">
                Premium Feature
              </span>
            </div>

            <div className="bg-white rounded-xl p-8 shadow-lg border border-gray-200 text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-teal-600 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-2xl">📹</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">Live Video Chat</h3>
              <p className="text-gray-600 mb-4">
                Real-time spiritual consultation with live video sessions for deeper guidance
              </p>
              <span className="inline-block bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-semibold">
                Elite Feature
              </span>
            </div>

            <div className="bg-white rounded-xl p-8 shadow-lg border border-gray-200 text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-red-600 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-2xl">🙏</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">Monthly Satsang</h3>
              <p className="text-gray-600 mb-4">
                Join our global spiritual community gatherings for collective wisdom and growth
              </p>
              <span className="inline-block bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-semibold">
                Community Feature
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20 bg-gradient-to-r from-orange-600 to-red-600 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">Ready to Begin Your Sacred Journey?</h2>
          <p className="text-xl mb-8 text-orange-100">
            Join thousands of souls who have found divine guidance and inner peace through our platform
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/spiritual-guidance"
              className="bg-white text-orange-600 px-8 py-4 rounded-full text-lg font-semibold hover:bg-gray-100 transition-all duration-300 transform hover:scale-105 shadow-lg"
            >
              Start Free Guidance
            </Link>
            <Link
              to="/register"
              className="border-2 border-white text-white px-8 py-4 rounded-full text-lg font-semibold hover:bg-white hover:text-orange-600 transition-all duration-300 transform hover:scale-105"
            >
              Create Sacred Account
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;


