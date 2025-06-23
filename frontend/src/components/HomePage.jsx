import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Play, Star, Users, Calendar, Award, Globe } from 'lucide-react';
import spiritualAPI from '../lib/api';
import DailyWisdom from './spiritual/DailyWisdom';

const HomePage = () => {
  const [platformStats, setPlatformStats] = useState({
    total_users: 25000,
    total_sessions: 75000,
    active_users: 8247,
    community_members: 8247,
    satsangs_completed: 42,
    countries_reached: 67,
    total_guidance_hours: 12000,
    total_revenue: 125075,
    daily_revenue: 12575
  });
  const [nextSatsang, setNextSatsang] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadPlatformData();
  }, []);

  const loadPlatformData = async () => {
    try {
      // Load platform statistics
      const stats = await spiritualAPI.loadPlatformStats();
      if (stats) {
        setPlatformStats(stats);
      }

      // Load next satsang information
      const satsangData = await spiritualAPI.getSatsangSchedule();
      if (satsangData && satsangData.success && satsangData.data) {
        setNextSatsang(satsangData.data);
      }

      // Track homepage visit
      await spiritualAPI.trackSpiritualEngagement('homepage_visit', {
        timestamp: new Date().toISOString(),
        user_agent: navigator.userAgent
      });
    } catch (error) {
      console.log('🕉️ Platform data loading blessed with patience:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAvatarClick = async () => {
    await spiritualAPI.trackSpiritualEngagement('avatar_interaction', {
      action: 'click',
      location: 'homepage_hero'
    });

    if (spiritualAPI.isAuthenticated()) {
      window.location.href = '/profile';
    } else {
      window.location.href = '/register?welcome=true';
    }
  };

  const handleServiceClick = async (serviceType) => {
    await spiritualAPI.trackSpiritualEngagement('service_selection', {
      service_type: serviceType,
      location: 'homepage'
    });
    
    window.location.href = `/login?service=${serviceType}&redirect=profile`;
  };

  const formatNumber = (num, addPlus = false) => {
    if (num >= 1000000) {
      return Math.floor(num / 1000000) + 'M' + (addPlus ? '+' : '');
    } else if (num >= 1000) {
      return Math.floor(num / 1000) + 'K' + (addPlus ? '+' : '');
    }
    return num.toString() + (addPlus ? '+' : '');
  };

  const services = [
    {
      id: 'clarity',
      name: 'Clarity Plus',
      description: 'Essential spiritual guidance for life\'s questions',
      icon: '🔮',
      features: ['Personal guidance', 'Birth chart insights', 'Life direction'],
      tier: 'Essential'
    },
    {
      id: 'love',
      name: 'AstroLove',
      description: 'Divine guidance for relationships and love',
      icon: '💕',
      features: ['Relationship compatibility', 'Love guidance', 'Partner insights'],
      tier: 'Relationship'
    },
    {
      id: 'premium',
      name: 'Premium',
      description: 'Advanced spiritual guidance with avatar videos',
      icon: '🌟',
      features: ['Avatar video guidance', 'Priority support', 'Advanced insights'],
      tier: 'Premium',
      popular: true
    },
    {
      id: 'elite',
      name: 'Elite',
      description: 'Complete spiritual transformation journey',
      icon: '👑',
      features: ['Live video sessions', 'Personal mentorship', 'Exclusive satsangs'],
      tier: 'Elite'
    }
  ];

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="consciousness-pulse">
          <div className="om-symbol text-6xl">🕉️</div>
          <p className="text-white mt-4 text-center">Loading divine wisdom...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="pt-16">
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center px-4">
        <div className="max-w-6xl mx-auto text-center">
          {/* Swami Avatar */}
          <div className="mb-8 divine-entrance">
            <div 
              className="swami-showcase cursor-pointer consciousness-pulse"
              onClick={handleAvatarClick}
            >
              <div className="swami-container mx-auto max-w-md">
                <div className="swami-image relative">
                  <div className="w-64 h-64 mx-auto rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 p-1 divine-glow">
                    <div className="w-full h-full rounded-full bg-gray-800 flex items-center justify-center">
                      <div className="swami-placeholder text-center">
                        <div className="om-symbol text-6xl mb-2">🕉️</div>
                        <div className="text-white">
                          <strong className="text-xl">Swami Jyotirananthan</strong><br />
                          <span className="text-gray-300">Your Virtual Guru for Inner Transformation</span><br />
                          <small className="text-yellow-400">Click to receive divine wisdom</small>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="divine-indicators mt-4 flex justify-center space-x-2">
                  <span className="divine-badge bg-yellow-500 text-black px-3 py-1 rounded-full text-sm">AI Spiritual Guide</span>
                  <span className="divine-badge bg-orange-500 text-white px-3 py-1 rounded-full text-sm">Live Sessions</span>
                  <span className="divine-badge bg-purple-500 text-white px-3 py-1 rounded-full text-sm">Personal Guidance</span>
                </div>
              </div>
            </div>
          </div>

          {/* Hero Text */}
          <div className="divine-entrance" style={{ animationDelay: '0.3s' }}>
            <h1 className="text-5xl md:text-7xl font-bold text-white mb-6">
              <span className="divine-text">Welcome to Divine</span><br />
              <span className="text-yellow-400">Digital Guidance</span>
            </h1>
            <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-3xl mx-auto">
              Experience divine guidance through advanced AI avatar technology with Swami Jyotirananthan
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button 
                onClick={() => handleServiceClick('clarity')}
                className="divine-button text-lg px-8 py-4"
              >
                Begin Sacred Journey
              </button>
              <Link 
                to="/satsang"
                className="bg-transparent border-2 border-yellow-400 text-yellow-400 hover:bg-yellow-400 hover:text-black transition-all duration-300 px-8 py-4 rounded-lg text-lg font-semibold"
              >
                Join Community
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Platform Statistics */}
      <section className="py-16 bg-black bg-opacity-50">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center text-white mb-12">
            <span className="divine-text">Sacred Community Metrics</span>
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div className="text-center sacred-card p-6">
              <div className="text-3xl md:text-4xl font-bold text-yellow-500 mb-2">
                {formatNumber(platformStats.total_users, true)}
              </div>
              <div className="text-gray-600">Divine Souls</div>
            </div>
            <div className="text-center sacred-card p-6">
              <div className="text-3xl md:text-4xl font-bold text-orange-500 mb-2">
                {formatNumber(platformStats.total_sessions, true)}
              </div>
              <div className="text-gray-600">Guidance Sessions</div>
            </div>
            <div className="text-center sacred-card p-6">
              <div className="text-3xl md:text-4xl font-bold text-purple-500 mb-2">
                {formatNumber(platformStats.community_members, true)}
              </div>
              <div className="text-gray-600">Sacred Community</div>
            </div>
            <div className="text-center sacred-card p-6">
              <div className="text-3xl md:text-4xl font-bold text-blue-500 mb-2">
                {platformStats.countries_reached}
              </div>
              <div className="text-gray-600">Countries Reached</div>
            </div>
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section className="py-16 px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center text-white mb-4">
            <span className="divine-text">Sacred Guidance Services</span>
          </h2>
          <p className="text-gray-300 text-center mb-12 max-w-2xl mx-auto">
            Choose your spiritual journey path. Each service is blessed with divine wisdom and personalized guidance.
          </p>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {services.map((service, index) => (
              <div 
                key={service.id}
                className={`sacred-card p-6 cursor-pointer transition-all duration-300 hover:scale-105 ${
                  service.popular ? 'ring-2 ring-yellow-400' : ''
                }`}
                onClick={() => handleServiceClick(service.id)}
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                {service.popular && (
                  <div className="bg-yellow-400 text-black text-xs font-bold px-2 py-1 rounded-full inline-block mb-3">
                    MOST POPULAR
                  </div>
                )}
                <div className="text-4xl mb-4">{service.icon}</div>
                <h3 className="text-xl font-bold text-gray-800 mb-2">{service.name}</h3>
                <p className="text-gray-600 mb-4">{service.description}</p>
                <ul className="space-y-2 mb-6">
                  {service.features.map((feature, idx) => (
                    <li key={idx} className="flex items-center text-sm text-gray-600">
                      <Star size={12} className="text-yellow-500 mr-2" />
                      {feature}
                    </li>
                  ))}
                </ul>
                <button className="w-full divine-button">
                  Login to Access {service.tier}
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Next Satsang Section */}
      {nextSatsang && (
        <section className="py-16 bg-gradient-to-r from-purple-900 to-blue-900">
          <div className="max-w-4xl mx-auto px-4 text-center">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
              <span className="divine-text">Next Sacred Satsang</span>
            </h2>
            <div className="sacred-card p-8">
              <div className="text-6xl mb-4">🙏</div>
              <h3 className="text-2xl font-bold text-gray-800 mb-2">
                {nextSatsang.theme || "Divine Wisdom Gathering"}
              </h3>
              <p className="text-gray-600 mb-6">
                {nextSatsang.scheduled_date 
                  ? new Date(nextSatsang.scheduled_date).toLocaleDateString('en-US', {
                      weekday: 'long',
                      month: 'long',
                      day: 'numeric',
                      hour: 'numeric',
                      minute: '2-digit'
                    })
                  : "Date to be announced"
                }
              </p>
              <Link to="/satsang" className="divine-button text-lg px-8 py-3">
                Join Sacred Gathering
              </Link>
            </div>
          </div>
        </section>
      )}

      {/* Community Features */}
      <section className="py-16 px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center text-white mb-12">
            <span className="divine-text">Sacred Platform Features</span>
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center sacred-card p-8">
              <div className="text-5xl mb-4">🎥</div>
              <h3 className="text-xl font-bold text-gray-800 mb-4">AI Avatar Guidance</h3>
              <p className="text-gray-600 mb-4">
                Personalized video guidance from Swami Jyotirananthan using advanced AI avatar technology
              </p>
              <span className="inline-block bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm font-semibold">
                Premium Feature
              </span>
            </div>
            
            <div className="text-center sacred-card p-8">
              <div className="text-5xl mb-4">📹</div>
              <h3 className="text-xl font-bold text-gray-800 mb-4">Live Video Chat</h3>
              <p className="text-gray-600 mb-4">
                Real-time spiritual consultation with live video sessions for deeper guidance
              </p>
              <span className="inline-block bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-semibold">
                Elite Feature
              </span>
            </div>
            
            <div className="text-center sacred-card p-8">
              <div className="text-5xl mb-4">🙏</div>
              <h3 className="text-xl font-bold text-gray-800 mb-4">Monthly Satsang</h3>
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

      {/* Call to Action */}
      <section className="py-16 bg-gradient-to-r from-yellow-400 to-orange-500">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-black mb-6">
            Ready to Begin Your Sacred Journey?
          </h2>
          <p className="text-black text-lg mb-8 opacity-80">
            Join thousands of souls who have found divine guidance and inner peace through our platform
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button 
              onClick={() => handleServiceClick('clarity')}
              className="bg-black text-white hover:bg-gray-800 transition-all duration-300 px-8 py-4 rounded-lg text-lg font-semibold"
            >
              Start Free Guidance
            </button>
            <Link 
              to="/register"
              className="bg-transparent border-2 border-black text-black hover:bg-black hover:text-white transition-all duration-300 px-8 py-4 rounded-lg text-lg font-semibold"
            >
              Create Sacred Account
            </Link>
          </div>
        </div>
      </section>

            {/* Daily Wisdom Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Daily Spiritual Nourishment
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Begin each day with divine wisdom from Swami Jyotirananthan
            </p>
          </div>
          
          <div className="max-w-4xl mx-auto">
            <DailyWisdom />
          </div>
        </div>
      </section>

    </div>
  );
};

export default HomePage;

