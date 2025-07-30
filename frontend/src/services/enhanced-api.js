/**
 * Enhanced API Wrapper for JyotiFlow
 * This file bridges the gap between new enhanced features and the main API client
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://jyotiflow-ai.onrender.com';

class EnhancedAPI {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  getAuthHeaders() {
    const token = localStorage.getItem('jyotiflow_token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...this.getAuthHeaders(),
      ...(options.headers || {})
    };

    // CORE.MD: Do not set Content-Type for FormData, let the browser handle it.
    if (options.body instanceof FormData) {
      delete headers['Content-Type'];
    }

    const config = {
      headers,
      credentials: 'include',
      ...options
    };

    try {
      const response = await fetch(url, config);
      
      // CRITICAL FIX: Handle 401 Unauthorized (token expiry) with auto-redirect
      if (response.status === 401) {
        console.error('🔐 Authentication failed - token may have expired');
        
        // Clear expired token
        localStorage.removeItem('jyotiflow_token');
        localStorage.removeItem('jyotiflow_user');
        
        // Redirect to admin login for admin endpoints
        if (endpoint.includes('/admin/')) {
          console.log('🔐 Redirecting to admin login due to token expiry');
          window.location.href = '/login?admin=true&redirect=' + encodeURIComponent(window.location.pathname);
          return { success: false, message: 'Authentication expired - redirecting to login', status: 401 };
        }
        
        return { success: false, message: 'Authentication expired', status: 401 };
      }
      
      if (!response.ok) {
        console.error(`API Error: ${response.status} - ${response.statusText}`);
        return { success: false, message: `Server error: ${response.status}`, status: response.status };
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API request failed:', error);
      return { success: false, message: 'Network connection failed', error: error.message };
    }
  }

  async get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  }

  async post(endpoint, data) {
    return this.request(endpoint, { method: 'POST', body: JSON.stringify(data) });
  }

  async put(endpoint, data) {
    return this.request(endpoint, { method: 'PUT', body: JSON.stringify(data) });
  }

  async patch(endpoint, data) {
    return this.request(endpoint, { method: 'PATCH', body: JSON.stringify(data) });
  }

  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }

  // Social Media Marketing API Methods
  async getMarketingOverview() {
    return this.get('/api/admin/social-marketing/overview');
  }

  async getContentCalendar(date = null, platform = null) {
    const params = new URLSearchParams();
    if (date) params.append('date', date);
    if (platform) params.append('platform', platform);
    const query = params.toString() ? `?${params.toString()}` : '';
    return this.get(`/api/admin/social-marketing/content-calendar${query}`);
  }

  async getCampaigns(status = null, platform = null) {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (platform) params.append('platform', platform);
    const query = params.toString() ? `?${params.toString()}` : '';
    return this.get(`/api/admin/social-marketing/campaigns${query}`);
  }

  async generateDailyContent(request = {}) {
    const defaultRequest = {
      platforms: ["youtube", "instagram", "facebook", "tiktok"],
      content_types: ["daily_wisdom", "spiritual_quote", "satsang_promo"]
    };
    return this.post('/api/admin/social-marketing/generate-daily-content', { ...defaultRequest, ...request });
  }

  async executePosting() {
    return this.post('/api/admin/social-marketing/execute-posting', {});
  }

  async getAnalytics(dateRange = '7d', platform = null) {
    const params = new URLSearchParams();
    params.append('date_range', dateRange);
    if (platform) params.append('platform', platform);
    return this.get(`/api/admin/social-marketing/analytics?${params.toString()}`);
  }

  async getPerformanceMetrics() {
    return this.get('/api/admin/social-marketing/performance');
  }

  async getComments(platform = null, status = null) {
    const params = new URLSearchParams();
    if (platform) params.append('platform', platform);
    if (status) params.append('status', status);
    const query = params.toString() ? `?${params.toString()}` : '';
    return this.get(`/api/admin/social-marketing/comments${query}`);
  }

  async executeCommentResponses() {
    return this.post('/api/admin/social-marketing/comments/respond', {});
  }

  async getAutomationSettings() {
    return this.get('/api/admin/social-marketing/automation-settings');
  }

  async updateAutomationSettings(settings) {
    return this.put('/api/admin/social-marketing/automation-settings', settings);
  }

  async createCampaign(campaignData) {
    return this.post('/api/admin/social-marketing/campaigns', campaignData);
  }

  // Platform Configuration Methods
  async getPlatformConfig() {
    return this.get('/api/admin/social-marketing/platform-config');
  }

  async updatePlatformConfig(configData) {
    return this.patch('/api/admin/social-marketing/platform-config', configData);
  }

  async testConnection(connectionData) {
    return this.post('/api/admin/social-marketing/test-connection', connectionData);
  }

  // Avatar Methods
  getSwamjiAvatarConfig() {
    return this.get('/api/admin/social-marketing/swamiji-avatar-config');
  }

  async uploadSwamjiImage(formData) {
    return this.request('/api/admin/social-marketing/upload-swamiji-image', {
      method: 'POST',
      body: formData
    });
  }

  async generateImagePreview(previewData) {
    return this.post('/api/admin/social-marketing/generate-image-preview', previewData);
  }

  async generateVideoFromPreview(videoData) {
    return this.post('/api/admin/social-marketing/generate-video-from-preview', videoData);
  }

  async approveSwamjiAvatar(avatarData) {
    return this.post('/api/admin/social-marketing/approve-swamiji-avatar', avatarData);
  }

  // Agent Chat
  async sendAgentMessage(message) {
    return this.post('/api/admin/social-marketing/agent-chat', { message });
  }
}

const enhanced_api = new EnhancedAPI();
export default enhanced_api;