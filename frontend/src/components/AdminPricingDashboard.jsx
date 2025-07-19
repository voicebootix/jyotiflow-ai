/**
 * Admin Pricing Dashboard Component (Integrated)
 * Comprehensive reading dynamic pricing management - integrated into existing admin dashboard
 */

import React, { useState, useEffect } from 'react';
import { 
  DollarSign, TrendingUp, AlertTriangle, CheckCircle, 
  Clock, Target, BarChart3, Settings, Zap, Users,
  Heart, Video, Mic, MessageCircle, Gift, Calendar
} from 'lucide-react';
import { getProkeralaEndpoints } from '../config/prokeralaEndpoints';
import spiritualAPI from '../lib/api';

const AdminPricingDashboard = () => {
  const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://jyotiflow-ai.onrender.com';
  const [pricingData, setPricingData] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [satsangEvents, setSatsangEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('recommendations');
  const [apiStatus, setApiStatus] = useState({});
  const [welcomeCredits, setWelcomeCredits] = useState(20);
  const [updatingCredits, setUpdatingCredits] = useState(false);
  const [prokeralaCosts, setProkeralaCosts] = useState({});
  const [prokeralaConfig, setProkeralaConfig] = useState(null);
  const [services, setServices] = useState(null);
  const [showEndpointModal, setShowEndpointModal] = useState(false);
  const [modalService, setModalService] = useState(null);
  const [modalEndpoints, setModalEndpoints] = useState([]);
  const [modalCacheEffectiveness, setModalCacheEffectiveness] = useState(70);
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState(''); // 'success' or 'error'

  useEffect(() => {
    fetchPricingDashboard();
    fetchSatsangEvents();
    fetchWelcomeCredits();
  }, []);

  const fetchPricingDashboard = async () => {
    try {
      setLoading(true);
      
      // Fetch smart pricing recommendations
      const response = await fetch(`${API_BASE_URL}/api/spiritual/enhanced/pricing/smart-recommendations`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.recommendations) {
        setRecommendations(data.recommendations);
        setApiStatus(data.api_status || {});
        setPricingData({
          total_services: data.total_services,
          dynamic_services: data.dynamic_services,
          high_priority: data.high_priority
        });
      }
    } catch (error) {
      console.error('Error fetching pricing dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSatsangEvents = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/spiritual/enhanced/satsang/events`);
      const data = await response.json();
      setSatsangEvents(data.events || []);
    } catch (error) {
      console.error('Error fetching Satsang events:', error);
    }
  };

  const fetchWelcomeCredits = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/pricing/welcome-credits`);
      const data = await response.json();
      if (data.success) {
        setWelcomeCredits(data.welcome_credits);
      }
    } catch (error) {
      console.error('Error fetching welcome credits:', error);
    }
  };

  const updateWelcomeCredits = async () => {
    setUpdatingCredits(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/pricing/welcome-credits`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ welcome_credits: welcomeCredits })
      });
      
      if (response.ok) {
        alert('Welcome credits updated successfully!');
      } else {
        alert('Failed to update welcome credits');
      }
    } catch (error) {
      console.error('Error updating welcome credits:', error);
      alert('Error updating welcome credits');
    } finally {
      setUpdatingCredits(false);
    }
  };

  const applyPricingRecommendation = async (recommendation, adminNotes = '') => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/spiritual/enhanced/pricing/apply`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          service_name: recommendation.service_name,
          approved_price: recommendation.recommended_price,
          admin_notes: adminNotes
        })
      });
      
      if (response.ok) {
        showToast(`Price updated for ${recommendation.display_name}`, 'success');
        fetchPricingDashboard();
      }
    } catch (error) {
      console.error('Error applying pricing:', error);
    }
  };

  const createSatsangEvent = async (eventData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/spiritual/enhanced/satsang/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(eventData)
      });
      
      if (response.ok) {
        showToast('Satsang event created successfully', 'success');
        fetchSatsangEvents();
      }
    } catch (error) {
      console.error('Error creating Satsang:', error);
    }
  };

  const loadProkeralaCosts = async (serviceId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/products/pricing/prokerala-cost/${serviceId}`);
      const data = await response.json();
      if (data.success) {
        setProkeralaCosts(prev => ({
          ...prev,
          [serviceId]: data.data
        }));
      }
    } catch (error) {
      console.error('Error loading Prokerala costs:', error);
    }
  };

  const loadProkeralaConfig = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/products/pricing/prokerala-config`);
      const data = await response.json();
      if (data.success) {
        setProkeralaConfig(data.data);
      }
    } catch (error) {
      console.error('Error loading Prokerala config:', error);
    }
  };

  const updateProkeralaConfig = async (config) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/products/pricing/update-prokerala-config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });
      
      if (response.ok) {
        showToast('Prokerala configuration updated successfully', 'success');
        loadProkeralaConfig();
      }
    } catch (error) {
      console.error('Error updating Prokerala config:', error);
    }
  };

  const loadServicesForConfiguration = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/products/service-types`);
      const data = await response.json();
      if (response.ok) {
        setServices(data);
      }
    } catch (error) {
      console.error('Error loading services:', error);
    }
  };

  const configureServiceEndpoints = (serviceId) => {
    const service = services.find(s => s.id === serviceId);
    if (!service) return;

    setModalService(service);
    setModalEndpoints(service.prokerala_endpoints || []);
    setModalCacheEffectiveness(service.cache_effectiveness || 70);
    setShowEndpointModal(true);
  };

  const saveEndpointConfiguration = async () => {
    if (!modalService) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/products/service-types/${modalService.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...modalService,
          prokerala_endpoints: modalEndpoints,
          estimated_api_calls: modalEndpoints.length,
          cache_effectiveness: modalCacheEffectiveness
        })
      });

      if (response.ok) {
        showToast('Service configuration updated successfully', 'success');
        loadServicesForConfiguration();
        setShowEndpointModal(false);
      }
    } catch (error) {
      console.error('Error updating service:', error);
    }
  };

  const handleEndpointToggle = (endpoint) => {
    setModalEndpoints(prev => 
      prev.includes(endpoint) 
        ? prev.filter(e => e !== endpoint)
        : [...prev, endpoint]
    );
  };

  const showToast = (message, type = 'success') => {
    setToastMessage(message);
    setToastType(type);
    setTimeout(() => {
      setToastMessage('');
      setToastType('');
    }, 3000);
  };

  const getUrgencyColor = (urgency) => {
    switch (urgency) {
      case 'high': return 'text-red-600 bg-red-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getApiStatusColor = (status) => {
    return status ? 'text-green-600' : 'text-red-600';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Universal Pricing Dashboard</h2>
          <p className="text-gray-600">Smart pricing for all services with real API cost calculations</p>
        </div>
        <button
          onClick={fetchPricingDashboard}
          className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors flex items-center space-x-2"
        >
          <Zap size={16} />
          <span>Refresh Data</span>
        </button>
      </div>

      {/* API Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">ElevenLabs API</p>
              <p className={`text-lg font-semibold ${getApiStatusColor(apiStatus.elevenlabs)}`}>
                {apiStatus.elevenlabs ? 'Connected' : 'Not Connected'}
              </p>
            </div>
            <Mic className={getApiStatusColor(apiStatus.elevenlabs)} size={20} />
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">D-ID Video API</p>
              <p className={`text-lg font-semibold ${getApiStatusColor(apiStatus.d_id)}`}>
                {apiStatus.d_id ? 'Connected' : 'Not Connected'}
              </p>
            </div>
            <Video className={getApiStatusColor(apiStatus.d_id)} size={20} />
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Agora Interactive</p>
              <p className={`text-lg font-semibold ${getApiStatusColor(apiStatus.agora)}`}>
                {apiStatus.agora ? 'Connected' : 'Not Connected'}
              </p>
            </div>
            <Users className={getApiStatusColor(apiStatus.agora)} size={20} />
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">OpenAI API</p>
              <p className={`text-lg font-semibold ${getApiStatusColor(apiStatus.openai)}`}>
                {apiStatus.openai ? 'Connected' : 'Not Connected'}
              </p>
            </div>
            <Zap className={getApiStatusColor(apiStatus.openai)} size={20} />
          </div>
        </div>
      </div>

      {/* Welcome Credits Configuration */}
      <div className="bg-white p-6 rounded-lg shadow border mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Welcome Credits Configuration</h3>
            <p className="text-sm text-gray-600">Set the number of credits given to new users upon registration</p>
          </div>
          <Gift className="text-purple-600" size={24} />
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Welcome Credits for New Users
            </label>
            <input
              type="number"
              min="0"
              max="1000"
              value={welcomeCredits}
              onChange={(e) => setWelcomeCredits(parseInt(e.target.value) || 0)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Enter number of credits"
            />
          </div>
          <button
            onClick={updateWelcomeCredits}
            disabled={updatingCredits}
            className="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 flex items-center space-x-2"
          >
            {updatingCredits ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Updating...</span>
              </>
            ) : (
              <>
                <CheckCircle size={16} />
                <span>Update</span>
              </>
            )}
          </button>
        </div>
        
        <div className="mt-3 text-sm text-gray-500">
          <p>💡 Tip: This affects all new user registrations. Consider your business strategy when setting this value.</p>
        </div>
      </div>

      {/* Statistics Cards */}
      {pricingData && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Services</p>
                <p className="text-2xl font-bold text-gray-900">{pricingData.total_services}</p>
              </div>
              <Target className="text-blue-600" size={24} />
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Dynamic Pricing Enabled</p>
                <p className="text-2xl font-bold text-purple-600">{pricingData.dynamic_services}</p>
              </div>
              <TrendingUp className="text-purple-600" size={24} />
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">High Priority Changes</p>
                <p className="text-2xl font-bold text-red-600">{pricingData.high_priority}</p>
              </div>
              <AlertTriangle className="text-red-600" size={24} />
            </div>
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('recommendations')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'recommendations'
                ? 'border-purple-500 text-purple-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <TrendingUp className="inline mr-2" size={16} />
            Pricing Recommendations
          </button>
          <button
            onClick={() => setActiveTab('satsang')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'satsang'
                ? 'border-purple-500 text-purple-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <Heart className="inline mr-2" size={16} />
            Satsang Management
          </button>
          <button
            onClick={() => setActiveTab('analytics')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'analytics'
                ? 'border-purple-500 text-purple-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <BarChart3 className="inline mr-2" size={16} />
            Cost Analytics
          </button>
          <button
            onClick={() => setActiveTab('prokerala')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'prokerala'
                ? 'border-purple-500 text-purple-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <DollarSign className="inline mr-2" size={16} />
            Prokerala Costs
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'recommendations' && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">Smart Pricing Recommendations</h3>
          {recommendations.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No pricing recommendations available
            </div>
          ) : (
            <div className="space-y-4">
              {recommendations?.map((rec, index) => (
                <div key={index} className="bg-white p-6 rounded-lg shadow border">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h4 className="text-lg font-semibold text-gray-900">{rec.display_name}</h4>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getUrgencyColor(rec.urgency)}`}>
                          {rec.urgency.toUpperCase()}
                        </span>
                        <span className="text-sm text-gray-500">
                          Confidence: {(rec.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                        <div>
                          <p className="text-sm text-gray-600">Current Price</p>
                          <p className="text-xl font-bold text-gray-900">{rec.current_price} credits</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Recommended Price</p>
                          <p className="text-xl font-bold text-purple-600">{rec.recommended_price} credits</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Price Change</p>
                          <p className={`text-xl font-bold ${rec.price_difference >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {rec.price_difference > 0 ? '+' : ''}{rec.price_difference.toFixed(1)} credits
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">API Costs</p>
                          <p className="text-sm text-gray-900">
                            {rec.cost_breakdown?.total_api_cost?.toFixed(1) || 'N/A'} credits
                          </p>
                        </div>
                      </div>
                      
                      <p className="text-sm text-gray-600 mb-4">{rec.rationale}</p>
                      
                      {rec.cost_breakdown && (
                        <div className="bg-gray-50 p-3 rounded-lg mb-4">
                          <p className="text-sm font-medium text-gray-700 mb-2">Cost Breakdown:</p>
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                            {Object.entries(rec.cost_breakdown)
                              .filter(([key]) => key.includes('_cost') || key.includes('_api'))
                              .map(([key, value]) => (
                                <div key={key}>
                                  <span className="text-gray-600 capitalize">
                                    {key.replace(/_/g, ' ').replace('cost', '').replace('api', '')}:
                                  </span>
                                  <span className="font-medium ml-1">{value?.toFixed(1) || 0}</span>
                                </div>
                              ))}
                          </div>
                        </div>
                      )}
                    </div>
                    
                    <div className="ml-4">
                      <button
                        onClick={() => {
                          const notes = prompt(`Admin notes for ${rec.display_name} pricing change:`);
                          if (notes !== null) {
                            applyPricingRecommendation(rec, notes);
                          }
                        }}
                        className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors flex items-center space-x-2"
                      >
                        <CheckCircle size={16} />
                        <span>Apply</span>
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'satsang' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold text-gray-900">Satsang Event Management</h3>
            <button
              onClick={() => {
                const title = prompt('Satsang Event Title:');
                const duration = prompt('Duration (minutes):', '90');
                const theme = prompt('Theme/Topic:');
                if (title && duration && theme) {
                  createSatsangEvent({
                    title,
                    duration_minutes: parseInt(duration),
                    theme,
                    event_type: 'community',
                    has_donations: true,
                    interactive_level: 'basic'
                  });
                }
              }}
              className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors flex items-center space-x-2"
            >
              <Calendar size={16} />
              <span>Create Satsang</span>
            </button>
          </div>

          {/* Satsang Events */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {satsangEvents?.map((event, index) => (
              <div key={index} className="bg-white p-6 rounded-lg shadow border">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900">{event.title}</h4>
                    <p className="text-sm text-gray-600">{event.theme}</p>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    event.status === 'scheduled' ? 'bg-blue-100 text-blue-800' :
                    event.status === 'live' ? 'bg-green-100 text-green-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {event.status.toUpperCase()}
                  </span>
                </div>
                
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <p className="text-sm text-gray-600">Duration</p>
                    <p className="font-medium">{event.duration_minutes} minutes</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Base Credits</p>
                    <p className="font-medium">{event.base_credits} credits</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Participants</p>
                    <p className="font-medium">{event.current_participants}/{event.max_participants}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Type</p>
                    <p className="font-medium capitalize">{event.event_type}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4 mb-4">
                  {event.voice_enabled && (
                    <span className="flex items-center text-sm text-green-600">
                      <Mic size={14} className="mr-1" />
                      Voice
                    </span>
                  )}
                  {event.video_enabled && (
                    <span className="flex items-center text-sm text-blue-600">
                      <Video size={14} className="mr-1" />
                      Video
                    </span>
                  )}
                  {event.has_donations && (
                    <span className="flex items-center text-sm text-purple-600">
                      <Gift size={14} className="mr-1" />
                      Donations
                    </span>
                  )}
                  {event.interactive_level === 'premium' && (
                    <span className="flex items-center text-sm text-orange-600">
                      <MessageCircle size={14} className="mr-1" />
                      Interactive
                    </span>
                  )}
                </div>
                
                <div className="flex justify-between items-center">
                  <p className="text-sm text-gray-500">
                    {new Date(event.scheduled_at).toLocaleDateString()} at{' '}
                    {new Date(event.scheduled_at).toLocaleTimeString()}
                  </p>
                  <div className="space-x-2">
                    <button className="text-purple-600 hover:text-purple-700 text-sm">
                      Edit
                    </button>
                    <button className="text-green-600 hover:text-green-700 text-sm">
                      View Donations
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'analytics' && (
        <div className="space-y-6">
          <h3 className="text-lg font-semibold text-gray-900">API Cost Analytics</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* API Usage Chart Placeholder */}
            <div className="bg-white p-6 rounded-lg shadow border">
              <h4 className="text-md font-semibold text-gray-900 mb-4">Daily API Costs</h4>
              <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
                <p className="text-gray-500">Cost analytics chart will be implemented</p>
              </div>
            </div>
            
            {/* Service Performance */}
            <div className="bg-white p-6 rounded-lg shadow border">
              <h4 className="text-md font-semibold text-gray-900 mb-4">Service Performance</h4>
              <div className="space-y-3">
                {recommendations?.slice(0, 5).map((rec, index) => (
                  <div key={index} className="flex justify-between items-center">
                    <span className="text-sm text-gray-700">{rec.display_name}</span>
                    <span className="text-sm font-medium text-purple-600">
                      {rec.recommended_price} credits
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'prokerala' && (
        <div className="space-y-6">
          <h3 className="text-lg font-semibold text-gray-900">📊 Prokerala API Cost Analysis</h3>
          
          {/* Configuration Panel */}
          <div className="bg-white p-6 rounded-lg shadow border">
            <h4 className="text-md font-semibold text-gray-900 mb-4">Cost Configuration</h4>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Max Cost per API Call ($)
                </label>
                <input
                  type="number"
                  step="0.001"
                  defaultValue={prokeralaConfig?.max_cost_per_call || 0.036}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  onBlur={(e) => {
                    if (prokeralaConfig) {
                      updateProkeralaConfig({
                        ...prokeralaConfig,
                        max_cost_per_call: parseFloat(e.target.value)
                      });
                    }
                  }}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Margin Percentage (%)
                </label>
                <input
                  type="number"
                  defaultValue={prokeralaConfig?.margin_percentage || 500}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  onBlur={(e) => {
                    if (prokeralaConfig) {
                      updateProkeralaConfig({
                        ...prokeralaConfig,
                        margin_percentage: parseFloat(e.target.value)
                      });
                    }
                  }}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cache Discounts
                </label>
                <select
                  defaultValue={prokeralaConfig?.cache_discount_enabled ? 'enabled' : 'disabled'}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  onChange={(e) => {
                    if (prokeralaConfig) {
                      updateProkeralaConfig({
                        ...prokeralaConfig,
                        cache_discount_enabled: e.target.value === 'enabled'
                      });
                    }
                  }}
                >
                  <option value="enabled">Enabled</option>
                  <option value="disabled">Disabled</option>
                </select>
              </div>
            </div>
            
            <button
              onClick={loadProkeralaConfig}
              className="mt-4 bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 transition-colors"
            >
              Load Current Config
            </button>
          </div>
          
          {/* Service Cost Analysis */}
          <div className="bg-white p-6 rounded-lg shadow border">
            <h4 className="text-md font-semibold text-gray-900 mb-4">Service Cost Analysis</h4>
            
                         <div className="space-y-4">
               {/* Service Configuration */}
               <div className="mb-6">
                 <button
                   onClick={loadServicesForConfiguration}
                   className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 transition-colors"
                 >
                   Load Services for Configuration
                 </button>
               </div>
               
               {services?.map(service => (
                 <div key={service.id} className="border-l-4 border-purple-500 pl-4">
                   <div className="flex justify-between items-start">
                     <div>
                       <h5 className="font-semibold text-gray-900">{service.display_name || service.name}</h5>
                       <p className="text-sm text-gray-600">{service.description}</p>
                       
                       {/* Endpoint Configuration */}
                       <div className="mt-2">
                         <label className="block text-xs font-medium text-gray-700 mb-1">
                           Prokerala Endpoints:
                         </label>
                         <div className="flex flex-wrap gap-1 mb-2">
                           {(service.prokerala_endpoints || []).map((endpoint, idx) => (
                             <span key={idx} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                               {endpoint}
                             </span>
                           ))}
                           {(!service.prokerala_endpoints || service.prokerala_endpoints.length === 0) && (
                             <span className="text-gray-500 text-xs">No endpoints configured</span>
                           )}
                         </div>
                         
                         <div className="grid grid-cols-3 gap-2">
                           <div>
                             <label className="block text-xs text-gray-600">API Calls:</label>
                             <span className="text-sm font-medium">{service.estimated_api_calls || 1}</span>
                           </div>
                           <div>
                             <label className="block text-xs text-gray-600">Cache Rate:</label>
                             <span className="text-sm font-medium">{service.cache_effectiveness || 70}%</span>
                           </div>
                           <div>
                             <label className="block text-xs text-gray-600">Credits:</label>
                             <span className="text-sm font-medium">{service.credits_required}</span>
                           </div>
                         </div>
                       </div>
                       
                       <div className="mt-2 space-x-2">
                         <button 
                           onClick={() => loadProkeralaCosts(service.id)}
                           className="text-sm text-purple-600 hover:underline"
                         >
                           Calculate API Costs
                         </button>
                         <button 
                           onClick={() => configureServiceEndpoints(service.id)}
                           className="text-sm text-indigo-600 hover:underline"
                         >
                           Configure Endpoints
                         </button>
                       </div>
                                           </div>
                     
                     {prokeralaCosts[service.id] && (
                       <div className="text-right">
                         <p className="text-lg font-bold text-purple-600">
                           {prokeralaCosts[service.id].pricing.suggested_credits} credits
                                                 </p>
                         <p className="text-sm text-gray-600">
                           {prokeralaCosts[service.id].pricing.user_message}
                         </p>
                       </div>
                     )}
                   </div>
                   
                   {prokeralaCosts[service.id] && (
                     <div className="mt-4 p-4 bg-gray-50 rounded">
                       <h6 className="font-semibold mb-2">Cost Breakdown</h6>
                       
                       <div className="space-y-2 text-sm">
                         <div className="flex justify-between">
                           <span>Base API Cost:</span>
                           <span>${prokeralaCosts[service.id].cost_breakdown.prokerala_base_cost.toFixed(3)}</span>
                         </div>
                         
                         {prokeralaCosts[service.id].cost_breakdown.cache_discount_rate > 0 && (
                           <div className="flex justify-between text-green-600">
                             <span>Cache Discount ({prokeralaCosts[service.id].cost_breakdown.cache_discount_rate.toFixed(0)}%):</span>
                             <span>-${(prokeralaCosts[service.id].cost_breakdown.prokerala_base_cost - prokeralaCosts[service.id].cost_breakdown.prokerala_effective_cost).toFixed(3)}</span>
                           </div>
                         )}
                         
                         <div className="flex justify-between font-semibold">
                           <span>Effective API Cost:</span>
                           <span>${prokeralaCosts[service.id].cost_breakdown.prokerala_effective_cost.toFixed(3)}</span>
                         </div>
                         
                         <div className="border-t pt-2 mt-2">
                           {Object.entries(prokeralaCosts[service.id].cost_breakdown.other_costs).map(([key, value]) => (
                             <div key={key} className="flex justify-between">
                               <span>{key.replace(/_/g, ' ')}:</span>
                               <span>${value.toFixed(3)}</span>
                             </div>
                           ))}
                         </div>
                         
                         <div className="border-t pt-2 mt-2">
                           <div className="flex justify-between font-bold text-lg">
                             <span>Suggested Credits:</span>
                             <span className="text-purple-600">{prokeralaCosts[service.id].pricing.suggested_credits}</span>
                           </div>
                           {prokeralaCosts[service.id].pricing.savings_from_cache > 0 && (
                             <div className="flex justify-between text-green-600">
                               <span>Cache Savings:</span>
                               <span>{prokeralaCosts[service.id].pricing.savings_from_cache.toFixed(1)} credits</span>
                             </div>
                           )}
                         </div>
                       </div>
                       
                       {prokeralaCosts[service.id].suggestions.length > 0 && (
                         <div className="mt-4">
                           <h6 className="font-semibold mb-2">💡 Value Suggestions</h6>
                           {prokeralaCosts[service.id].suggestions.map((sugg, idx) => (
                            <div key={idx} className="text-sm bg-blue-50 p-2 rounded mb-2">
                              <p>{sugg.suggestion}</p>
                              <p className="text-gray-600">Cost impact: {sugg.cost_impact}</p>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Toast Notification */}
      {toastMessage && (
        <div className={`fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
          toastType === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
        }`}>
          <div className="flex items-center justify-between">
            <span>{toastMessage}</span>
            <button
              onClick={() => setToastMessage('')}
              className="ml-4 text-white hover:text-gray-200"
            >
              ×
            </button>
          </div>
        </div>
      )}

      {/* Endpoint Configuration Modal */}
      {showEndpointModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-semibold mb-4">
              Configure Endpoints for {modalService?.name}
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Select Endpoints:
                </label>
                <div className="max-h-40 overflow-y-auto border rounded-md p-2">
                  {getProkeralaEndpoints().map(endpoint => (
                    <label key={endpoint} className="flex items-center space-x-2 p-1">
                      <input
                        type="checkbox"
                        checked={modalEndpoints.includes(endpoint)}
                        onChange={() => handleEndpointToggle(endpoint)}
                        className="rounded"
                      />
                      <span className="text-sm">{endpoint}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Cache Effectiveness (%):
                </label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={modalCacheEffectiveness}
                  onChange={(e) => setModalCacheEffectiveness(Number(e.target.value))}
                  className="w-full border rounded-md px-3 py-2"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-4">
                <button
                  onClick={() => setShowEndpointModal(false)}
                  className="px-4 py-2 text-gray-600 border rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={saveEndpointConfiguration}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  Save
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminPricingDashboard;