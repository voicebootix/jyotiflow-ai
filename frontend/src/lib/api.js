const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://jyotiflow-ai.onrender.com';

const spiritualAPI = {
  // Base request method
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...this.getAuthHeaders(),
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  },

  // GET request
  async get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  },

  // POST request
  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
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
    return this.post('/api/spiritual/guidance', questionData);
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

  // Daily content methods
  async getDailyWisdom() {
    return this.get('/api/content/daily-wisdom');
  },

  async getSatsangSchedule() {
    return this.get('/api/content/satsang-schedule');
  },

  async getSpiritualQuote() {
    return this.get('/api/content/spiritual-quote');
  }
};

export default spiritualAPI;

