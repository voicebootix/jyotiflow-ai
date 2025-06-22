import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Calendar, Users, Clock, MapPin, Bell } from 'lucide-react';
import spiritualAPI from '../lib/api';

const Satsang = () => {
  const [satsangSchedule, setSatsangSchedule] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [registeredEvents, setRegisteredEvents] = useState(new Set());
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    loadSatsangData();
    setIsAuthenticated(spiritualAPI.isAuthenticated());
    spiritualAPI.trackSpiritualEngagement('satsang_visit');
  }, []);

  const loadSatsangData = async () => {
    try {
      const schedule = await spiritualAPI.getSatsangSchedule();
      if (schedule && schedule.success) {
        setSatsangSchedule(schedule.data || []);
      } else {
        // Fallback data if API is not available
        setSatsangSchedule([
          {
            id: 'next_satsang',
            title: 'Divine Wisdom Gathering',
            theme: 'Finding Inner Peace in Modern Times',
            scheduled_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
            duration: '90 minutes',
            max_participants: 100,
            registered_count: 67,
            description: 'Join our global spiritual community for a transformative session on finding peace amidst life\'s challenges.'
          },
          {
            id: 'monthly_satsang',
            title: 'Monthly Sacred Circle',
            theme: 'The Path of Self-Realization',
            scheduled_date: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(),
            duration: '120 minutes',
            max_participants: 150,
            registered_count: 89,
            description: 'A deeper exploration of spiritual practices and ancient wisdom for modern seekers.'
          }
        ]);
      }
    } catch (error) {
      console.log('Satsang data loading blessed with patience:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const registerForSatsang = async (eventId) => {
    if (!isAuthenticated) {
      window.location.href = '/register?service=satsang';
      return;
    }

    try {
      const result = await spiritualAPI.registerForSatsang(eventId);
      if (result && result.success) {
        setRegisteredEvents(prev => new Set([...prev, eventId]));
        await spiritualAPI.trackSpiritualEngagement('satsang_registration', {
          event_id: eventId
        });
        alert('🙏 Registration successful! You will receive divine reminders before the satsang.');
      } else {
        alert('Registration encountered divine turbulence. Please try again.');
      }
    } catch (error) {
      console.error('Satsang registration blessed with patience:', error);
      alert('Connection to sacred servers temporarily unavailable.');
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      timeZoneName: 'short'
    });
  };

  if (isLoading) {
    return (
      <div className="pt-16 min-h-screen flex items-center justify-center">
        <div className="consciousness-pulse text-center">
          <div className="om-symbol text-6xl">🙏</div>
          <p className="text-white mt-4">Loading sacred gatherings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="pt-16 min-h-screen">
      {/* Header */}
      <div className="bg-gradient-to-r from-orange-500 to-pink-500 py-16">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <Link 
            to="/" 
            className="inline-flex items-center text-white hover:text-gray-200 mb-6 transition-colors"
          >
            <ArrowLeft size={20} className="mr-2" />
            Back to Home
          </Link>
          
          <div className="text-6xl mb-4">🙏</div>
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Monthly Satsang
          </h1>
          <p className="text-xl text-white opacity-90 max-w-2xl mx-auto">
            Join our global spiritual community gatherings for collective wisdom and divine connection
          </p>
        </div>
      </div>

      {/* What is Satsang */}
      <div className="py-16 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-white mb-8">
            <span className="divine-text">What is Satsang?</span>
          </h2>
          <div className="sacred-card p-8 mb-12">
            <p className="text-lg text-gray-700 mb-6">
              Satsang, meaning "gathering with truth," is a sacred practice where spiritual seekers come together 
              to share wisdom, meditate, and experience divine presence collectively. In our digital age, 
              we maintain this ancient tradition through virtual gatherings that connect souls worldwide.
            </p>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-3xl mb-3">🧘</div>
                <h3 className="font-semibold text-gray-800 mb-2">Collective Meditation</h3>
                <p className="text-sm text-gray-600">Experience the power of group meditation and shared spiritual energy</p>
              </div>
              <div className="text-center">
                <div className="text-3xl mb-3">💬</div>
                <h3 className="font-semibold text-gray-800 mb-2">Wisdom Sharing</h3>
                <p className="text-sm text-gray-600">Learn from Swami Jyotirananthan and fellow spiritual seekers</p>
              </div>
              <div className="text-center">
                <div className="text-3xl mb-3">🌍</div>
                <h3 className="font-semibold text-gray-800 mb-2">Global Community</h3>
                <p className="text-sm text-gray-600">Connect with like-minded souls from around the world</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Upcoming Satsangs */}
      <div className="py-16 px-4 bg-gradient-to-br from-purple-900 to-blue-900">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-white mb-12">
            <span className="divine-text">Upcoming Sacred Gatherings</span>
          </h2>
          
          {satsangSchedule.length === 0 ? (
            <div className="text-center sacred-card p-12">
              <div className="text-6xl mb-6">📅</div>
              <h3 className="text-2xl font-bold text-gray-800 mb-4">
                New Satsangs Coming Soon
              </h3>
              <p className="text-gray-600 mb-6">
                We are preparing divine gatherings for our sacred community. 
                Stay connected for announcements of upcoming satsangs.
              </p>
              <button className="divine-button">
                <Bell className="mr-2" size={16} />
                Notify Me of New Satsangs
              </button>
            </div>
          ) : (
            <div className="grid gap-8">
              {satsangSchedule.map((event) => (
                <div key={event.id} className="sacred-card p-8">
                  <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
                    <div className="flex-1 mb-6 lg:mb-0">
                      <div className="flex items-center mb-4">
                        <div className="text-3xl mr-4">🕉️</div>
                        <div>
                          <h3 className="text-2xl font-bold text-gray-800">{event.title}</h3>
                          <p className="text-lg text-gray-600">{event.theme}</p>
                        </div>
                      </div>
                      
                      <div className="grid md:grid-cols-2 gap-4 mb-4">
                        <div className="flex items-center text-gray-600">
                          <Calendar className="mr-2" size={16} />
                          <span>{formatDate(event.scheduled_date)}</span>
                        </div>
                        <div className="flex items-center text-gray-600">
                          <Clock className="mr-2" size={16} />
                          <span>{formatTime(event.scheduled_date)} • {event.duration}</span>
                        </div>
                        <div className="flex items-center text-gray-600">
                          <Users className="mr-2" size={16} />
                          <span>{event.registered_count || 0} / {event.max_participants || 100} registered</span>
                        </div>
                        <div className="flex items-center text-gray-600">
                          <MapPin className="mr-2" size={16} />
                          <span>Virtual Gathering</span>
                        </div>
                      </div>
                      
                      <p className="text-gray-700">{event.description}</p>
                    </div>
                    
                    <div className="lg:ml-8 text-center">
                      {registeredEvents.has(event.id) ? (
                        <div className="bg-green-100 text-green-800 px-6 py-3 rounded-lg font-semibold">
                          ✓ Registered
                        </div>
                      ) : (
                        <button
                          onClick={() => registerForSatsang(event.id)}
                          className="divine-button text-lg px-8 py-3"
                        >
                          Join Sacred Gathering
                        </button>
                      )}
                      
                      <div className="mt-4 text-sm text-gray-500">
                        {event.max_participants && event.registered_count && 
                          `${event.max_participants - event.registered_count} spots remaining`
                        }
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Community Benefits */}
      <div className="py-16 px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-white mb-12">
            <span className="divine-text">Sacred Community Benefits</span>
          </h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="text-center sacred-card p-6">
              <div className="text-4xl mb-4">🌟</div>
              <h3 className="text-lg font-bold text-gray-800 mb-3">Spiritual Growth</h3>
              <p className="text-gray-600 text-sm">
                Accelerate your spiritual journey through collective energy and shared wisdom
              </p>
            </div>
            
            <div className="text-center sacred-card p-6">
              <div className="text-4xl mb-4">🤝</div>
              <h3 className="text-lg font-bold text-gray-800 mb-3">Divine Connections</h3>
              <p className="text-gray-600 text-sm">
                Build meaningful relationships with fellow seekers on the spiritual path
              </p>
            </div>
            
            <div className="text-center sacred-card p-6">
              <div className="text-4xl mb-4">📚</div>
              <h3 className="text-lg font-bold text-gray-800 mb-3">Ancient Wisdom</h3>
              <p className="text-gray-600 text-sm">
                Learn timeless teachings and practices from traditional spiritual texts
              </p>
            </div>
            
            <div className="text-center sacred-card p-6">
              <div className="text-4xl mb-4">🎯</div>
              <h3 className="text-lg font-bold text-gray-800 mb-3">Life Guidance</h3>
              <p className="text-gray-600 text-sm">
                Receive practical guidance for applying spiritual principles in daily life
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Call to Action */}
      {!isAuthenticated && (
        <div className="py-16 bg-gradient-to-r from-yellow-400 to-orange-500">
          <div className="max-w-4xl mx-auto px-4 text-center">
            <h2 className="text-3xl font-bold text-black mb-6">
              Ready to Join Our Sacred Community?
            </h2>
            <p className="text-black text-lg mb-8 opacity-80">
              Create your account to register for satsangs and connect with thousands of spiritual seekers worldwide
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link 
                to="/register"
                className="bg-black text-white hover:bg-gray-800 transition-all duration-300 px-8 py-4 rounded-lg text-lg font-semibold"
              >
                Join Sacred Community
              </Link>
              <Link 
                to="/login"
                className="bg-transparent border-2 border-black text-black hover:bg-black hover:text-white transition-all duration-300 px-8 py-4 rounded-lg text-lg font-semibold"
              >
                Sign In
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Satsang;

