// தமில - வணிக நுண்ணறிவு
import { useEffect, useState } from 'react';
import api from '../../lib/api';
import Loader from '../ui/Loader';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function BusinessIntelligence() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;
    api.getAdminBI()
      .then(data => { if (mounted) setData(data); })
      .catch(e => setError('AI நுண்ணறிவு தரவு ஏற்ற முடியவில்லை.'))
      .finally(() => setLoading(false));
    return () => { mounted = false; };
  }, []);

  if (loading) return <Loader message="AI நுண்ணறிவு தரவு ஏற்றப்படுகிறது..." />;
  if (error) return <div className="text-red-600">{error}</div>;
  if (!data) return <div className="text-gray-600">No data available.</div>;

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">AI Business Intelligence</h2>
      {/* AI Recommendations */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h3 className="font-bold mb-2">AI Recommendations</h3>
        <ul className="list-disc pl-6">
          {data.recommendations.map((rec, i) => (
            <li key={i} className="mb-2">{rec.title} — <span className="text-gray-500">{rec.impact_estimate}</span>
              <div className="text-sm text-gray-700">{rec.description}</div>
            </li>
          ))}
        </ul>
      </div>
      {/* A/B Test Results */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h3 className="font-bold mb-2">A/B Test Results</h3>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={data.ab_tests}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="experiment_name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="conversion_rate_test" fill="#8b5cf6" />
            <Bar dataKey="conversion_rate_control" fill="#f59e42" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      {/* Market Analysis */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="font-bold mb-2">Market Analysis</h3>
        <ul className="list-disc pl-6">
          {data.market_analysis.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
      </div>
    </div>
  );
} 