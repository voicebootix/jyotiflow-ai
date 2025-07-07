/**
 * Real-Time Birth Chart Component
 * Displays Vedic astrological charts with planetary positions, house analysis, and predictions
 */

import { useState, useEffect } from 'react';
import { 
  Star, Sun, Moon, Circle, Triangle, Square, 
  ArrowRight, Calendar, Clock, MapPin, Eye, Info
} from 'lucide-react';

const RealTimeBirthChart = ({ chartData }) => {
  const [activeView, setActiveView] = useState('chart');
  const [selectedPlanet, setSelectedPlanet] = useState(null);
  const [chartCalculated, setChartCalculated] = useState(false);

  useEffect(() => {
    if (chartData) {
      setChartCalculated(true);
    }
  }, [chartData]);

  if (!chartData) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
        <p className="text-white">Calculating your birth chart...</p>
      </div>
    );
  }

  const { 
    birth_details, 
    planetary_positions, 
    house_cusps, 
    chart_analysis, 
    dasha_predictions,
    divisional_charts 
  } = chartData;

  const planetIcons = {
    'Sun': <Sun className="w-4 h-4" />,
    'Moon': <Moon className="w-4 h-4" />,
    'Mars': <Circle className="w-4 h-4 text-red-400" />,
    'Mercury': <Circle className="w-4 h-4 text-green-400" />,
    'Jupiter': <Circle className="w-4 h-4 text-yellow-400" />,
    'Venus': <Circle className="w-4 h-4 text-pink-400" />,
    'Saturn': <Circle className="w-4 h-4 text-blue-400" />,
    'Rahu': <Triangle className="w-4 h-4 text-purple-400" />,
    'Ketu': <Square className="w-4 h-4 text-orange-400" />
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
    return (
      <div className="grid grid-cols-4 gap-1 w-64 h-64 mx-auto">
        {Array.from({ length: 12 }, (_, i) => {
          const houseNumber = i + 1;
          const planetsInHouse = planetary_positions?.filter(p => p.house === houseNumber) || [];
          
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
                {planetsInHouse.map(planet => (
                  <div
                    key={planet.name}
                    className="cursor-pointer hover:scale-110 transition-transform"
                    onClick={() => setSelectedPlanet(planet)}
                    title={`${planet.name}: ${planet.sign} ${planet.degree}°`}
                  >
                    {planetIcons[planet.name]}
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
    return (
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-600">
              <th className="text-left text-white p-2">Planet</th>
              <th className="text-left text-white p-2">Sign</th>
              <th className="text-left text-white p-2">Degree</th>
              <th className="text-left text-white p-2">House</th>
              <th className="text-left text-white p-2">Strength</th>
            </tr>
          </thead>
          <tbody>
            {planetary_positions?.map(planet => (
              <tr 
                key={planet.name}
                className="border-b border-gray-700 hover:bg-gray-800 cursor-pointer"
                onClick={() => setSelectedPlanet(planet)}
              >
                <td className="p-2 flex items-center">
                  {planetIcons[planet.name]}
                  <span className="ml-2 text-white">{planet.name}</span>
                </td>
                <td className="p-2 text-gray-300">{planet.sign}</td>
                <td className="p-2 text-gray-300">{planet.degree.toFixed(2)}°</td>
                <td className="p-2 text-gray-300">{planet.house}</td>
                <td className="p-2">
                  <div className={`px-2 py-1 rounded text-xs ${
                    planet.strength > 70 ? 'bg-green-600 text-white' :
                    planet.strength > 40 ? 'bg-yellow-600 text-white' :
                    'bg-red-600 text-white'
                  }`}>
                    {planet.strength?.toFixed(1) || 'N/A'}%
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const renderDashaPredictions = () => {
    if (!dasha_predictions) {
      return <div className="text-gray-400 text-center">Dasha calculations in progress...</div>;
    }

    return (
      <div className="space-y-4">
        <div className="bg-purple-900 bg-opacity-50 p-4 rounded-lg">
          <h4 className="text-white font-semibold mb-2 flex items-center">
            <Calendar className="w-4 h-4 mr-2" />
            Current Dasha Period
          </h4>
          <div className="text-gray-300">
            <div><strong>Mahadasha:</strong> {dasha_predictions.current_mahadasha}</div>
            <div><strong>Antardasha:</strong> {dasha_predictions.current_antardasha}</div>
            <div><strong>Period:</strong> {dasha_predictions.period_start} - {dasha_predictions.period_end}</div>
          </div>
        </div>
        
        {dasha_predictions.predictions && (
          <div className="bg-gray-800 p-4 rounded-lg">
            <h4 className="text-white font-semibold mb-2">Dasha Predictions</h4>
            <div className="text-gray-300 leading-relaxed">
              {dasha_predictions.predictions}
            </div>
          </div>
        )}
        
        {dasha_predictions.upcoming_changes && (
          <div className="bg-blue-900 bg-opacity-50 p-4 rounded-lg">
            <h4 className="text-white font-semibold mb-2 flex items-center">
              <ArrowRight className="w-4 h-4 mr-2" />
              Upcoming Transitions
            </h4>
            <div className="space-y-2">
              {dasha_predictions.upcoming_changes.map((change, index) => (
                <div key={index} className="text-gray-300">
                  <strong>{change.date}:</strong> {change.description}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderChartAnalysis = () => {
    if (!chart_analysis) {
      return <div className="text-gray-400 text-center">Chart analysis in progress...</div>;
    }

    return (
      <div className="space-y-4">
        {chart_analysis.yogas && chart_analysis.yogas.length > 0 && (
          <div className="bg-yellow-900 bg-opacity-50 p-4 rounded-lg">
            <h4 className="text-white font-semibold mb-2 flex items-center">
              <Star className="w-4 h-4 mr-2" />
              Special Yogas
            </h4>
            <div className="space-y-2">
              {chart_analysis.yogas.map((yoga, index) => (
                <div key={index} className="text-gray-300">
                  <strong>{yoga.name}:</strong> {yoga.description}
                </div>
              ))}
            </div>
          </div>
        )}
        
        {chart_analysis.strengths && (
          <div className="bg-green-900 bg-opacity-50 p-4 rounded-lg">
            <h4 className="text-white font-semibold mb-2">Chart Strengths</h4>
            <ul className="text-gray-300 space-y-1">
              {chart_analysis.strengths.map((strength, index) => (
                <li key={index}>• {strength}</li>
              ))}
            </ul>
          </div>
        )}
        
        {chart_analysis.challenges && (
          <div className="bg-red-900 bg-opacity-50 p-4 rounded-lg">
            <h4 className="text-white font-semibold mb-2">Areas for Growth</h4>
            <ul className="text-gray-300 space-y-1">
              {chart_analysis.challenges.map((challenge, index) => (
                <li key={index}>• {challenge}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="w-full">
      <div className="mb-6">
        <h4 className="text-xl font-bold text-white mb-4 flex items-center">
          <Star className="w-5 h-5 mr-2" />
          Your Vedic Birth Chart
        </h4>
        
        {/* Birth Details */}
        <div className="bg-gray-800 p-4 rounded-lg mb-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div className="flex items-center text-gray-300">
              <Calendar className="w-4 h-4 mr-2" />
              <span>{birth_details?.date}</span>
            </div>
            <div className="flex items-center text-gray-300">
              <Clock className="w-4 h-4 mr-2" />
              <span>{birth_details?.time}</span>
            </div>
            <div className="flex items-center text-gray-300">
              <MapPin className="w-4 h-4 mr-2" />
              <span>{birth_details?.location}</span>
            </div>
          </div>
        </div>
        
        {/* View Selection */}
        <div className="flex flex-wrap gap-2 mb-4">
          {[
            { key: 'chart', label: 'Chart', icon: <Square className="w-4 h-4" /> },
            { key: 'planets', label: 'Planets', icon: <Star className="w-4 h-4" /> },
            { key: 'dasha', label: 'Dasha', icon: <Calendar className="w-4 h-4" /> },
            { key: 'analysis', label: 'Analysis', icon: <Eye className="w-4 h-4" /> }
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
      </div>
      
      {/* Chart Content */}
      <div className="bg-gray-800 p-6 rounded-lg">
        {activeView === 'chart' && (
          <div className="text-center">
            <h5 className="text-white font-semibold mb-4">Vedic Chart (North Indian Style)</h5>
            {renderVedicChart()}
            <p className="text-gray-400 text-sm mt-4">
              Click on planets to see detailed information
            </p>
          </div>
        )}
        
        {activeView === 'planets' && (
          <div>
            <h5 className="text-white font-semibold mb-4">Planetary Positions</h5>
            {renderPlanetaryTable()}
          </div>
        )}
        
        {activeView === 'dasha' && (
          <div>
            <h5 className="text-white font-semibold mb-4">Dasha Predictions</h5>
            {renderDashaPredictions()}
          </div>
        )}
        
        {activeView === 'analysis' && (
          <div>
            <h5 className="text-white font-semibold mb-4">Chart Analysis</h5>
            {renderChartAnalysis()}
          </div>
        )}
      </div>
      
      {/* Selected Planet Details */}
      {selectedPlanet && (
        <div className="mt-4 bg-gray-800 p-4 rounded-lg border border-purple-500">
          <div className="flex items-center justify-between mb-2">
            <h5 className="text-white font-semibold flex items-center">
              {planetIcons[selectedPlanet.name]}
              <span className="ml-2">{selectedPlanet.name} Details</span>
            </h5>
            <button
              onClick={() => setSelectedPlanet(null)}
              className="text-gray-400 hover:text-white"
            >
              ✕
            </button>
          </div>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <div className="text-gray-400">Sign:</div>
              <div className="text-white font-medium">{selectedPlanet.sign}</div>
            </div>
            <div>
              <div className="text-gray-400">House:</div>
              <div className="text-white font-medium">{selectedPlanet.house}</div>
            </div>
            <div>
              <div className="text-gray-400">Degree:</div>
              <div className="text-white font-medium">{selectedPlanet.degree.toFixed(2)}°</div>
            </div>
            <div>
              <div className="text-gray-400">Strength:</div>
              <div className="text-white font-medium">{selectedPlanet.strength?.toFixed(1) || 'N/A'}%</div>
            </div>
          </div>
          {selectedPlanet.significance && (
            <div className="mt-3 p-3 bg-gray-700 rounded">
              <div className="text-gray-400 text-xs mb-1">Significance:</div>
              <div className="text-gray-300 text-sm">{selectedPlanet.significance}</div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default RealTimeBirthChart;