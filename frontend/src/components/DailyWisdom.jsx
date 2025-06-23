// src/components/spiritual/DailyWisdom.jsx
import { useState, useEffect } from 'react';
import { Calendar, Sun, Star, Heart } from 'lucide-react';
import spiritualAPI from '../../lib/api';

const DailyWisdom = () => {
  const [wisdom, setWisdom] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDailyWisdom();
  }, []);

  const fetchDailyWisdom = async () => {
    try {
      setLoading(true);
      const response = await spiritualAPI.get('/api/content/daily-wisdom');
      setWisdom(response.data);
    } catch (err) {
      setError('Unable to fetch daily wisdom');
      console.error('Daily wisdom error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-gradient-to-br from-orange-50 to-yellow-50 rounded-xl p-6 shadow-lg">
        <div className="animate-pulse">
          <div className="h-4 bg-orange-200 rounded w-3/4 mb-4"></div>
          <div className="h-4 bg-orange-200 rounded w-1/2 mb-2"></div>
          <div className="h-4 bg-orange-200 rounded w-2/3"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gradient-to-br from-orange-50 to-yellow-50 rounded-xl p-6 shadow-lg">
        <div className="text-center">
          <Sun className="h-8 w-8 text-orange-400 mx-auto mb-2" />
          <p className="text-orange-600">Daily wisdom will be available soon</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-br from-orange-50 to-yellow-50 rounded-xl p-6 shadow-lg border border-orange-100">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Sun className="h-6 w-6 text-orange-500" />
          <h3 className="text-lg font-semibold text-orange-800">Daily Wisdom</h3>
        </div>
        <div className="flex items-center space-x-1 text-sm text-orange-600">
          <Calendar className="h-4 w-4" />
          <span>{new Date(wisdom.date).toLocaleDateString()}</span>
        </div>
      </div>

      {/* Wisdom Content */}
      <div className="space-y-4">
        <div className="text-gray-700 leading-relaxed">
          {wisdom.wisdom}
        </div>

        {/* Swamiji's Blessing */}
        <div className="bg-white/50 rounded-lg p-4 border-l-4 border-orange-400">
          <div className="flex items-start space-x-2">
            <Heart className="h-5 w-5 text-orange-500 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-sm font-medium text-orange-800 mb-1">Swamiji's Blessing</p>
              <p className="text-sm text-gray-600 italic">{wisdom.swamiji_blessing}</p>
            </div>
          </div>
        </div>

        {/* Prana Points Earned */}
        <div className="flex items-center justify-between pt-2 border-t border-orange-200">
          <div className="flex items-center space-x-2">
            <Star className="h-4 w-4 text-yellow-500" />
            <span className="text-sm text-gray-600">
              +{wisdom.prana_points} Prana Points earned
            </span>
          </div>
          <button 
            onClick={fetchDailyWisdom}
            className="text-sm text-orange-600 hover:text-orange-700 font-medium"
          >
            Refresh
          </button>
        </div>
      </div>
    </div>
  );
};

export default DailyWisdom;