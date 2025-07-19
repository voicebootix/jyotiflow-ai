/**
 * Birth Chart Session Service
 * Handles continuity between anonymous birth chart generation and user signup
 * This ensures seamless experience when users generate charts then sign up
 */

const BIRTH_CHART_SESSION_KEY = 'jyotiflow_birth_chart_session';
const BIRTH_CHART_CACHE_KEY = 'jyotiflow_birth_chart_cache';

class BirthChartSessionService {
  
  /**
   * Store birth chart data in session storage for anonymous users
   * @param {Object} birthDetails - Birth details (date, time, location, timezone)
   * @param {Object} chartData - Generated chart data from Pro Kerala API
   */
  storeAnonymousChart(birthDetails, chartData) {
    try {
      const sessionData = {
        birthDetails,
        chartData,
        timestamp: Date.now(),
        sessionId: this.generateSessionId(),
        status: 'anonymous_generated'
      };
      
      sessionStorage.setItem(BIRTH_CHART_SESSION_KEY, JSON.stringify(sessionData));
      
      // Also store in localStorage for persistence across tabs
      this.addToChartHistory(sessionData);
      
      console.log('[BirthChartSession] Anonymous chart stored:', sessionData.sessionId);
      return sessionData.sessionId;
    } catch (error) {
      console.error('[BirthChartSession] Error storing anonymous chart:', error);
      return null;
    }
  }
  
  /**
   * Retrieve stored anonymous chart data
   * @returns {Object|null} - Stored chart data or null if not found
   */
  getAnonymousChart() {
    try {
      const stored = sessionStorage.getItem(BIRTH_CHART_SESSION_KEY);
      if (!stored) return null;
      
      const sessionData = JSON.parse(stored);
      
      // Check if data is still valid (within 24 hours)
      const isValid = Date.now() - sessionData.timestamp < 24 * 60 * 60 * 1000;
      
      if (!isValid) {
        this.clearAnonymousChart();
        return null;
      }
      
      return sessionData;
    } catch (error) {
      console.error('[BirthChartSession] Error retrieving anonymous chart:', error);
      return null;
    }
  }
  
  /**
   * Clear anonymous chart data from session
   */
  clearAnonymousChart() {
    try {
      sessionStorage.removeItem(BIRTH_CHART_SESSION_KEY);
      console.log('[BirthChartSession] Anonymous chart cleared');
    } catch (error) {
      console.error('[BirthChartSession] Error clearing anonymous chart:', error);
    }
  }
  
  /**
   * Link anonymous chart to user account after signup
   * @param {string} userEmail - User's email address
   * @returns {Promise<boolean>} - Success status
   */
  async linkChartToUser(userEmail) {
    try {
      const anonymousChart = this.getAnonymousChart();
      if (!anonymousChart) return false;
      
      // Call backend to link chart to user
      const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://jyotiflow-ai.onrender.com';
      const response = await fetch(`${API_BASE_URL}/api/spiritual/birth-chart/link-to-user`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('jyotiflow_token')}`
        },
        body: JSON.stringify({
          session_id: anonymousChart.sessionId,
          birth_details: anonymousChart.birthDetails,
          chart_data: anonymousChart.chartData,
          user_email: userEmail
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          // Update session data to linked status
          anonymousChart.status = 'linked_to_user';
          anonymousChart.userEmail = userEmail;
          sessionStorage.setItem(BIRTH_CHART_SESSION_KEY, JSON.stringify(anonymousChart));
          
          console.log('[BirthChartSession] Chart linked to user:', userEmail);
          return true;
        }
      }
      
      console.error('[BirthChartSession] Failed to link chart to user');
      return false;
    } catch (error) {
      console.error('[BirthChartSession] Error linking chart to user:', error);
      return false;
    }
  }
  
  /**
   * Generate unique session ID for anonymous charts
   */
  generateSessionId() {
    return 'chart_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }
  
  /**
   * Add chart to history in localStorage
   */
  addToChartHistory(sessionData) {
    try {
      const history = this.getChartHistory();
      history.unshift({
        sessionId: sessionData.sessionId,
        birthDetails: sessionData.birthDetails,
        timestamp: sessionData.timestamp,
        status: sessionData.status
      });
      
      // Keep only last 10 charts
      if (history.length > 10) {
        history.splice(10);
      }
      
      localStorage.setItem(BIRTH_CHART_CACHE_KEY, JSON.stringify(history));
    } catch (error) {
      console.error('[BirthChartSession] Error adding to chart history:', error);
    }
  }
  
  /**
   * Get chart history from localStorage
   */
  getChartHistory() {
    try {
      const stored = localStorage.getItem(BIRTH_CHART_CACHE_KEY);
      return stored ? JSON.parse(stored) : [];
    } catch (error) {
      console.error('[BirthChartSession] Error getting chart history:', error);
      return [];
    }
  }
  
  /**
   * Check if user has generated a chart in this session
   */
  hasGeneratedChart() {
    const anonymousChart = this.getAnonymousChart();
    return anonymousChart !== null;
  }
  
  /**
   * Get conversion hook message for signup encouragement
   */
  getConversionHookMessage() {
    const anonymousChart = this.getAnonymousChart();
    if (!anonymousChart) return null;
    
    const { birthDetails } = anonymousChart;
    return {
      title: "🌟 Unlock Your Complete Spiritual Journey",
      message: `Your birth chart for ${birthDetails.location} is ready! Sign up now to get Swamiji's personalized interpretation and spiritual guidance.`,
      benefits: [
        "Complete spiritual interpretation by Swamiji",
        "Personalized guidance based on your chart",
        "Current period analysis and predictions",
        "Access to all spiritual services"
      ],
      cta: "Get My Complete Reading"
    };
  }
  
  /**
   * Track conversion funnel events
   */
  trackConversionEvent(eventType, details = {}) {
    try {
      const anonymousChart = this.getAnonymousChart();
      const eventData = {
        event_type: eventType,
        session_id: anonymousChart?.sessionId,
        timestamp: Date.now(),
        details
      };
      
      // Send to analytics endpoint
      const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://jyotiflow-ai.onrender.com';
    fetch(`${API_BASE_URL}/api/analytics/conversion-funnel`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(eventData)
      }).catch(error => console.warn('Analytics tracking failed:', error));
      
    } catch (error) {
      console.error('[BirthChartSession] Error tracking conversion event:', error);
    }
  }
}

export default new BirthChartSessionService();