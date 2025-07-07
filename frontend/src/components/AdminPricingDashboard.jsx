/**
 * Admin Pricing Dashboard Component
 * Complete interface for managing dynamic pricing of comprehensive readings
 */

import { useState, useEffect } from 'react';
import { 
  DollarSign, TrendingUp, TrendingDown, AlertTriangle, CheckCircle, 
  Clock, BarChart3, Settings, RefreshCw, Save, Eye, Calendar,
  Activity, Target, Zap, Shield, Brain, Star
} from 'lucide-react';

import enhancedAPI from '../lib/enhanced-api.js';

const AdminPricingDashboard = () => {
  // State management
  const [pricingOverview, setPricingOverview] = useState(null);
  const [pricingAnalytics, setPricingAnalytics] = useState(null);
  const [currentRecommendation, setCurrentRecommendation] = useState(null);
  const [pricingAlerts, setPricingAlerts] = useState([]);
  const [systemHealth, setSystemHealth] = useState(null);
  
  // UI state
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [showApprovalModal, setShowApprovalModal] = useState(false);
  const [adminNotes, setAdminNotes] = useState('');
  const [approvedPrice, setApprovedPrice] = useState(0);
  
  // Auto-refresh
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [lastRefresh, setLastRefresh] = useState(new Date());

  // Initialize dashboard
  useEffect(() => {
    loadDashboardData();
    
    if (autoRefresh) {
      const interval = setInterval(loadDashboardData, 5 * 60 * 1000); // Refresh every 5 minutes
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      
      // Load all pricing data in parallel
      const [
        overviewResponse,
        analyticsResponse,
        alertsResponse,
        healthResponse
      ] = await Promise.all([
        enhancedAPI.getPricingOverview(),
        enhancedAPI.getPricingAnalytics(),
        enhancedAPI.getPricingAlerts(),
        enhancedAPI.getPricingSystemHealth()
      ]);

      if (overviewResponse?.success) {
        setPricingOverview(overviewResponse.data || overviewResponse);
      }
      
      if (analyticsResponse?.success) {
        setPricingAnalytics(analyticsResponse.analytics || analyticsResponse.data);
      }
      
      if (Array.isArray(alertsResponse)) {
        setPricingAlerts(alertsResponse);
      }
      
      if (healthResponse) {
        setSystemHealth(healthResponse);
      }
      
      setLastRefresh(new Date());
      
    } catch (error) {
      console.error('Dashboard data loading error:', error);
      // Set fallback data
      setPricingOverview({
        status: 'error',
        message: 'Failed to load pricing data',
        current_pricing: { current_price: 15 },
        pricing_recommendation: { recommended_price: 15, confidence_level: 0.5 }
      });
    } finally {
      setIsLoading(false);
    }
  };

  const generatePricingRecommendation = async () => {
    try {
      setIsLoading(true);
      const response = await enhancedAPI.generatePricingRecommendation();
      
      if (response?.success) {
        setCurrentRecommendation(response.recommendation);
        await loadDashboardData(); // Refresh all data
      }
    } catch (error) {
      console.error('Pricing recommendation error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleApprovePrice = () => {
    if (currentRecommendation || pricingOverview?.pricing_recommendation) {
      const recommendation = currentRecommendation || pricingOverview.pricing_recommendation;
      setApprovedPrice(recommendation.recommended_price);
      setShowApprovalModal(true);
    }
  };

  const applyPriceChange = async () => {
    try {
      setIsLoading(true);
      
      const response = await enhancedAPI.applyAdminPricing(approvedPrice, adminNotes);
      
      if (response?.success) {
        alert(`✅ Price updated successfully to ${approvedPrice} credits!`);
        setShowApprovalModal(false);
        setAdminNotes('');
        await loadDashboardData();
      } else {
        alert(`❌ Failed to update price: ${response?.message || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Price application error:', error);
      alert(`❌ Error applying price change: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const formatPrice = (price) => {
    return typeof price === 'number' ? price.toFixed(1) : '0.0';
  };

  const formatPercentage = (value) => {
    return typeof value === 'number' ? (value * 100).toFixed(1) : '0.0';
  };

  const getUrgencyColor = (urgency) => {
    switch (urgency) {
      case 'high': return 'text-red-600 bg-red-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (isLoading && !pricingOverview) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading pricing dashboard...</p>
        </div>
      </div>
    );
  }

  const currentPrice = pricingOverview?.current_pricing?.current_price || 15;
  const recommendedPrice = pricingOverview?.pricing_recommendation?.recommended_price || currentPrice;
  const confidence = pricingOverview?.pricing_recommendation?.confidence_level || 0.5;
  const urgency = pricingOverview?.pricing_recommendation?.recommendation_urgency || 'low';

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <DollarSign className="w-8 h-8 text-blue-600 mr-3" />
              <h1 className="text-2xl font-bold text-gray-900">Pricing Dashboard</h1>
              {systemHealth && (
                <span className={`ml-4 px-2 py-1 rounded-full text-xs font-medium ${
                  systemHealth.dynamic_pricing_available ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {systemHealth.system_status}
                </span>
              )}
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-500">
                Last updated: {lastRefresh.toLocaleTimeString()}
              </div>
              <button
                onClick={loadDashboardData}
                disabled={isLoading}
                className={`inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium ${
                  isLoading 
                    ? 'text-gray-400 cursor-not-allowed' 
                    : 'text-gray-700 bg-white hover:bg-gray-50'
                }`}
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                Refresh
              </button>
              <button
                onClick={generatePricingRecommendation}
                disabled={isLoading}
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                <Brain className="w-4 h-4 mr-2" />
                Generate Recommendation
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Alerts */}
      {pricingAlerts.length > 0 && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-center">
              <AlertTriangle className="w-5 h-5 text-yellow-600 mr-2" />
              <h3 className="font-medium text-yellow-800">Pricing Alerts</h3>
            </div>
            <div className="mt-2 space-y-1">
              {pricingAlerts.slice(0, 3).map((alert, index) => (
                <p key={index} className="text-sm text-yellow-700">
                  {alert.message}
                </p>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Current Pricing Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <DollarSign className="w-8 h-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Current Price</p>
                <p className="text-2xl font-bold text-gray-900">{formatPrice(currentPrice)} credits</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <Target className="w-8 h-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Recommended Price</p>
                <p className="text-2xl font-bold text-gray-900">{formatPrice(recommendedPrice)} credits</p>
                <div className={`flex items-center mt-1 ${
                  recommendedPrice > currentPrice ? 'text-red-600' : 
                  recommendedPrice < currentPrice ? 'text-green-600' : 'text-gray-600'
                }`}>
                  {recommendedPrice > currentPrice ? (
                    <TrendingUp className="w-4 h-4 mr-1" />
                  ) : recommendedPrice < currentPrice ? (
                    <TrendingDown className="w-4 h-4 mr-1" />
                  ) : null}
                  <span className="text-sm">
                    {recommendedPrice !== currentPrice 
                      ? `${recommendedPrice > currentPrice ? '+' : ''}${formatPrice(recommendedPrice - currentPrice)}`
                      : 'No change'
                    }
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <Activity className="w-8 h-8 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Confidence Level</p>
                <p className={`text-2xl font-bold ${getConfidenceColor(confidence)}`}>
                  {formatPercentage(confidence)}%
                </p>
                <p className="text-sm text-gray-500">Recommendation strength</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <Clock className="w-8 h-8 text-orange-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Urgency</p>
                <span className={`inline-flex px-2 py-1 rounded-full text-sm font-medium ${getUrgencyColor(urgency)}`}>
                  {urgency}
                </span>
                <p className="text-sm text-gray-500 mt-1">
                  {urgency === 'high' ? 'Immediate attention needed' :
                   urgency === 'medium' ? 'Review recommended' : 'Stable pricing'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Cost Breakdown */}
        {pricingOverview?.pricing_recommendation?.cost_breakdown && (
          <div className="bg-white rounded-lg shadow mb-8">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Cost Breakdown</h3>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(pricingOverview.pricing_recommendation.cost_breakdown).map(([key, value]) => {
                  if (key === 'total_operational_cost') return null;
                  
                  const displayName = key.replace(/_/g, ' ').replace(/cost/g, '').trim();
                  const icon = key.includes('openai') ? <Brain className="w-5 h-5" /> :
                              key.includes('elevenlabs') ? <Zap className="w-5 h-5" /> :
                              key.includes('did') ? <Star className="w-5 h-5" /> :
                              <Shield className="w-5 h-5" />;
                  
                  return (
                    <div key={key} className="flex items-center p-3 bg-gray-50 rounded-lg">
                      <div className="text-gray-600 mr-3">{icon}</div>
                      <div>
                        <p className="text-sm font-medium text-gray-900 capitalize">{displayName}</p>
                        <p className="text-lg font-bold text-blue-600">{formatPrice(value)}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
              
              <div className="mt-6 pt-4 border-t border-gray-200">
                <div className="flex justify-between items-center">
                  <span className="text-lg font-medium text-gray-900">Total Operational Cost:</span>
                  <span className="text-2xl font-bold text-red-600">
                    {formatPrice(pricingOverview.pricing_recommendation.cost_breakdown.total_operational_cost)} credits
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Pricing Recommendation */}
        {(currentRecommendation || pricingOverview?.pricing_recommendation) && (
          <div className="bg-white rounded-lg shadow mb-8">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Pricing Recommendation</h3>
            </div>
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="text-sm text-gray-500">AI Analysis suggests:</p>
                  <p className="text-xl font-bold text-gray-900">
                    Change price from {formatPrice(currentPrice)} to {formatPrice(recommendedPrice)} credits
                  </p>
                  <p className="text-sm text-gray-600 mt-1">
                    {pricingOverview?.pricing_recommendation?.pricing_rationale || 'Based on current market conditions and costs'}
                  </p>
                </div>
                
                {recommendedPrice !== currentPrice && (
                  <button
                    onClick={handleApprovePrice}
                    className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                  >
                    <CheckCircle className="w-4 h-4 mr-2" />
                    Approve Change
                  </button>
                )}
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="font-medium text-gray-500">Confidence:</span>
                  <span className={`ml-2 font-bold ${getConfidenceColor(confidence)}`}>
                    {formatPercentage(confidence)}%
                  </span>
                </div>
                <div>
                  <span className="font-medium text-gray-500">Urgency:</span>
                  <span className={`ml-2 px-2 py-1 rounded text-xs font-medium ${getUrgencyColor(urgency)}`}>
                    {urgency}
                  </span>
                </div>
                <div>
                  <span className="font-medium text-gray-500">Impact:</span>
                  <span className="ml-2">
                    {recommendedPrice > currentPrice ? 'Revenue +' : 'Demand +'}
                    {Math.abs(((recommendedPrice - currentPrice) / currentPrice) * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Pricing History */}
        {pricingAnalytics?.pricing_history && pricingAnalytics.pricing_history.length > 0 && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Recent Pricing Changes</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Old Price</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">New Price</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Change</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Reasoning</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {pricingAnalytics.pricing_history.slice(0, 10).map((change, index) => (
                    <tr key={index}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {new Date(change.changed_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatPrice(change.old_price)} credits
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatPrice(change.new_price)} credits
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className={`inline-flex items-center ${
                          change.price_change > 0 ? 'text-red-600' : change.price_change < 0 ? 'text-green-600' : 'text-gray-600'
                        }`}>
                          {change.price_change > 0 ? (
                            <TrendingUp className="w-4 h-4 mr-1" />
                          ) : change.price_change < 0 ? (
                            <TrendingDown className="w-4 h-4 mr-1" />
                          ) : null}
                          {change.price_change > 0 ? '+' : ''}{formatPrice(change.price_change)}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">
                        {change.reasoning || 'No reason provided'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Approval Modal */}
      {showApprovalModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Approve Price Change</h3>
              
              <div className="mb-4">
                <p className="text-sm text-gray-600 mb-2">
                  Change price from <span className="font-bold">{formatPrice(currentPrice)}</span> to:
                </p>
                <input
                  type="number"
                  step="0.5"
                  value={approvedPrice}
                  onChange={(e) => setApprovedPrice(parseFloat(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Admin Notes (optional)
                </label>
                <textarea
                  value={adminNotes}
                  onChange={(e) => setAdminNotes(e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Reason for price change..."
                />
              </div>
              
              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setShowApprovalModal(false)}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
                >
                  Cancel
                </button>
                <button
                  onClick={applyPriceChange}
                  disabled={isLoading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  {isLoading ? 'Applying...' : 'Apply Change'}
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