/**
 * User Dashboard API Service
 * Centralized API service for all user dashboard data
 * Eliminates hardcoded data and provides real-time information
 */

import spiritualAPI from '../lib/api';

class UserDashboardAPI {
  
  /**
   * Get comprehensive user dashboard data
   * @returns {Promise<Object>} - Complete dashboard data
   */
  async getDashboardData() {
    try {
      const [profile, sessions, credits, services, recommendations, birthChart, followups] = await Promise.all([
        this.getUserProfile(),
        this.getUserSessions(),
        this.getUserCredits(),
        this.getAvailableServices(),
        this.getPersonalRecommendations(),
        this.getUserBirthChart(),
        this.getUserFollowups()
      ]);
      
      return {
        success: true,
        data: {
          profile,
          sessions,
          credits,
          services,
          recommendations,
          birthChart,
          followups,
          lastUpdated: new Date().toISOString()
        }
      };
    } catch (error) {
      console.error('[UserDashboard] Error fetching dashboard data:', error);
      return {
        success: false,
        error: error.message,
        data: null
      };
    }
  }
  
  /**
   * Get user profile with extended information
   */
  async getUserProfile() {
    try {
      const response = await spiritualAPI.request('/api/user/profile');
      
      if (response && response.success !== false) {
        return {
          ...response,
          subscription_tier: response.subscription_tier || 'basic',
          spiritual_progress: await this.getSpiritualProgress(response.id),
          joined_date: response.created_at,
          last_session: await this.getLastSessionDate(response.id)
        };
      }
      
      return null;
    } catch (error) {
      console.error('[UserDashboard] Error fetching user profile:', error);
      return null;
    }
  }
  
  /**
   * Get user's spiritual progress and journey metrics
   */
  async getSpiritualProgress(userId) {
    try {
      const response = await spiritualAPI.request(`/api/spiritual/progress/${userId}`);
      
      if (response && response.success) {
        return response.data;
      }
      
      // Fallback: calculate basic progress from sessions
      const sessions = await this.getUserSessions();
      const totalSessions = sessions?.length || 0;
      const completedSessions = sessions?.filter(s => s.status === 'completed').length || 0;
      
      return {
        total_sessions: totalSessions,
        completed_sessions: completedSessions,
        completion_rate: totalSessions > 0 ? (completedSessions / totalSessions) * 100 : 0,
        spiritual_level: this.calculateSpiritualLevel(totalSessions),
        progress_percentage: Math.min((totalSessions * 10), 100),
        milestones_achieved: Math.floor(totalSessions / 5),
        next_milestone: Math.ceil(totalSessions / 5) * 5
      };
    } catch (error) {
      console.error('[UserDashboard] Error fetching spiritual progress:', error);
      return {
        total_sessions: 0,
        completed_sessions: 0,
        completion_rate: 0,
        spiritual_level: 'Seeker',
        progress_percentage: 0,
        milestones_achieved: 0,
        next_milestone: 5
      };
    }
  }
  
  /**
   * Calculate spiritual level based on session count
   */
  calculateSpiritualLevel(sessionCount) {
    if (sessionCount >= 100) return 'Enlightened';
    if (sessionCount >= 50) return 'Advanced Practitioner';
    if (sessionCount >= 25) return 'Dedicated Seeker';
    if (sessionCount >= 10) return 'Growing Student';
    if (sessionCount >= 5) return 'Committed Learner';
    return 'New Seeker';
  }
  
  /**
   * Get user's session history with analytics
   */
  async getUserSessions() {
    try {
      const response = await spiritualAPI.request('/api/user/sessions');
      
      if (response && response.success) {
        return response.data.map(session => ({
          ...session,
          duration: this.calculateSessionDuration(session),
          effectiveness_score: this.calculateEffectivenessScore(session)
        }));
      }
      
      return [];
    } catch (error) {
      console.error('[UserDashboard] Error fetching user sessions:', error);
      return [];
    }
  }
  
  /**
   * Get user's credit information and purchase history
   */
  async getUserCredits() {
    try {
      const [balance, packages, history] = await Promise.all([
        spiritualAPI.request('/api/user/credits'),
        spiritualAPI.request('/api/credits/packages'),
        spiritualAPI.request('/api/user/credit-history')
      ]);
      
      return {
        current_balance: balance?.data?.credits || 0,
        available_packages: packages?.data || [],
        purchase_history: history?.data || [],
        spending_analysis: this.calculateSpendingAnalysis(history?.data || [])
      };
    } catch (error) {
      console.error('[UserDashboard] Error fetching credit information:', error);
      return {
        current_balance: 0,
        available_packages: [],
        purchase_history: [],
        spending_analysis: { total_spent: 0, average_purchase: 0, most_popular_package: null }
      };
    }
  }
  
  /**
   * Get available services with dynamic pricing
   */
  async getAvailableServices() {
    try {
      const response = await spiritualAPI.request('/api/services/types');
      
      if (response && response.success) {
        return response.data.map(service => ({
          ...service,
          popularity_score: this.calculateServicePopularity(service),
          recommended_for_user: this.isServiceRecommended(service)
        }));
      }
      
      return [];
    } catch (error) {
      console.error('[UserDashboard] Error fetching available services:', error);
      return [];
    }
  }
  
  /**
   * Get personalized AI recommendations for the user
   */
  async getPersonalRecommendations() {
    try {
      const response = await spiritualAPI.request('/api/ai/user-recommendations');
      
      if (response && response.success) {
        return response.data;
      }
      
      // Fallback: Generate basic recommendations
      const profile = await this.getUserProfile();
      const sessions = await this.getUserSessions();
      
      return this.generateFallbackRecommendations(profile, sessions);
    } catch (error) {
      console.error('[UserDashboard] Error fetching personal recommendations:', error);
      return [];
    }
  }
  
  /**
   * Get user's birth chart information
   */
  async getUserBirthChart() {
    try {
      const response = await spiritualAPI.request('/api/spiritual/birth-chart/cache-status');
      
      if (response && response.success) {
        return response.cache_status;
      }
      
      return null;
    } catch (error) {
      console.error('[UserDashboard] Error fetching birth chart:', error);
      return null;
    }
  }
  
  /**
   * Get user's follow-up messages
   */
  async getUserFollowups() {
    try {
      const response = await spiritualAPI.request('/api/followup/my-followups');
      
      if (response && response.success) {
        return response.data;
      }
      
      return [];
    } catch (error) {
      console.error('[UserDashboard] Error fetching follow-ups:', error);
      return [];
    }
  }
  
  /**
   * Get user's community participation
   */
  async getCommunityParticipation() {
    try {
      const response = await spiritualAPI.request('/api/community/my-participation');
      
      if (response && response.success) {
        return response.data;
      }
      
      return {
        satsang_attended: 0,
        satsang_upcoming: [],
        community_rank: 'New Member',
        contribution_score: 0
      };
    } catch (error) {
      console.error('[UserDashboard] Error fetching community participation:', error);
      return {
        satsang_attended: 0,
        satsang_upcoming: [],
        community_rank: 'New Member',
        contribution_score: 0
      };
    }
  }
  
  /**
   * Get session analytics for the user
   */
  async getSessionAnalytics() {
    try {
      const response = await spiritualAPI.request('/api/sessions/analytics');
      
      if (response && response.success) {
        return response.data;
      }
      
      // Fallback: Calculate basic analytics
      const sessions = await this.getUserSessions();
      return this.calculateSessionAnalytics(sessions);
    } catch (error) {
      console.error('[UserDashboard] Error fetching session analytics:', error);
      return this.calculateSessionAnalytics([]);
    }
  }
  
  /**
   * Helper method to calculate session duration
   */
  calculateSessionDuration(session) {
    if (session.started_at && session.completed_at) {
      const start = new Date(session.started_at);
      const end = new Date(session.completed_at);
      return Math.round((end - start) / (1000 * 60)); // Duration in minutes
    }
    return 0;
  }
  
  /**
   * Helper method to calculate session effectiveness score
   */
  calculateEffectivenessScore(session) {
    // Basic scoring algorithm
    let score = 0;
    
    if (session.status === 'completed') score += 40;
    if (session.user_feedback && session.user_feedback.rating) {
      score += session.user_feedback.rating * 10;
    }
    if (session.duration > 0) score += Math.min(session.duration, 20);
    
    return Math.min(score, 100);
  }
  
  /**
   * Helper method to calculate spending analysis
   */
  calculateSpendingAnalysis(purchaseHistory) {
    if (!purchaseHistory || purchaseHistory.length === 0) {
      return { total_spent: 0, average_purchase: 0, most_popular_package: null };
    }
    
    const totalSpent = purchaseHistory.reduce((sum, purchase) => sum + purchase.amount, 0);
    const averagePurchase = totalSpent / purchaseHistory.length;
    
    // Find most popular package
    const packageCounts = {};
    purchaseHistory.forEach(purchase => {
      packageCounts[purchase.package_name] = (packageCounts[purchase.package_name] || 0) + 1;
    });
    
    const mostPopularPackage = Object.keys(packageCounts).reduce((a, b) => 
      packageCounts[a] > packageCounts[b] ? a : b
    );
    
    return {
      total_spent: totalSpent,
      average_purchase: averagePurchase,
      most_popular_package: mostPopularPackage
    };
  }
  
  /**
   * Helper method to calculate service popularity
   */
  calculateServicePopularity(service) {
    // This would be replaced with real analytics data
    return Math.random() * 100; // Placeholder
  }
  
  /**
   * Helper method to check if service is recommended for user
   */
  isServiceRecommended(service) {
    // This would be replaced with real AI recommendation logic
    return Math.random() > 0.7; // Placeholder
  }
  
  /**
   * Generate fallback recommendations when AI service is unavailable
   */
  generateFallbackRecommendations(profile, sessions) {
    const recommendations = [];
    
    if (sessions.length === 0) {
      recommendations.push({
        type: 'first_session',
        title: 'Start Your Spiritual Journey',
        description: 'Begin with a personalized spiritual guidance session',
        priority: 'high',
        action: 'book_session'
      });
    }
    
    if (sessions.length >= 5 && sessions.length < 10) {
      recommendations.push({
        type: 'birth_chart',
        title: 'Discover Your Birth Chart',
        description: 'Unlock deeper insights with your complete birth chart analysis',
        priority: 'medium',
        action: 'view_birth_chart'
      });
    }
    
    return recommendations;
  }
  
  /**
   * Calculate session analytics from raw session data
   */
  calculateSessionAnalytics(sessions) {
    const totalSessions = sessions.length;
    const completedSessions = sessions.filter(s => s.status === 'completed').length;
    const avgDuration = sessions.reduce((sum, s) => sum + (s.duration || 0), 0) / totalSessions || 0;
    const avgEffectiveness = sessions.reduce((sum, s) => sum + (s.effectiveness_score || 0), 0) / totalSessions || 0;
    
    return {
      total_sessions: totalSessions,
      completed_sessions: completedSessions,
      completion_rate: totalSessions > 0 ? (completedSessions / totalSessions) * 100 : 0,
      average_duration: avgDuration,
      average_effectiveness: avgEffectiveness,
      most_active_day: this.findMostActiveDay(sessions),
      preferred_time: this.findPreferredTime(sessions)
    };
  }
  
  /**
   * Find most active day of the week
   */
  findMostActiveDay(sessions) {
    const dayCount = {};
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    
    sessions.forEach(session => {
      const day = new Date(session.created_at).getDay();
      dayCount[days[day]] = (dayCount[days[day]] || 0) + 1;
    });
    
    return Object.keys(dayCount).reduce((a, b) => dayCount[a] > dayCount[b] ? a : b, 'Monday');
  }
  
  /**
   * Find preferred time of day
   */
  findPreferredTime(sessions) {
    const timeCount = { morning: 0, afternoon: 0, evening: 0, night: 0 };
    
    sessions.forEach(session => {
      const hour = new Date(session.created_at).getHours();
      if (hour >= 6 && hour < 12) timeCount.morning++;
      else if (hour >= 12 && hour < 17) timeCount.afternoon++;
      else if (hour >= 17 && hour < 22) timeCount.evening++;
      else timeCount.night++;
    });
    
    return Object.keys(timeCount).reduce((a, b) => timeCount[a] > timeCount[b] ? a : b, 'morning');
  }
  
  /**
   * Get last session date
   */
  async getLastSessionDate(userId) {
    try {
      const sessions = await this.getUserSessions();
      if (sessions.length > 0) {
        return sessions[0].created_at;
      }
      return null;
    } catch (error) {
      return null;
    }
  }
  
  /**
   * Refresh all dashboard data
   */
  async refreshDashboard() {
    return await this.getDashboardData();
  }
}

export default new UserDashboardAPI();