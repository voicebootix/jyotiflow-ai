// Test file for the new unified BirthChart component
// This can be run in the browser console to test the functionality

const testBirthChart = async () => {
  console.log('🧪 Testing new unified BirthChart component...');
  
  try {
    // Test API call
    const response = await fetch('/api/spiritual/birth-chart', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        birth_details: {
          date: '1990-01-01',
          time: '12:00',
          location: 'Chennai, Tamil Nadu, India',
          timezone: 'Asia/Kolkata'
        }
      })
    });
    
    const data = await response.json();
    
    if (data.success) {
      console.log('✅ Birth chart API working correctly');
      console.log('📊 Chart data structure:', Object.keys(data.birth_chart));
      console.log('🌍 Metadata:', data.birth_chart.metadata);
      
      if (data.birth_chart.planets) {
        console.log('🪐 Planets found:', Object.keys(data.birth_chart.planets));
      }
      
      if (data.birth_chart.houses) {
        console.log('🏠 Houses found:', Object.keys(data.birth_chart.houses));
      }
      
      return true;
    } else {
      console.error('❌ Birth chart API failed:', data.message);
      return false;
    }
  } catch (error) {
    console.error('❌ Test failed:', error);
    return false;
  }
};

// Test localStorage functionality
const testLocalStorage = () => {
  console.log('🧪 Testing localStorage functionality...');
  
  try {
    // Test saving
    const testChart = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      birthDetails: {
        date: '1990-01-01',
        time: '12:00',
        location: 'Test Location',
        timezone: 'Asia/Kolkata'
      },
      chartData: {
        planets: { Sun: { rashi: 'Sagittarius', degree: 15, house: 1 } },
        houses: { 1: { sign: 'Sagittarius', degree: 0, lord: 'Jupiter' } }
      }
    };
    
    localStorage.setItem('jyotiflow_saved_charts', JSON.stringify([testChart]));
    
    // Test loading
    const saved = localStorage.getItem('jyotiflow_saved_charts');
    const parsed = JSON.parse(saved);
    
    if (parsed && parsed.length > 0) {
      console.log('✅ localStorage working correctly');
      console.log('💾 Saved charts:', parsed.length);
      return true;
    } else {
      console.error('❌ localStorage test failed');
      return false;
    }
  } catch (error) {
    console.error('❌ localStorage test failed:', error);
    return false;
  }
};

// Run all tests
const runAllTests = async () => {
  console.log('🚀 Running BirthChart component tests...\n');
  
  const apiTest = await testBirthChart();
  const storageTest = testLocalStorage();
  
  console.log('\n📋 Test Results:');
  console.log(`API Test: ${apiTest ? '✅ PASS' : '❌ FAIL'}`);
  console.log(`Storage Test: ${storageTest ? '✅ PASS' : '❌ FAIL'}`);
  
  if (apiTest && storageTest) {
    console.log('\n🎉 All tests passed! The new BirthChart component is working correctly.');
  } else {
    console.log('\n⚠️ Some tests failed. Please check the implementation.');
  }
};

// Export for use in browser console
window.testBirthChart = testBirthChart;
window.testLocalStorage = testLocalStorage;
window.runAllTests = runAllTests;

console.log('🧪 BirthChart test functions loaded. Run runAllTests() to test everything.'); 