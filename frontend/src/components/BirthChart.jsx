import React, { useState, useEffect } from 'react';
import { Calendar, Clock, MapPin, Sun, Moon, Star, Circle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import './BirthChart.css'; // Add custom CSS for South Indian chart
import spiritualAPI from '../lib/api';
import FreeReportHook from './FreeReportHook';

const BirthChart = () => {
  const navigate = useNavigate();
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
    
    // Create export with real Prokerala API data
    let exportData = `
VEDIC BIRTH CHART REPORT
Generated on: ${new Date().toLocaleString()}
Data Source: ${chartData.metadata?.data_source || 'Prokerala API'}
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
ASTROLOGICAL INFORMATION
=====================================================`;

    // Add nakshatra information
    if (chartData.nakshatra) {
      exportData += `
Birth Nakshatra: ${chartData.nakshatra.name}
Nakshatra Pada: ${chartData.nakshatra.pada}`;
      if (chartData.nakshatra.lord) {
        exportData += `
Nakshatra Lord: ${chartData.nakshatra.lord.vedic_name || chartData.nakshatra.lord.name}`;
      }
    }

    // Add rashi information
    if (chartData.chandra_rasi) {
      exportData += `
Moon Sign (Chandra Rasi): ${chartData.chandra_rasi.name}`;
      if (chartData.chandra_rasi.lord) {
        exportData += `
Moon Sign Lord: ${chartData.chandra_rasi.lord.vedic_name || chartData.chandra_rasi.lord.name}`;
      }
    }

    if (chartData.soorya_rasi) {
      exportData += `
Sun Sign (Soorya Rasi): ${chartData.soorya_rasi.name}`;
      if (chartData.soorya_rasi.lord) {
        exportData += `
Sun Sign Lord: ${chartData.soorya_rasi.lord.vedic_name || chartData.soorya_rasi.lord.name}`;
      }
    }

    if (chartData.lagna) {
      exportData += `
Ascendant (Lagna): ${chartData.lagna.name}`;
      if (chartData.lagna.lord) {
        exportData += `
Lagna Lord: ${chartData.lagna.lord.vedic_name || chartData.lagna.lord.name}`;
      }
    }

    // Add time information
    if (chartData.sunrise || chartData.sunset || chartData.ayanamsa) {
      exportData += `

=====================================================
TIME & CALCULATION DETAILS
=====================================================`;
      
      if (chartData.sunrise) {
        exportData += `
Sunrise: ${chartData.sunrise}`;
      }
      if (chartData.sunset) {
        exportData += `
Sunset: ${chartData.sunset}`;
      }
      if (chartData.ayanamsa) {
        exportData += `
Ayanamsa: ${chartData.ayanamsa}°`;
      }
    }

    // Add additional information
    if (chartData.additional_info) {
      exportData += `

=====================================================
ADDITIONAL INFORMATION
=====================================================`;
      
      Object.entries(chartData.additional_info).forEach(([key, value]) => {
        const formattedKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        exportData += `
${formattedKey}: ${value}`;
      });
    }

    // Add zodiac information if available
    if (chartData.zodiac) {
      exportData += `

=====================================================
WESTERN ZODIAC
=====================================================
Western Zodiac Sign: ${chartData.zodiac.name}`;
    }

    exportData += `

=====================================================
DATA NOTES
=====================================================
- This report is based on Vedic Astrology principles
- Data source: Prokerala API (birth-details endpoint)
- Generated by JyotiFlow AI Platform
- For complete planetary positions and house cusps, additional API endpoints are required

Report generated on: ${new Date().toISOString()}
`;

    // Create download
    const blob = new Blob([exportData], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = `birth-chart-${birthDetails.date}-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
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
    // Show what real data we have from Prokerala API
    if (!chartData) {
      return (
        <div className="text-center p-8">
          <div className="text-gray-400 text-lg mb-4">No chart data available</div>
          <div className="text-sm text-gray-500">
            Please check your birth details and try again
          </div>
        </div>
      );
    }

    const { chart_visualization, planetary_positions, birth_details, metadata } = chartData;

    return (
      <div className="space-y-8">
        {/* Data Source Info */}
        <div className="bg-blue-900 border border-blue-700 text-blue-200 px-4 py-3 rounded-md text-sm">
          <div className="font-medium">✅ Real Astrological Data</div>
          <div>Source: {metadata?.data_source || 'Prokerala API'}</div>
          <div>Chart Style: {metadata?.chart_style || 'South Indian'} | Type: {metadata?.chart_type || 'Rasi'}</div>
          <div>Ayanamsa: {metadata?.ayanamsa || 'Lahiri'}</div>
        </div>

        {/* South Indian Chart Visualization */}
        {chart_visualization && renderSouthIndianChart(chart_visualization)}

        {/* Birth Details Summary */}
        {birth_details && (
          <div className="bg-purple-900 border border-purple-700 rounded-lg p-6">
            <h3 className="text-xl font-semibold text-purple-200 mb-4">Birth Details</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-purple-300">Nakshatra:</span>{' '}
                <span className="text-white font-medium">
                  {typeof birth_details.nakshatra === 'object' 
                    ? birth_details.nakshatra?.name 
                    : birth_details.nakshatra || 'N/A'}
                </span>
              </div>
              <div>
                <span className="text-purple-300">Moon Sign:</span>{' '}
                <span className="text-white font-medium">
                  {typeof birth_details.chandra_rasi === 'object'
                    ? birth_details.chandra_rasi?.name
                    : birth_details.chandra_rasi || 'N/A'}
                </span>
              </div>
              <div>
                <span className="text-purple-300">Sun Sign:</span>{' '}
                <span className="text-white font-medium">
                  {typeof birth_details.soorya_rasi === 'object'
                    ? birth_details.soorya_rasi?.name
                    : birth_details.soorya_rasi || birth_details.zodiac || 'N/A'}
                </span>
              </div>
              {birth_details.additional_info?.ascendant && (
                <div>
                  <span className="text-purple-300">Ascendant:</span>{' '}
                  <span className="text-white font-medium">
                    {birth_details.additional_info.ascendant}
                  </span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Planetary Positions */}
        {planetary_positions && renderPlanetaryPositions(planetary_positions)}

        {/* Dasha Information */}
        {chartData.dasha_periods && renderDashaInfo(chartData.dasha_periods)}

        {/* Houses Information */}
        {chart_visualization?.houses && renderHousesInfo(chart_visualization.houses)}
      </div>
    );
  };

  const renderSouthIndianChart = (chartViz) => {
    const houses = chartViz.houses || [];
    
    return (
      <div className="bg-indigo-900 border border-indigo-700 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-indigo-200 mb-6">
          South Indian Rasi Chart
        </h3>
        
        {houses.length > 0 ? (
          <div className="south-indian-chart">
            {/* South Indian Chart Grid (4x4 with center empty) */}
            <div className="grid grid-cols-4 gap-1 max-w-md mx-auto bg-gray-800 p-2 rounded">
              {renderSouthIndianHouses(houses)}
            </div>
            
            {/* Chart Legend */}
            <div className="mt-6 text-center">
              <div className="text-indigo-300 text-sm">
                Chart showing planetary positions in South Indian format
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center text-indigo-300">
            Chart visualization data not available
          </div>
        )}
      </div>
    );
  };

  const renderSouthIndianHouses = (houses) => {
    // South Indian chart layout (4x4 grid)
    // Layout:
    // [12] [1]  [2]  [3]
    // [11] [X]  [X]  [4] 
    // [10] [X]  [X]  [5]
    // [9]  [8]  [7]  [6]
    
    const layout = [
      12, 1, 2, 3,
      11, 0, 0, 4,
      10, 0, 0, 5,
      9, 8, 7, 6
    ];

    return layout.map((houseNum, index) => {
      if (houseNum === 0) {
        // Empty center cells
        return (
          <div key={index} className="aspect-square bg-gray-700 rounded"></div>
        );
      }

      const house = houses.find(h => h.house_number === houseNum) || {
        house_number: houseNum,
        sign: getDefaultSign(houseNum - 1),
        planets: [],
        lord: getDefaultLord(houseNum - 1)
      };

      return (
        <div
          key={houseNum}
          className="aspect-square bg-indigo-800 border border-indigo-600 rounded p-1 text-xs relative hover:bg-indigo-700 transition-colors"
        >
          {/* House Number */}
          <div className="absolute top-0 left-0 bg-indigo-600 text-white text-[10px] px-1 rounded-br">
            {houseNum}
          </div>
          
          {/* Sign */}
          <div className="text-center text-indigo-200 font-medium text-[10px] mt-2">
            {house.sign}
          </div>
          
          {/* Planets */}
          <div className="text-center mt-1">
            {house.planets && house.planets.length > 0 ? (
              <div className="flex flex-wrap justify-center gap-[2px]">
                {house.planets.map((planet, idx) => (
                  <span
                    key={idx}
                    className="bg-yellow-600 text-yellow-100 text-[8px] px-1 rounded"
                  >
                    {getPlanetSymbol(planet)}
                  </span>
                ))}
              </div>
            ) : (
              <div className="text-gray-500 text-[8px]">-</div>
            )}
          </div>
          
          {/* House Lord */}
          <div className="absolute bottom-0 right-0 text-[8px] text-indigo-400">
            {house.lord && getPlanetSymbol(house.lord)}
          </div>
        </div>
      );
    });
  };

  const renderPlanetaryPositions = (positions) => {
    if (!positions || !positions.planets) return null;

    return (
      <div className="bg-green-900 border border-green-700 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-green-200 mb-4">Planetary Positions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {positions.planets.map((planet, index) => (
            <div key={index} className="bg-green-800 rounded p-3">
              <div className="font-medium text-green-200">{planet.name}</div>
              <div className="text-sm text-green-300">
                Position: {planet.position || 'N/A'}
              </div>
              <div className="text-sm text-green-300">
                Sign: {planet.sign || 'N/A'}
              </div>
              {planet.house && (
                <div className="text-sm text-green-300">
                  House: {planet.house}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderDashaInfo = (dashaData) => {
    return (
      <div className="bg-orange-900 border border-orange-700 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-orange-200 mb-4">Current Dasha Period</h3>
        <div className="text-orange-300">
          {dashaData.current_dasha ? (
            <div>
              <div>Main Period: {dashaData.current_dasha.planet}</div>
              <div>Sub Period: {dashaData.current_dasha.sub_planet || 'N/A'}</div>
              <div>Duration: {dashaData.current_dasha.duration || 'N/A'}</div>
            </div>
          ) : (
            <div>Dasha information will be displayed here</div>
          )}
        </div>
      </div>
    );
  };

  const renderHousesInfo = (houses) => {
    return (
      <div className="bg-teal-900 border border-teal-700 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-teal-200 mb-4">Houses Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-sm">
          {houses.slice(0, 12).map((house, index) => (
            <div key={index} className="bg-teal-800 rounded p-3">
              <div className="font-medium text-teal-200">
                House {house.house_number || index + 1}
              </div>
              <div className="text-teal-300">Sign: {house.sign}</div>
              <div className="text-teal-300">Lord: {house.lord}</div>
              {house.planets && house.planets.length > 0 && (
                <div className="text-teal-300">
                  Planets: {house.planets.join(', ')}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  const getPlanetSymbol = (planetName) => {
    const symbols = {
      'Sun': '☉',
      'Moon': '☽',
      'Mars': '♂',
      'Mercury': '☿',
      'Jupiter': '♃',
      'Venus': '♀',
      'Saturn': '♄',
      'Rahu': '☊',
      'Ketu': '☋',
      'Uranus': '♅',
      'Neptune': '♆',
      'Pluto': '♇',
      'Asc': 'As',
      'MC': 'MC'
    };
    return symbols[planetName] || planetName?.substring(0, 2) || '?';
  };

  const getDefaultSign = (index) => {
    const signs = [
      "Ari", "Tau", "Gem", "Can", "Leo", "Vir",
      "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"
    ];
    return signs[index % 12];
  };

  const getDefaultLord = (index) => {
    const lords = [
      "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
      "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"
    ];
    return lords[index % 12];
  };

  const renderPlanetaryTable = () => {
    if (!chartData) {
      return <div className="text-gray-400">No chart data available</div>;
    }

    // Display available astrological information from real API
    return (
      <div className="space-y-4">
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-xl font-semibold mb-4 text-yellow-400">Available Astrological Data</h3>
          
          {/* Planetary Positions from Chart Data */}
          {chartData.chart_visualization && chartData.chart_visualization.planets && (
            <div className="mb-6">
              <h4 className="text-lg font-medium text-white mb-3">Planetary Positions</h4>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-600">
                      <th className="text-left py-2 text-gray-400">Planet</th>
                      <th className="text-left py-2 text-gray-400">Sign</th>
                      <th className="text-left py-2 text-gray-400">House</th>
                      <th className="text-left py-2 text-gray-400">Degree</th>
                      <th className="text-left py-2 text-gray-400">Nakshatra</th>
                    </tr>
                  </thead>
                  <tbody>
                    {chartData.chart_visualization.planets.map((planet, index) => (
                      <tr key={index} className="border-b border-gray-700 hover:bg-gray-700">
                        <td className="py-2 text-white flex items-center">
                          {planetIcons[planet.name] || <Circle className="w-4 h-4" />}
                          <span className="ml-2">{planet.name}</span>
                        </td>
                        <td className="py-2 text-white">{planet.sign || 'N/A'}</td>
                        <td className="py-2 text-white">{planet.house || 'N/A'}</td>
                        <td className="py-2 text-white">{planet.degree || 'N/A'}</td>
                        <td className="py-2 text-white">{planet.nakshatra || 'N/A'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Nakshatra Information */}
            {chartData.nakshatra && (
              <div className="bg-gray-700 p-4 rounded-lg">
                <h4 className="text-lg font-medium text-white mb-3">Nakshatra Details</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Name:</span>
                    <span className="text-white">{chartData.nakshatra.name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Pada:</span>
                    <span className="text-white">{chartData.nakshatra.pada}</span>
                  </div>
                  {chartData.nakshatra.lord && (
                    <div className="flex justify-between">
                      <span className="text-gray-400">Lord:</span>
                      <span className="text-white">{chartData.nakshatra.lord.vedic_name || chartData.nakshatra.lord.name}</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Rashi Information */}
            <div className="bg-gray-700 p-4 rounded-lg">
              <h4 className="text-lg font-medium text-white mb-3">Rashi Information</h4>
              <div className="space-y-2 text-sm">
                {chartData.chandra_rasi && (
                  <div className="flex justify-between">
                    <span className="text-gray-400">Moon Sign:</span>
                    <span className="text-white">{chartData.chandra_rasi.name}</span>
                  </div>
                )}
                {chartData.soorya_rasi && (
                  <div className="flex justify-between">
                    <span className="text-gray-400">Sun Sign:</span>
                    <span className="text-white">{chartData.soorya_rasi.name}</span>
                  </div>
                )}
                {chartData.lagna && (
                  <div className="flex justify-between">
                    <span className="text-gray-400">Ascendant:</span>
                    <span className="text-white">{chartData.lagna.name}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Additional Information */}
            {chartData.additional_info && (
              <div className="bg-gray-700 p-4 rounded-lg">
                <h4 className="text-lg font-medium text-white mb-3">Additional Info</h4>
                <div className="space-y-2 text-sm">
                  {Object.entries(chartData.additional_info).map(([key, value]) => (
                    <div key={key} className="flex justify-between">
                      <span className="text-gray-400 capitalize">{key.replace(/_/g, ' ')}:</span>
                      <span className="text-white">{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Time Information */}
            {(chartData.sunrise || chartData.sunset) && (
              <div className="bg-gray-700 p-4 rounded-lg">
                <h4 className="text-lg font-medium text-white mb-3">Time Information</h4>
                <div className="space-y-2 text-sm">
                  {chartData.sunrise && (
                    <div className="flex justify-between">
                      <span className="text-gray-400">Sunrise:</span>
                      <span className="text-white">{chartData.sunrise}</span>
                    </div>
                  )}
                  {chartData.sunset && (
                    <div className="flex justify-between">
                      <span className="text-gray-400">Sunset:</span>
                      <span className="text-white">{chartData.sunset}</span>
                    </div>
                  )}
                  {chartData.ayanamsa && (
                    <div className="flex justify-between">
                      <span className="text-gray-400">Ayanamsa:</span>
                      <span className="text-white">{chartData.ayanamsa}°</span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Notice about additional data */}
        <div className="bg-yellow-900 border border-yellow-700 text-yellow-200 px-4 py-3 rounded-md text-sm">
          <div className="font-medium">ℹ️ API Data Source</div>
          <div>
            {chartData.chart_visualization ? 
              "This data includes chart visualization from the Prokerala API chart endpoint!" :
              "This data is from the working Prokerala API endpoint (birth-details). Additional planetary positions and house data would require different API endpoints."
            }
          </div>
        </div>
      </div>
    );
  };

  const renderHousesTable = () => {
    if (!chartData) {
      return <div className="text-gray-400">No chart data available</div>;
    }

    return (
      <div className="space-y-4">
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-xl font-semibold mb-4 text-yellow-400">House System Information</h3>
          
          {/* Display house data from chart visualization if available */}
          {chartData.chart_visualization && chartData.chart_visualization.houses ? (
            <div className="mb-6">
              <h4 className="text-lg font-medium text-white mb-3">House Positions</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(chartData.chart_visualization.houses).map(([houseNum, houseData]) => (
                  <div key={houseNum} className="bg-gray-700 p-4 rounded-lg">
                    <div className="text-yellow-400 font-medium mb-2">House {houseNum}</div>
                    <div className="text-white text-sm mb-1">
                      Sign: {houseData.sign || 'N/A'}
                    </div>
                    <div className="text-gray-400 text-xs mb-2">
                      {getHouseSignificance(parseInt(houseNum))}
                    </div>
                    {houseData.planets && houseData.planets.length > 0 && (
                      <div className="text-gray-300 text-xs">
                        <div className="font-medium mb-1">Planets:</div>
                        {houseData.planets.map((planet, index) => (
                          <div key={index} className="flex items-center mb-1">
                            {planetIcons[planet.name] || <Circle className="w-3 h-3" />}
                            <span className="ml-1">{planet.name}</span>
                            {planet.degree && (
                              <span className="text-gray-500 ml-2">({planet.degree}°)</span>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="text-center p-8 border-2 border-dashed border-gray-600 rounded-lg">
              <div className="text-gray-400 mb-2">🏠 House positions loading...</div>
              <div className="text-sm text-gray-500">
                Attempting to fetch house data from Prokerala API chart endpoint
              </div>
            </div>
          )}

          {/* Show basic house interpretation based on available signs */}
          {(chartData.chandra_rasi || chartData.soorya_rasi || chartData.lagna) && (
            <div className="mt-6">
              <h4 className="text-lg font-medium text-white mb-3">Available Sign Information</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {chartData.lagna && (
                  <div className="bg-gray-700 p-4 rounded-lg">
                    <div className="text-yellow-400 font-medium">1st House (Ascendant)</div>
                    <div className="text-white">{chartData.lagna.name}</div>
                    <div className="text-gray-400 text-sm mt-1">Self, personality, appearance</div>
                  </div>
                )}
                {chartData.chandra_rasi && (
                  <div className="bg-gray-700 p-4 rounded-lg">
                    <div className="text-yellow-400 font-medium">Moon Position</div>
                    <div className="text-white">{chartData.chandra_rasi.name}</div>
                    <div className="text-gray-400 text-sm mt-1">Mind, emotions, mother</div>
                  </div>
                )}
                {chartData.soorya_rasi && (
                  <div className="bg-gray-700 p-4 rounded-lg">
                    <div className="text-yellow-400 font-medium">Sun Position</div>
                    <div className="text-white">{chartData.soorya_rasi.name}</div>
                    <div className="text-gray-400 text-sm mt-1">Soul, father, authority</div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Notice about house data */}
        <div className="bg-blue-900 border border-blue-700 text-blue-200 px-4 py-3 rounded-md text-sm">
          <div className="font-medium">📊 House Data Status</div>
          <div>
            {chartData.chart_visualization && chartData.chart_visualization.houses ? 
              "House data successfully loaded from Prokerala API chart endpoint!" :
              "Complete house cusps and planetary house positions would be available once the correct Prokerala API endpoints for planets and houses are identified."
            }
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

            {/* Conversion Hook - After user sees their chart */}
            <div className="mt-8">
              <FreeReportHook 
                size="large"
                buttonText="Get Your Complete Personalized Reading from Swamiji FREE"
                onButtonClick={() => navigate('/register')}
              />
            </div>
          </div>
        )}

        {/* Always show hook for non-logged in users */}
        {!chartData && (
          <div className="mt-8 max-w-4xl mx-auto">
            <FreeReportHook 
              size="default"
              buttonText="Skip the Wait - Get Your Complete Report FREE"
              onButtonClick={() => navigate('/register')}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default BirthChart; 