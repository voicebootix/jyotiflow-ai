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
    
    // Create a simple text export
    const exportData = `
Birth Chart Report
Generated on: ${new Date().toLocaleString()}

Birth Details:
Date: ${birthDetails.date}
Time: ${birthDetails.time}
Location: ${birthDetails.location}
Timezone: ${birthDetails.timezone}

Planetary Positions:
${chartData.planets ? Object.entries(chartData.planets).map(([planet, details]) => 
  `${planet}: ${details.rashi} ${details.degree}° (House ${details.house})`
).join('\n') : 'No planetary data available'}

Houses:
${chartData.houses ? Object.entries(chartData.houses).map(([house, details]) => 
  `House ${house}: ${details.sign} ${details.degree}° (Lord: ${details.lord})`
).join('\n') : 'No house data available'}
    `.trim();

    const blob = new Blob([exportData], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `birth-chart-${birthDetails.date}.txt`;
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
    if (!chartData?.planets) return <div className="text-gray-400">No chart data available</div>;

    return (
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
    );
  };

  const renderPlanetaryTable = () => {
    if (!chartData?.planets) return <div className="text-gray-400">No planetary data available</div>;

    return (
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-600">
              <th className="text-left text-white p-2">Planet</th>
              <th className="text-left text-white p-2">Sign</th>
              <th className="text-left text-white p-2">Degree</th>
              <th className="text-left text-white p-2">House</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(chartData.planets).map(([planet, details]) => (
              <tr 
                key={planet}
                className="border-b border-gray-700 hover:bg-gray-800 cursor-pointer"
                onClick={() => setSelectedPlanet({ name: planet, ...details })}
              >
                <td className="p-2 flex items-center">
                  {planetIcons[planet] || <Circle className="w-4 h-4" />}
                  <span className="ml-2 text-white">{planet}</span>
                </td>
                <td className="p-2 text-gray-300">{details.rashi}</td>
                <td className="p-2 text-gray-300">{details.degree}°</td>
                <td className="p-2 text-gray-300">{details.house}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const renderHousesTable = () => {
    if (!chartData?.houses) return <div className="text-gray-400">No house data available</div>;

    return (
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
            {Object.entries(chartData.houses).map(([house, details]) => (
              <tr key={house} className="border-b border-gray-700">
                <td className="p-2 text-white font-medium">{house}</td>
                <td className="p-2 text-gray-300">{details.sign}</td>
                <td className="p-2 text-gray-300">{details.degree}°</td>
                <td className="p-2 text-gray-300">{details.lord}</td>
                <td className="p-2 text-gray-300 text-xs">{getHouseSignificance(parseInt(house))}</td>
              </tr>
            ))}
          </tbody>
        </table>
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
                    <p className="text-gray-400 text-sm mt-4">
                      Click on planets to see detailed information
                    </p>
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