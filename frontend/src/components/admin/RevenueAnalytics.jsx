import { useEffect, useState } from 'react';
import spiritualAPI from '../../lib/api';
import Loader from '../ui/Loader';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell, Legend } from 'recharts';

// தமில - Metric card
function MetricCard({ label, value, icon, color }) {
  return (
    <div className={`bg-gradient-to-br ${color} text-white rounded-lg p-6 flex flex-col items-center shadow`}>
      <span className="text-3xl mb-2">{icon}</span>
      <div className="text-2xl font-bold">{value}</div>
      <div className="text-sm mt-1">{label}</div>
    </div>
  );
}

const COLORS = ['#8b5cf6', '#f59e42', '#10b981', '#f43f5e', '#6366f1', '#fbbf24'];

export default function RevenueAnalytics() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // தமில - API call
  useEffect(() => {
    let mounted = true;
    spiritualAPI.getAdminRevenueAnalytics()
      .then(data => { if (mounted) setData(data); })
      .catch(e => setError('வருவாய் தரவு ஏற்ற முடியவில்லை.'))
      .finally(() => setLoading(false));
    return () => { mounted = false; };
  }, []);

  if (loading) return <Loader message="வருவாய் தரவு ஏற்றப்படுகிறது..." />;
  if (error) return <div className="text-red-600">{error}</div>;
  if (!data) return <div className="text-gray-600">No data available.</div>;

  return (
    <div>
      {/* தமில - Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <MetricCard label="MRR" value={`$${data.mrr}`} icon="💸" color="from-yellow-600 to-yellow-400" />
        <MetricCard label="ARPU" value={`$${data.arpu}`} icon="🧘" color="from-blue-700 to-blue-400" />
        <MetricCard label="CLV" value={`$${data.clv}`} icon="🌱" color="from-green-700 to-green-400" />
        <MetricCard label="Churn Rate" value={data.churn + '%'} icon="🔄" color="from-red-700 to-red-400" />
      </div>
      {/* தமில - Revenue Trend Chart */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-xl font-bold mb-4">Revenue Trend (Monthly)</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data.revenue_trend}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="revenue" stroke="#8b5cf6" strokeWidth={3} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      {/* தமில - Subscription vs One-Time Revenue */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-xl font-bold mb-4">Revenue Breakdown</h2>
        <ResponsiveContainer width="100%" height={250}>
          <PieChart>
            <Pie
              data={data.revenue_breakdown}
              dataKey="value"
              nameKey="type"
              cx="50%"
              cy="50%"
              outerRadius={80}
              label
            >
              {data.revenue_breakdown.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Legend />
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>
      {/* தமில - Cohort Analysis */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-xl font-bold mb-4">Cohort Retention Analysis</h2>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={data.cohort_analysis}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="cohort" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="retention" fill="#10b981" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      {/* தமில - AI Pricing Recommendations */}
      {data.pricing_recommendations && data.pricing_recommendations.length > 0 && (
        <div className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-800 p-4 mb-8 rounded">
          <h3 className="font-bold mb-2">AI Pricing Recommendations</h3>
          <ul className="list-disc pl-6">
            {data.pricing_recommendations.map((rec, i) => (
              <li key={i}>{rec}</li>
            ))}
          </ul>
        </div>
      )}
      {/* தமில - Revenue Forecast (AI) */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold mb-4">Revenue Forecast (AI)</h2>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={data.revenue_forecast}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="forecast" stroke="#f59e42" strokeWidth={3} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
} 