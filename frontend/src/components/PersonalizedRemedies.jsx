/**
 * Personalized Remedies Component
 * Displays customized spiritual remedies based on astrological analysis
 */

import { useState, useEffect } from 'react';
import { 
  Sparkles, Heart, Gem, HandHeart, MapPin, 
  Clock, BookOpen, Volume2, Star, Info, 
  Calendar, CheckCircle, Play, Pause
} from 'lucide-react';
import spiritualAPI from '../lib/api';

const PersonalizedRemedies = ({ remedies: propsRemedies }) => {
  const [activeTab, setActiveTab] = useState('mantras');
  const [playingMantra, setPlayingMantra] = useState(null);
  const [completedRemedies, setCompletedRemedies] = useState([]);
  const [remedies, setRemedies] = useState(propsRemedies);
  const [loading, setLoading] = useState(!propsRemedies);
  const [error, setError] = useState('');
  const [birthDetails, setBirthDetails] = useState({
    birth_date: '',
    birth_time: '',
    birth_location: ''
  });
  const [showBirthForm, setShowBirthForm] = useState(false);

  useEffect(() => {
    // If remedies are provided as props, use them
    if (propsRemedies) {
      setRemedies(propsRemedies);
      setLoading(false);
      return;
    }

    // Otherwise, try to load from user profile or show form
    loadUserRemedies();
  }, [propsRemedies]);

  const loadUserRemedies = async () => {
    try {
      setLoading(true);
      setError('');

      // Check if user is authenticated
      if (!spiritualAPI.isAuthenticated()) {
        setShowBirthForm(true);
        setLoading(false);
        return;
      }

      // Try to get user profile first to see if we have birth details
      const profileResponse = await spiritualAPI.getUserProfile();
      if (profileResponse.success && profileResponse.data?.birth_details) {
        // Generate remedies using profile data
        const remediesResponse = await generateRemedies(profileResponse.data.birth_details);
        if (remediesResponse.success) {
          setRemedies(remediesResponse.data);
        } else {
          setError('Unable to generate remedies. Please try again.');
        }
      } else {
        // Show form to collect birth details
        setShowBirthForm(true);
      }
    } catch (error) {
      console.error('Error loading remedies:', error);
      setError('Failed to load remedies. Please try again.');
      setShowBirthForm(true);
    } finally {
      setLoading(false);
    }
  };

  const generateRemedies = async (birthDetailsData) => {
    try {
      const response = await spiritualAPI.getPersonalizedRemedies(birthDetailsData);
      return response;
    } catch (error) {
      console.error('Error generating remedies:', error);
      return { success: false, message: error.message };
    }
  };

  const handleBirthFormSubmit = async (e) => {
    e.preventDefault();
    if (!birthDetails.birth_date || !birthDetails.birth_time || !birthDetails.birth_location) {
      setError('Please fill in all birth details.');
      return;
    }

    setLoading(true);
    setError('');

    const remediesResponse = await generateRemedies(birthDetails);
    if (remediesResponse.success) {
      setRemedies(remediesResponse.data);
      setShowBirthForm(false);
    } else {
      setError(remediesResponse.message || 'Failed to generate remedies.');
    }
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen pt-20 px-4">
        <div className="max-w-md mx-auto text-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-500 mx-auto mb-4"></div>
          <p className="text-white">Preparing your personalized remedies...</p>
        </div>
      </div>
    );
  }

  if (showBirthForm) {
    return (
      <div className="min-h-screen pt-20 px-4">
        <div className="max-w-md mx-auto p-6 bg-gradient-to-br from-purple-900/50 to-blue-900/50 rounded-lg border border-purple-500">
          <h3 className="text-xl font-bold text-white mb-4 text-center flex items-center justify-center">
            <Sparkles className="w-5 h-5 mr-2" />
            Generate Your Personalized Remedies
          </h3>
        
        <form onSubmit={handleBirthFormSubmit} className="space-y-4">
          <div>
            <label className="block text-purple-300 text-sm font-medium mb-1">Birth Date</label>
            <input
              type="date"
              value={birthDetails.birth_date}
              onChange={(e) => setBirthDetails(prev => ({ ...prev, birth_date: e.target.value }))}
              className="w-full px-3 py-2 bg-gray-800 text-white rounded-lg border border-gray-600 focus:border-purple-500 focus:outline-none"
              required
            />
          </div>
          
          <div>
            <label className="block text-purple-300 text-sm font-medium mb-1">Birth Time</label>
            <input
              type="time"
              value={birthDetails.birth_time}
              onChange={(e) => setBirthDetails(prev => ({ ...prev, birth_time: e.target.value }))}
              className="w-full px-3 py-2 bg-gray-800 text-white rounded-lg border border-gray-600 focus:border-purple-500 focus:outline-none"
              required
            />
          </div>
          
          <div>
            <label className="block text-purple-300 text-sm font-medium mb-1">Birth Location</label>
            <input
              type="text"
              value={birthDetails.birth_location}
              onChange={(e) => setBirthDetails(prev => ({ ...prev, birth_location: e.target.value }))}
              placeholder="City, Country"
              className="w-full px-3 py-2 bg-gray-800 text-white rounded-lg border border-gray-600 focus:border-purple-500 focus:outline-none"
              required
            />
          </div>
          
          {error && (
            <p className="text-red-400 text-sm">{error}</p>
          )}
          
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-4 rounded-lg transition-colors disabled:opacity-50"
          >
            {loading ? 'Generating...' : 'Generate Remedies'}
          </button>
        </form>
        </div>
      </div>
    );
  }

  if (!remedies) {
    return (
      <div className="min-h-screen pt-20 px-4">
        <div className="max-w-md mx-auto text-center py-8">
          <p className="text-white mb-4">No remedies available. Please try generating them again.</p>
          <button
            onClick={() => setShowBirthForm(true)}
            className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Generate Remedies
          </button>
        </div>
      </div>
    );
  }

  const { mantras, gemstones, charity, temple_worship, general_guidance } = remedies;

  const toggleMantraPlay = (mantraId) => {
    if (playingMantra === mantraId) {
      setPlayingMantra(null);
    } else {
      setPlayingMantra(mantraId);
      // In a real app, you would integrate with an audio player here
    }
  };

  const markRemedyCompleted = (remedyId) => {
    setCompletedRemedies(prev => 
      prev.includes(remedyId) 
        ? prev.filter(id => id !== remedyId)
        : [...prev, remedyId]
    );
  };

  const renderMantras = () => {
    if (!mantras || mantras.length === 0) {
      return <div className="text-gray-400 text-center">No specific mantras recommended at this time.</div>;
    }

    return (
      <div className="space-y-6">
        {mantras.map((mantra, index) => (
          <div key={index} className="bg-gradient-to-r from-yellow-900 to-orange-900 bg-opacity-50 p-6 rounded-lg border border-yellow-600">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-xl font-bold text-yellow-300 flex items-center">
                <Sparkles className="w-5 h-5 mr-2" />
                {mantra.name}
              </h4>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => toggleMantraPlay(index)}
                  className="bg-yellow-600 hover:bg-yellow-700 text-white p-2 rounded-full transition-colors"
                  title={playingMantra === index ? 'Pause' : 'Play Audio Guide'}
                >
                  {playingMantra === index ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                </button>
                <button
                  onClick={() => markRemedyCompleted(`mantra_${index}`)}
                  className={`p-2 rounded-full transition-colors ${
                    completedRemedies.includes(`mantra_${index}`)
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-600 hover:bg-gray-700 text-gray-300'
                  }`}
                  title="Mark as completed"
                >
                  <CheckCircle className="w-4 h-4" />
                </button>
              </div>
            </div>
            
            {/* Sanskrit Text */}
            <div className="bg-black bg-opacity-30 p-4 rounded-lg mb-4">
              <div className="text-yellow-200 text-lg font-semibold mb-2 text-center">
                {mantra.sanskrit}
              </div>
              <div className="text-yellow-100 text-sm text-center italic">
                {mantra.transliteration}
              </div>
            </div>
            
            {/* Meaning and Benefits */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <h5 className="text-yellow-300 font-semibold mb-2">Meaning:</h5>
                <p className="text-gray-300 text-sm">{mantra.meaning}</p>
              </div>
              <div>
                <h5 className="text-yellow-300 font-semibold mb-2">Benefits:</h5>
                <p className="text-gray-300 text-sm">{mantra.benefits}</p>
              </div>
            </div>
            
            {/* Practice Instructions */}
            <div className="bg-yellow-900 bg-opacity-30 p-4 rounded-lg">
              <h5 className="text-yellow-300 font-semibold mb-2 flex items-center">
                <Clock className="w-4 h-4 mr-2" />
                Practice Instructions:
              </h5>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="text-yellow-400 font-medium">Repetitions:</span>
                  <div className="text-gray-300">{mantra.repetitions}</div>
                </div>
                <div>
                  <span className="text-yellow-400 font-medium">Best Time:</span>
                  <div className="text-gray-300">{mantra.best_time}</div>
                </div>
                <div>
                  <span className="text-yellow-400 font-medium">Duration:</span>
                  <div className="text-gray-300">{mantra.duration}</div>
                </div>
              </div>
              {mantra.special_instructions && (
                <div className="mt-3 p-3 bg-yellow-800 bg-opacity-40 rounded">
                  <div className="text-yellow-300 text-sm font-medium mb-1">Special Instructions:</div>
                  <div className="text-gray-300 text-sm">{mantra.special_instructions}</div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderGemstones = () => {
    if (!gemstones || gemstones.length === 0) {
      return <div className="text-gray-400 text-center">No specific gemstones recommended at this time.</div>;
    }

    return (
      <div className="space-y-6">
        {gemstones.map((gemstone, index) => (
          <div key={index} className="bg-gradient-to-r from-purple-900 to-indigo-900 bg-opacity-50 p-6 rounded-lg border border-purple-600">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-xl font-bold text-purple-300 flex items-center">
                <Gem className="w-5 h-5 mr-2" />
                {gemstone.name}
              </h4>
              <button
                onClick={() => markRemedyCompleted(`gemstone_${index}`)}
                className={`p-2 rounded-full transition-colors ${
                  completedRemedies.includes(`gemstone_${index}`)
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-600 hover:bg-gray-700 text-gray-300'
                }`}
                title="Mark as acquired"
              >
                <CheckCircle className="w-4 h-4" />
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Gemstone Details */}
              <div>
                <div className="space-y-3">
                  <div>
                    <span className="text-purple-400 font-medium">Planet:</span>
                    <div className="text-gray-300">{gemstone.planet}</div>
                  </div>
                  <div>
                    <span className="text-purple-400 font-medium">Benefits:</span>
                    <div className="text-gray-300 text-sm">{gemstone.benefits}</div>
                  </div>
                  <div>
                    <span className="text-purple-400 font-medium">Weight Range:</span>
                    <div className="text-gray-300">{gemstone.weight_range}</div>
                  </div>
                  <div>
                    <span className="text-purple-400 font-medium">Metal Setting:</span>
                    <div className="text-gray-300">{gemstone.metal}</div>
                  </div>
                  <div>
                    <span className="text-purple-400 font-medium">Finger/Position:</span>
                    <div className="text-gray-300">{gemstone.wearing_position}</div>
                  </div>
                </div>
              </div>
              
              {/* Quality Guidelines */}
              <div>
                <h5 className="text-purple-300 font-semibold mb-3">Quality Guidelines:</h5>
                <div className="space-y-2 text-sm">
                  {gemstone.quality_guidelines?.map((guideline, idx) => (
                    <div key={idx} className="flex items-start">
                      <Star className="w-3 h-3 text-purple-400 mt-1 mr-2 flex-shrink-0" />
                      <span className="text-gray-300">{guideline}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            
            {/* Energization Instructions */}
            <div className="mt-4 bg-purple-900 bg-opacity-30 p-4 rounded-lg">
              <h5 className="text-purple-300 font-semibold mb-2">Energization Process:</h5>
              <div className="text-gray-300 text-sm space-y-2">
                {gemstone.energization_process?.map((step, idx) => (
                  <div key={idx} className="flex items-start">
                    <span className="text-purple-400 font-medium mr-2">{idx + 1}.</span>
                    <span>{step}</span>
                  </div>
                ))}
              </div>
            </div>
            
            {/* Best Day to Wear */}
            {gemstone.best_day && (
              <div className="mt-3 p-3 bg-purple-800 bg-opacity-40 rounded">
                <span className="text-purple-300 font-medium">Best Day to Start Wearing:</span>
                <div className="text-gray-300">{gemstone.best_day}</div>
              </div>
            )}
          </div>
        ))}
      </div>
    );
  };

  const renderCharity = () => {
    if (!charity || charity.length === 0) {
      return <div className="text-gray-400 text-center">No specific charity recommendations at this time.</div>;
    }

    return (
      <div className="space-y-6">
        {charity.map((charityItem, index) => (
          <div key={index} className="bg-gradient-to-r from-green-900 to-teal-900 bg-opacity-50 p-6 rounded-lg border border-green-600">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-xl font-bold text-green-300 flex items-center">
                <HandHeart className="w-5 h-5 mr-2" />
                {charityItem.name}
              </h4>
              <button
                onClick={() => markRemedyCompleted(`charity_${index}`)}
                className={`p-2 rounded-full transition-colors ${
                  completedRemedies.includes(`charity_${index}`)
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-600 hover:bg-gray-700 text-gray-300'
                }`}
                title="Mark as completed"
              >
                <CheckCircle className="w-4 h-4" />
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <div className="space-y-3">
                  <div>
                    <span className="text-green-400 font-medium">Purpose:</span>
                    <div className="text-gray-300 text-sm">{charityItem.purpose}</div>
                  </div>
                  <div>
                    <span className="text-green-400 font-medium">Suggested Amount:</span>
                    <div className="text-gray-300">{charityItem.suggested_amount}</div>
                  </div>
                  <div>
                    <span className="text-green-400 font-medium">Best Day:</span>
                    <div className="text-gray-300">{charityItem.best_day}</div>
                  </div>
                  <div>
                    <span className="text-green-400 font-medium">Planet Benefited:</span>
                    <div className="text-gray-300">{charityItem.planet}</div>
                  </div>
                </div>
              </div>
              
              <div>
                <h5 className="text-green-300 font-semibold mb-3">Specific Items to Donate:</h5>
                <div className="space-y-1">
                  {charityItem.items?.map((item, idx) => (
                    <div key={idx} className="flex items-center">
                      <Heart className="w-3 h-3 text-green-400 mr-2" />
                      <span className="text-gray-300 text-sm">{item}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            
            {charityItem.spiritual_significance && (
              <div className="mt-4 bg-green-900 bg-opacity-30 p-4 rounded-lg">
                <h5 className="text-green-300 font-semibold mb-2">Spiritual Significance:</h5>
                <p className="text-gray-300 text-sm">{charityItem.spiritual_significance}</p>
              </div>
            )}
          </div>
        ))}
      </div>
    );
  };

  const renderTempleWorship = () => {
    if (!temple_worship || temple_worship.length === 0) {
      return <div className="text-gray-400 text-center">No specific temple worship recommendations at this time.</div>;
    }

    return (
      <div className="space-y-6">
        {temple_worship.map((temple, index) => (
          <div key={index} className="bg-gradient-to-r from-orange-900 to-red-900 bg-opacity-50 p-6 rounded-lg border border-orange-600">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-xl font-bold text-orange-300 flex items-center">
                <MapPin className="w-5 h-5 mr-2" />
                {temple.deity} Temple Visit
              </h4>
              <button
                onClick={() => markRemedyCompleted(`temple_${index}`)}
                className={`p-2 rounded-full transition-colors ${
                  completedRemedies.includes(`temple_${index}`)
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-600 hover:bg-gray-700 text-gray-300'
                }`}
                title="Mark as completed"
              >
                <CheckCircle className="w-4 h-4" />
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <div className="space-y-3">
                  <div>
                    <span className="text-orange-400 font-medium">Deity:</span>
                    <div className="text-gray-300">{temple.deity}</div>
                  </div>
                  <div>
                    <span className="text-orange-400 font-medium">Purpose:</span>
                    <div className="text-gray-300 text-sm">{temple.purpose}</div>
                  </div>
                  <div>
                    <span className="text-orange-400 font-medium">Best Days:</span>
                    <div className="text-gray-300">{temple.best_days}</div>
                  </div>
                  <div>
                    <span className="text-orange-400 font-medium">Best Time:</span>
                    <div className="text-gray-300">{temple.best_time}</div>
                  </div>
                </div>
              </div>
              
              <div>
                <h5 className="text-orange-300 font-semibold mb-3">Offerings to Make:</h5>
                <div className="space-y-1">
                  {temple.offerings?.map((offering, idx) => (
                    <div key={idx} className="flex items-center">
                      <Star className="w-3 h-3 text-orange-400 mr-2" />
                      <span className="text-gray-300 text-sm">{offering}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            
            {/* Special Prayers */}
            {temple.special_prayers && (
              <div className="mt-4 bg-orange-900 bg-opacity-30 p-4 rounded-lg">
                <h5 className="text-orange-300 font-semibold mb-2">Special Prayers:</h5>
                <div className="space-y-2">
                  {temple.special_prayers.map((prayer, idx) => (
                    <div key={idx} className="text-gray-300 text-sm">
                      <span className="text-orange-400 font-medium">{prayer.name}:</span> {prayer.description}
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Recommended Temples */}
            {temple.recommended_temples && (
              <div className="mt-4 bg-orange-800 bg-opacity-40 p-4 rounded-lg">
                <h5 className="text-orange-300 font-semibold mb-2">Recommended Temples:</h5>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {temple.recommended_temples.map((templeLocation, idx) => (
                    <div key={idx} className="text-gray-300 text-sm">
                      <MapPin className="w-3 h-3 inline mr-1" />
                      {templeLocation}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    );
  };

  const tabs = [
    { key: 'mantras', label: 'Mantras', icon: <Volume2 className="w-4 h-4" />, count: mantras?.length || 0 },
    { key: 'gemstones', label: 'Gemstones', icon: <Gem className="w-4 h-4" />, count: gemstones?.length || 0 },
    { key: 'charity', label: 'Charity', icon: <HandHeart className="w-4 h-4" />, count: charity?.length || 0 },
    { key: 'temples', label: 'Temple Worship', icon: <MapPin className="w-4 h-4" />, count: temple_worship?.length || 0 }
  ];

  return (
    <div className="min-h-screen pt-20 px-4">
      <div className="max-w-6xl mx-auto">
        <h3 className="text-2xl font-bold text-white mb-6 text-center flex items-center justify-center">
          <Sparkles className="w-6 h-6 mr-2" />
          Your Personalized Remedies
        </h3>
      
      {/* General Guidance */}
      {general_guidance && (
        <div className="mb-6 bg-gradient-to-r from-purple-900 to-blue-900 bg-opacity-50 p-6 rounded-lg border border-purple-500">
          <h4 className="text-lg font-semibold text-purple-300 mb-3 flex items-center">
            <Info className="w-5 h-5 mr-2" />
            General Guidance
          </h4>
          <p className="text-gray-300 leading-relaxed">{general_guidance}</p>
        </div>
      )}
      
      {/* Tab Navigation */}
      <div className="flex flex-wrap gap-2 mb-6">
        {tabs.map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`flex items-center px-4 py-2 rounded-lg text-sm transition-colors ${
              activeTab === tab.key
                ? 'bg-purple-600 text-white'
                : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
            }`}
          >
            {tab.icon}
            <span className="ml-2">{tab.label}</span>
            {tab.count > 0 && (
              <span className="ml-2 bg-purple-500 text-white text-xs px-2 py-1 rounded-full">
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>
      
      {/* Tab Content */}
      <div className="min-h-96">
        {activeTab === 'mantras' && renderMantras()}
        {activeTab === 'gemstones' && renderGemstones()}
        {activeTab === 'charity' && renderCharity()}
        {activeTab === 'temples' && renderTempleWorship()}
      </div>
      
      {/* Progress Tracker */}
      {completedRemedies.length > 0 && (
        <div className="mt-8 bg-green-900 bg-opacity-20 p-4 rounded-lg border border-green-600">
          <h4 className="text-green-300 font-semibold mb-2 flex items-center">
            <CheckCircle className="w-5 h-5 mr-2" />
            Your Progress
          </h4>
          <p className="text-gray-300">
            You have completed {completedRemedies.length} remedial practices. 
            Keep up the excellent spiritual discipline! 🙏
          </p>
        </div>
      )}
      </div>
    </div>
  );
};

export default PersonalizedRemedies;