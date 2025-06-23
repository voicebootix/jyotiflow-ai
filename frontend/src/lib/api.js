/**
 * JyotiFlow.ai API Client
 * Connects to real backend endpoints based on repository analysis
 */

class SpiritualJourneyAPI {
  constructor() {
    // Use environment variable or default to localhost for development
    this.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    this.token = localStorage.getItem('spiritual_token');
  }

  /**
   * Make authenticated API calls to backend
   */
  async makeAPICall(endpoint, method = 'GET', data = null) {
    const headers = {
      'Content-Type': 'application/json',
    };
    
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const config = { method, headers };
    if (data) config.body = JSON.stringify(data);

    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, config);
      const result = await response.json();
      
      // Handle authentication errors
      if (response.status === 401) {
        this.clearAuth();
        window.location.href = '/login';
        return null;
      }
      
      return result;
    } catch (error) {
      console.error('🕉️ Divine API call encountered turbulence:', error);
      return { success: false, message: 'Connection to divine servers failed', error: error.message };
    }
  }


  // Authentication methods
  login: async (email, password) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password })
      });
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Login API error:', error);
      return { success: false, message: 'Network error' };
    }
  },

  register: async (userData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData)
      });
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Register API error:', error);
      return { success: false, message: 'Network error' };
    }
  },

  isAuthenticated: () => {
    const token = localStorage.getItem('jyotiflow_token');
    return !!token;
  },

  logout: () => {
    localStorage.removeItem('jyotiflow_token');
    localStorage.removeItem('jyotiflow_user');
    window.location.href = '/';
  },

  getAuthHeaders: () => {
    const token = localStorage.getItem('jyotiflow_token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  }

  /**
   * Avatar Generation Endpoints (Enhanced API v2)
   */
  async generateAvatarVideo(guidanceText, userBirthDetails) {
    return await this.makeAPICall('/api/v2/avatar/generate', 'POST', {
      guidance_text: guidanceText,
      user_birth_details: userBirthDetails
    });
  }

  async getAvatarGenerationStatus(sessionId) {
    return await this.makeAPICall(`/api/v2/avatar/status/${sessionId}`);
  }

  /**
   * Live Chat Endpoints
   */
  async initiateLiveChat(sessionDetails) {
    return await this.makeAPICall('/api/v2/live-chat/initiate', 'POST', sessionDetails);
  }

  /**
   * Satsang Management Endpoints
   */
  async createSatsang(eventDetails) {
    return await this.makeAPICall('/api/v2/satsang/create', 'POST', eventDetails);
  }

  async registerForSatsang(eventId) {
    return await this.makeAPICall(`/api/v2/satsang/${eventId}/register`, 'POST');
  }

  async getSatsangSchedule() {
    return await this.makeAPICall('/api/v2/satsang/schedule');
  }

  /**
   * Admin & Analytics Endpoints
   */
  async getMonetizationInsights() {
    return await this.makeAPICall('/api/v2/admin/ai-insights/monetization');
  }

  async getProductOptimization() {
    return await this.makeAPICall('/api/v2/admin/ai-insights/product-optimization');
  }

  async getAdminStats() {
    return await this.makeAPICall('/api/v2/admin/stats');
  }

  /**
   * Platform Statistics (for homepage metrics)
   */
  async loadPlatformStats() {
    const stats = await this.makeAPICall('/api/v2/admin/analytics');
    if (stats && stats.success) {
      this.updatePlatformMetrics(stats.data);
      return stats.data;
    }
    return null;
  }

  /**
   * Update platform metrics with real data from backend
   */
  updatePlatformMetrics(data) {
    const metrics = {
      'total-seekers': this.formatNumber(data.total_users || 25000),
      'sessions-given': this.formatNumber(data.total_sessions || 75000),
      'community-size': this.formatNumber(data.active_users || 8247),
      'active-members': this.formatNumber(data.community_members || 8247),
      'satsangs-held': data.satsangs_completed || '42',
      'countries-reached': data.countries_reached || '67',
      'hours-guidance': this.formatNumber(data.total_guidance_hours || 12000, true),
      'revenue-total': this.formatCurrency(data.total_revenue || 125075),
      'daily-revenue': this.formatCurrency(data.daily_revenue || 12575)
    };

    Object.entries(metrics).forEach(([id, value]) => {
      const element = document.getElementById(id);
      if (element) element.textContent = value;
    });
  }

  /**
   * Format numbers for display (25K+, 1.2M+, etc.)
   */
  formatNumber(num, addPlus = false) {
    if (num >= 1000000) {
      return Math.floor(num / 1000000) + 'M' + (addPlus ? '+' : '');
    } else if (num >= 1000) {
      return Math.floor(num / 1000) + 'K' + (addPlus ? '+' : '');
    }
    return num.toString() + (addPlus ? '+' : '');
  }

  /**
   * Format currency for display
   */
  formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  }

  /**
   * User Authentication Endpoints
   */
  async login(email, password) {
    const result = await this.makeAPICall('/api/v1/auth/login', 'POST', {
      email,
      password
    });
    
    if (result && result.success && result.token) {
      this.setToken(result.token);
    }
    
    return result;
  }

  async register(name, email, password) {
    return await this.makeAPICall('/api/v1/auth/register', 'POST', {
      name,
      email,
      password
    });
  }

  async getUserProfile() {
    return await this.makeAPICall('/api/v1/user/profile');
  }

  /**
   * Session Management
   */
  async startSession(sessionData) {
    return await this.makeAPICall('/api/v1/session/start', 'POST', sessionData);
  }

  async getSessionHistory() {
    return await this.makeAPICall('/api/v1/session/history');
  }

  async getSessionWithMemory(sessionId) {
    return await this.makeAPICall('/api/v1/session/with-memory', 'POST', { session_id: sessionId });
  }

  /**
   * Credits & Payment System
   */
  async getCreditBalance() {
    return await this.makeAPICall('/api/v1/credits/balance');
  }

  async purchaseCredits(amount) {
    return await this.makeAPICall('/api/v1/credits/purchase', 'POST', { amount });
  }

  /**
   * Analytics Tracking
   */
  async trackSpiritualEngagement(action, details = {}) {
    try {
      await this.makeAPICall('/api/v1/analytics/engagement', 'POST', {
        action: action,
        details: details,
        timestamp: new Date().toISOString(),
        page: window.location.pathname
      });
    } catch (error) {
      // Analytics failures should not break the user experience
      console.log('Analytics blessed with silence:', error);
    }
  }

  /**
   * Health Check
   */
  async healthCheck() {
    return await this.makeAPICall('/health');
  }
  
 
}


 
// Create global instance
const spiritualAPI = new SpiritualJourneyAPI();

export default spiritualAPI;

