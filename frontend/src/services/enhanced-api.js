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
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...this.getAuthHeaders(),
        ...(options.headers || {})
      },
      credentials: 'include',
      ...options
    };

    try {
      const response = await fetch(url, config);
      
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
    return this.post('/api/admin/social-marketing/platform-config', configData);
  }

  async testConnection(connectionData) {
    return this.post('/api/admin/social-marketing/test-connection', connectionData);
  }

  // Avatar Methods
  async getSwamjiAvatarConfig() {
    return this.get('/api/admin/social-marketing/swamji-avatar-config');
  }

  async uploadSwamjiImage(formData) {
    return this.request('/api/admin/social-marketing/upload-swamiji-image', {
      method: 'POST',
      body: formData,
      headers: {
        // Don't set Content-Type for FormData, let browser set it
        ...this.getAuthHeaders()
      }
    });
  }

  async generateAvatarPreview(previewData) {
    return this.post('/api/admin/social-marketing/generate-avatar-preview', previewData);
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