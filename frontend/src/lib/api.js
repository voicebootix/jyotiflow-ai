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
      // Mock data to prevent crashes - replace with real API later
      return {
        totalUsers: 25000,
        totalSessions: 75000,
        communityMembers: 8000,
        countriesReached: 67
      };
    } catch (error) {
      console.log('🕉️ Platform stats loading blessed with patience:', error);
      return {};
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
      if (data.success && data.data && data.data.token) {
        this.setAuthToken(data.data.token, data.data.user);
      }
      return data;
    } catch (error) {
      console.error('Login API error:', error);
      return { success: false, message: 'Network error' };
    }
  },

  async register(userData) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData)
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

  // Credit Packages Management
  async getCreditPackages() {
    return this.get('/api/admin/products/credit-packages');
  },

  async createCreditPackage(packageData) {
    return this.post('/api/admin/products/credit-packages', packageData);
  },

  async updateCreditPackage(packageId, packageData) {
    return this.request(`/api/admin/products/credit-packages/${packageId}`, { 
      method: 'PUT', 
      body: JSON.stringify(packageData) 
    });
  },

  async deleteCreditPackage(packageId) {
    return this.request(`/api/admin/products/credit-packages/${packageId}`, { method: 'DELETE' });
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
};

export default spiritualAPI;

