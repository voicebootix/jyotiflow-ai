import React, { useState, useEffect } from 'react';
import { Key, Eye, EyeOff, Save, TestTube, CheckCircle, AlertCircle, Info, ExternalLink, HelpCircle } from 'lucide-react';
import enhanced_api from '../../services/enhanced-api.js';

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
  const [notifications, setNotifications] = useState([]);
  const [validationErrors, setValidationErrors] = useState({});
  const [isValidating, setIsValidating] = useState({});
  const [showHelpFor, setShowHelpFor] = useState(null);

  useEffect(() => {
    fetchCurrentKeys();
  }, []);

  // Notification management (core.md: clear user feedback)
  const addNotification = (type, message, platform = null, details = null) => {
    const id = Date.now();
    setNotifications(prev => [...prev, {
      id,
      type, // 'success', 'error', 'warning', 'info'
      message,
      platform,
      details,
      timestamp: new Date()
    }]);

    // Auto-remove after 5 seconds for success, 10 seconds for errors
    setTimeout(() => {
      removeNotification(id);
    }, type === 'success' ? 5000 : 10000);
  };

  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  // Input validation (refresh.md: real-time feedback)
  const validateField = (platform, field, value) => {
    const errors = {};
    
    if (field === 'channel_id' && platform === 'youtube') {
      if (!value) {
        errors.channel_id = 'Channel ID is required';
      } else if (!value.trim()) {
        errors.channel_id = 'Channel ID cannot be empty';
      } else {
        // Clear previous error
        setValidationErrors(prev => ({
          ...prev,
          [`${platform}_${field}`]: null
        }));
        
        // Provide helpful guidance based on input format
        if (value.includes('youtube.com')) {
          addNotification('info', 'YouTube URL detected. We\'ll extract the Channel ID automatically.', platform);
        } else if (value.startsWith('@')) {
          addNotification('info', 'Channel handle detected. We\'ll convert it to Channel ID during validation.', platform);
        } else if (value.startsWith('UC') && value.length === 24) {
          addNotification('success', 'Valid Channel ID format detected.', platform);
        } else if (value.length > 0) {
          addNotification('warning', 'We\'ll try to find your channel. For best results, use the full Channel ID (starts with UC).', platform);
        }
      }
    }

    if (field === 'api_key' && platform === 'youtube') {
      if (!value) {
        errors.api_key = 'YouTube API Key is required';
      } else if (value.length < 30) {
        errors.api_key = 'API Key seems too short. Please check your key.';
      }
    }

    // Add more platform-specific validations
    if (platform === 'facebook' || platform === 'instagram') {
      if (field === 'app_id' && value && !/^\d+$/.test(value)) {
        errors[field] = 'App ID should contain only numbers';
      }
    }

    // Update validation errors
    if (Object.keys(errors).length > 0) {
      setValidationErrors(prev => ({
        ...prev,
        [`${platform}_${field}`]: errors[field]
      }));
    } else {
      setValidationErrors(prev => ({
        ...prev,
        [`${platform}_${field}`]: null
      }));
    }
  };

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

    // Real-time validation (core.md: immediate feedback)
    validateField(platform, field, value);
  };

  const saveConfiguration = async (platform) => {
    let responseData; // ✅ SCOPE FIX: Declare in higher scope
    let saveSuccessful = false; // ✅ Boolean flag for success tracking
    
    try {
      setLoading(true);
      
      // Validate required fields before saving (core.md: proactive validation)
      const config = apiKeys[platform];
      const platformConfig = platformConfigs[platform];
      const missingFields = platformConfig.fields
        .filter(field => field.required && !config[field.key]?.trim())
        .map(field => field.label);
      
      if (missingFields.length > 0) {
        addNotification('error', `Please fill in required fields: ${missingFields.join(', ')}`, platform);
        setLoading(false);
        return;
      }

      const response = await enhanced_api.updatePlatformConfig({
        platform,
        config: apiKeys[platform]
      });
      
      responseData = response.data; // ✅ Assign to higher scope variable
      
      // DIAGNOSTIC: Log the actual response for debugging
      console.log('🔍 SAVE RESPONSE DEBUG:', {
        platform,
        httpStatus: response.status,
        responseData,
        hasSuccess: responseData?.success,
        successValue: responseData?.success,
        message: responseData?.message
      });
      
      if (responseData && responseData.success) {
        saveSuccessful = true; // ✅ Track success with boolean flag
        addNotification('success', `${platform.charAt(0).toUpperCase() + platform.slice(1)} configuration saved successfully!`, platform);
        setLoading(false); // ✅ Reset loading state on success
      } else {
        const errorMessage = responseData?.message || 'Failed to save configuration';
        console.log('❌ SAVE FAILED - Response Analysis:', {
          responseData,
          errorMessage,
          successField: responseData?.success,
          hasResponseData: !!responseData
        });
        addNotification('error', errorMessage, platform, responseData);
        setLoading(false);
      }
    } catch (error) {
      console.error('Error saving configuration:', error);
      const errorMessage = error.response?.data?.message || error.message || 'Failed to save configuration';
      addNotification('error', `Save failed: ${errorMessage}`, platform, {
        status: error.response?.status,
        details: error.response?.data
      });
      setLoading(false);
    }
    
    // ✅ SCOPE FIX: Separate try-catch for fetchCurrentKeys with proper scope
    // This prevents fetchCurrentKeys errors from overriding save success
    try {
      await fetchCurrentKeys();
      console.log('✅ fetchCurrentKeys completed successfully');
    } catch (fetchError) {
      console.error('❌ fetchCurrentKeys failed:', fetchError);
      // ✅ FIXED: Use boolean flag instead of responseData scope access
      if (saveSuccessful) {
        addNotification('warning', 'Configuration saved but refresh failed. Please reload the page.', platform);
      }
    }
  };

  const testConnection = async (platform) => {
    try {
      setIsValidating(prev => ({ ...prev, [platform]: true }));
      
      // Pre-test validation (refresh.md: early error detection)
      const config = apiKeys[platform];
      const platformConfig = platformConfigs[platform];
      const missingFields = platformConfig.fields
        .filter(field => field.required && !config[field.key]?.trim())
        .map(field => field.label);
      
      if (missingFields.length > 0) {
        addNotification('error', `Cannot test connection: Missing ${missingFields.join(', ')}`, platform);
        setTestResults(prev => ({ ...prev, [platform]: 'error' }));
        return;
      }

      // Enhanced YouTube handle validation (core.md: proactive validation)
      if (platform === 'youtube' && config.channel_id) {
        const handle = config.channel_id.trim();
        
        // Comprehensive input format validation (refresh.md: support all documented formats)
        const isValidHandle = handle.match(/^@[a-zA-Z0-9._-]+$/);
        const isValidChannelId = handle.match(/^UC[a-zA-Z0-9_-]{22}$/);
        const isValidURL = handle.match(/^https?:\/\/(www\.)?(youtube\.com|youtu\.be)\/.+/);
        const isValidFormat = isValidHandle || isValidChannelId || isValidURL;
        
        // Only warn for genuinely invalid formats
        if (!isValidFormat && handle.length > 0) {
          addNotification('warning', 'Invalid format. Use @YourHandle, channel URL, or Channel ID (UC...)', platform);
        }
        
        // Specific guidance for known non-existent test channel
        if (handle === '@jyotiGuru-h9v') {
          addNotification('warning', '⚠️ Testing with @jyotiGuru-h9v (this channel may not exist). Try @SadhguruJV or create your channel first.', platform);
        }
      }

      addNotification('info', `Testing ${platform} connection...`, platform);
      
      const response = await enhanced_api.testConnection({
        platform,
        config: apiKeys[platform]
      });
      
      // SURGICAL FIX: Robust response format handling (core.md & refresh.md)
      // Backend returns: { success: true, data: {...}, message: "..." }
      // But some responses might be nested: { data: { success: true, ... } }
      const responseData = response.data;
      
      // Parse response with proper error detection and data extraction
      let isSuccess, successData, responseMessage;
      
      if (responseData.success !== undefined) {
        // Direct StandardResponse format: { success: true, data: {...}, message: "..." }
        isSuccess = responseData.success;
        successData = responseData.data;
        responseMessage = responseData.message;
      } else if (responseData.data && responseData.data.success !== undefined) {
        // Nested format: { data: { success: true, ... } }
        isSuccess = responseData.data.success;
        successData = responseData.data; // ✅ FIXED: Use responseData.data, not responseData.data.data
        responseMessage = responseData.data.message;
      } else {
        // Comprehensive fallback with proper error detection
        const hasError = responseData.error || 
                         (responseData.data && responseData.data.error) ||
                         responseData.success === false ||
                         (responseData.data && responseData.data.success === false);
        
        isSuccess = !hasError; // ✅ FIXED: Check all possible error locations
        successData = responseData.data || responseData;
        responseMessage = responseData.message || 
                         (responseData.data && responseData.data.message) ||
                         null; // ✅ FIXED: No misleading default message
      }
      
      setTestResults(prev => ({
        ...prev,
        [platform]: isSuccess ? 'success' : 'error'
      }));
      
      if (isSuccess) {
        // ✅ FIXED: Clear success message handling
        const successMessage = responseMessage || 'Connection successful!';
        
        // Enhanced success feedback (core.md: informative responses)
        if (platform === 'youtube' && successData?.resolved_channel_id) {
          addNotification('success', `${successMessage} Channel: ${successData.channel_info?.title || 'Connected'}`, platform, successData);
        } else if (platform === 'facebook' && successData?.page_name) {
          addNotification('success', `${successMessage} Page: ${successData.page_name}`, platform, successData);
        } else {
          addNotification('success', successMessage, platform, successData);
        }
      } else {
        // ✅ FIXED: Proper error message extraction with comprehensive fallback
        const errorMessage = responseMessage ||
                             responseData?.message ||
                             (responseData?.data && responseData.data.message) ||
                             (responseData?.data && responseData.data.error) ||
                             responseData?.error ||
                             'Connection failed';
        
        const errorDetails = responseData?.data?.error || 
                           responseData?.error || 
                           responseData?.data ||
                           responseData;
        
        // Enhanced error feedback with actionable guidance (refresh.md: helpful errors)
        let guidanceMessage = errorMessage;
        if (platform === 'youtube' && errorMessage.includes('Channel ID')) {
          guidanceMessage += '. Try using your channel URL (youtube.com/@handle) or full Channel ID.';
        } else if (platform === 'facebook' && errorMessage.includes('token')) {
          guidanceMessage += '. Check if your Page Access Token has the required permissions.';
        }
        
        addNotification('error', guidanceMessage, platform, { 
          original_error: errorDetails,
          troubleshooting: getTroubleshootingSteps(platform, errorMessage)
        });
      }
    } catch (error) {
      setTestResults(prev => ({ ...prev, [platform]: 'error' }));
      const errorMessage = error.response?.data?.message || error.message || 'Connection test failed';
      
      // Network/server error handling (core.md: clear error categorization)
      if (error.code === 'NETWORK_ERROR' || !error.response) {
        addNotification('error', 'Network error: Please check your internet connection and try again.', platform);
      } else if (error.response?.status === 401) {
        addNotification('error', 'Authentication failed: Please check your API credentials.', platform);
      } else if (error.response?.status >= 500) {
        addNotification('error', 'Server error: The service is temporarily unavailable. Please try again later.', platform);
      } else {
        addNotification('error', `Test failed: ${errorMessage}`, platform, {
          status: error.response?.status,
          details: error.response?.data
        });
      }
    } finally {
      setIsValidating(prev => ({ ...prev, [platform]: false }));
    }
  };

  // Troubleshooting guidance (refresh.md: actionable help)
  const getTroubleshootingSteps = (platform, errorMessage) => {
    const steps = {
      youtube: [
        'Ensure your YouTube API is enabled in Google Cloud Console',
        'Check that your API key has YouTube Data API v3 permissions',
        'Verify your channel is public and not suspended',
        'Try using your channel URL instead of Channel ID'
      ],
      facebook: [
        'Verify your Page Access Token is not expired',
        'Check that your app has required permissions (pages_manage_posts, etc.)',
        'Ensure your Facebook page is published and active',
        'Confirm your app is not in development mode restrictions'
      ],
      instagram: [
        'Make sure your Instagram account is a business account',
        'Verify your app has Instagram Basic Display permissions',
        'Check that your access token is not expired',
        'Ensure your Instagram account is linked to your Facebook page'
      ],
      tiktok: [
        'Confirm your TikTok for Business account is approved',
        'Check that your app has Marketing API access',
        'Verify your client credentials are correct',
        'Ensure your TikTok account meets the API requirements'
      ]
    };
    
    return steps[platform] || ['Check your API credentials', 'Verify account permissions', 'Contact support if issues persist'];
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
        { 
          key: 'api_key', 
          label: 'API Key', 
          type: 'password', 
          required: true,
          placeholder: 'AIzaSyBhbXxXxXxXxXxXxXxXxXxXxXxXxXx',
          helpText: 'Get this from Google Cloud Console → Credentials → API Keys'
        },
        { 
          key: 'channel_id', 
          label: 'Channel ID or URL', 
          type: 'text', 
          required: true,
          placeholder: 'UCxxxxxxxxxxxxxxxxxxx or https://youtube.com/@yourhandle',
          helpText: 'Your Channel ID, channel URL, or @handle. For testing: @SadhguruJV, @BeerBiceps, or @SaiBabaIsStillAlive'
        }
      ],
      instructions: 'Enable YouTube Data API v3 in Google Cloud Console and create an API key',
      helpLinks: [
        { text: 'How to get YouTube API Key', url: 'https://developers.google.com/youtube/v3/getting-started' },
        { text: 'Find your Channel ID', url: 'https://support.google.com/youtube/answer/3250431' }
      ]
    },
    instagram: {
      name: 'Instagram',
      color: 'bg-pink-500',
      icon: '📸',
      fields: [
        { 
          key: 'app_id', 
          label: 'App ID', 
          type: 'text', 
          required: true,
          placeholder: '1234567890123456',
          helpText: 'Numeric App ID from Facebook Developers console'
        },
        { 
          key: 'app_secret', 
          label: 'App Secret', 
          type: 'password', 
          required: true,
          placeholder: 'abcdef1234567890abcdef1234567890',
          helpText: 'App Secret from your Facebook app settings'
        },
        { 
          key: 'access_token', 
          label: 'Access Token', 
          type: 'password', 
          required: true,
          placeholder: 'IGQVJXxxxxxxxxxxxxxxxxxxxxxxx',
          helpText: 'Instagram User Access Token or Page Access Token'
        }
      ],
      instructions: 'Create app in Facebook Developers → Instagram Basic Display API',
      helpLinks: [
        { text: 'Instagram Basic Display Setup', url: 'https://developers.facebook.com/docs/instagram-basic-display-api' },
        { text: 'Get Access Tokens', url: 'https://developers.facebook.com/docs/instagram-basic-display-api/getting-started' }
      ]
    },
    facebook: {
      name: 'Facebook',
      color: 'bg-blue-500',
      icon: '👥',
      fields: [
        { 
          key: 'app_id', 
          label: 'App ID', 
          type: 'text', 
          required: true,
          placeholder: '1234567890123456',
          helpText: 'Your Facebook App ID (numeric)'
        },
        { 
          key: 'app_secret', 
          label: 'App Secret', 
          type: 'password', 
          required: true,
          placeholder: 'abcdef1234567890abcdef1234567890',
          helpText: 'App Secret from Facebook App Dashboard'
        },
        { 
          key: 'page_access_token', 
          label: 'Page Access Token', 
          type: 'password', 
          required: true,
          placeholder: 'EAAxxxxxxxxxxxxxxxxxxxxxxxxx',
          helpText: 'Never-expiring Page Access Token for your Facebook Page'
        }
      ],
      instructions: 'Create Facebook app with pages_manage_posts permissions',
      helpLinks: [
        { text: 'Facebook for Developers', url: 'https://developers.facebook.com/' },
        { text: 'Page Access Tokens', url: 'https://developers.facebook.com/docs/pages/access-tokens' }
      ]
    },
    tiktok: {
      name: 'TikTok',
      color: 'bg-gray-800',
      icon: '🎵',
      fields: [
        { 
          key: 'client_key', 
          label: 'Client Key', 
          type: 'text', 
          required: true,
          placeholder: 'aw1234567890abcdef',
          helpText: 'Client Key from TikTok for Business Developer Portal'
        },
        { 
          key: 'client_secret', 
          label: 'Client Secret', 
          type: 'password', 
          required: true,
          placeholder: 'abcdef1234567890abcdef1234567890abcdef12',
          helpText: 'Client Secret from your TikTok app configuration'
        }
      ],
      instructions: 'Apply for TikTok for Business API → Marketing API access',
      helpLinks: [
        { text: 'TikTok for Business', url: 'https://ads.tiktok.com/marketing_api/docs' },
        { text: 'Apply for API Access', url: 'https://ads.tiktok.com/marketing_api/docs?id=1738455508553729' }
      ]
    }
  };

  return (
    <div className="space-y-6">
      {/* Notifications (core.md: clear user feedback) */}
      {notifications.length > 0 && (
        <div className="space-y-2">
          {notifications.map((notification) => (
            <div
              key={notification.id}
              className={`p-4 rounded-lg border flex items-start justify-between ${
                notification.type === 'success' ? 'bg-green-50 border-green-200 text-green-800' :
                notification.type === 'error' ? 'bg-red-50 border-red-200 text-red-800' :
                notification.type === 'warning' ? 'bg-yellow-50 border-yellow-200 text-yellow-800' :
                'bg-blue-50 border-blue-200 text-blue-800'
              }`}
            >
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 mt-0.5">
                  {notification.type === 'success' && <CheckCircle size={16} />}
                  {notification.type === 'error' && <AlertCircle size={16} />}
                  {notification.type === 'warning' && <AlertCircle size={16} />}
                  {notification.type === 'info' && <Info size={16} />}
                </div>
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    {notification.platform && (
                      <span className="text-xs bg-white bg-opacity-50 px-2 py-1 rounded">
                        {notification.platform.toUpperCase()}
                      </span>
                    )}
                    <span className="font-medium">{notification.message}</span>
                  </div>
                  {notification.details?.troubleshooting && (
                    <details className="mt-2">
                      <summary className="text-sm cursor-pointer hover:underline">Troubleshooting Steps</summary>
                      <ul className="mt-1 text-sm space-y-1">
                        {notification.details.troubleshooting.map((step, idx) => (
                          <li key={idx} className="ml-4">• {step}</li>
                        ))}
                      </ul>
                    </details>
                  )}
                </div>
              </div>
              <button
                onClick={() => removeNotification(notification.id)}
                className="flex-shrink-0 ml-4 text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}

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
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <h4 className="font-semibold text-gray-900">{config.name}</h4>
                    {config.helpLinks && (
                      <button
                        onClick={() => setShowHelpFor(showHelpFor === platform ? null : platform)}
                        className="text-gray-400 hover:text-gray-600"
                      >
                        <HelpCircle size={16} />
                      </button>
                    )}
                  </div>
                  <p className="text-sm text-gray-500">{config.instructions}</p>
                  {showHelpFor === platform && config.helpLinks && (
                    <div className="mt-2 p-3 bg-gray-50 rounded border space-y-1">
                      <div className="text-sm font-medium text-gray-700">Helpful Links:</div>
                      {config.helpLinks.map((link, idx) => (
                        <div key={idx}>
                          <a
                            href={link.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm text-blue-600 hover:text-blue-800 flex items-center space-x-1"
                          >
                            <ExternalLink size={12} />
                            <span>{link.text}</span>
                          </a>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
              <div className="flex items-center space-x-2">
                {/* Enhanced status indicators (core.md: clear status communication) */}
                {isValidating[platform] && (
                  <div className="flex items-center space-x-1 text-blue-600 text-sm">
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-600 border-t-transparent"></div>
                    <span>Testing...</span>
                  </div>
                )}
                {!isValidating[platform] && testResults[platform] === 'success' && (
                  <div className="flex items-center space-x-1 text-green-600 text-sm">
                    <CheckCircle size={16} />
                    <span>Connected</span>
                  </div>
                )}
                {!isValidating[platform] && testResults[platform] === 'error' && (
                  <div className="flex items-center space-x-1 text-red-600 text-sm">
                    <AlertCircle size={16} />
                    <span>Failed</span>
                  </div>
                )}
                {!isValidating[platform] && !testResults[platform] && apiKeys[platform].status === 'connected' && (
                  <div className="flex items-center space-x-1 text-green-600 text-sm">
                    <CheckCircle size={16} />
                    <span>Saved</span>
                  </div>
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {config.fields.map((field) => {
                const fieldError = validationErrors[`${platform}_${field.key}`];
                const fieldValue = apiKeys[platform][field.key] || '';
                
                return (
                  <div key={field.key}>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {field.label} {field.required && <span className="text-red-500">*</span>}
                    </label>
                    <div className="relative">
                      <input
                        type={showSecrets[`${platform}_${field.key}`] ? 'text' : field.type}
                        value={fieldValue}
                        onChange={(e) => updateApiKey(platform, field.key, e.target.value)}
                        className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 transition-colors ${
                          fieldError 
                            ? 'border-red-300 focus:ring-red-500 focus:border-red-500' 
                            : fieldValue && !fieldError
                            ? 'border-green-300 focus:ring-green-500 focus:border-green-500'
                            : 'border-gray-300 focus:ring-purple-500 focus:border-purple-500'
                        }`}
                        placeholder={field.placeholder || `Enter ${field.label.toLowerCase()}`}
                        aria-describedby={`${platform}_${field.key}_help`}
                        aria-invalid={!!fieldError}
                      />
                      {field.type === 'password' && (
                        <button
                          type="button"
                          onClick={() => toggleSecret(platform, field.key)}
                          className="absolute right-2 top-2 text-gray-400 hover:text-gray-600"
                          aria-label={showSecrets[`${platform}_${field.key}`] ? 'Hide password' : 'Show password'}
                        >
                          {showSecrets[`${platform}_${field.key}`] ? <EyeOff size={16} /> : <Eye size={16} />}
                        </button>
                      )}
                      {/* Validation indicator (refresh.md: immediate feedback) */}
                      {!fieldError && fieldValue && (
                        <div className="absolute right-8 top-2 text-green-500">
                          <CheckCircle size={16} />
                        </div>
                      )}
                    </div>
                    
                    {/* Help text (core.md: clear guidance) */}
                    {field.helpText && (
                      <p id={`${platform}_${field.key}_help`} className="mt-1 text-xs text-gray-500">
                        {field.helpText}
                      </p>
                    )}
                    
                    {/* Validation error (refresh.md: actionable errors) */}
                    {fieldError && (
                      <p className="mt-1 text-xs text-red-600 flex items-center space-x-1" role="alert">
                        <AlertCircle size={12} />
                        <span>{fieldError}</span>
                      </p>
                    )}
                  </div>
                );
              })}
            </div>

            <div className="flex space-x-3 mt-4">
              <button
                onClick={() => saveConfiguration(platform)}
                disabled={loading || isValidating[platform]}
                className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 transition-all"
              >
                {loading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                ) : (
                  <Save size={16} />
                )}
                <span>{loading ? 'Saving...' : 'Save'}</span>
              </button>
              <button
                onClick={() => testConnection(platform)}
                disabled={loading || isValidating[platform]}
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 transition-all"
              >
                {isValidating[platform] ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                ) : (
                  <TestTube size={16} />
                )}
                <span>{isValidating[platform] ? 'Testing...' : 'Test Connection'}</span>
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