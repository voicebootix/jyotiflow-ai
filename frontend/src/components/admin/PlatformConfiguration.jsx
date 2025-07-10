import React, { useState, useEffect } from 'react';
import { Key, Eye, EyeOff, Save, TestTube, CheckCircle, AlertCircle } from 'lucide-react';
import enhanced_api from '../../services/enhanced-api';

const PlatformConfiguration = () => {
  const [apiKeys, setApiKeys] = useState({
    youtube: { api_key: '', channel_id: '', status: 'not_connected' },
    instagram: { app_id: '', app_secret: '', access_token: '', status: 'not_connected' },
    facebook: { app_id: '', app_secret: '', page_access_token: '', status: 'not_connected' },
    tiktok: { client_key: '', client_secret: '', status: 'not_connected' }
  });
  
  const [showSecrets, setShowSecrets] = useState({});
  const [loading, setLoading] = useState(false);
  const [testResults, setTestResults] = useState({});

  useEffect(() => {
    fetchCurrentKeys();
  }, []);

  const fetchCurrentKeys = async () => {
    try {
      const response = await enhanced_api.get('/api/admin/social-marketing/platform-config');
      // SURGICAL FIX: Handle StandardResponse format correctly
      const responseData = response.data;
      if (responseData && responseData.success && responseData.data) {
        setApiKeys(responseData.data);
      }
    } catch (error) {
      console.error('Error fetching API keys:', error);
    }
  };

  const updateApiKey = (platform, field, value) => {
    setApiKeys(prev => ({
      ...prev,
      [platform]: {
        ...prev[platform],
        [field]: value
      }
    }));
  };

  const saveConfiguration = async (platform) => {
    try {
      setLoading(true);
      const response = await enhanced_api.post('/api/admin/social-marketing/platform-config', {
        platform,
        config: apiKeys[platform]
      });
      
      // SURGICAL FIX: Handle StandardResponse format correctly
      const responseData = response.data;
      if (responseData && responseData.success) {
        alert(`✅ ${platform.charAt(0).toUpperCase() + platform.slice(1)} configuration saved successfully!`);
        await fetchCurrentKeys();
      } else {
        const errorMessage = responseData?.message || 'Failed to save configuration';
        alert(`❌ ${errorMessage}`);
      }
    } catch (error) {
      console.error('Error saving configuration:', error);
      const errorMessage = error.response?.data?.message || 'Failed to save configuration';
      alert(`❌ ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const testConnection = async (platform) => {
    try {
      setLoading(true);
      const response = await enhanced_api.post('/api/admin/social-marketing/test-connection', {
        platform,
        config: apiKeys[platform]
      });
      
      // SURGICAL FIX: Handle StandardResponse format correctly
      const responseData = response.data;
      const isSuccess = responseData && responseData.success;
      
      setTestResults(prev => ({
        ...prev,
        [platform]: isSuccess ? 'success' : 'error'
      }));
      
      const message = responseData?.message || (isSuccess ? 'Connection successful!' : 'Connection failed');
      alert(isSuccess ? `✅ ${message}` : `❌ ${message}`);
    } catch (error) {
      setTestResults(prev => ({ ...prev, [platform]: 'error' }));
      const errorMessage = error.response?.data?.message || 'Connection test failed';
      alert(`❌ ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const toggleSecret = (platform, field) => {
    setShowSecrets(prev => ({
      ...prev,
      [`${platform}_${field}`]: !prev[`${platform}_${field}`]
    }));
  };

  const platformConfigs = {
    youtube: {
      name: 'YouTube',
      color: 'bg-red-500',
      icon: '🎥',
      fields: [
        { key: 'api_key', label: 'API Key', type: 'password', required: true },
        { key: 'channel_id', label: 'Channel ID', type: 'text', required: true }
      ],
      instructions: 'Get your API key from Google Cloud Console → YouTube Data API v3'
    },
    instagram: {
      name: 'Instagram',
      color: 'bg-pink-500',
      icon: '📸',
      fields: [
        { key: 'app_id', label: 'App ID', type: 'text', required: true },
        { key: 'app_secret', label: 'App Secret', type: 'password', required: true },
        { key: 'access_token', label: 'Access Token', type: 'password', required: true }
      ],
      instructions: 'Create app in Facebook Developers → Instagram Basic Display API'
    },
    facebook: {
      name: 'Facebook',
      color: 'bg-blue-500',
      icon: '👥',
      fields: [
        { key: 'app_id', label: 'App ID', type: 'text', required: true },
        { key: 'app_secret', label: 'App Secret', type: 'password', required: true },
        { key: 'page_access_token', label: 'Page Access Token', type: 'password', required: true }
      ],
      instructions: 'Get tokens from Facebook Developers → Graph API → Page Access Tokens'
    },
    tiktok: {
      name: 'TikTok',
      color: 'bg-gray-800',
      icon: '🎵',
      fields: [
        { key: 'client_key', label: 'Client Key', type: 'text', required: true },
        { key: 'client_secret', label: 'Client Secret', type: 'password', required: true }
      ],
      instructions: 'Apply for TikTok for Business API → Marketing API access'
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Key className="mr-2" size={20} />
          Social Media Platform Configuration
        </h3>
        <p className="text-gray-600 mb-6">
          Configure API keys to enable automated posting to social media platforms.
        </p>

        {Object.entries(platformConfigs).map(([platform, config]) => (
          <div key={platform} className="border border-gray-200 rounded-lg p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <div className={`${config.color} rounded-full w-10 h-10 flex items-center justify-center text-white mr-3`}>
                  <span className="text-lg">{config.icon}</span>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">{config.name}</h4>
                  <p className="text-sm text-gray-500">{config.instructions}</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                {apiKeys[platform].status === 'connected' && (
                  <CheckCircle className="text-green-500" size={20} />
                )}
                {testResults[platform] === 'success' && (
                  <div className="text-green-600 text-sm">✅ Connected</div>
                )}
                {testResults[platform] === 'error' && (
                  <div className="text-red-600 text-sm">❌ Failed</div>
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {config.fields.map((field) => (
                <div key={field.key}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {field.label} {field.required && <span className="text-red-500">*</span>}
                  </label>
                  <div className="relative">
                    <input
                      type={showSecrets[`${platform}_${field.key}`] ? 'text' : field.type}
                      value={apiKeys[platform][field.key] || ''}
                      onChange={(e) => updateApiKey(platform, field.key, e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                      placeholder={`Enter ${field.label.toLowerCase()}`}
                    />
                    {field.type === 'password' && (
                      <button
                        type="button"
                        onClick={() => toggleSecret(platform, field.key)}
                        className="absolute right-2 top-2 text-gray-400 hover:text-gray-600"
                      >
                        {showSecrets[`${platform}_${field.key}`] ? <EyeOff size={16} /> : <Eye size={16} />}
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>

            <div className="flex space-x-3 mt-4">
              <button
                onClick={() => saveConfiguration(platform)}
                disabled={loading}
                className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center space-x-2"
              >
                <Save size={16} />
                <span>Save</span>
              </button>
              <button
                onClick={() => testConnection(platform)}
                disabled={loading}
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center space-x-2"
              >
                <TestTube size={16} />
                <span>Test Connection</span>
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Cost Information */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-medium text-blue-900 mb-2">💰 Cost Information</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• YouTube: FREE (up to 10,000 API calls/day)</li>
          <li>• Instagram: FREE (basic posting)</li>
          <li>• Facebook: FREE (organic posts)</li>
          <li>• TikTok: FREE (basic API usage)</li>
          <li>• Content Generation: ~$60-180/month</li>
          <li>• Avatar Videos: ~$0.50-2.00 per video</li>
        </ul>
      </div>
    </div>
  );
};

export default PlatformConfiguration;