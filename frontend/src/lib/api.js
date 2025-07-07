// Removed: import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://jyotiflow-ai.onrender.com';

const spiritualAPI = {
  // Base request method
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
        ...this.getAuthHeaders(),
      },
      credentials: 'include',
      ...options,
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
  },

  // GET request
  async get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  },

  // POST request
  async post(endpoint, data) {
    return this.request(endpoint, { method: 'POST', body: JSON.stringify(data) });
  },

  // Platform statistics
  async loadPlatformStats() {
    try {
      const response = await this.get('/api/services/stats');
      if (response && response.success) {
        return response.data;
      }
      // Fallback to reasonable defaults if API fails
      return {
        totalUsers: 1000,
        totalSessions: 2500,
        communityMembers: 150,
        countriesReached: 25
      };
    } catch (error) {
      console.log('🕉️ Platform stats loading blessed with patience:', error);
      return {
        totalUsers: 1000,
        totalSessions: 2500,
        communityMembers: 150,
        countriesReached: 25
      };
    }
  },

  // Engagement tracking
  async trackSpiritualEngagement(eventType, data) {
    try {
      console.log(`🕉️ Spiritual engagement tracked: ${eventType}`, data);
      // Mock tracking - replace with real analytics later
      return { success: true };
    } catch (error) {
      console.log('🕉️ Engagement tracking blessed with patience:', error);
      return { success: false };
    }
  },

  // Authentication methods
  async login(email, password) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password })
      });
      const data = await response.json();
      
      // Check for access_token to determine success
      if (data.access_token && data.user) {
        // Set admin role if admin email
        const user = {
          ...data.user,
          role: this.isAdminEmail(email) ? 'admin' : (data.user.role || 'user')
        };
        
        this.setAuthToken(data.access_token, user);
        return { success: true, user: user, token: data.access_token };
      } else {
        return { success: false, message: data.detail || 'Invalid credentials' };
      }
    } catch (error) {
      console.error('Login API error:', error);
      return { success: false, message: 'Network error' };
    }
  },

  // Helper method to check if email is admin
  isAdminEmail(email) {
    const adminEmails = ['admin@jyotiflow.ai', 'admin@gmail.com'];
    return adminEmails.includes(email.toLowerCase());
  },

  // Helper method to check if current user is admin
  isCurrentUserAdmin() {
    const user = JSON.parse(localStorage.getItem('jyotiflow_user') || '{}');
    return user.role === 'admin' || this.isAdminEmail(user.email || '');
  },

  async register(userData) {
    try {
      // Map 'name' to 'full_name' for backend compatibility
      const payload = {
        ...userData,
        full_name: userData.name || userData.full_name || '',
      };
      delete payload.name;
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });
      
      const data = await response.json();
      if (data.success && data.data && data.data.token) {
        this.setAuthToken(data.data.token, data.data.user);
      }
      return data;
    } catch (error) {
      console.error('Register API error:', error);
      return { success: false, message: 'Network error' };
    }
  },

  setAuthToken(token, user) {
    localStorage.setItem('jyotiflow_token', token);
    localStorage.setItem('jyotiflow_user', JSON.stringify(user));
    console.log('Divine token stored successfully');
    
    // Trigger auth state change event for components
    window.dispatchEvent(new CustomEvent('auth-state-changed', { 
      detail: { authenticated: true, user } 
    }));
  },

  isAuthenticated() {
    const token = localStorage.getItem('jyotiflow_token');
    return !!token;
  },

  logout() {
    localStorage.removeItem('jyotiflow_token');
    localStorage.removeItem('jyotiflow_user');
    console.log('Sacred logout completed');
    
    // Trigger auth state change event
    window.dispatchEvent(new CustomEvent('auth-state-changed', { 
      detail: { authenticated: false, user: null } 
    }));
  },

  getAuthHeaders() {
    const token = localStorage.getItem('jyotiflow_token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  },

  // Spiritual guidance methods
  async submitSpiritualQuestion(questionData) {
    const language = localStorage.getItem('jyotiflow_language') || 'en';
    return this.post('/api/spiritual/guidance', { ...questionData, language });
  },

  async getSpiritualResponse(sessionId) {
    return this.get(`/api/spiritual/response/${sessionId}`);
  },

  // User profile methods
  async getUserProfile() {
    return this.get('/api/user/profile');
  },

  async updateUserProfile(profileData) {
    return this.post('/api/user/profile', profileData);
  },

  // Session history
  async getSessionHistory() {
    return this.get('/api/user/sessions');
  },

  // Credits and billing
  async getCreditBalance() {
    return this.get('/api/user/credits');
  },
  
// Admin methods - Add these before getDailyWisdom()
  async getAdminStats() {
    return this.get('/api/admin/stats');
  },

  async getMonetizationInsights() {
    return this.get('/api/admin/monetization');
  },

  async getProductOptimization() {
    return this.get('/api/admin/optimization');
  },

  async initiateLiveChat(sessionDetails) {
    return this.post('/api/livechat/initiate', sessionDetails);
  },

  async endLiveChat(sessionId) {
    return this.request(`/api/livechat/end/${sessionId}`, { method: 'DELETE' });
  },

  async startSession(sessionData) {
    return this.post('/api/sessions/start', sessionData);
  },

  async generateAvatarVideo(guidanceText, birthDetails) {
    return this.post('/api/avatar/generate', {
      guidance_text: guidanceText,
      birth_details: birthDetails
    });
  },

  async getAvatarGenerationStatus(sessionId) {
    return this.get(`/api/avatar/status/${sessionId}`);
  },

  async purchaseCredits(amount) {
    return this.post('/api/credits/purchase', { amount });
  },

  // Daily content methods
  async getDailyWisdom() {
    return this.get('/api/content/daily-wisdom');
  },

  async getSatsangSchedule() {
    return this.get('/api/content/satsang-schedule');
  },

  async getSpiritualQuote() {
    return this.get('/api/content/spiritual-quote');
  },

  // Admin: Get all users
  async getAdminUsers() {
    return this.get('/api/admin/users');
  },

  // Admin: Get all content
  async getAdminContent() {
    return this.get('/api/admin/content');
  },

  // Admin overview (for dashboard)
  async getAdminOverview() {
    return this.get('/api/admin/overview');
  },

  // Admin product management methods
  async createAdminProduct(productData) {
    return this.post('/api/admin/products', productData);
  },

  async updateAdminProduct(productId, productData) {
    return this.post(`/api/admin/products/${productId}`, productData);
  },

  async deleteAdminProduct(productId) {
    return this.request(`/api/admin/products/${productId}`, { method: 'DELETE' });
  },

  async getAdminProducts() {
    return this.get('/api/admin/products');
  },

  async syncStripeProducts() {
    return this.post('/api/admin/stripe/sync-products');
  },

  // Admin: Get platform settings
  async getAdminSettings() {
    return this.get('/api/admin/platform-settings');
  },

  // Admin: Get all satsang events
  async getAdminSatsangs() {
    return this.get('/api/admin/satsang-events');
  },

  // Admin: Get subscription plans
  async getAdminSubscriptionPlans() {
    return this.get('/api/admin/subscription-plans');
  },

  // Admin: Get revenue analytics
  async getAdminRevenueAnalytics() {
    return this.get('/api/admin/revenue-insights');
  },

  // Admin: Get business intelligence (AI insights)
  async getAdminBI() {
    return this.get('/api/admin/ai-insights');
  },

  // AI Pricing Recommendations
  async getAIPricingRecommendations() {
    return this.get('/api/admin/ai-pricing-recommendations');
  },

  async approveAIRecommendation(recommendationId) {
    return this.post(`/api/admin/ai-pricing-recommendations/${recommendationId}/approve`);
  },

  async rejectAIRecommendation(recommendationId) {
    return this.post(`/api/admin/ai-pricing-recommendations/${recommendationId}/reject`);
  },

  async triggerDailyAnalysis() {
    return this.post('/api/admin/trigger-daily-analysis');
  },

  // Service Types Management
  async getServiceTypes() {
    return this.get('/api/admin/products/service-types');
  },

  async createServiceType(serviceTypeData) {
    return this.post('/api/admin/products/service-types', serviceTypeData);
  },

  async updateServiceType(serviceTypeId, serviceTypeData) {
    return this.request(`/api/admin/products/service-types/${serviceTypeId}`, {
      method: 'PUT',
      body: JSON.stringify(serviceTypeData)
    });
  },

  async deleteServiceType(serviceTypeId) {
    return this.request(`/api/admin/products/service-types/${serviceTypeId}`, { method: 'DELETE' });
  },

  // Pricing Configuration Management
  async getPricingConfig() {
    return this.get('/api/admin/products/pricing-config');
  },

  async createPricingConfig(configData) {
    return this.post('/api/admin/products/pricing-config', configData);
  },

  async updatePricingConfig(configKey, configData) {
    return this.request(`/api/admin/products/pricing-config/${configKey}`, { 
      method: 'PUT', 
      body: JSON.stringify(configData) 
    });
  },

  // Donations Management
  async getDonations() {
    return this.get('/api/admin/products/donations');
  },

  async createDonation(donationData) {
    return this.post('/api/admin/products/donations', donationData);
  },

  async updateDonation(donationId, donationData) {
    return this.request(`/api/admin/products/donations/${donationId}`, { 
      method: 'PUT', 
      body: JSON.stringify(donationData) 
    });
  },

  async deleteDonation(donationId) {
    return this.request(`/api/admin/products/donations/${donationId}`, { method: 'DELETE' });
  },

  // Donation Payment Processing
  async processDonation(donationData) {
    return this.post('/api/donations/process', donationData);
  },

  async confirmDonation(paymentIntentId) {
    return this.post('/api/donations/confirm', { payment_intent_id: paymentIntentId });
  },

  async getDonationHistory() {
    return this.get('/api/donations/history');
  },

  async getDonationAnalytics() {
    return this.get('/api/donations/analytics');
  },

  async getSessionTotalDonations(sessionId) {
    return this.get(`/api/donations/session-total/${sessionId}`);
  },

  async getMonthlyTopDonors() {
    return this.get('/api/donations/top-donors/monthly');
  },

  // Credit Packages
  async getCreditPackages() {
    return this.get('/api/credits/packages');
  },

  async purchaseCredits(packageId) {
    return this.post('/api/credits/purchase', { package_id: packageId });
  },

  // Admin: Social Content Management
  async getAdminSocialContent() {
    return this.get('/api/admin/social-content');
  },

  async createAdminSocialContent(contentData) {
    return this.post('/api/admin/social-content/schedule', contentData);
  },

  async updateAdminSocialContent(contentId, contentData) {
    return this.request(`/api/admin/social-content/${contentId}`, {
      method: 'PUT',
      body: JSON.stringify(contentData)
    });
  },

  async deleteAdminSocialContent(contentId) {
    return this.request(`/api/admin/social-content/${contentId}`, { method: 'DELETE' });
  },

  // Notification/Follow-up
  async sendFollowupNotification({ channel, to, subject, message, device_token }) {
    return this.post('/api/notify/followup', { channel, to, subject, message, device_token });
  },

  // ===== AVATAR GENERATION ENDPOINTS =====
  
  async generateAvatarWithGuidance(data) {
    return this.post('/api/avatar/generate-with-guidance', data);
  },

  async getAvatarGenerationStatusDetailed(sessionId) {
    return this.get(`/api/avatar/status/${sessionId}`);
  },

  async testAvatarServices() {
    return this.get('/api/avatar/services/test');
  },

  async createSwamjiPresenter() {
    return this.post('/api/avatar/presenter/create', {});
  },

  async getUserAvatarHistory(limit = 10) {
    return this.get(`/api/avatar/user/history?limit=${limit}`);
  },

  // ===== ENHANCED SPIRITUAL GUIDANCE =====
  
  async getEnhancedSpiritualGuidance(requestData) {
    return this.post('/api/spiritual/enhanced/enhanced-guidance', requestData);
  },

  async getServiceInsights(serviceName) {
    return this.get(`/api/spiritual/enhanced/service-insights/${serviceName}`);
  },

  async getKnowledgeDomains() {
    return this.get('/api/spiritual/enhanced/knowledge-domains');
  },

  async getPersonaModes() {
    return this.get('/api/spiritual/enhanced/persona-modes');
  },

  async getComprehensiveReading(requestData) {
    return this.post('/api/spiritual/enhanced/comprehensive-reading', requestData);
  },

  async getComprehensivePricing() {
    return this.get('/api/spiritual/enhanced/comprehensive-pricing');
  },

  async getPricingDashboard() {
    return this.get('/api/spiritual/enhanced/pricing-dashboard');
  },

  // ===== UNIVERSAL PRICING ENDPOINTS =====
  
  async getPricingRecommendations() {
    return this.get('/api/spiritual/enhanced/pricing-recommendations');
  },

  async applyPricingChange(pricingData) {
    return this.post('/api/spiritual/enhanced/apply-pricing-change', pricingData);
  },

  async getPricingHistory(serviceName, limit = 50) {
    return this.get(`/api/spiritual/enhanced/pricing-history/${serviceName}?limit=${limit}`);
  },

  async getSatsangEvents(status = null) {
    let endpoint = '/api/spiritual/enhanced/satsang-events';
    if (status) endpoint += `?status=${status}`;
    return this.get(endpoint);
  },

  async createSatsangEvent(eventData) {
    return this.post('/api/spiritual/enhanced/satsang-events', eventData);
  },

  async getSatsangPricing(eventId) {
    return this.get(`/api/spiritual/enhanced/satsang-pricing/${eventId}`);
  },

  async getSatsangDonations(eventId) {
    return this.get(`/api/spiritual/enhanced/satsang-donations/${eventId}`);
  },

  async getAPIUsageMetrics(days = 7) {
    return this.get(`/api/spiritual/enhanced/api-usage-metrics?days=${days}`);
  },

  async trackAPIUsage(usageData) {
    return this.post('/api/spiritual/enhanced/track-api-usage', usageData);
  },

  async getSystemHealth() {
    return this.get('/api/spiritual/enhanced/system-health');
  },
};

export default spiritualAPI;

