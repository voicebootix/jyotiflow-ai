// தமில - வணிக நுண்ணறிவு
import { useEffect, useState } from 'react';
import spiritualAPI from '../../lib/api';
import Loader from '../ui/Loader';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Alert, AlertDescription } from '../ui/alert';
import { CheckCircle, XCircle, TrendingUp, DollarSign, Target, Clock } from 'lucide-react';

export default function BusinessIntelligence() {
  const [data, setData] = useState(null);
  const [pricingRecommendations, setPricingRecommendations] = useState([]);
  const [dailyAnalysisSummary, setDailyAnalysisSummary] = useState(null);
  const [realUsageAnalytics, setRealUsageAnalytics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionLoading, setActionLoading] = useState({});
  const [triggerLoading, setTriggerLoading] = useState(false);

  useEffect(() => {
    let mounted = true;
    const loadData = async () => {
      try {
        const [biData, pricingData] = await Promise.all([
          spiritualAPI.getAdminBI(),
          spiritualAPI.getAIPricingRecommendations()
        ]);
        
        if (mounted) {
          setData(biData);
          setPricingRecommendations(pricingData.recommendations || []);
          
          // Get daily analysis summary if available
          if (biData.daily_analysis_summary) {
            setDailyAnalysisSummary(biData.daily_analysis_summary);
          }
          
          // Get real usage analytics
          if (biData.real_usage_analytics) {
            setRealUsageAnalytics(biData.real_usage_analytics);
          }
        }
      } catch (e) {
        if (mounted) setError('AI நுண்ணறிவு தரவு ஏற்ற முடியவில்லை.');
      } finally {
        if (mounted) setLoading(false);
      }
    };
    
    loadData();
    return () => { mounted = false; };
  }, []);

  const handleRecommendationAction = async (recommendationId, action) => {
    setActionLoading(prev => ({ ...prev, [recommendationId]: true }));
    
    try {
      // Update recommendation status
      if (action === 'approve') {
        await spiritualAPI.approveAIRecommendation(recommendationId);
      } else {
        await spiritualAPI.rejectAIRecommendation(recommendationId);
      }
      
      // Refresh recommendations
      const response = await spiritualAPI.getAIPricingRecommendations();
      setPricingRecommendations(response.recommendations || []);
      
    } catch (error) {
      console.error('Failed to update recommendation:', error);
    } finally {
      setActionLoading(prev => ({ ...prev, [recommendationId]: false }));
    }
  };

  const handleTriggerDailyAnalysis = async () => {
    setTriggerLoading(true);
    try {
      const response = await spiritualAPI.triggerDailyAnalysis();
      if (response.success) {
        // Refresh data after analysis
        const [biData, pricingData] = await Promise.all([
          spiritualAPI.getAdminBI(),
          spiritualAPI.getAIPricingRecommendations()
        ]);
        setData(biData);
        setPricingRecommendations(pricingData.recommendations || []);
        alert('தினசரி AI பகுப்பாய்வு வெற்றிகரமாக முடிந்தது!');
      } else {
        alert('பகுப்பாய்வு தோல்வியடைந்தது: ' + response.message);
      }
    } catch (error) {
      console.error('Failed to trigger analysis:', error);
      alert('பகுப்பாய்வு தொடங்க முடியவில்லை');
    } finally {
      setTriggerLoading(false);
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 1: return 'text-green-600';
      case 2: return 'text-blue-600';
      case 3: return 'text-yellow-600';
      case 4: return 'text-orange-600';
      case 5: return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  if (loading) return <Loader message="AI நுண்ணறிவு தரவு ஏற்றப்படுகிறது..." />;
  if (error) return <div className="text-red-600">{error}</div>;

  // Fallbacks for arrays
  const recommendations = Array.isArray(data?.recommendations) ? data.recommendations : [];
  const ab_tests = Array.isArray(data?.ab_tests) ? data.ab_tests : [];
  const market_analysis = Array.isArray(data?.market_analysis) ? data.market_analysis : [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">AI வணிக நுண்ணறிவு</h2>
        <div className="flex gap-2">
          <Button 
            onClick={handleTriggerDailyAnalysis}
            disabled={triggerLoading}
            className="bg-purple-600 hover:bg-purple-700 text-white"
            size="sm"
          >
            {triggerLoading ? 'பகுப்பாய்வு செயல்படுகிறது...' : 'தினசரி பகுப்பாய்வு'}
          </Button>
          <Button 
            onClick={() => window.location.reload()} 
            variant="outline"
            size="sm"
          >
            புதுப்பிக்கவும்
          </Button>
        </div>
      </div>

      {/* Daily Analysis Summary */}
      {dailyAnalysisSummary && (
        <Card className="border-2 border-green-200">
          <CardHeader className="bg-gradient-to-r from-green-50 to-blue-50">
            <CardTitle className="flex items-center gap-2 text-green-800">
              <Clock className="h-5 w-5" />
              தினசரி பகுப்பாய்வு சுருக்கம்
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {dailyAnalysisSummary.total_recommendations}
                </div>
                <div className="text-sm text-gray-600">மொத்த பரிந்துரைகள்</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {dailyAnalysisSummary.top_recommendations_count}
                </div>
                <div className="text-sm text-gray-600">சிறந்த பரிந்துரைகள்</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  ${dailyAnalysisSummary.total_expected_impact?.toLocaleString() || 0}
                </div>
                <div className="text-sm text-gray-600">மொத்த எதிர்பார்க்கப்படும் வருவாய்</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {Math.round((dailyAnalysisSummary.confidence_average || 0) * 100)}%
                </div>
                <div className="text-sm text-gray-600">சராசரி நம்பிக்கை</div>
              </div>
            </div>
            <div className="mt-4 text-sm text-gray-600">
              <strong>பகுப்பாய்வு தேதி:</strong> {new Date(dailyAnalysisSummary.analysis_date).toLocaleString('ta-IN')}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Real Usage Analytics Section */}
      {realUsageAnalytics.length > 0 && (
        <Card className="border-2 border-blue-200">
          <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50">
            <CardTitle className="flex items-center gap-2 text-blue-800">
              <TrendingUp className="h-5 w-5" />
              உண்மையான பயன்பாட்டு பகுப்பாய்வு
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-2 font-semibold">சேவை</th>
                    <th className="text-center py-2 font-semibold">மொத்த அமர்வுகள்</th>
                    <th className="text-center py-2 font-semibold">சராசரி காலம் (நிமிடங்கள்)</th>
                    <th className="text-center py-2 font-semibold">முடிவு விகிதம் (%)</th>
                    <th className="text-center py-2 font-semibold">சராசரி மதிப்பீடு</th>
                    <th className="text-center py-2 font-semibold">சராசரி வருவாய்</th>
                    <th className="text-center py-2 font-semibold">தனிப்பட்ட பயனர்கள்</th>
                  </tr>
                </thead>
                <tbody>
                  {realUsageAnalytics.map((service, index) => (
                    <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 font-medium text-gray-900">{service.service_name}</td>
                      <td className="py-3 text-center text-blue-600 font-semibold">{service.total_sessions}</td>
                      <td className="py-3 text-center text-gray-600">{service.avg_duration}</td>
                      <td className="py-3 text-center">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          service.completion_rate >= 90 ? 'bg-green-100 text-green-800' :
                          service.completion_rate >= 75 ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {service.completion_rate}%
                        </span>
                      </td>
                      <td className="py-3 text-center">
                        <div className="flex items-center justify-center gap-1">
                          <span className="text-yellow-600">★</span>
                          <span className="font-medium">{service.avg_rating}</span>
                        </div>
                      </td>
                      <td className="py-3 text-center text-green-600 font-medium">
                        ${service.avg_revenue}
                      </td>
                      <td className="py-3 text-center text-gray-600">{service.unique_users}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="mt-4 text-xs text-gray-500">
              <strong>குறிப்பு:</strong> கடந்த 90 நாட்களின் தரவு அடிப்படையில் பகுப்பாய்வு செய்யப்பட்டது
            </div>
          </CardContent>
        </Card>
      )}

      {/* AI Pricing Recommendations Section */}
      <Card className="border-2 border-purple-200">
        <CardHeader className="bg-gradient-to-r from-purple-50 to-blue-50">
          <CardTitle className="flex items-center gap-2 text-purple-800">
            <Target className="h-5 w-5" />
            AI விலை பரிந்துரைகள்
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          {pricingRecommendations.length === 0 ? (
            <Alert>
              <AlertDescription>
                தற்போது AI விலை பரிந்துரைகள் எதுவும் இல்லை.
              </AlertDescription>
            </Alert>
          ) : (
            <div className="grid gap-4">
              {pricingRecommendations.map((rec) => (
                <div key={rec.id} className="border rounded-lg p-4 bg-white shadow-sm">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant="outline" className={getPriorityColor(rec.priority_level)}>
                          {rec.priority_level === 'high' ? 'உயர் முன்னுரிமை' : 
                           rec.priority_level === 'medium' ? 'நடுத்தர முன்னுரிமை' : 'குறைந்த முன்னுரிமை'}
                        </Badge>
                        <Badge variant="outline" className="bg-blue-100 text-blue-800">
                          {rec.recommendation_type === 'service_price' ? 'சேவை விலை' :
                           rec.recommendation_type === 'credit_package' ? 'கிரெடிட் தொகுப்பு' :
                           rec.recommendation_type === 'donation_price' ? 'தானம் விலை' :
                           rec.recommendation_type === 'subscription_plan' ? 'சந்தா திட்டம்' : rec.recommendation_type}
                        </Badge>
                      </div>
                      
                      <h4 className="font-semibold text-lg text-gray-900 mb-1">
                        {rec.service_name || 'பொதுவான பரிந்துரை'}
                      </h4>
                      
                      <div className="flex items-center gap-4 mb-3 text-sm">
                        <div className="flex items-center gap-1">
                          <DollarSign className="h-4 w-4 text-gray-500" />
                          <span className="text-gray-600">
                            தற்போதைய: {formatCurrency(rec.current_value)}
                          </span>
                        </div>
                        <div className="flex items-center gap-1">
                          <TrendingUp className="h-4 w-4 text-green-500" />
                          <span className="text-green-600 font-medium">
                            பரிந்துரை: {formatCurrency(rec.suggested_value)}
                          </span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Clock className={`h-4 w-4 ${getDifficultyColor(rec.implementation_difficulty)}`} />
                          <span className={getDifficultyColor(rec.implementation_difficulty)}>
                            சிரமம்: {rec.implementation_difficulty}/5
                          </span>
                        </div>
                      </div>
                      
                      <div className="bg-yellow-50 border border-yellow-200 rounded p-3 mb-3">
                        <p className="text-sm text-gray-700 leading-relaxed mb-2">
                          {rec.reasoning}
                        </p>
                        
                        {/* Real Usage Data Indicators */}
                        {rec.metadata && (
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                            {rec.metadata.completion_rate && (
                              <div className="flex items-center gap-1">
                                <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                                <span>முடிவு: {(rec.metadata.completion_rate * 100).toFixed(0)}%</span>
                              </div>
                            )}
                            {rec.metadata.user_satisfaction && (
                              <div className="flex items-center gap-1">
                                <div className="w-2 h-2 rounded-full bg-green-500"></div>
                                <span>திருப்தி: {(rec.metadata.user_satisfaction * 100).toFixed(0)}%</span>
                              </div>
                            )}
                            {rec.metadata.total_sessions && (
                              <div className="flex items-center gap-1">
                                <div className="w-2 h-2 rounded-full bg-purple-500"></div>
                                <span>அமர்வுகள்: {rec.metadata.total_sessions}</span>
                              </div>
                            )}
                            {rec.metadata.data_quality && (
                              <div className="flex items-center gap-1">
                                <div className="w-2 h-2 rounded-full bg-orange-500"></div>
                                <span>தரம்: {rec.metadata.data_quality === 'high' ? 'உயர்' : 'நடுத்தர'}</span>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <div className="text-center">
                            <div className="text-lg font-bold text-green-600">
                              {formatCurrency(rec.expected_impact)}
                            </div>
                            <div className="text-xs text-gray-500">எதிர்பார்க்கப்படும் வருவாய்</div>
                          </div>
                          <div className="text-center">
                            <div className="text-lg font-bold text-blue-600">
                              {Math.round(rec.confidence_level * 100)}%
                            </div>
                            <div className="text-xs text-gray-500">AI நம்பிக்கை</div>
                          </div>
                        </div>
                        
                        <div className="flex gap-2">
                          <Button
                            onClick={() => handleRecommendationAction(rec.id, 'approve')}
                            disabled={actionLoading[rec.id]}
                            size="sm"
                            className="bg-green-600 hover:bg-green-700"
                          >
                            <CheckCircle className="h-4 w-4 mr-1" />
                            {actionLoading[rec.id] ? 'செயல்படுகிறது...' : 'ஏற்கவும்'}
                          </Button>
                          <Button
                            onClick={() => handleRecommendationAction(rec.id, 'reject')}
                            disabled={actionLoading[rec.id]}
                            size="sm"
                            variant="outline"
                            className="border-red-300 text-red-600 hover:bg-red-50"
                          >
                            <XCircle className="h-4 w-4 mr-1" />
                            {actionLoading[rec.id] ? 'செயல்படுகிறது...' : 'நிராகரிக்கவும்'}
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* General AI Recommendations */}
      <Card>
        <CardHeader>
          <CardTitle>பொதுவான AI பரிந்துரைகள்</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="list-disc pl-6 space-y-2">
            {recommendations.map((rec, i) => (
              <li key={i} className="mb-2">
                <span className="font-medium">{rec.title}</span> — 
                <span className="text-gray-500 ml-2">{rec.impact_estimate}</span>
                <div className="text-sm text-gray-700 mt-1">{rec.description}</div>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      {/* A/B Test Results */}
      <Card>
        <CardHeader>
          <CardTitle>A/B சோதனை முடிவுகள்</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={ab_tests}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="experiment_name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="conversion_rate_test" fill="#8b5cf6" />
              <Bar dataKey="conversion_rate_control" fill="#f59e42" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Market Analysis */}
      <Card>
        <CardHeader>
          <CardTitle>சந்தை பகுப்பாய்வு</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="list-disc pl-6 space-y-2">
            {market_analysis.map((item, i) => (
              <li key={i} className="text-gray-700">{item}</li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
} 