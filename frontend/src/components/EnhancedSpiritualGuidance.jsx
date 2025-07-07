/**
 * Enhanced Spiritual Guidance Component
 * Integrates RAG system, real-time birth chart generation, and 30-minute comprehensive readings
 */

import { useState, useEffect, useCallback } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, Send, Play, Mail, MessageSquare, Phone, RefreshCw,
  Brain, Star, Zap, Heart, Briefcase, Shield, Calendar, Clock,
  BookOpen, Sparkles, Target, TrendingUp, Eye, Compass
} from 'lucide-react';

import enhancedAPI from '../lib/enhanced-api.js';
import RealTimeBirthChart from './RealTimeBirthChart.jsx';
import PersonalizedRemedies from './PersonalizedRemedies.jsx';

const EnhancedSpiritualGuidance = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  // Enhanced service state
  const [selectedService, setSelectedService] = useState('');
  const [serviceConfiguration, setServiceConfiguration] = useState(null);
  const [knowledgeDomains, setKnowledgeDomains] = useState([]);
  const [personaModes, setPersonaModes] = useState([]);
  const [systemHealth, setSystemHealth] = useState(null);
  
  // Form and guidance state
  const [formData, setFormData] = useState({
    birthDate: '',
    birthTime: '',
    birthLocation: '',
    question: '',
    preferredLanguage: 'tamil_english',
    analysisDepth: 'comprehensive'
  });
  
  const [guidance, setGuidance] = useState(null);
  const [birthChart, setBirthChart] = useState(null);
  const [personalizedRemedies, setPersonalizedRemedies] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [enhancedLoading, setEnhancedLoading] = useState(false);
  
  // Enhanced features state
  const [realTimeUpdates, setRealTimeUpdates] = useState(false);
  const [comprehensiveAnalysis, setComprehensiveAnalysis] = useState(false);
  const [knowledgeEffectiveness, setKnowledgeEffectiveness] = useState(null);
  
  // Service and UI state
  const [services, setServices] = useState([]);
  const [credits, setCredits] = useState(0);
  const [selectedKnowledgeDomains, setSelectedKnowledgeDomains] = useState([]);
  const [selectedPersona, setSelectedPersona] = useState('comprehensive_life_master');
  const [currentSessionId, setCurrentSessionId] = useState(null);
  
  // Initialize enhanced system
  useEffect(() => {
    initializeEnhancedSystem();
    loadEnhancedData();
    
    const serviceFromUrl = searchParams.get('service');
    if (serviceFromUrl) {
      setSelectedService(serviceFromUrl);
    }
  }, [searchParams]);

  const initializeEnhancedSystem = async () => {
    try {
      // Check system health
      const health = await enhancedAPI.getEnhancedSystemHealth();
      setSystemHealth(health);
      
      // Load knowledge domains
      const domains = await enhancedAPI.getKnowledgeDomains();
      setKnowledgeDomains(domains.data || []);
      
      // Load persona modes
      const personas = await enhancedAPI.getPersonaModes();
      setPersonaModes(personas.data || []);
      
      // Load knowledge effectiveness
      const effectiveness = await enhancedAPI.getKnowledgeEffectiveness();
      setKnowledgeEffectiveness(effectiveness.data || null);
      
      // Setup real-time updates if available
      if (realTimeUpdates) {
        setupRealTimeUpdates();
      }
      
    } catch (error) {
      console.error('Enhanced system initialization error:', error);
    }
  };

  const loadEnhancedData = async () => {
    try {
      // Load enhanced services
      const enhancedServices = await enhancedAPI.getEnhancedServices();
      if (enhancedServices.data) {
        setServices(enhancedServices.data);
      }
      
      // Load user credits
      if (enhancedAPI.isAuthenticated()) {
        const creditsData = await enhancedAPI.getCreditBalance();
        if (creditsData && creditsData.success) {
          setCredits(creditsData.data.credits || 0);
        }
      }
      
    } catch (error) {
      console.error('Enhanced data loading error:', error);
    }
  };

  const setupRealTimeUpdates = useCallback(() => {
    const ws = enhancedAPI.subscribeToRealTimeUpdates((data) => {
      switch (data.type) {
        case 'service_update':
          setServices(prev => prev.map(s => 
            s.id === data.service_id ? { ...s, ...data.updates } : s
          ));
          break;
        case 'credit_update':
          setCredits(data.new_balance);
          break;
        case 'knowledge_update':
          setKnowledgeDomains(data.domains);
          break;
        default:
          break;
      }
    });
    
    return () => ws.close();
  }, []);

  const handleEnhancedSubmit = async (e) => {
    e.preventDefault();
    
    if (credits <= 0) {
      alert('⚠️ போதிய கிரெடிட்கள் இல்லை! தயவுசெய்து கிரெடிட்கள் வாங்கி மீண்டும் முயற்சிக்கவும்.');
      return;
    }
    
    setIsLoading(true);
    setEnhancedLoading(true);
    setGuidance(null);
    setBirthChart(null);
    setPersonalizedRemedies(null);

    try {
      // Track enhanced guidance request
      await enhancedAPI.trackSpiritualEngagement('enhanced_guidance_requested', {
        service: selectedService,
        knowledge_domains: selectedKnowledgeDomains,
        persona_mode: selectedPersona,
        analysis_depth: formData.analysisDepth,
        birth_details_provided: !!(formData.birthDate && formData.birthTime && formData.birthLocation)
      });

      // Determine if this is a comprehensive reading
      const isComprehensive = selectedService === 'comprehensive_life_reading_30min';
      
      let guidanceResponse;
      
      if (isComprehensive) {
        // Use comprehensive reading endpoint
        guidanceResponse = await enhancedAPI.requestComprehensiveReading({
          question: formData.question,
          birth_details: {
            date: formData.birthDate,
            time: formData.birthTime,
            location: formData.birthLocation
          },
          preferred_language: formData.preferredLanguage,
          user_context: {
            previous_sessions: currentSessionId ? [currentSessionId] : [],
            spiritual_background: 'seeking_guidance'
          }
        });
      } else {
        // Use enhanced guidance endpoint
        guidanceResponse = await enhancedAPI.getEnhancedGuidance({
          service_type: selectedService,
          question: formData.question,
          birth_details: {
            date: formData.birthDate,
            time: formData.birthTime,
            location: formData.birthLocation
          },
          knowledge_domains: selectedKnowledgeDomains,
          persona_mode: selectedPersona,
          analysis_depth: formData.analysisDepth,
          preferred_language: formData.preferredLanguage
        });
      }

      if (guidanceResponse && guidanceResponse.success) {
        // Set guidance response
        setGuidance(guidanceResponse.data);
        setCurrentSessionId(guidanceResponse.data.session_id);
        
        // Update credits
        if (guidanceResponse.credits_used) {
          setCredits(prev => prev - guidanceResponse.credits_used);
        }
        
        // Generate birth chart if birth details provided
        if (formData.birthDate && formData.birthTime && formData.birthLocation) {
          await generateRealTimeBirthChart();
        }
        
        // Get personalized remedies
        if (guidanceResponse.data.planetary_analysis) {
          await getPersonalizedRemedies(guidanceResponse.data.planetary_analysis);
        }
        
      } else {
        setGuidance({
          guidance: "Enhanced spiritual guidance is temporarily in meditation. Please try again in a few moments.",
          session_id: null,
          fallback_mode: true
        });
      }
      
    } catch (error) {
      console.error('Enhanced guidance error:', error);
      setGuidance({
        guidance: "The enhanced spiritual servers are currently in deep meditation. Please try again shortly.",
        session_id: null,
        error: true
      });
    } finally {
      setIsLoading(false);
      setEnhancedLoading(false);
    }
  };

  const generateRealTimeBirthChart = async () => {
    try {
      const chartResponse = await enhancedAPI.generateBirthChart({
        date: formData.birthDate,
        time: formData.birthTime,
        location: formData.birthLocation
      });
      
      if (chartResponse && chartResponse.success) {
        setBirthChart(chartResponse.data);
      }
    } catch (error) {
      console.error('Birth chart generation error:', error);
    }
  };

  const getPersonalizedRemedies = async (planetaryAnalysis) => {
    try {
      const remediesResponse = await enhancedAPI.getPersonalizedRemedies({
        planetary_analysis: planetaryAnalysis,
        birth_details: {
          date: formData.birthDate,
          time: formData.birthTime,
          location: formData.birthLocation
        },
        user_preferences: {
          remedy_types: ['mantras', 'gemstones', 'charity', 'temple_worship'],
          cultural_context: 'tamil_tradition'
        }
      });
      
      if (remediesResponse && remediesResponse.success) {
        setPersonalizedRemedies(remediesResponse.data);
      }
    } catch (error) {
      console.error('Personalized remedies error:', error);
    }
  };

  const handleKnowledgeDomainToggle = (domain) => {
    setSelectedKnowledgeDomains(prev => 
      prev.includes(domain) 
        ? prev.filter(d => d !== domain)
        : [...prev, domain]
    );
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const getServiceIcon = (serviceType) => {
    const iconMap = {
      'comprehensive_life_reading_30min': <Compass className="w-6 h-6" />,
      'love_relationship_mastery': <Heart className="w-6 h-6" />,
      'business_success_mastery': <Briefcase className="w-6 h-6" />,
      'health_wellness_guidance': <Shield className="w-6 h-6" />,
      'career_advancement': <TrendingUp className="w-6 h-6" />,
      'spiritual_evolution': <Sparkles className="w-6 h-6" />
    };
    return iconMap[serviceType] || <Star className="w-6 h-6" />;
  };

  const getDomainIcon = (domain) => {
    const iconMap = {
      'classical_astrology': <Star className="w-4 h-4" />,
      'tamil_spiritual_literature': <BookOpen className="w-4 h-4" />,
      'relationship_astrology': <Heart className="w-4 h-4" />,
      'career_astrology': <Briefcase className="w-4 h-4" />,
      'health_astrology': <Shield className="w-4 h-4" />,
      'remedial_measures': <Zap className="w-4 h-4" />,
      'world_knowledge': <Eye className="w-4 h-4" />,
      'psychological_integration': <Brain className="w-4 h-4" />
    };
    return iconMap[domain] || <Target className="w-4 h-4" />;
  };

  return (
    <div className="pt-16 min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900">
      {/* Enhanced Header */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 py-16">
        <div className="max-w-6xl mx-auto px-4 text-center">
          <div className="flex items-center justify-between mb-6">
            <Link 
              to="/" 
              className="inline-flex items-center text-white hover:text-gray-200 transition-colors"
            >
              <ArrowLeft size={20} className="mr-2" />
              Back to Home
            </Link>
            
            {/* System Health Indicator */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center text-white">
                <div className={`w-3 h-3 rounded-full mr-2 ${
                  systemHealth?.system_ready ? 'bg-green-400' : 'bg-yellow-400'
                }`}></div>
                <span className="text-sm">
                  {systemHealth?.system_ready ? 'Enhanced System Active' : 'Fallback Mode'}
                </span>
              </div>
              <button
                onClick={loadEnhancedData}
                className="inline-flex items-center text-white hover:text-gray-200 transition-colors"
              >
                <RefreshCw size={16} className="mr-1" />
                Refresh
              </button>
            </div>
          </div>
          
          <div className="text-6xl mb-4">🕉️</div>
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Enhanced Spiritual Guidance
          </h1>
          <p className="text-xl text-white opacity-90 max-w-3xl mx-auto">
            Experience the power of AI-enhanced Vedic wisdom with real-time birth chart generation,
            personalized remedies, and 30-minute comprehensive life readings.
          </p>
          
          {/* Enhanced Features */}
          <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4 max-w-4xl mx-auto">
            <div className="bg-white bg-opacity-10 p-4 rounded-lg backdrop-blur-sm">
              <Brain className="w-8 h-8 text-yellow-300 mx-auto mb-2" />
              <h3 className="text-white font-semibold">RAG-Powered Wisdom</h3>
              <p className="text-white opacity-80 text-sm">
                {knowledgeDomains.length}+ authentic knowledge domains
              </p>
            </div>
            <div className="bg-white bg-opacity-10 p-4 rounded-lg backdrop-blur-sm">
              <Compass className="w-8 h-8 text-blue-300 mx-auto mb-2" />
              <h3 className="text-white font-semibold">Real-Time Birth Charts</h3>
              <p className="text-white opacity-80 text-sm">
                Live astrological calculations
              </p>
            </div>
            <div className="bg-white bg-opacity-10 p-4 rounded-lg backdrop-blur-sm">
              <Clock className="w-8 h-8 text-green-300 mx-auto mb-2" />
              <h3 className="text-white font-semibold">30-Min Comprehensive</h3>
              <p className="text-white opacity-80 text-sm">
                Complete life analysis
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Enhanced Service Selection */}
      <div className="py-8 bg-black bg-opacity-20">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-white mb-6 text-center">
            Choose Your Enhanced Service
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* 30-Minute Comprehensive Reading */}
            <div className="bg-gradient-to-br from-purple-600 to-pink-600 p-6 rounded-lg border-2 border-yellow-400 relative">
              <div className="absolute -top-2 left-1/2 transform -translate-x-1/2 bg-yellow-400 text-black text-xs font-bold px-3 py-1 rounded-full">
                PREMIUM
              </div>
              <div className="text-center">
                <Compass className="w-12 h-12 text-yellow-300 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-white mb-2">
                  30-Minute Comprehensive Reading
                </h3>
                <p className="text-white opacity-90 text-sm mb-4">
                  Complete life analysis with birth chart, predictions, and personalized remedies
                </p>
                <div className="text-2xl font-bold text-yellow-300 mb-2">15 Credits</div>
                <button
                  onClick={() => setSelectedService('comprehensive_life_reading_30min')}
                  className={`w-full py-2 px-4 rounded-lg font-semibold transition-colors ${
                    selectedService === 'comprehensive_life_reading_30min'
                      ? 'bg-yellow-400 text-black'
                      : 'bg-white bg-opacity-20 text-white hover:bg-opacity-30'
                  }`}
                >
                  Select Service
                </button>
              </div>
            </div>
            
            {/* Love & Relationship Mastery */}
            <div className="bg-gradient-to-br from-pink-600 to-red-600 p-6 rounded-lg">
              <div className="text-center">
                <Heart className="w-12 h-12 text-pink-300 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-white mb-2">
                  Love & Relationship Mastery
                </h3>
                <p className="text-white opacity-90 text-sm mb-4">
                  Deep relationship guidance with compatibility analysis
                </p>
                <div className="text-2xl font-bold text-pink-300 mb-2">8 Credits</div>
                <button
                  onClick={() => setSelectedService('love_relationship_mastery')}
                  className={`w-full py-2 px-4 rounded-lg font-semibold transition-colors ${
                    selectedService === 'love_relationship_mastery'
                      ? 'bg-pink-400 text-black'
                      : 'bg-white bg-opacity-20 text-white hover:bg-opacity-30'
                  }`}
                >
                  Select Service
                </button>
              </div>
            </div>
            
            {/* Business Success Mastery */}
            <div className="bg-gradient-to-br from-blue-600 to-indigo-600 p-6 rounded-lg">
              <div className="text-center">
                <Briefcase className="w-12 h-12 text-blue-300 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-white mb-2">
                  Business Success Mastery
                </h3>
                <p className="text-white opacity-90 text-sm mb-4">
                  Career advancement and professional success guidance
                </p>
                <div className="text-2xl font-bold text-blue-300 mb-2">10 Credits</div>
                <button
                  onClick={() => setSelectedService('business_success_mastery')}
                  className={`w-full py-2 px-4 rounded-lg font-semibold transition-colors ${
                    selectedService === 'business_success_mastery'
                      ? 'bg-blue-400 text-black'
                      : 'bg-white bg-opacity-20 text-white hover:bg-opacity-30'
                  }`}
                >
                  Select Service
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Knowledge Domain Selection */}
      {selectedService && (
        <div className="py-8 bg-black bg-opacity-30">
          <div className="max-w-6xl mx-auto px-4">
            <h3 className="text-2xl font-bold text-white mb-6 text-center">
              Select Knowledge Domains
            </h3>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {knowledgeDomains.map(domain => (
                <button
                  key={domain.name}
                  onClick={() => handleKnowledgeDomainToggle(domain.name)}
                  className={`p-4 rounded-lg border-2 transition-all duration-300 ${
                    selectedKnowledgeDomains.includes(domain.name)
                      ? 'border-yellow-400 bg-yellow-400 bg-opacity-20'
                      : 'border-gray-600 bg-gray-800 hover:border-gray-400'
                  }`}
                >
                  <div className="flex items-center justify-center mb-2">
                    {getDomainIcon(domain.name)}
                  </div>
                  <div className="text-white font-semibold text-sm">{domain.display_name}</div>
                  <div className="text-gray-400 text-xs mt-1">
                    {domain.knowledge_count} pieces
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Enhanced Input Form */}
      {selectedService && (
        <div className="py-8 bg-black bg-opacity-40">
          <div className="max-w-4xl mx-auto px-4">
            <div className="bg-gray-900 bg-opacity-80 p-8 rounded-lg backdrop-blur-sm">
              <h3 className="text-2xl font-bold text-white mb-6 text-center">
                Provide Your Details
              </h3>
              
              <form onSubmit={handleEnhancedSubmit} className="space-y-6">
                {/* Birth Details */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-white text-sm font-medium mb-2">
                      Birth Date
                    </label>
                    <input
                      type="date"
                      name="birthDate"
                      value={formData.birthDate}
                      onChange={handleInputChange}
                      className="w-full p-3 bg-gray-800 text-white rounded-lg border border-gray-600 focus:border-purple-500 focus:outline-none"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-white text-sm font-medium mb-2">
                      Birth Time
                    </label>
                    <input
                      type="time"
                      name="birthTime"
                      value={formData.birthTime}
                      onChange={handleInputChange}
                      className="w-full p-3 bg-gray-800 text-white rounded-lg border border-gray-600 focus:border-purple-500 focus:outline-none"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-white text-sm font-medium mb-2">
                      Birth Location
                    </label>
                    <input
                      type="text"
                      name="birthLocation"
                      value={formData.birthLocation}
                      onChange={handleInputChange}
                      placeholder="City, Country"
                      className="w-full p-3 bg-gray-800 text-white rounded-lg border border-gray-600 focus:border-purple-500 focus:outline-none"
                      required
                    />
                  </div>
                </div>
                
                {/* Question */}
                <div>
                  <label className="block text-white text-sm font-medium mb-2">
                    Your Question
                  </label>
                  <textarea
                    name="question"
                    value={formData.question}
                    onChange={handleInputChange}
                    rows={4}
                    placeholder="What would you like to know about your life path?"
                    className="w-full p-3 bg-gray-800 text-white rounded-lg border border-gray-600 focus:border-purple-500 focus:outline-none"
                    required
                  />
                </div>
                
                {/* Enhanced Options */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-white text-sm font-medium mb-2">
                      Preferred Language
                    </label>
                    <select
                      name="preferredLanguage"
                      value={formData.preferredLanguage}
                      onChange={handleInputChange}
                      className="w-full p-3 bg-gray-800 text-white rounded-lg border border-gray-600 focus:border-purple-500 focus:outline-none"
                    >
                      <option value="tamil_english">Tamil + English</option>
                      <option value="english">English</option>
                      <option value="tamil">Tamil</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-white text-sm font-medium mb-2">
                      Analysis Depth
                    </label>
                    <select
                      name="analysisDepth"
                      value={formData.analysisDepth}
                      onChange={handleInputChange}
                      className="w-full p-3 bg-gray-800 text-white rounded-lg border border-gray-600 focus:border-purple-500 focus:outline-none"
                    >
                      <option value="comprehensive">Comprehensive</option>
                      <option value="detailed">Detailed</option>
                      <option value="focused">Focused</option>
                    </select>
                  </div>
                </div>
                
                {/* Submit Button */}
                <div className="text-center">
                  <button
                    type="submit"
                    disabled={isLoading || credits <= 0}
                    className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-3 px-8 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
                  >
                    {isLoading ? (
                      <div className="flex items-center">
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                        Processing Enhanced Guidance...
                      </div>
                    ) : (
                      `Get Enhanced Guidance (${credits} credits available)`
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Enhanced Guidance Results */}
      {guidance && (
        <div className="py-8 bg-black bg-opacity-50">
          <div className="max-w-6xl mx-auto px-4">
            <div className="bg-gray-900 bg-opacity-90 p-8 rounded-lg backdrop-blur-sm">
              <h3 className="text-2xl font-bold text-white mb-6 text-center">
                Your Enhanced Spiritual Guidance
              </h3>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Guidance Content */}
                <div className="bg-gray-800 p-6 rounded-lg">
                  <h4 className="text-xl font-bold text-white mb-4">
                    Divine Guidance
                  </h4>
                  <div className="text-white leading-relaxed">
                    {guidance.guidance}
                  </div>
                  
                  {guidance.knowledge_sources && (
                    <div className="mt-4 p-4 bg-gray-700 rounded-lg">
                      <h5 className="text-sm font-semibold text-yellow-400 mb-2">
                        Knowledge Sources:
                      </h5>
                      <div className="text-xs text-gray-300">
                        {guidance.knowledge_sources.join(', ')}
                      </div>
                    </div>
                  )}
                </div>
                
                {/* Birth Chart */}
                {birthChart && (
                  <div className="bg-gray-800 p-6 rounded-lg">
                    <RealTimeBirthChart chartData={birthChart} />
                  </div>
                )}
              </div>
              
              {/* Personalized Remedies */}
              {personalizedRemedies && (
                <div className="mt-8">
                  <PersonalizedRemedies remedies={personalizedRemedies} />
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedSpiritualGuidance;