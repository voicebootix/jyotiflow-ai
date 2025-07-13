/**
 * Community Hub Component
 * Provides satsang participation, community features, and social interaction
 */

import React, { useState, useEffect } from 'react';
import { Users, Calendar, MessageCircle, Award, Star, Clock, MapPin, Video, Play, Heart, Share2, Bell } from 'lucide-react';
import { Link } from 'react-router-dom';

const CommunityHub = ({ userProfile, communityData }) => {
  const [activeSection, setActiveSection] = useState('satsang');
  const [upcomingSatsangs, setUpcomingSatsangs] = useState([]);
  const [myParticipation, setMyParticipation] = useState(null);
  const [communityMembers, setCommunityMembers] = useState([]);
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    loadCommunityData();
  }, []);

  const loadCommunityData = async () => {
    // Generate sample data for demonstration
    const sampleSatsangs = [
      {
        id: 1,
        title: 'Divine Wisdom Gathering',
        theme: 'Finding Inner Peace in Modern Times',
        date: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(),
        time: '7:00 PM IST',
        duration: '90 minutes',
        participants: 67,
        maxParticipants: 100,
        type: 'live',
        status: 'upcoming',
        description: 'Join our global spiritual community for a transformative session on finding peace amidst life\'s challenges.',
        swamiji_topic: 'The Path to Eternal Bliss',
        level: 'All Levels',
        language: 'Tamil & English'
      },
      {
        id: 2,
        title: 'Meditation & Mantras',
        theme: 'Sacred Sound Healing',
        date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
        time: '6:00 AM IST',
        duration: '60 minutes',
        participants: 43,
        maxParticipants: 75,
        type: 'meditation',
        status: 'upcoming',
        description: 'Experience the transformative power of sacred mantras and guided meditation.',
        swamiji_topic: 'Mantra Yoga for Spiritual Awakening',
        level: 'Intermediate',
        language: 'Tamil'
      },
      {
        id: 3,
        title: 'Q&A with Swamiji',
        theme: 'Ask Your Spiritual Questions',
        date: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(),
        time: '8:00 PM IST',
        duration: '120 minutes',
        participants: 89,
        maxParticipants: 150,
        type: 'interactive',
        status: 'upcoming',
        description: 'Direct interaction with Swamiji for your spiritual queries and guidance.',
        swamiji_topic: 'Answers from the Heart of Wisdom',
        level: 'All Levels',
        language: 'Tamil & English'
      }
    ];

    const sampleParticipation = {
      total_attended: communityData?.satsang_attended || 5,
      upcoming_registered: 2,
      favorite_themes: ['Meditation', 'Divine Wisdom', 'Spiritual Growth'],
      community_rank: communityData?.community_rank || 'Active Member',
      contribution_score: communityData?.contribution_score || 850,
      badges: ['Regular Attendee', 'Early Bird', 'Question Asker'],
      spiritual_level: 'Growing Seeker'
    };

    const sampleMembers = [
      {
        id: 1,
        name: 'Spiritual Seeker',
        rank: 'Devoted Practitioner',
        sessions: 45,
        joined: '6 months ago',
        location: 'Chennai',
        avatar: '🧘‍♀️'
      },
      {
        id: 2,
        name: 'Divine Soul',
        rank: 'Wisdom Seeker',
        sessions: 32,
        joined: '4 months ago',
        location: 'Mumbai',
        avatar: '🙏'
      },
      {
        id: 3,
        name: 'Peace Walker',
        rank: 'Growing Student',
        sessions: 28,
        joined: '3 months ago',
        location: 'Bangalore',
        avatar: '🕉️'
      }
    ];

    const sampleNotifications = [
      {
        id: 1,
        type: 'satsang_reminder',
        title: 'Satsang Starting Soon',
        message: 'Divine Wisdom Gathering starts in 2 hours. Join the sacred space.',
        time: '2 hours ago',
        read: false
      },
      {
        id: 2,
        type: 'community_milestone',
        title: 'Community Milestone',
        message: 'You\'ve attended 5 satsangs! Unlock the Regular Attendee badge.',
        time: '1 day ago',
        read: false
      },
      {
        id: 3,
        type: 'new_session',
        title: 'New Meditation Session',
        message: 'Special morning meditation session added for this weekend.',
        time: '2 days ago',
        read: true
      }
    ];

    setUpcomingSatsangs(sampleSatsangs);
    setMyParticipation(sampleParticipation);
    setCommunityMembers(sampleMembers);
    setNotifications(sampleNotifications);
  };

  const handleSatsangRegistration = (satsangId) => {
    setUpcomingSatsangs(prev => 
      prev.map(satsang => 
        satsang.id === satsangId 
          ? { ...satsang, participants: satsang.participants + 1, registered: true }
          : satsang
      )
    );
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'live': return <Video className="w-5 h-5" />;
      case 'meditation': return <Heart className="w-5 h-5" />;
      case 'interactive': return <MessageCircle className="w-5 h-5" />;
      default: return <Users className="w-5 h-5" />;
    }
  };

  const getTypeColor = (type) => {
    switch (type) {
      case 'live': return 'bg-red-100 text-red-700';
      case 'meditation': return 'bg-green-100 text-green-700';
      case 'interactive': return 'bg-blue-100 text-blue-700';
      default: return 'bg-purple-100 text-purple-700';
    }
  };

  const sectionTabs = [
    { id: 'satsang', label: 'Satsang Events', icon: Calendar },
    { id: 'participation', label: 'My Journey', icon: Award },
    { id: 'community', label: 'Community', icon: Users },
    { id: 'notifications', label: 'Updates', icon: Bell }
  ];

  return (
    <div className="space-y-8">
      {/* Community Stats Header */}
      <div className="grid md:grid-cols-4 gap-6">
        <div className="sacred-card p-6 text-center bg-gradient-to-br from-orange-50 to-red-50">
          <div className="text-3xl mb-2">🎯</div>
          <div className="text-2xl font-bold text-orange-700">
            {myParticipation?.total_attended || 0}
          </div>
          <div className="text-gray-600">Satsangs Attended</div>
          <div className="text-xs text-orange-600 mt-1">
            {myParticipation?.upcoming_registered || 0} upcoming
          </div>
        </div>

        <div className="sacred-card p-6 text-center bg-gradient-to-br from-blue-50 to-indigo-50">
          <div className="text-3xl mb-2">🏆</div>
          <div className="text-2xl font-bold text-blue-700">
            {myParticipation?.contribution_score || 0}
          </div>
          <div className="text-gray-600">Community Score</div>
          <div className="text-xs text-blue-600 mt-1">
            {myParticipation?.community_rank || 'New Member'}
          </div>
        </div>

        <div className="sacred-card p-6 text-center bg-gradient-to-br from-green-50 to-teal-50">
          <div className="text-3xl mb-2">🎖️</div>
          <div className="text-2xl font-bold text-green-700">
            {myParticipation?.badges?.length || 0}
          </div>
          <div className="text-gray-600">Badges Earned</div>
          <div className="text-xs text-green-600 mt-1">
            {myParticipation?.spiritual_level || 'New Seeker'}
          </div>
        </div>

        <div className="sacred-card p-6 text-center bg-gradient-to-br from-purple-50 to-pink-50">
          <div className="text-3xl mb-2">👥</div>
          <div className="text-2xl font-bold text-purple-700">
            {communityMembers.length}k+
          </div>
          <div className="text-gray-600">Community Size</div>
          <div className="text-xs text-purple-600 mt-1">
            Growing daily
          </div>
        </div>
      </div>

      {/* Section Navigation */}
      <div className="sacred-card p-6">
        <div className="flex flex-wrap gap-2 mb-6">
          {sectionTabs.map(section => (
            <button
              key={section.id}
              onClick={() => setActiveSection(section.id)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all ${
                activeSection === section.id
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <section.icon size={16} />
              <span>{section.label}</span>
              {section.id === 'notifications' && notifications.filter(n => !n.read).length > 0 && (
                <span className="bg-red-500 text-white text-xs rounded-full px-2 py-1">
                  {notifications.filter(n => !n.read).length}
                </span>
              )}
            </button>
          ))}
        </div>

        {/* Section Content */}
        {activeSection === 'satsang' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-xl font-bold text-gray-800">🕉️ Upcoming Satsang Events</h3>
              <Link 
                to="/satsang" 
                className="text-purple-600 hover:text-purple-700 text-sm"
              >
                View All Events →
              </Link>
            </div>

            <div className="grid gap-6">
              {upcomingSatsangs.map(satsang => (
                <div key={satsang.id} className="p-6 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg border border-indigo-200">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h4 className="text-xl font-bold text-gray-800">{satsang.title}</h4>
                        <span className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs ${getTypeColor(satsang.type)}`}>
                          {getTypeIcon(satsang.type)}
                          <span>{satsang.type.charAt(0).toUpperCase() + satsang.type.slice(1)}</span>
                        </span>
                      </div>
                      <p className="text-gray-600 text-lg font-medium mb-1">{satsang.theme}</p>
                      <p className="text-gray-500 text-sm mb-3">{satsang.description}</p>
                      
                      <div className="grid md:grid-cols-2 gap-4 text-sm text-gray-600">
                        <div className="space-y-2">
                          <div className="flex items-center space-x-2">
                            <Calendar className="w-4 h-4" />
                            <span>{formatDate(satsang.date)}</span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Clock className="w-4 h-4" />
                            <span>{satsang.time} ({satsang.duration})</span>
                          </div>
                        </div>
                        <div className="space-y-2">
                          <div className="flex items-center space-x-2">
                            <Users className="w-4 h-4" />
                            <span>{satsang.participants}/{satsang.maxParticipants} participants</span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Star className="w-4 h-4" />
                            <span>{satsang.language} • {satsang.level}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="text-sm text-indigo-700 font-medium">
                      🎭 {satsang.swamiji_topic}
                    </div>
                    <div className="flex space-x-3">
                      <button 
                        onClick={() => handleSatsangRegistration(satsang.id)}
                        disabled={satsang.registered}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                          satsang.registered 
                            ? 'bg-green-100 text-green-700 cursor-not-allowed'
                            : 'bg-purple-600 text-white hover:bg-purple-700'
                        }`}
                      >
                        {satsang.registered ? '✓ Registered' : 'Join Satsang'}
                      </button>
                      <button className="p-2 text-gray-400 hover:text-gray-600">
                        <Share2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="mt-4">
                    <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                      <span>Registration Progress</span>
                      <span>{Math.round((satsang.participants / satsang.maxParticipants) * 100)}% full</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-gradient-to-r from-purple-500 to-indigo-500 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${(satsang.participants / satsang.maxParticipants) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeSection === 'participation' && (
          <div className="space-y-6">
            <h3 className="text-xl font-bold text-gray-800">🏆 Your Community Journey</h3>
            
            {/* Badges Section */}
            <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
              <h4 className="font-semibold text-yellow-800 mb-3">🎖️ Earned Badges</h4>
              <div className="flex flex-wrap gap-2">
                {myParticipation?.badges?.map((badge, index) => (
                  <span key={index} className="px-3 py-1 bg-yellow-100 text-yellow-700 rounded-full text-sm font-medium">
                    {badge}
                  </span>
                ))}
              </div>
            </div>

            {/* Favorite Themes */}
            <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
              <h4 className="font-semibold text-blue-800 mb-3">💙 Favorite Themes</h4>
              <div className="flex flex-wrap gap-2">
                {myParticipation?.favorite_themes?.map((theme, index) => (
                  <span key={index} className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
                    {theme}
                  </span>
                ))}
              </div>
            </div>

            {/* Progress to Next Level */}
            <div className="p-4 bg-green-50 rounded-lg border border-green-200">
              <h4 className="font-semibold text-green-800 mb-3">📈 Progress to Next Level</h4>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Current: {myParticipation?.community_rank}</span>
                  <span>Next: Devoted Member</span>
                </div>
                <div className="w-full bg-green-200 rounded-full h-3">
                  <div className="bg-green-500 h-3 rounded-full" style={{ width: '60%' }}></div>
                </div>
                <p className="text-xs text-green-600">Attend 3 more satsangs to reach the next level</p>
              </div>
            </div>
          </div>
        )}

        {activeSection === 'community' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-xl font-bold text-gray-800">👥 Community Members</h3>
              <span className="text-sm text-gray-500">Connect with fellow seekers</span>
            </div>

            <div className="grid gap-4">
              {communityMembers.map(member => (
                <div key={member.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-4">
                    <div className="text-3xl">{member.avatar}</div>
                    <div>
                      <h4 className="font-semibold text-gray-800">{member.name}</h4>
                      <p className="text-sm text-gray-600">{member.rank} • {member.location}</p>
                      <p className="text-xs text-gray-500">{member.sessions} sessions • Joined {member.joined}</p>
                    </div>
                  </div>
                  <button className="px-4 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors text-sm">
                    Connect
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeSection === 'notifications' && (
          <div className="space-y-6">
            <h3 className="text-xl font-bold text-gray-800">🔔 Community Updates</h3>
            
            <div className="space-y-4">
              {notifications.map(notification => (
                <div 
                  key={notification.id} 
                  className={`p-4 rounded-lg border ${
                    notification.read 
                      ? 'bg-gray-50 border-gray-200' 
                      : 'bg-blue-50 border-blue-200'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className={`font-semibold ${
                        notification.read ? 'text-gray-700' : 'text-blue-800'
                      }`}>
                        {notification.title}
                      </h4>
                      <p className={`text-sm ${
                        notification.read ? 'text-gray-600' : 'text-blue-700'
                      }`}>
                        {notification.message}
                      </p>
                    </div>
                    <span className="text-xs text-gray-500">{notification.time}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CommunityHub;