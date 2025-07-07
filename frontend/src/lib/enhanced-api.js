/**
 * Enhanced API Integration for JyotiFlow
 * Includes RAG-powered spiritual guidance and real-time birth chart generation
 */

import spiritualAPI from './api.js';

const enhancedAPI = {
  // Inherit all existing API methods
  ...spiritualAPI,

  // Enhanced Spiritual Guidance Endpoints
  async getEnhancedGuidance(request) {
    return this.post('/api/spiritual/enhanced/guidance', request);
  },

  async getEnhancedSystemHealth() {
    return this.get('/api/spiritual/enhanced/health');
  },

  async getKnowledgeDomains() {
    return this.get('/api/spiritual/enhanced/knowledge-domains');
  },

  async getPersonaModes() {
    return this.get('/api/spiritual/enhanced/persona-modes');
  },

  async configureService(serviceConfig) {
    return this.post('/api/spiritual/enhanced/configure-service', serviceConfig);
  },

  // Real-time Birth Chart Generation
  async generateBirthChart(birthDetails) {
    return this.post('/api/spiritual/enhanced/birth-chart', {
      birth_date: birthDetails.date,
      birth_time: birthDetails.time,
      birth_location: birthDetails.location,
      include_divisional_charts: true,
      include_dasha_predictions: true,
      include_transit_analysis: true
    });
  },

  async getBirthChartAnalysis(chartId) {
    return this.get(`/api/spiritual/enhanced/birth-chart/${chartId}/analysis`);
  },

  async getTransitPredictions(chartId) {
    return this.get(`/api/spiritual/enhanced/birth-chart/${chartId}/transits`);
  },

  async getDashaPredictions(chartId) {
    return this.get(`/api/spiritual/enhanced/birth-chart/${chartId}/dashas`);
  },

  // Enhanced Service Management
  async getEnhancedServices() {
    return this.get('/api/spiritual/enhanced/services');
  },

  async createEnhancedService(serviceData) {
    return this.post('/api/spiritual/enhanced/services', serviceData);
  },

  async updateEnhancedService(serviceId, serviceData) {
    return this.request(`/api/spiritual/enhanced/services/${serviceId}`, {
      method: 'PUT',
      body: JSON.stringify(serviceData)
    });
  },

  // Knowledge Base Management
  async getKnowledgeBase() {
    return this.get('/api/spiritual/enhanced/knowledge-base');
  },

  async addKnowledgePiece(knowledgeData) {
    return this.post('/api/spiritual/enhanced/knowledge-base', knowledgeData);
  },

  async updateKnowledgePiece(knowledgeId, knowledgeData) {
    return this.request(`/api/spiritual/enhanced/knowledge-base/${knowledgeId}`, {
      method: 'PUT',
      body: JSON.stringify(knowledgeData)
    });
  },

  async deleteKnowledgePiece(knowledgeId) {
    return this.request(`/api/spiritual/enhanced/knowledge-base/${knowledgeId}`, {
      method: 'DELETE'
    });
  },

  // Enhanced Analytics
  async getEnhancedAnalytics() {
    return this.get('/api/spiritual/enhanced/analytics');
  },

  async getKnowledgeEffectiveness() {
    return this.get('/api/spiritual/enhanced/knowledge-effectiveness');
  },

  async getPersonaPerformance() {
    return this.get('/api/spiritual/enhanced/persona-performance');
  },

  // Real-time Features
  async subscribeToRealTimeUpdates(callback) {
    // WebSocket connection for real-time updates
    const ws = new WebSocket(`${this.getWebSocketUrl()}/spiritual/enhanced/realtime`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      callback(data);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return ws;
  },

  // Astrological Calculations
  async calculatePlanetaryPositions(birthDetails) {
    return this.post('/api/spiritual/enhanced/astro-calc/planetary-positions', birthDetails);
  },

  async calculateHouseCusps(birthDetails) {
    return this.post('/api/spiritual/enhanced/astro-calc/house-cusps', birthDetails);
  },

  async calculateAshtakavarga(birthDetails) {
    return this.post('/api/spiritual/enhanced/astro-calc/ashtakavarga', birthDetails);
  },

  async calculateDivisionalCharts(birthDetails) {
    return this.post('/api/spiritual/enhanced/astro-calc/divisional-charts', birthDetails);
  },

  // Enhanced Remedies
  async getPersonalizedRemedies(chartAnalysis) {
    return this.post('/api/spiritual/enhanced/remedies/personalized', chartAnalysis);
  },

  async getMantraRecommendations(planetaryConditions) {
    return this.post('/api/spiritual/enhanced/remedies/mantras', planetaryConditions);
  },

  async getGemstoneRecommendations(birthChart) {
    return this.post('/api/spiritual/enhanced/remedies/gemstones', birthChart);
  },

  async getCharityRecommendations(karmaAnalysis) {
    return this.post('/api/spiritual/enhanced/remedies/charity', karmaAnalysis);
  },

  // Performance Optimization
  async preloadKnowledgeCache(domains) {
    return this.post('/api/spiritual/enhanced/cache/preload', { domains });
  },

  async clearKnowledgeCache() {
    return this.post('/api/spiritual/enhanced/cache/clear');
  },

  async getSystemPerformance() {
    return this.get('/api/spiritual/enhanced/performance');
  },

  // Integration Testing
  async testEnhancedIntegration() {
    return this.get('/api/spiritual/enhanced/test-integration');
  },

  async runSystemHealthCheck() {
    return this.get('/api/spiritual/enhanced/health-check');
  },

  // Utility Methods
  getWebSocketUrl() {
    const baseUrl = this.API_BASE_URL || 'https://jyotiflow-ai.onrender.com';
    return baseUrl.replace('http', 'ws');
  },

  // 30-Minute Comprehensive Reading
  async requestComprehensiveReading(request) {
    return this.post('/api/spiritual/enhanced/guidance', {
      ...request,
      service_type: 'comprehensive_life_reading_30min',
      analysis_depth: 'comprehensive_30_minute',
      knowledge_domains: [
        'classical_astrology',
        'tamil_spiritual_literature', 
        'health_astrology',
        'career_astrology',
        'relationship_astrology',
        'remedial_measures'
      ],
      persona_mode: 'comprehensive_life_master',
      include_birth_chart: true,
      include_remedies: true,
      include_predictions: true
    });
  },

  // Enhanced Error Handling
  async handleEnhancedError(error) {
    console.error('Enhanced API Error:', error);
    
    // Track error for analytics
    await this.trackSpiritualEngagement('enhanced_api_error', {
      error_type: error.name,
      error_message: error.message,
      timestamp: new Date().toISOString()
    });

    // Return graceful error response
    return {
      success: false,
      error: error.message,
      fallback_available: true
    };
  }
};

export default enhancedAPI;