/**
 * Enhanced API Integration for JyotiFlow
 * Includes RAG-powered spiritual guidance, real-time birth chart generation, and DYNAMIC PRICING
 */

import spiritualAPI from './api.js';

// Enhanced API client for JyotiFlow dynamic pricing and comprehensive readings
class EnhancedAPI {
  constructor() {
    this.baseURL = 'http://localhost:8000/api/spiritual/enhanced';
  }

  // Dynamic Pricing endpoints - these are unique and not duplicated
  async getCurrentPricing(serviceType = 'comprehensive') {
    const response = await fetch(`${this.baseURL}/pricing/${serviceType}`);
    if (!response.ok) throw new Error('Failed to fetch pricing');
    return response.json();
  }

  async generatePricingRecommendation(serviceType = 'comprehensive') {
    const response = await fetch(`${this.baseURL}/pricing/${serviceType}/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    if (!response.ok) throw new Error('Failed to generate pricing recommendation');
    return response.json();
  }

  async applyPricingRecommendation(serviceType, recommendationId, adminNotes = '') {
    const response = await fetch(`${this.baseURL}/pricing/${serviceType}/apply`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ recommendation_id: recommendationId, admin_notes: adminNotes })
    });
    if (!response.ok) throw new Error('Failed to apply pricing recommendation');
    return response.json();
  }

  async getPricingHistory(serviceType = 'comprehensive', limit = 50) {
    const response = await fetch(`${this.baseURL}/pricing/${serviceType}/history?limit=${limit}`);
    if (!response.ok) throw new Error('Failed to fetch pricing history');
    return response.json();
  }

  async getPricingAnalytics(serviceType = 'comprehensive') {
    const response = await fetch(`${this.baseURL}/pricing/${serviceType}/analytics`);
    if (!response.ok) throw new Error('Failed to fetch pricing analytics');
    return response.json();
  }

  // Comprehensive Reading - Main service endpoint
  async getComprehensiveReading(requestData) {
    const response = await fetch(`${this.baseURL}/comprehensive-reading`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestData)
    });
    if (!response.ok) throw new Error('Failed to get comprehensive reading');
    return response.json();
  }

  // Integration helper - check if service exists in regular ServiceTypes
  async validateEnhancedService(serviceId) {
    try {
      // Use existing API to check if service exists
      const services = await spiritualAPI.getServiceTypes();
      return services.find(s => s.id === serviceId && s.comprehensive_reading_enabled);
    } catch (error) {
      console.error('Error validating enhanced service:', error);
      return null;
    }
  }
}

export default new EnhancedAPI();