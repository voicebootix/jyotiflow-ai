#!/usr/bin/env node
/**
 * 🧪 Frontend Monitoring Components Test
 * Verifies all monitoring UI components are properly set up
 */

const fs = require('fs');
const path = require('path');

class FrontendMonitoringTester {
  constructor() {
    this.results = {
      files: {},
      imports: {},
      components: {},
      integration: {}
    };
    this.confidenceScore = 0;
  }

  run() {
    console.log('\n🧪 FRONTEND MONITORING COMPONENTS TEST\n');
    console.log('='.repeat(60));

    this.testFileExistence();
    this.testImports();
    this.testComponentStructure();
    this.testIntegration();
    this.calculateConfidence();
    this.printResults();
  }

  testFileExistence() {
    console.log('\n📁 Testing File Existence...');

    const requiredFiles = [
      'src/components/admin/SystemMonitoring.jsx',
      'src/components/admin/MonitoringWidget.jsx',
      'src/components/AdminDashboard.jsx'
    ];

    requiredFiles.forEach(file => {
      const filePath = path.join(__dirname, file);
      const exists = fs.existsSync(filePath);
      this.results.files[file] = exists;
      console.log(`${exists ? '✅' : '❌'} ${file}`);
    });
  }

  testImports() {
    console.log('\n📦 Testing Imports...');

    // Check AdminDashboard imports SystemMonitoring
    try {
      const adminDashPath = path.join(__dirname, 'src/components/AdminDashboard.jsx');
      const adminDashContent = fs.readFileSync(adminDashPath, 'utf8');
      
      const hasSystemMonitoringImport = adminDashContent.includes("import SystemMonitoring from './admin/SystemMonitoring'");
      this.results.imports['SystemMonitoring in AdminDashboard'] = hasSystemMonitoringImport;
      console.log(`${hasSystemMonitoringImport ? '✅' : '❌'} SystemMonitoring imported in AdminDashboard`);

      // Check Overview imports MonitoringWidget
      const overviewPath = path.join(__dirname, 'src/components/admin/Overview.jsx');
      if (fs.existsSync(overviewPath)) {
        const overviewContent = fs.readFileSync(overviewPath, 'utf8');
        const hasMonitoringWidgetImport = overviewContent.includes("import MonitoringWidget from './MonitoringWidget'");
        this.results.imports['MonitoringWidget in Overview'] = hasMonitoringWidgetImport;
        console.log(`${hasMonitoringWidgetImport ? '✅' : '❌'} MonitoringWidget imported in Overview`);
      }
    } catch (error) {
      console.log(`❌ Import test failed: ${error.message}`);
    }
  }

  testComponentStructure() {
    console.log('\n🏗️ Testing Component Structure...');

    // Test SystemMonitoring component
    try {
      const systemMonitoringPath = path.join(__dirname, 'src/components/admin/SystemMonitoring.jsx');
      if (fs.existsSync(systemMonitoringPath)) {
        const content = fs.readFileSync(systemMonitoringPath, 'utf8');
        
        const hasWebSocket = content.includes('WebSocket');
        const hasFetchMonitoring = content.includes('fetchMonitoringData');
        const hasRealtimeUpdate = content.includes('handleRealtimeUpdate');
        
        this.results.components['SystemMonitoring WebSocket'] = hasWebSocket;
        this.results.components['SystemMonitoring API calls'] = hasFetchMonitoring;
        this.results.components['SystemMonitoring realtime'] = hasRealtimeUpdate;
        
        console.log(`${hasWebSocket ? '✅' : '❌'} SystemMonitoring has WebSocket support`);
        console.log(`${hasFetchMonitoring ? '✅' : '❌'} SystemMonitoring has API integration`);
        console.log(`${hasRealtimeUpdate ? '✅' : '❌'} SystemMonitoring handles realtime updates`);
      }
    } catch (error) {
      console.log(`❌ Component structure test failed: ${error.message}`);
    }
  }

  testIntegration() {
    console.log('\n🔗 Testing Integration...');

    try {
      const adminDashPath = path.join(__dirname, 'src/components/AdminDashboard.jsx');
      const adminDashContent = fs.readFileSync(adminDashPath, 'utf8');
      
      // Check if monitoring tab is added
      const hasMonitoringTab = adminDashContent.includes("key: 'monitoring'") && 
                              adminDashContent.includes("System Monitor");
      this.results.integration['Monitoring tab'] = hasMonitoringTab;
      console.log(`${hasMonitoringTab ? '✅' : '❌'} Monitoring tab added to admin dashboard`);

      // Check if monitoring component is rendered
      const hasMonitoringRender = adminDashContent.includes("activeTab === 'monitoring'") && 
                                 adminDashContent.includes("<SystemMonitoring />");
      this.results.integration['Monitoring render'] = hasMonitoringRender;
      console.log(`${hasMonitoringRender ? '✅' : '❌'} SystemMonitoring component rendered`);

    } catch (error) {
      console.log(`❌ Integration test failed: ${error.message}`);
    }
  }

  calculateConfidence() {
    let totalTests = 0;
    let passedTests = 0;

    Object.values(this.results).forEach(category => {
      Object.values(category).forEach(result => {
        totalTests++;
        if (result) passedTests++;
      });
    });

    this.confidenceScore = totalTests > 0 ? (passedTests / totalTests * 100) : 0;
  }

  printResults() {
    console.log('\n' + '='.repeat(60));
    console.log('📊 TEST RESULTS SUMMARY');
    console.log('='.repeat(60));

    Object.entries(this.results).forEach(([category, tests]) => {
      const passed = Object.values(tests).filter(r => r).length;
      const total = Object.values(tests).length;
      console.log(`\n${category.toUpperCase()}:`);
      console.log(`  Passed: ${passed}/${total}`);
      
      Object.entries(tests).forEach(([test, result]) => {
        console.log(`  ${result ? '✅' : '❌'} ${test}`);
      });
    });

    console.log('\n' + '='.repeat(60));
    console.log(`🎯 FRONTEND CONFIDENCE SCORE: ${this.confidenceScore.toFixed(1)}%`);
    console.log('='.repeat(60));

    if (this.confidenceScore < 100) {
      console.log('\n⚠️ ACTIONS NEEDED:');
      if (!this.results.files['src/components/admin/SystemMonitoring.jsx']) {
        console.log('- SystemMonitoring.jsx file is missing');
      }
      if (!this.results.files['src/components/admin/MonitoringWidget.jsx']) {
        console.log('- MonitoringWidget.jsx file is missing');
      }
      if (!this.results.integration['Monitoring tab']) {
        console.log('- Monitoring tab not added to AdminDashboard');
      }
    } else {
      console.log('\n✅ FRONTEND MONITORING COMPONENTS ARE 100% READY!');
    }
  }
}

// Run the test
const tester = new FrontendMonitoringTester();
tester.run();

// Exit with appropriate code
process.exit(tester.confidenceScore === 100 ? 0 : 1);