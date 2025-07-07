import React, { useState, useEffect } from 'react';
import { 
  Calendar, Users, TrendingUp, DollarSign, Target, MessageCircle, 
  Video, Image, BarChart3, Settings, Play, Pause, Edit, Eye,
  Zap, Globe, Heart, Share2, ThumbsUp, Filter, Search, RefreshCw,
  AlertCircle, CheckCircle, Clock, ArrowUp, ArrowDown, Star
} from 'lucide-react';
import enhanced_api from '../../services/enhanced-api';
import PlatformConfiguration from './PlatformConfiguration';
import SwamjiAvatarPreview from './SwamjiAvatarPreview';

const SocialMediaMarketing = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(false);
  const [marketingData, setMarketingData] = useState(null);
  const [contentCalendar, setContentCalendar] = useState([]);
  const [campaigns, setCampaigns] = useState([]);
  const [performanceData, setPerformanceData] = useState({});

  useEffect(() => {
    fetchMarketingData();
    fetchContentCalendar();
    fetchCampaigns();
  }, []);

  const fetchMarketingData = async () => {
    try {
      setLoading(true);
      const response = await enhanced_api.get('/admin/social-marketing/overview');
      if (response.data.success) {
        setMarketingData(response.data.data);
        setPerformanceData(response.data.data.performance || {});
      }
    } catch (error) {
      console.error('Error fetching marketing data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchContentCalendar = async () => {
    try {
      const response = await enhanced_api.get('/admin/social-marketing/content-calendar');
      if (response.data.success) {
        setContentCalendar(response.data.data);
      }
    } catch (error) {
      console.error('Error fetching content calendar:', error);
    }
  };

  const fetchCampaigns = async () => {
    try {
      const response = await enhanced_api.get('/admin/social-marketing/campaigns');
      if (response.data.success) {
        setCampaigns(response.data.data);
      }
    } catch (error) {
      console.error('Error fetching campaigns:', error);
    }
  };

  const generateDailyContent = async () => {
    try {
      setLoading(true);
      const response = await enhanced_api.post('/admin/social-marketing/generate-daily-content');
      if (response.data.success) {
        await fetchContentCalendar();
        alert('Daily content generated successfully!');
      }
    } catch (error) {
      console.error('Error generating content:', error);
      alert('Failed to generate content');
    } finally {
      setLoading(false);
    }
  };

  const executePosting = async () => {
    try {
      setLoading(true);
      const response = await enhanced_api.post('/admin/social-marketing/execute-posting');
      if (response.data.success) {
        alert(`Posted to ${response.data.platforms_updated} platforms successfully!`);
        await fetchMarketingData();
      }
    } catch (error) {
      console.error('Error executing posting:', error);
      alert('Failed to execute posting');
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'overview', label: 'Marketing Overview', icon: BarChart3 },
    { id: 'content', label: 'Content Calendar', icon: Calendar },
    { id: 'campaigns', label: 'Ad Campaigns', icon: Target },
    { id: 'performance', label: 'Analytics', icon: TrendingUp },
    { id: 'automation', label: 'Automation', icon: Zap },
    { id: 'comments', label: 'Engagement', icon: MessageCircle },
    { id: 'avatar', label: 'Avatar Preview', icon: Video }
  ];

  if (loading && !marketingData) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <RefreshCw className="animate-spin mx-auto mb-4" size={32} />
          <p>Loading marketing dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">🚀 Social Media Marketing</h1>
          <p className="text-gray-600">Complete automation for Swamiji's digital presence</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={generateDailyContent}
            disabled={loading}
            className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center space-x-2"
          >
            <Zap size={16} />
            <span>Generate Content</span>
          </button>
          <button
            onClick={executePosting}
            disabled={loading}
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center space-x-2"
          >
            <Play size={16} />
            <span>Execute Posting</span>
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                activeTab === tab.id
                  ? 'border-purple-500 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <tab.icon size={16} />
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <MarketingOverview data={marketingData} />
      )}

      {activeTab === 'content' && (
        <ContentCalendarView 
          calendar={contentCalendar} 
          onRefresh={fetchContentCalendar}
        />
      )}

      {activeTab === 'campaigns' && (
        <CampaignManagement 
          campaigns={campaigns} 
          onRefresh={fetchCampaigns}
        />
      )}

      {activeTab === 'performance' && (
        <PerformanceAnalytics data={performanceData} />
      )}

      {activeTab === 'automation' && (
        <AutomationSettings />
      )}

      {activeTab === 'comments' && (
        <EngagementManagement />
      )}

      {activeTab === 'avatar' && (
        <SwamjiAvatarPreview />
      )}
    </div>
  );
};

const MarketingOverview = ({ data }) => {
  if (!data) return <div>Loading overview...</div>;

  const kpis = [
    {
      title: 'Total Reach',
      value: data.total_reach || '127K',
      change: '+12%',
      trend: 'up',
      icon: Globe,
      color: 'bg-blue-500'
    },
    {
      title: 'Engagement Rate',
      value: data.engagement_rate || '8.4%',
      change: '+2.1%',
      trend: 'up',
      icon: Heart,
      color: 'bg-red-500'
    },
    {
      title: 'Conversion Rate',
      value: data.conversion_rate || '3.2%',
      change: '+0.8%',
      trend: 'up',
      icon: Target,
      color: 'bg-green-500'
    },
    {
      title: 'Ad Spend ROI',
      value: data.ad_roi || '420%',
      change: '+45%',
      trend: 'up',
      icon: DollarSign,
      color: 'bg-yellow-500'
    }
  ];

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {kpis.map((kpi, index) => (
          <div key={index} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{kpi.title}</p>
                <p className="text-3xl font-bold text-gray-900">{kpi.value}</p>
                <div className="flex items-center mt-2">
                  {kpi.trend === 'up' ? <ArrowUp size={16} className="text-green-500" /> : <ArrowDown size={16} className="text-red-500" />}
                  <span className={`text-sm font-medium ${kpi.trend === 'up' ? 'text-green-500' : 'text-red-500'}`}>
                    {kpi.change}
                  </span>
                </div>
              </div>
              <div className={`${kpi.color} rounded-full p-3`}>
                <kpi.icon className="text-white" size={24} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Platform Performance */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold">Platform Performance</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {['YouTube', 'Instagram', 'Facebook', 'TikTok'].map((platform) => (
              <div key={platform} className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {data.platforms?.[platform.toLowerCase()]?.followers || '12.5K'}
                </div>
                <div className="text-sm text-gray-600">{platform} Followers</div>
                <div className="mt-2">
                  <span className="text-green-500 text-sm font-medium">
                    +{data.platforms?.[platform.toLowerCase()]?.growth || '5.2'}% this week
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold">Recent Marketing Activity</h3>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {(data.recent_activity || [
              { action: 'Posted daily wisdom video', platform: 'YouTube', time: '2 hours ago', status: 'success' },
              { action: 'Launched Satsang promotion campaign', platform: 'Facebook', time: '4 hours ago', status: 'success' },
              { action: 'Responded to 15 comments as Swamiji', platform: 'Instagram', time: '6 hours ago', status: 'success' },
              { action: 'A/B tested spiritual quote format', platform: 'TikTok', time: '8 hours ago', status: 'pending' }
            ]).map((activity, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className={`w-2 h-2 rounded-full ${
                    activity.status === 'success' ? 'bg-green-500' : 
                    activity.status === 'pending' ? 'bg-yellow-500' : 'bg-red-500'
                  }`} />
                  <div>
                    <p className="text-sm font-medium text-gray-900">{activity.action}</p>
                    <p className="text-xs text-gray-500">{activity.platform}</p>
                  </div>
                </div>
                <span className="text-xs text-gray-500">{activity.time}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

const ContentCalendarView = ({ calendar, onRefresh }) => {
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [selectedPlatform, setSelectedPlatform] = useState('all');

  const platforms = ['all', 'youtube', 'instagram', 'facebook', 'tiktok'];
  const platformColors = {
    youtube: 'bg-red-100 text-red-800',
    instagram: 'bg-pink-100 text-pink-800',
    facebook: 'bg-blue-100 text-blue-800',
    tiktok: 'bg-gray-100 text-gray-800'
  };

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex justify-between items-center">
        <div className="flex space-x-4">
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-2"
          />
          <select
            value={selectedPlatform}
            onChange={(e) => setSelectedPlatform(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-2"
          >
            {platforms.map(platform => (
              <option key={platform} value={platform}>
                {platform === 'all' ? 'All Platforms' : platform.charAt(0).toUpperCase() + platform.slice(1)}
              </option>
            ))}
          </select>
        </div>
        <button
          onClick={onRefresh}
          className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 flex items-center space-x-2"
        >
          <RefreshCw size={16} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Content Calendar Grid */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {(calendar || [
              {
                id: 1,
                platform: 'youtube',
                title: '✨ Daily Wisdom from Swamiji',
                content_type: 'daily_wisdom',
                scheduled_time: '07:00',
                status: 'scheduled',
                engagement_prediction: '8.5%'
              },
              {
                id: 2,
                platform: 'instagram',
                title: '🙏 Tamil Spiritual Quote',
                content_type: 'spiritual_quote',
                scheduled_time: '12:00',
                status: 'posted',
                actual_engagement: '12.3%'
              },
              {
                id: 3,
                platform: 'facebook',
                title: '🕉️ Join Our Sacred Satsang',
                content_type: 'satsang_promo',
                scheduled_time: '18:00',
                status: 'scheduled',
                engagement_prediction: '6.8%'
              }
            ]).filter(post => 
              selectedPlatform === 'all' || post.platform === selectedPlatform
            ).map((post) => (
              <div key={post.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-start justify-between mb-3">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${platformColors[post.platform]}`}>
                    {post.platform}
                  </span>
                  <div className="flex space-x-2">
                    <button className="text-gray-400 hover:text-gray-600">
                      <Eye size={16} />
                    </button>
                    <button className="text-gray-400 hover:text-gray-600">
                      <Edit size={16} />
                    </button>
                  </div>
                </div>
                
                <h4 className="font-medium text-gray-900 mb-2">{post.title}</h4>
                
                <div className="flex items-center justify-between text-sm text-gray-500 mb-3">
                  <span>{post.scheduled_time}</span>
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    post.status === 'posted' ? 'bg-green-100 text-green-800' :
                    post.status === 'scheduled' ? 'bg-blue-100 text-blue-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {post.status}
                  </span>
                </div>
                
                <div className="text-sm">
                  <span className="text-gray-500">
                    {post.status === 'posted' ? 'Actual' : 'Predicted'} Engagement:
                  </span>
                  <span className="font-medium text-green-600 ml-1">
                    {post.actual_engagement || post.engagement_prediction}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

const CampaignManagement = ({ campaigns, onRefresh }) => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Active Campaigns</h3>
        <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700">
          Create Campaign
        </button>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Campaign</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Platform</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Budget</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Spent</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ROI</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {(campaigns || [
              {
                id: 1,
                name: 'Satsang Community Growth',
                platform: 'Facebook',
                budget: '$500',
                spent: '$320',
                roi: '450%',
                status: 'active',
                conversions: 45
              },
              {
                id: 2,
                name: 'Spiritual Guidance Promotion',
                platform: 'Instagram',
                budget: '$300',
                spent: '$180',
                roi: '380%',
                status: 'active',
                conversions: 28
              }
            ]).map((campaign) => (
              <tr key={campaign.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{campaign.name}</div>
                  <div className="text-sm text-gray-500">{campaign.conversions} conversions</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{campaign.platform}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{campaign.budget}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{campaign.spent}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="text-sm font-medium text-green-600">{campaign.roi}</span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    campaign.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {campaign.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button className="text-purple-600 hover:text-purple-900 mr-3">Edit</button>
                  <button className="text-red-600 hover:text-red-900">Pause</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const PerformanceAnalytics = ({ data }) => {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Customer Acquisition</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Organic Traffic</span>
              <span className="font-medium">65%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Paid Social</span>
              <span className="font-medium">25%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Referrals</span>
              <span className="font-medium">10%</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Conversion Funnel</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Social Media Visitors</span>
              <span className="font-medium">12,500</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Service Page Views</span>
              <span className="font-medium">3,200</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Sign-ups</span>
              <span className="font-medium">480</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Paying Customers</span>
              <span className="font-medium text-green-600">156</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const AutomationSettings = () => {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Automation Rules</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <h4 className="font-medium">Daily Content Generation</h4>
              <p className="text-sm text-gray-600">Automatically generate and schedule daily spiritual content</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" defaultChecked />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
            </label>
          </div>
          
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <h4 className="font-medium">Comment Response as Swamiji</h4>
              <p className="text-sm text-gray-600">AI responses to comments in Swamiji's voice and personality</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" defaultChecked />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
            </label>
          </div>
          
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <h4 className="font-medium">Avatar Video Generation</h4>
              <p className="text-sm text-gray-600">Create Swamiji avatar videos for daily wisdom posts</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" defaultChecked />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
            </label>
          </div>
        </div>
      </div>
      
      {/* Platform Configuration */}
      <PlatformConfiguration />
    </div>
  );
};

const EngagementManagement = () => {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Recent Comments & Responses</h3>
        <div className="space-y-4">
          {[
            {
              user: 'DevoteeRavi',
              comment: 'Thank you Swamiji for the beautiful guidance! 🙏',
              platform: 'YouTube',
              response: 'Divine blessings upon you, dear soul. May your spiritual journey be filled with peace and wisdom. Om Namah Shivaya 🕉️',
              time: '2 hours ago'
            },
            {
              user: 'SpiritualSeeker88',
              comment: 'How can I overcome my fears in life?',
              platform: 'Instagram',
              response: 'Fear is but an illusion, beloved child. Trust in the divine plan and surrender your worries to the highest consciousness. Practice daily meditation and you will find inner strength.',
              time: '4 hours ago'
            }
          ].map((interaction, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <span className="font-medium text-gray-900">{interaction.user}</span>
                  <span className="text-sm text-gray-500">on {interaction.platform}</span>
                </div>
                <span className="text-sm text-gray-500">{interaction.time}</span>
              </div>
              
              <div className="bg-gray-50 rounded-lg p-3 mb-3">
                <p className="text-sm text-gray-700">{interaction.comment}</p>
              </div>
              
              <div className="bg-purple-50 rounded-lg p-3">
                <div className="flex items-center space-x-2 mb-2">
                  <span className="text-xs font-medium text-purple-600">Swami Jyotirananthan</span>
                  <CheckCircle size={14} className="text-green-500" />
                </div>
                <p className="text-sm text-gray-700">{interaction.response}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SocialMediaMarketing;