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

  isAuthenticated() {
    const token = localStorage.getItem('jyotiflow_token');
    return !!token;
  },

  logout() {
    localStorage.removeItem('jyotiflow_token');
    localStorage.removeItem('jyotiflow_user');
    window.location.href = '/';
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