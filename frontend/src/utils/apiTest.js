/**
 * 🧪 JyotiFlow API Integration Test Suite
 * Tests all backend endpoints to ensure frontend-backend integration works
 */

import spiritualAPI from '../lib/api';
import enhanced_api from '../services/enhanced-api';

class JyotiFlowAPITest {
  constructor() {
    this.testResults = [];
    this.errors = [];
  }

  async runAllTests() {
    console.log('🧪 Starting JyotiFlow API Integration Tests...');
    
    try {
      // Test authentication
      await this.testAuthentication();
      
      // Test core features
      await this.testSpiritualGuidance();
      await this.testAvatarGeneration();
      await this.testLiveChat();
      await this.testFollowUpSystem();
      await this.testBirthChart();
      await this.testPersonalizedRemedies();
      
      // Test admin features
      await this.testAdminFeatures();
      
      // Test enhanced features
      await this.testEnhancedFeatures();
      
      this.printResults();
      
    } catch (error) {
      console.error('❌ API Test Suite failed:', error);
      this.errors.push(error.message);
    }
  }

  async testAuthentication() {
    console.log('🔐 Testing Authentication...');
    
    try {
      // Test login endpoint
      const loginResponse = await spiritualAPI.login('test@example.com', 'password');
      this.addResult('Authentication - Login', loginResponse ? 'PASS' : 'FAIL');
      
      // Test registration endpoint
      const registerResponse = await spiritualAPI.register({
        name: 'Test User',
        email: 'test@example.com',
        password: 'password'
      });
      this.addResult('Authentication - Registration', registerResponse ? 'PASS' : 'FAIL');
      
    } catch (error) {
      this.addResult('Authentication', 'FAIL', error.message);
    }
  }

  async testSpiritualGuidance() {
    console.log('🕉️ Testing Spiritual Guidance...');
    
    try {
      // Test enhanced spiritual guidance
      const response = await enhanced_api.post('/enhanced-spiritual-guidance/generate', {
        question: 'How can I find inner peace?',
        service_type: 'comprehensive_life_reading_30min',
        birth_details: {
          birth_date: '1990-01-01',
          birth_time: '12:00:00',
          birth_location: 'Chennai, India'
        }
      });
      
      this.addResult('Spiritual Guidance - Enhanced', response.data.success ? 'PASS' : 'FAIL');
      
    } catch (error) {
      this.addResult('Spiritual Guidance', 'FAIL', error.message);
    }
  }

  async testAvatarGeneration() {
    console.log('🎭 Testing Avatar Generation...');
    
    try {
      // Test avatar generation endpoint
      const response = await enhanced_api.post('/avatar/generate-with-guidance', {
        question: 'What is my spiritual path?',
        service_type: 'comprehensive_life_reading_30min',
        avatar_style: 'traditional',
        voice_tone: 'compassionate'
      });
      
      this.addResult('Avatar Generation - Generate', response.data.success ? 'PASS' : 'FAIL');
      
      // Test avatar status endpoint
      if (response.data.session_id) {
        const statusResponse = await enhanced_api.get(`/avatar/status/${response.data.session_id}`);
        this.addResult('Avatar Generation - Status', statusResponse.data ? 'PASS' : 'FAIL');
      }
      
    } catch (error) {
      this.addResult('Avatar Generation', 'FAIL', error.message);
    }
  }

  async testLiveChat() {
    console.log('🗨️ Testing Live Chat...');
    
    try {
      // Test live chat session creation
      const response = await enhanced_api.post('/livechat/create-session', {
        service_type: 'comprehensive_life_reading_30min',
        user_question: 'I need spiritual guidance'
      });
      
      this.addResult('Live Chat - Session Creation', response.data.success ? 'PASS' : 'FAIL');
      
    } catch (error) {
      this.addResult('Live Chat', 'FAIL', error.message);
    }
  }

  async testFollowUpSystem() {
    console.log('📧 Testing Follow-up System...');
    
    try {
      // Test follow-up creation
      const response = await enhanced_api.post('/followup/create', {
        user_email: 'test@example.com',
        template_id: 'daily_wisdom',
        scheduled_time: new Date(Date.now() + 86400000).toISOString(),
        channel: 'email'
      });
      
      this.addResult('Follow-up System - Creation', response.data.success ? 'PASS' : 'FAIL');
      
    } catch (error) {
      this.addResult('Follow-up System', 'FAIL', error.message);
    }
  }

  async testBirthChart() {
    console.log('📊 Testing Birth Chart...');
    
    try {
      // Test birth chart generation
      const response = await enhanced_api.post('/spiritual/birth-chart', {
        birth_date: '1990-01-01',
        birth_time: '12:00:00',
        birth_location: 'Chennai, India'
      });
      
      this.addResult('Birth Chart - Generation', response.data.success ? 'PASS' : 'FAIL');
      
    } catch (error) {
      this.addResult('Birth Chart', 'FAIL', error.message);
    }
  }

  async testPersonalizedRemedies() {
    console.log('💊 Testing Personalized Remedies...');
    
    try {
      // Test remedies generation
      const response = await enhanced_api.post('/spiritual/personalized-remedies', {
        birth_details: {
          birth_date: '1990-01-01',
          birth_time: '12:00:00',
          birth_location: 'Chennai, India'
        },
        current_issues: ['stress', 'anxiety'],
        preferences: {
          include_mantras: true,
          include_gemstones: true,
          include_dietary: true
        }
      });
      
      this.addResult('Personalized Remedies - Generation', response.data.success ? 'PASS' : 'FAIL');
      
    } catch (error) {
      this.addResult('Personalized Remedies', 'FAIL', error.message);
    }
  }

  async testAdminFeatures() {
    console.log('👑 Testing Admin Features...');
    
    try {
      // Test admin analytics
      const analyticsResponse = await enhanced_api.get('/admin/analytics/overview');
      this.addResult('Admin - Analytics', analyticsResponse.data ? 'PASS' : 'FAIL');
      
      // Test user management
      const usersResponse = await enhanced_api.get('/admin/users');
      this.addResult('Admin - User Management', usersResponse.data ? 'PASS' : 'FAIL');
      
      // Test social media marketing
      const socialResponse = await enhanced_api.get('/admin/social-marketing/overview');
      this.addResult('Admin - Social Media Marketing', socialResponse.data ? 'PASS' : 'FAIL');
      
    } catch (error) {
      this.addResult('Admin Features', 'FAIL', error.message);
    }
  }

  async testEnhancedFeatures() {
    console.log('🚀 Testing Enhanced Features...');
    
    try {
      // Test universal pricing
      const pricingResponse = await enhanced_api.get('/universal-pricing/recommendations');
      this.addResult('Enhanced - Universal Pricing', pricingResponse.data ? 'PASS' : 'FAIL');
      
      // Test service types
      const servicesResponse = await enhanced_api.get('/service-types');
      this.addResult('Enhanced - Service Types', servicesResponse.data ? 'PASS' : 'FAIL');
      
    } catch (error) {
      this.addResult('Enhanced Features', 'FAIL', error.message);
    }
  }

  addResult(testName, status, error = null) {
    this.testResults.push({
      test: testName,
      status: status,
      error: error,
      timestamp: new Date().toISOString()
    });
    
    if (status === 'FAIL') {
      this.errors.push(`${testName}: ${error}`);
    }
  }

  printResults() {
    console.log('\n📊 JyotiFlow API Test Results:');
    console.log('=' .repeat(50));
    
    const passed = this.testResults.filter(r => r.status === 'PASS').length;
    const failed = this.testResults.filter(r => r.status === 'FAIL').length;
    const total = this.testResults.length;
    
    console.log(`✅ Passed: ${passed}`);
    console.log(`❌ Failed: ${failed}`);
    console.log(`📈 Success Rate: ${((passed / total) * 100).toFixed(1)}%`);
    
    console.log('\n📋 Detailed Results:');
    this.testResults.forEach(result => {
      const icon = result.status === 'PASS' ? '✅' : '❌';
      console.log(`${icon} ${result.test}: ${result.status}`);
      if (result.error) {
        console.log(`   Error: ${result.error}`);
      }
    });
    
    if (this.errors.length > 0) {
      console.log('\n🚨 Errors Found:');
      this.errors.forEach(error => {
        console.log(`   - ${error}`);
      });
    }
    
    console.log('\n🎯 Recommendations:');
    if (failed === 0) {
      console.log('🎉 All tests passed! Frontend-backend integration is working perfectly.');
    } else {
      console.log('⚠️ Some tests failed. Check the errors above and fix the integration issues.');
    }
  }
}

// Export for use in components
export const runAPITests = () => {
  const tester = new JyotiFlowAPITest();
  return tester.runAllTests();
};

export default JyotiFlowAPITest; 