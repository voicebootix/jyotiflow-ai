import { useState, useEffect } from 'react';
import { 
  Star, Sun, Moon, Circle, Triangle, Square, 
  ArrowRight, Calendar, Clock, MapPin, Eye, Info,
  Download, Share2, Save, Loader2, AlertCircle, CheckCircle
} from 'lucide-react';
import spiritualAPI from '../lib/api';

const BirthChart = () => {
  const [birthDetails, setBirthDetails] = useState({
    date: '',
    time: '',
    location: '',
    timezone: 'Asia/Colombo'
  });
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeView, setActiveView] = useState('chart');
  const [selectedPlanet, setSelectedPlanet] = useState(null);
  const [savedCharts, setSavedCharts] = useState([]);
  const [showSavedCharts, setShowSavedCharts] = useState(false);

  // Timezone options
  const timezones = [
    { value: 'Asia/Colombo', label: 'Colombo (UTC+5:30)' },
    { value: 'Asia/Kolkata', label: 'Mumbai (UTC+5:30)' },
    { value: 'Asia/Dhaka', label: 'Dhaka (UTC+6:00)' },
    { value: 'Asia/Bangkok', label: 'Bangkok (UTC+7:00)' },
    { value: 'Asia/Singapore', label: 'Singapore (UTC+8:00)' },
    { value: 'America/New_York', label: 'New York (UTC-5:00)' },
    { value: 'Europe/London', label: 'London (UTC+0:00)' },
    { value: 'Australia/Sydney', label: 'Sydney (UTC+10:00)' }
  ];

  useEffect(() => {
    // Load saved charts from localStorage
    const saved = localStorage.getItem('jyotiflow_saved_charts');
    if (saved) {
      try {
        setSavedCharts(JSON.parse(saved));
      } catch (e) {
        console.error('Error loading saved charts:', e);
      }
    }
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setBirthDetails(prev => ({ ...prev, [name]: value }));
    setError(''); // Clear error when user types
  };

  const validateForm = () => {
    if (!birthDetails.date) {
      setError('Please select your birth date');
      return false;
    }
    if (!birthDetails.time) {
      setError('Please select your birth time');
      return false;
    }
    if (!birthDetails.location.trim()) {
      setError('Please enter your birth location');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setLoading(true);
    setError('');
    setChartData(null);

    try {
      const response = await spiritualAPI.request('/api/spiritual/birth-chart', {
        method: 'POST',
        body: JSON.stringify({ 
          birth_details: {
            date: birthDetails.date,
            time: birthDetails.time,
            location: birthDetails.location,
            timezone: birthDetails.timezone
          }
        })
      });

      if (response.success) {
        // Use .data if present, else fallback to root
        const chart = response.birth_chart?.data ? {
          ...response.birth_chart.data,
          metadata: response.birth_chart.metadata
        } : response.birth_chart;
        setChartData(chart);
        // Save to localStorage
        saveChartToHistory(chart);
      } else {
        setError(response.message || 'Failed to generate birth chart');
      }
    } catch (err) {
      console.error('Birth chart error:', err);
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const saveChartToHistory = (chart) => {
    const chartRecord = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      birthDetails,
      chartData: chart
    };
    
    const updatedCharts = [chartRecord, ...savedCharts.slice(0, 9)]; // Keep last 10
    setSavedCharts(updatedCharts);
    localStorage.setItem('jyotiflow_saved_charts', JSON.stringify(updatedCharts));
  };

  const loadSavedChart = (savedChart) => {
    setBirthDetails(savedChart.birthDetails);
    setChartData(savedChart.chartData);
    setShowSavedCharts(false);
  };

  const exportChart = () => {
    if (!chartData) return;
    
    // Create a comprehensive export
    let exportData = `
VEDIC BIRTH CHART REPORT
Generated on: ${new Date().toLocaleString()}
Calculation Method: ${chartData.metadata?.calculation_method || 'Vedic Astrology'}

=====================================================
BIRTH DETAILS
=====================================================
Date: ${birthDetails.date}
Time: ${birthDetails.time}
Location: ${birthDetails.location}
Timezone: ${birthDetails.timezone}
Coordinates: ${chartData.metadata?.birth_details?.coordinates || 'N/A'}

=====================================================
BASIC BIRTH INFORMATION
=====================================================`;

    // Add basic birth details
    if (chartData.nakshatra) {
      exportData += `
Birth Nakshatra: ${chartData.nakshatra.name}
Pada: ${chartData.nakshatra.pada}
Ruling Planet: ${chartData.nakshatra.lord?.vedic_name || chartData.nakshatra.lord?.name || 'N/A'}`;
    }

    if (chartData.chandra_rasi) {
      exportData += `
Moon Sign (Rashi): ${chartData.chandra_rasi.name}
Moon Sign Lord: ${chartData.chandra_rasi.lord?.vedic_name || chartData.chandra_rasi.lord?.name || 'N/A'}`;
    }

    if (chartData.soorya_rasi) {
      exportData += `
Sun Sign: ${chartData.soorya_rasi.name}
Sun Sign Lord: ${chartData.soorya_rasi.lord?.vedic_name || chartData.soorya_rasi.lord?.name || 'N/A'}`;
    }

    if (chartData.zodiac) {
      exportData += `
Western Zodiac: ${chartData.zodiac.name}`;
    }

    // Add planetary positions
    if (chartData.planets && Object.keys(chartData.planets).length > 0) {
      exportData += `

=====================================================
PLANETARY POSITIONS
=====================================================`;
      
      Object.entries(chartData.planets).forEach(([planet, details]) => {
        exportData += `
${planet}:
  Sign: ${details.rashi || details.sign || 'N/A'}
  Degree: ${details.degree ? `${parseFloat(details.degree).toFixed(2)}°` : 'N/A'}
  House: ${details.house || 'N/A'}
  Status: ${details.status || 'Normal'}`;
        if (details.nakshatra) {
          exportData += `
  Nakshatra: ${details.nakshatra}`;
        }
      });
    }

    // Add houses information
    if (chartData.houses && Object.keys(chartData.houses).length > 0) {
      exportData += `

=====================================================
HOUSE SYSTEM
=====================================================`;
      
      Object.entries(chartData.houses).forEach(([house, details]) => {
        exportData += `
House ${house}:
  Sign: ${details.sign || details.rashi || 'N/A'}
  Degree: ${details.degree ? `${parseFloat(details.degree).toFixed(2)}°` : 'N/A'}
  Lord: ${details.lord || 'N/A'}
  Significance: ${details.significance || getHouseSignificance(parseInt(house))}`;
      });
    }

    // Add additional information
    if (chartData.additional_info) {
      exportData += `

=====================================================
ADDITIONAL INFORMATION
=====================================================`;
      
      Object.entries(chartData.additional_info).forEach(([key, value]) => {
        exportData += `
${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}: ${value}`;
      });
    }

    // Add data source information
    if (chartData.metadata?.data_sources) {
      exportData += `

=====================================================
DATA SOURCE INFORMATION
=====================================================
Basic Birth Details: ${chartData.metadata.data_sources.basic_details ? 'Available' : 'Not Available'}
Planetary Positions: ${chartData.metadata.data_sources.planets ? 'Available from API' : 'Calculated/Fallback'}
House System: ${chartData.metadata.data_sources.houses ? 'Available from API' : 'Standard System'}
${chartData.metadata.data_sources.fallback_used ? 'Note: Some data calculated from available birth details for demonstration purposes.' : ''}`;
    }

    exportData += `

=====================================================
DISCLAIMER
=====================================================
This birth chart is generated for educational and entertainment purposes.
For professional astrological consultation, please consult a qualified astrologer.
Generated by JyotiFlow AI - Your Spiritual Guide
${window.location.origin}

End of Report
=====================================================`;

    // Create and download the file
    const blob = new Blob([exportData], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `vedic-birth-chart-${birthDetails.date}-${birthDetails.time.replace(':', '')}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const planetIcons = {
    'Sun': <Sun className="w-4 h-4 text-yellow-500" />,
    'Moon': <Moon className="w-4 h-4 text-blue-500" />,
    'Mars': <Circle className="w-4 h-4 text-red-500" />,
    'Mercury': <Circle className="w-4 h-4 text-green-500" />,
    'Jupiter': <Circle className="w-4 h-4 text-yellow-600" />,
    'Venus': <Circle className="w-4 h-4 text-pink-500" />,
    'Saturn': <Circle className="w-4 h-4 text-gray-500" />,
    'Rahu': <Triangle className="w-4 h-4 text-purple-500" />,
    'Ketu': <Square className="w-4 h-4 text-orange-500" />
  };

  const getHouseSignificance = (houseNumber) => {
    const significances = {
      1: 'Self, Personality, Appearance',
      2: 'Wealth, Family, Speech',
      3: 'Courage, Siblings, Communication',
      4: 'Home, Mother, Property',
      5: 'Children, Creativity, Education',
      6: 'Health, Service, Enemies',
      7: 'Marriage, Partnership, Business',
      8: 'Transformation, Longevity, Research',
      9: 'Luck, Father, Higher Learning',
      10: 'Career, Reputation, Authority',
      11: 'Gains, Social Circle, Income',
      12: 'Spirituality, Liberation, Foreign'
    };
    return significances[houseNumber] || '';
  };

  const renderVedicChart = () => {
    // Check what data we have available
    const hasBasicData = chartData && (chartData.nakshatra || chartData.chandra_rasi || chartData.soorya_rasi);
    const hasPlanetsData = chartData && chartData.planets && Object.keys(chartData.planets).length > 0;
    const hasHousesData = chartData && chartData.houses && Object.keys(chartData.houses).length > 0;
    
    if (!hasBasicData) {
      return (
        <div className="text-center p-8">
          <div className="text-gray-400 text-lg mb-4">No chart data available</div>
          <div className="text-sm text-gray-500">
            Please check your birth details and try again
          </div>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        {/* Data Source Info */}
        {chartData.metadata?.data_sources && (
          <div className="bg-blue-900 border border-blue-700 rounded-lg p-4">
            <div className="text-sm text-blue-200">
              <div className="font-medium mb-2">Chart Data Sources:</div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className={chartData.metadata.data_sources.basic_details ? "text-green-300" : "text-red-300"}>
                  ✓ Basic Birth Details
                </div>
                <div className={chartData.metadata.data_sources.planets ? "text-green-300" : "text-yellow-300"}>
                  {chartData.metadata.data_sources.planets ? "✓" : "~"} Planetary Positions
                  {chartData.metadata.data_sources.fallback_used ? " (Calculated)" : ""}
                </div>
                <div className={chartData.metadata.data_sources.houses ? "text-green-300" : "text-yellow-300"}>
                  {chartData.metadata.data_sources.houses ? "✓" : "~"} House System
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Basic Birth Information */}
        <div className="bg-gray-700 rounded-lg p-4">
          <h4 className="text-white font-semibold mb-3">Birth Chart Summary</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-sm">
            {chartData.nakshatra && (
              <div className="bg-gray-800 p-3 rounded">
                <div className="text-gray-400">Birth Nakshatra</div>
                <div className="text-white font-medium">{chartData.nakshatra.name}</div>
                <div className="text-gray-300 text-xs">Pada: {chartData.nakshatra.pada}</div>
                <div className="text-gray-300 text-xs">Lord: {chartData.nakshatra.lord?.vedic_name}</div>
              </div>
            )}
            
            {chartData.chandra_rasi && (
              <div className="bg-gray-800 p-3 rounded">
                <div className="text-gray-400">Moon Sign (Rashi)</div>
                <div className="text-white font-medium">{chartData.chandra_rasi.name}</div>
                <div className="text-gray-300 text-xs">Lord: {chartData.chandra_rasi.lord?.vedic_name}</div>
              </div>
            )}
            
            {chartData.soorya_rasi && (
              <div className="bg-gray-800 p-3 rounded">
                <div className="text-gray-400">Sun Sign</div>
                <div className="text-white font-medium">{chartData.soorya_rasi.name}</div>
                <div className="text-gray-300 text-xs">Lord: {chartData.soorya_rasi.lord?.vedic_name}</div>
              </div>
            )}
            
            {chartData.zodiac && (
              <div className="bg-gray-800 p-3 rounded">
                <div className="text-gray-400">Western Zodiac</div>
                <div className="text-white font-medium">{chartData.zodiac.name}</div>
              </div>
            )}
            
            {chartData.additional_info && (
              <div className="bg-gray-800 p-3 rounded">
                <div className="text-gray-400">Birth Stone</div>
                <div className="text-white font-medium">{chartData.additional_info.birth_stone}</div>
                <div className="text-gray-300 text-xs">Color: {chartData.additional_info.color}</div>
              </div>
            )}
          </div>
        </div>

        {/* Vedic Chart Grid */}
        {hasPlanetsData && (
          <div className="text-center">
            <h4 className="text-white font-semibold mb-4">Vedic Chart (North Indian Style)</h4>
            <div className="grid grid-cols-4 gap-1 w-80 h-80 mx-auto">
              {Array.from({ length: 12 }, (_, i) => {
                const houseNumber = i + 1;
                const planetsInHouse = Object.entries(chartData.planets || {})
                  .filter(([_, details]) => details.house === houseNumber);
                
                return (
                  <div
                    key={houseNumber}
                    className="border border-gray-400 bg-gray-800 p-2 flex flex-col items-center justify-center relative cursor-pointer hover:bg-gray-700 transition-colors"
                    title={`House ${houseNumber}: ${getHouseSignificance(houseNumber)}`}
                  >
                    <div className="text-xs text-gray-400 absolute top-1 left-1">
                      {houseNumber}
                    </div>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {planetsInHouse.map(([planet, details]) => (
                        <div
                          key={planet}
                          className="cursor-pointer hover:scale-110 transition-transform"
                          onClick={() => setSelectedPlanet({ name: planet, ...details })}
                          title={`${planet}: ${details.rashi} ${details.degree}°`}
                        >
                          {planetIcons[planet] || <Circle className="w-4 h-4" />}
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
            <p className="text-gray-400 text-sm mt-4">
              Click on planets to see detailed information
            </p>
          </div>
        )}

        {/* Additional Birth Details */}
        {chartData.additional_info && (
          <div className="bg-gray-700 rounded-lg p-4">
            <h4 className="text-white font-semibold mb-3">Additional Information</h4>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
              {Object.entries(chartData.additional_info).map(([key, value]) => (
                <div key={key} className="bg-gray-800 p-2 rounded">
                  <div className="text-gray-400 capitalize">
                    {key.replace(/_/g, ' ')}
                  </div>
                  <div className="text-white">{value}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderPlanetaryTable = () => {
    if (!chartData?.planets) return <div className="text-gray-400">No planetary data available</div>;

    const planetsData = Object.entries(chartData.planets);
    if (planetsData.length === 0) {
      return <div className="text-gray-400">No planetary data available</div>;
    }

    return (
      <div className="space-y-4">
        {/* Data Quality Notice */}
        {chartData.metadata?.data_sources?.fallback_used && (
          <div className="bg-yellow-900 border border-yellow-700 text-yellow-200 px-4 py-3 rounded-md text-sm">
            <div className="font-medium">Notice:</div>
            <div>Planetary positions are calculated based on available birth details. 
            For precise calculations, please verify your exact birth time and location.</div>
          </div>
        )}
        
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-600">
                <th className="text-left text-white p-2">Planet</th>
                <th className="text-left text-white p-2">Sign (Rashi)</th>
                <th className="text-left text-white p-2">Degree</th>
                <th className="text-left text-white p-2">House</th>
                <th className="text-left text-white p-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {planetsData.map(([planet, details]) => (
                <tr 
                  key={planet}
                  className="border-b border-gray-700 hover:bg-gray-800 cursor-pointer"
                  onClick={() => setSelectedPlanet({ name: planet, ...details })}
                >
                  <td className="p-2 flex items-center">
                    {planetIcons[planet] || <Circle className="w-4 h-4" />}
                    <span className="ml-2 text-white font-medium">{planet}</span>
                  </td>
                  <td className="p-2 text-gray-300">
                    {details.rashi || details.sign || 'N/A'}
                    {details.nakshatra && (
                      <div className="text-xs text-gray-500">
                        {details.nakshatra}
                      </div>
                    )}
                  </td>
                  <td className="p-2 text-gray-300">
                    {details.degree ? `${parseFloat(details.degree).toFixed(1)}°` : 'N/A'}
                  </td>
                  <td className="p-2 text-gray-300">{details.house || 'N/A'}</td>
                  <td className="p-2">
                    <span className={`px-2 py-1 rounded text-xs ${
                      details.status === 'Exalted' ? 'bg-green-700 text-green-200' :
                      details.status === 'Debilitated' ? 'bg-red-700 text-red-200' :
                      details.status === 'Own Sign' ? 'bg-blue-700 text-blue-200' :
                      'bg-gray-700 text-gray-300'
                    }`}>
                      {details.status || 'Normal'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  const renderHousesTable = () => {
    if (!chartData?.houses) return <div className="text-gray-400">No house data available</div>;

    const housesData = Object.entries(chartData.houses);
    if (housesData.length === 0) {
      return <div className="text-gray-400">No house data available</div>;
    }

    return (
      <div className="space-y-4">
        {/* Houses Information */}
        <div className="bg-purple-900 border border-purple-700 text-purple-200 px-4 py-3 rounded-md text-sm">
          <div className="font-medium mb-1">House System Information:</div>
          <div>Each house represents different aspects of life. Click on any row for detailed house analysis.</div>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-600">
                <th className="text-left text-white p-2">House</th>
                <th className="text-left text-white p-2">Sign</th>
                <th className="text-left text-white p-2">Degree</th>
                <th className="text-left text-white p-2">Lord</th>
                <th className="text-left text-white p-2">Significance</th>
              </tr>
            </thead>
            <tbody>
              {housesData.map(([house, details]) => (
                <tr 
                  key={house} 
                  className="border-b border-gray-700 hover:bg-gray-800 cursor-pointer"
                  title={`House ${house}: ${details.significance || getHouseSignificance(parseInt(house))}`}
                >
                  <td className="p-2 text-white font-medium">
                    <div className="flex items-center">
                      <div className="w-6 h-6 bg-purple-600 rounded-full flex items-center justify-center text-xs mr-2">
                        {house}
                      </div>
                      House {house}
                    </div>
                  </td>
                  <td className="p-2 text-gray-300 font-medium">
                    {details.sign || details.rashi || 'N/A'}
                  </td>
                  <td className="p-2 text-gray-300">
                    {details.degree ? `${parseFloat(details.degree).toFixed(1)}°` : 'N/A'}
                  </td>
                  <td className="p-2 text-gray-300">
                    <div className="flex items-center">
                      {details.lord && planetIcons[details.lord] && (
                        <span className="mr-1">{planetIcons[details.lord]}</span>
                      )}
                      {details.lord || 'N/A'}
                    </div>
                  </td>
                  <td className="p-2 text-gray-300 text-xs">
                    {details.significance || getHouseSignificance(parseInt(house))}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {/* House Meanings Guide */}
        <div className="bg-gray-700 rounded-lg p-4">
          <h5 className="text-white font-semibold mb-2">House System Guide</h5>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-gray-300">
            <div><strong>1st House:</strong> Self, personality, appearance</div>
            <div><strong>2nd House:</strong> Wealth, family, speech</div>
            <div><strong>3rd House:</strong> Courage, siblings, communication</div>
            <div><strong>4th House:</strong> Home, mother, property</div>
            <div><strong>5th House:</strong> Children, creativity, education</div>
            <div><strong>6th House:</strong> Health, service, enemies</div>
            <div><strong>7th House:</strong> Marriage, partnership, business</div>
            <div><strong>8th House:</strong> Transformation, longevity</div>
            <div><strong>9th House:</strong> Luck, father, higher learning</div>
            <div><strong>10th House:</strong> Career, reputation, authority</div>
            <div><strong>11th House:</strong> Gains, social circle, income</div>
            <div><strong>12th House:</strong> Spirituality, liberation, foreign</div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 text-white">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-4 flex items-center justify-center">
            <Star className="w-8 h-8 mr-3 text-yellow-400" />
            Vedic Birth Chart
          </h1>
          <p className="text-gray-300 text-lg">
            Discover your cosmic blueprint through authentic Vedic astrology
          </p>
        </div>

        {/* Birth Details Form */}
        <div className="max-w-2xl mx-auto mb-8">
          <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
            <h2 className="text-xl font-semibold mb-4 flex items-center">
              <Calendar className="w-5 h-5 mr-2" />
              Enter Your Birth Details
            </h2>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Birth Date *
                  </label>
                  <input
                    type="date"
                    name="date"
                    value={birthDetails.date}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 text-white"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Birth Time *
                  </label>
                  <input
                    type="time"
                    name="time"
                    value={birthDetails.time}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 text-white"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Birth Location *
                </label>
                <input
                  type="text"
                  name="location"
                  value={birthDetails.location}
                  onChange={handleInputChange}
                  placeholder="e.g., Chennai, Tamil Nadu, India"
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 text-white"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Timezone
                </label>
                <select
                  name="timezone"
                  value={birthDetails.timezone}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 text-white"
                >
                  {timezones.map(tz => (
                    <option key={tz.value} value={tz.value}>{tz.label}</option>
                  ))}
                </select>
              </div>

              {/* Error Message */}
              {error && (
                <div className="bg-red-900 border border-red-700 text-red-200 px-4 py-3 rounded-md flex items-center">
                  <AlertCircle className="w-5 h-5 mr-2" />
                  {error}
                </div>
              )}

              <div className="flex flex-wrap gap-3">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex items-center px-6 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 rounded-md transition-colors"
                >
                  {loading ? (
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  ) : (
                    <Star className="w-5 h-5 mr-2" />
                  )}
                  {loading ? 'Generating Chart...' : 'Generate Birth Chart'}
                </button>

                {savedCharts.length > 0 && (
                  <button
                    type="button"
                    onClick={() => setShowSavedCharts(!showSavedCharts)}
                    className="flex items-center px-4 py-3 bg-gray-600 hover:bg-gray-700 rounded-md transition-colors"
                  >
                    <Save className="w-5 h-5 mr-2" />
                    Saved Charts ({savedCharts.length})
                  </button>
                )}
              </div>
            </form>
          </div>
        </div>

        {/* Saved Charts Modal */}
        {showSavedCharts && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4 max-h-96 overflow-y-auto">
              <h3 className="text-xl font-semibold mb-4">Saved Birth Charts</h3>
              <div className="space-y-2">
                {savedCharts.map((saved, index) => (
                  <div
                    key={saved.id}
                    className="p-3 bg-gray-700 rounded-md cursor-pointer hover:bg-gray-600 transition-colors"
                    onClick={() => loadSavedChart(saved)}
                  >
                    <div className="font-medium">
                      {saved.birthDetails.date} at {saved.birthDetails.time}
                    </div>
                    <div className="text-sm text-gray-400">
                      {saved.birthDetails.location}
                    </div>
                    <div className="text-xs text-gray-500">
                      {new Date(saved.timestamp).toLocaleDateString()}
                    </div>
                  </div>
                ))}
              </div>
              <button
                onClick={() => setShowSavedCharts(false)}
                className="mt-4 w-full px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded-md transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        )}

        {/* Chart Display */}
        {chartData && (
          <div className="max-w-6xl mx-auto">
            <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
              {/* Birth Details Summary */}
              <div className="bg-gray-700 p-4 rounded-lg mb-6">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                  <div className="flex items-center text-gray-300">
                    <Calendar className="w-4 h-4 mr-2" />
                    <span>{birthDetails.date}</span>
                  </div>
                  <div className="flex items-center text-gray-300">
                    <Clock className="w-4 h-4 mr-2" />
                    <span>{birthDetails.time}</span>
                  </div>
                  <div className="flex items-center text-gray-300">
                    <MapPin className="w-4 h-4 mr-2" />
                    <span>{birthDetails.location}</span>
                  </div>
                  <div className="flex items-center text-gray-300">
                    <Info className="w-4 h-4 mr-2" />
                    <span>{birthDetails.timezone}</span>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-wrap gap-3 mb-6">
                <button
                  onClick={exportChart}
                  className="flex items-center px-4 py-2 bg-green-600 hover:bg-green-700 rounded-md transition-colors"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Export Chart
                </button>
                <button
                  onClick={() => navigator.share && navigator.share({
                    title: 'My Vedic Birth Chart',
                    text: `Birth Chart for ${birthDetails.date} at ${birthDetails.time}`,
                    url: window.location.href
                  })}
                  className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-md transition-colors"
                >
                  <Share2 className="w-4 h-4 mr-2" />
                  Share
                </button>
              </div>

              {/* View Selection */}
              <div className="flex flex-wrap gap-2 mb-6">
                {[
                  { key: 'chart', label: 'Vedic Chart', icon: <Square className="w-4 h-4" /> },
                  { key: 'planets', label: 'Planets', icon: <Star className="w-4 h-4" /> },
                  { key: 'houses', label: 'Houses', icon: <Circle className="w-4 h-4" /> }
                ].map(view => (
                  <button
                    key={view.key}
                    onClick={() => setActiveView(view.key)}
                    className={`flex items-center px-3 py-2 rounded-lg text-sm transition-colors ${
                      activeView === view.key
                        ? 'bg-purple-600 text-white'
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    {view.icon}
                    <span className="ml-2">{view.label}</span>
                  </button>
                ))}
              </div>

              {/* Chart Content */}
              <div className="bg-gray-700 p-6 rounded-lg">
                {activeView === 'chart' && (
                  <div className="text-center">
                    <h3 className="text-white font-semibold mb-4">Vedic Chart (North Indian Style)</h3>
                    {renderVedicChart()}
                  </div>
                )}
                
                {activeView === 'planets' && (
                  <div>
                    <h3 className="text-white font-semibold mb-4">Planetary Positions</h3>
                    {renderPlanetaryTable()}
                  </div>
                )}
                
                {activeView === 'houses' && (
                  <div>
                    <h3 className="text-white font-semibold mb-4">House Analysis</h3>
                    {renderHousesTable()}
                  </div>
                )}
              </div>

              {/* Selected Planet Details */}
              {selectedPlanet && (
                <div className="mt-6 bg-gray-700 p-4 rounded-lg border border-purple-500">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="text-white font-semibold flex items-center">
                      {planetIcons[selectedPlanet.name] || <Circle className="w-4 h-4" />}
                      <span className="ml-2">{selectedPlanet.name} Details</span>
                    </h4>
                    <button
                      onClick={() => setSelectedPlanet(null)}
                      className="text-gray-400 hover:text-white"
                    >
                      ✕
                    </button>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <div className="text-gray-400">Sign:</div>
                      <div className="text-white font-medium">{selectedPlanet.rashi}</div>
                    </div>
                    <div>
                      <div className="text-gray-400">House:</div>
                      <div className="text-white font-medium">{selectedPlanet.house}</div>
                    </div>
                    <div>
                      <div className="text-gray-400">Degree:</div>
                      <div className="text-white font-medium">{selectedPlanet.degree}°</div>
                    </div>
                    <div>
                      <div className="text-gray-400">Status:</div>
                      <div className="text-white font-medium">{selectedPlanet.status || 'N/A'}</div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BirthChart; 