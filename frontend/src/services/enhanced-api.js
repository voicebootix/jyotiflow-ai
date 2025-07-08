/**
 * Enhanced API Wrapper for JyotiFlow
 * This file bridges the gap between new enhanced features and the main API client
 */

import spiritualAPI from '../lib/api.js';

// Enhanced API wrapper that extends the main API client
class EnhancedAPIWrapper {
  constructor() {
    this.mainAPI = spiritualAPI;
  }

  // ===== AVATAR GENERATION ENDPOINTS =====
  async post(endpoint, data) {
    return this.mainAPI.post(endpoint, data);
  }

  async get(endpoint) {
    return this.mainAPI.get(endpoint);
  }

  // Service types - direct pass-through to main API
  async getServiceTypes() {
    return this.mainAPI.getServiceTypes();
  }

  // Avatar generation with spiritual guidance (fixed endpoint)
  async generateAvatarWithGuidance(data) {
    return this.mainAPI.post('/api/avatar/generate-with-guidance', data);
  }

  // Avatar status check (fixed endpoint)
  async getAvatarStatus(sessionId) {
    return this.mainAPI.get(`/api/avatar/status/${sessionId}`);
  }

  // ===== SOCIAL MEDIA MARKETING ENDPOINTS =====
  
  // Marketing overview
  async getMarketingOverview() {
    return this.mainAPI.get('/api/admin/social-marketing/overview');
  }

  // Content calendar
  async getContentCalendar(params = {}) {
    let endpoint = '/api/admin/social-marketing/content-calendar';
    const queryParams = new URLSearchParams();
    
    if (params.date) queryParams.append('date', params.date);
    if (params.platform) queryParams.append('platform', params.platform);
    
    if (queryParams.toString()) {
      endpoint += `?${queryParams.toString()}`;
    }
    
    return this.mainAPI.get(endpoint);
  }

  // Campaigns management
  async getCampaigns(params = {}) {
    let endpoint = '/api/admin/social-marketing/campaigns';
    const queryParams = new URLSearchParams();
    
    if (params.status) queryParams.append('status', params.status);
    if (params.platform) queryParams.append('platform', params.platform);
    
    if (queryParams.toString()) {
      endpoint += `?${queryParams.toString()}`;
    }
    
    return this.mainAPI.get(endpoint);
  }

  // Generate daily content
  async generateDailyContent(data = {}) {
    return this.mainAPI.post('/api/admin/social-marketing/generate-daily-content', data);
  }

  // Execute automated posting
  async executePosting() {
    return this.mainAPI.post('/api/admin/social-marketing/execute-posting', {});
  }

  // Marketing analytics
  async getMarketingAnalytics(params = {}) {
    let endpoint = '/api/admin/social-marketing/analytics';
    const queryParams = new URLSearchParams();
    
    if (params.date_range) queryParams.append('date_range', params.date_range);
    if (params.platform) queryParams.append('platform', params.platform);
    
    if (queryParams.toString()) {
      endpoint += `?${queryParams.toString()}`;
    }
    
    return this.mainAPI.get(endpoint);
  }

  // Performance metrics
  async getPerformanceMetrics() {
    return this.mainAPI.get('/api/admin/social-marketing/performance');
  }

  // Comment management
  async getComments(params = {}) {
    let endpoint = '/api/admin/social-marketing/comments';
    const queryParams = new URLSearchParams();
    
    if (params.platform) queryParams.append('platform', params.platform);
    if (params.status) queryParams.append('status', params.status);
    
    if (queryParams.toString()) {
      endpoint += `?${queryParams.toString()}`;
    }
    
    return this.mainAPI.get(endpoint);
  }

  // Execute comment responses
  async executeCommentResponses() {
    return this.mainAPI.post('/api/admin/social-marketing/comments/respond', {});
  }

  // Automation settings
  async getAutomationSettings() {
    return this.mainAPI.get('/api/admin/social-marketing/automation-settings');
  }

  // Update automation settings
  async updateAutomationSettings(settings) {
    return this.mainAPI.request('/api/admin/social-marketing/automation-settings', {
      method: 'PUT',
      body: JSON.stringify(settings)
    });
  }

  // Create campaign
  async createCampaign(campaignData) {
    return this.mainAPI.post('/api/admin/social-marketing/campaigns', campaignData);
  }

  // ===== ENHANCED SPIRITUAL GUIDANCE =====
  
  // Enhanced guidance with cultural context
  async getEnhancedGuidance(requestData) {
    return this.mainAPI.post('/api/spiritual/enhanced/guidance', requestData);
  }

  // Service insights
  async getServiceInsights(serviceName) {
    return this.mainAPI.get(`/api/spiritual/enhanced/service-insights/${serviceName}`);
  }

  // Knowledge domains
  async getKnowledgeDomains() {
    return this.mainAPI.get('/api/spiritual/enhanced/knowledge-domains');
  }

  // Persona modes
  async getPersonaModes() {
    return this.mainAPI.get('/api/spiritual/enhanced/persona-modes');
  }

  // Comprehensive reading
  async getComprehensiveReading(requestData) {
    return this.mainAPI.post('/api/spiritual/enhanced/comprehensive-reading', requestData);
  }

  // ===== UNIVERSAL PRICING =====
  
  // Pricing recommendations
  async getPricingRecommendations() {
    return this.mainAPI.get('/api/admin/universal-pricing/pricing-recommendations');
  }

  // Apply pricing changes
  async applyPricingChange(pricingData) {
    return this.mainAPI.post('/api/admin/universal-pricing/apply-pricing-change', pricingData);
  }

  // Pricing history
  async getPricingHistory(serviceName, limit = 50) {
    return this.mainAPI.get(`/api/admin/universal-pricing/pricing-history/${serviceName}?limit=${limit}`);
  }

  // Satsang events
  async getSatsangEvents(status = null) {
    let endpoint = '/api/admin/universal-pricing/satsang-events';
    if (status) endpoint += `?status=${status}`;
    return this.mainAPI.get(endpoint);
  }

  // Create satsang event
  async createSatsangEvent(eventData) {
    return this.mainAPI.post('/api/admin/universal-pricing/satsang-events', eventData);
  }

  // API usage metrics
  async getAPIUsageMetrics(days = 7) {
    return this.mainAPI.get(`/api/admin/universal-pricing/api-usage-metrics?days=${days}`);
  }

  // Track API usage
  async trackAPIUsage(usageData) {
    return this.mainAPI.post('/api/admin/universal-pricing/track-api-usage', usageData);
  }

  // System health
  async getSystemHealth() {
    return this.mainAPI.get('/api/admin/universal-pricing/system-health');
  }

  // ===== AUTHENTICATION PASS-THROUGH =====
  
  isAuthenticated() {
    return this.mainAPI.isAuthenticated();
  }

  getAuthHeaders() {
    return this.mainAPI.getAuthHeaders();
  }

  // ===== UTILITY METHODS =====
  
  async request(endpoint, options = {}) {
    return this.mainAPI.request(endpoint, options);
  }
}

// Create and export the enhanced API instance
const enhanced_api = new EnhancedAPIWrapper();

export default enhanced_api;