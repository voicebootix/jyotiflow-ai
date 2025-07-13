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
        // Trust backend role data - no more hardcoded email checking
        const user = {
          ...data.user,
          role: data.user.role || 'user'
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
    return user.role === 'admin';
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
    return this.get('/api/health');
  },

  // Enhanced admin dashboard methods
  async getAdminAnalytics() {
    return this.get('/api/admin/analytics/overview');
  },

  async getSessionAnalytics() {
    return this.get('/api/admin/analytics/sessions');
  },

  async getActiveSessions() {
    return this.get('/api/admin/analytics/sessions/active');
  },

  async getSessionStats() {
    return this.get('/api/admin/analytics/sessions/stats');
  },

  async getIntegrationsStatus() {
    return this.get('/api/admin/analytics/integrations/status');
  },

  async getDatabaseStats() {
    return this.get('/api/admin/analytics/database/stats');
  },

  async runDatabaseMigrations() {
    return this.post('/api/admin/analytics/database/migrate', {});
  },

  async getKnowledgeSeedingStatus() {
    return this.get('/api/admin/analytics/knowledge/seeding-status');
  },

  async seedKnowledgeBase() {
    return this.post('/api/admin/analytics/knowledge/seed', {});
  },

  async getKnowledgeDomainsAdmin() {
    return this.get('/api/spiritual/enhanced/knowledge-domains');
  },

  async getEnhancedSystemHealth() {
    return this.get('/api/spiritual/enhanced/health');
  },

  async getPersonaModesAdmin() {
    return this.get('/api/spiritual/enhanced/persona-modes');
  },

  async getAIInsights() {
    return this.get('/api/admin/analytics/ai-insights');
  },

  async getAIPricingRecommendationsAdmin() {
    return this.get('/api/admin/analytics/ai-pricing-recommendations');
  },

  async updateAIPricingRecommendation(recommendationId, action) {
    return this.post(`/api/admin/analytics/ai-pricing-recommendations/${recommendationId}/${action}`, {});
  },

  // Follow-up system methods
  async getFollowUpTemplates() {
    return this.get('/api/admin/followup/templates');
  },

  async createFollowUpTemplate(templateData) {
    return this.post('/api/admin/followup/templates', templateData);
  },

  async updateFollowUpTemplate(templateId, templateData) {
    return this.request(`/api/admin/followup/templates/${templateId}`, {
      method: 'PUT',
      body: JSON.stringify(templateData)
    });
  },

  async deleteFollowUpTemplate(templateId) {
    return this.request(`/api/admin/followup/templates/${templateId}`, {
      method: 'DELETE'
    });
  },

  async getFollowUpSchedules() {
    return this.get('/api/admin/followup/schedules');
  },

  async scheduleFollowUp(scheduleData) {
    return this.post('/api/admin/followup/schedules', scheduleData);
  },

  async cancelFollowUp(scheduleId) {
    return this.request(`/api/admin/followup/schedules/${scheduleId}/cancel`, {
      method: 'POST'
    });
  },

  async getFollowUpAnalytics() {
    return this.get('/api/admin/followup/analytics');
  },

  async getFollowUpSettings() {
    return this.get('/api/admin/followup/settings');
  },

  async updateFollowUpSettings(settingsData) {
    return this.request('/api/admin/followup/settings', {
      method: 'PUT',
      body: JSON.stringify(settingsData)
    });
  },

  // Enhanced social media methods
  async getSocialMediaCampaigns() {
    return this.get('/api/admin/social-media/campaigns');
  },

  async createSocialMediaCampaign(campaignData) {
    return this.post('/api/admin/social-media/campaigns', campaignData);
  },

  async updateSocialMediaCampaign(campaignId, campaignData) {
    return this.request(`/api/admin/social-media/campaigns/${campaignId}`, {
      method: 'PUT',
      body: JSON.stringify(campaignData)
    });
  },

  async deleteSocialMediaCampaign(campaignId) {
    return this.request(`/api/admin/social-media/campaigns/${campaignId}`, {
      method: 'DELETE'
    });
  },

  async getSocialMediaAnalytics() {
    return this.get('/api/admin/social-media/analytics');
  },

  async getSocialMediaPerformance() {
    return this.get('/api/admin/social-media/performance');
  },

  async getAutomationSettings() {
    return this.get('/api/admin/social-media/automation/settings');
  },

  async updateAutomationSettings(settingsData) {
    return this.request('/api/admin/social-media/automation/settings', {
      method: 'PUT',
      body: JSON.stringify(settingsData)
    });
  },

  async triggerAutomation(automationType) {
    return this.post(`/api/admin/social-media/automation/trigger/${automationType}`, {});
  },

  // Enhanced user management methods
  async getUsersWithDetails() {
    return this.get('/api/admin/users/detailed');
  },

  async updateUserRole(userId, role) {
    return this.request(`/api/admin/users/${userId}/role`, {
      method: 'PUT',
      body: JSON.stringify({ role })
    });
  },

  async updateUserCredits(userId, credits) {
    return this.request(`/api/admin/users/${userId}/credits`, {
      method: 'PUT',
      body: JSON.stringify({ credits })
    });
  },

  async getUserSessionHistory(userId) {
    return this.get(`/api/admin/users/${userId}/sessions`);
  },

  async getUserCreditHistory(userId) {
    return this.get(`/api/admin/users/${userId}/credits/history`);
  },

  async suspendUser(userId, reason) {
    return this.post(`/api/admin/users/${userId}/suspend`, { reason });
  },

  async unsuspendUser(userId) {
    return this.post(`/api/admin/users/${userId}/unsuspend`, {});
  },

  // Enhanced product management methods
  async getProductsWithAnalytics() {
    return this.get('/api/admin/products/analytics');
  },

  async getProductPerformance(productId) {
    return this.get(`/api/admin/products/${productId}/performance`);
  },

  async updateProductStatus(productId, status) {
    return this.request(`/api/admin/products/${productId}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status })
    });
  },

  async duplicateProduct(productId) {
    return this.post(`/api/admin/products/${productId}/duplicate`, {});
  },

  // Enhanced revenue analytics methods
  async getRevenueBreakdown(period = '30d') {
    return this.get(`/api/admin/revenue/breakdown?period=${period}`);
  },

  async getRevenueForecasting() {
    return this.get('/api/admin/revenue/forecasting');
  },

  async getRevenueByProduct(period = '30d') {
    return this.get(`/api/admin/revenue/by-product?period=${period}`);
  },

  async getRevenueByUser(period = '30d') {
    return this.get(`/api/admin/revenue/by-user?period=${period}`);
  },

  async getRevenueMetrics() {
    return this.get('/api/admin/revenue/metrics');
  },

  async exportRevenueData(period = '30d', format = 'csv') {
    return this.get(`/api/admin/revenue/export?period=${period}&format=${format}`);
  },

  // Enhanced notifications methods
  async getNotificationTemplates() {
    return this.get('/api/admin/notifications/templates');
  },

  async createNotificationTemplate(templateData) {
    return this.post('/api/admin/notifications/templates', templateData);
  },

  async updateNotificationTemplate(templateId, templateData) {
    return this.request(`/api/admin/notifications/templates/${templateId}`, {
      method: 'PUT',
      body: JSON.stringify(templateData)
    });
  },

  async deleteNotificationTemplate(templateId) {
    return this.request(`/api/admin/notifications/templates/${templateId}`, {
      method: 'DELETE'
    });
  },

  async sendBulkNotification(notificationData) {
    return this.post('/api/admin/notifications/bulk', notificationData);
  },

  async getNotificationAnalytics() {
    return this.get('/api/admin/notifications/analytics');
  },

  async getNotificationHistory() {
    return this.get('/api/admin/notifications/history');
  },

  // Enhanced settings methods
  async getSystemSettings() {
    return this.get('/api/admin/settings/system');
  },

  async updateSystemSettings(settingsData) {
    return this.request('/api/admin/settings/system', {
      method: 'PUT',
      body: JSON.stringify(settingsData)
    });
  },

  async getAPISettings() {
    return this.get('/api/admin/settings/api');
  },

  async updateAPISettings(settingsData) {
    return this.request('/api/admin/settings/api', {
      method: 'PUT',
      body: JSON.stringify(settingsData)
    });
  },

  async getSecuritySettings() {
    return this.get('/api/admin/settings/security');
  },

  async updateSecuritySettings(settingsData) {
    return this.request('/api/admin/settings/security', {
      method: 'PUT',
      body: JSON.stringify(settingsData)
    });
  },

  async getBackupSettings() {
    return this.get('/api/admin/settings/backup');
  },

  async createBackup() {
    return this.post('/api/admin/settings/backup/create', {});
  },

  async restoreBackup(backupId) {
    return this.post(`/api/admin/settings/backup/restore/${backupId}`, {});
  },

  async getBackupHistory() {
    return this.get('/api/admin/settings/backup/history');
  },

  // Enhanced monitoring methods
  async getSystemLogs(level = 'info', limit = 100) {
    return this.get(`/api/admin/logs?level=${level}&limit=${limit}`);
  },

  async getErrorLogs(limit = 50) {
    return this.get(`/api/admin/logs/errors?limit=${limit}`);
  },

  async getPerformanceMetrics() {
    return this.get('/api/admin/monitoring/performance');
  },

  async getResourceUsage() {
    return this.get('/api/admin/monitoring/resources');
  },

  async getAPIUsageStats() {
    return this.get('/api/admin/monitoring/api-usage');
  },

  async getUptime() {
    return this.get('/api/admin/monitoring/uptime');
  },

  // Enhanced testing methods
  async testAllIntegrations() {
    return this.post('/api/admin/test/integrations', {});
  },

  async testSpecificIntegration(integrationName) {
    return this.post(`/api/admin/test/integration/${integrationName}`, {});
  },

  async runSystemHealthCheck() {
    return this.post('/api/admin/test/health-check', {});
  },

  async validateConfiguration() {
    return this.post('/api/admin/test/validate-config', {});
  },

  async runDatabaseCheck() {
    return this.post('/api/admin/test/database', {});
  },

  // Enhanced export methods
  async exportUserData(format = 'csv', filters = {}) {
    return this.post('/api/admin/export/users', { format, filters });
  },

  async exportSessionData(format = 'csv', filters = {}) {
    return this.post('/api/admin/export/sessions', { format, filters });
  },

  async exportAnalyticsData(format = 'csv', period = '30d') {
    return this.post('/api/admin/export/analytics', { format, period });
  },

  async exportSystemData(format = 'json') {
    return this.post('/api/admin/export/system', { format });
  },

  // Enhanced bulk operations
  async bulkUpdateUsers(updates) {
    return this.post('/api/admin/bulk/users/update', { updates });
  },

  async bulkDeleteUsers(userIds) {
    return this.post('/api/admin/bulk/users/delete', { userIds });
  },

  async bulkUpdateProducts(updates) {
    return this.post('/api/admin/bulk/products/update', { updates });
  },

  async bulkUpdatePricing(updates) {
    return this.post('/api/admin/bulk/pricing/update', { updates });
  },

  // Enhanced analytics methods
  async getAdvancedAnalytics(type, period = '30d') {
    return this.get(`/api/admin/analytics/advanced/${type}?period=${period}`);
  },

  async getCustomReport(reportConfig) {
    return this.post('/api/admin/analytics/custom-report', reportConfig);
  },

  async scheduleReport(reportConfig) {
    return this.post('/api/admin/analytics/schedule-report', reportConfig);
  },

  async getScheduledReports() {
    return this.get('/api/admin/analytics/scheduled-reports');
  },

  async deleteScheduledReport(reportId) {
    return this.request(`/api/admin/analytics/scheduled-reports/${reportId}`, {
      method: 'DELETE'
    });
  }
};

export default spiritualAPI;

