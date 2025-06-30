import { useEffect, useState } from 'react';
import spiritualAPI from '../../lib/api';
import Loader from '../ui/Loader';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

// தமில - Metrics card component
function MetricCard({ label, value, icon, color }) {
  return (
    <div className={`bg-gradient-to-br ${color} text-white rounded-lg p-6 flex flex-col items-center shadow`}>
      <span className="text-3xl mb-2">{icon}</span>
      <div className="text-2xl font-bold">{value}</div>
      <div className="text-sm mt-1">{label}</div>
    </div>
  );
}

// தமில - AI Alert card
function AIAlert({ message }) {
  return (
    <div className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-800 p-4 mb-4 rounded flex items-center">
      <span className="text-2xl mr-3">🧘</span>
      <span>{message}</span>
    </div>
  );
}

export default function Overview() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // தமில - API call
  useEffect(() => {
    let mounted = true;
    spiritualAPI.getAdminOverview()
      .then(response => {
        if (mounted && response && response.success && response.data) {
          setMetrics(response.data);
        } else {
          setError('No data available.');
        }
      })
      .catch(e => setError('தரவு ஏற்ற முடியவில்லை.'))
      .finally(() => setLoading(false));
    return () => { mounted = false; };
  }, []);

  if (loading) return <Loader message="தயவு செய்து காத்திருக்கவும்..." />;
  if (error) return <div className="text-red-600">{error}</div>;
  if (!metrics) return <div className="text-gray-600">No data available.</div>;

  return (
    <div>
      {/* தமில - Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <MetricCard label="Total Users" value={metrics.users} icon="👥" color="from-purple-700 to-indigo-700" />
        <MetricCard label="Revenue" value={`$${metrics.revenue}`} icon="💸" color="from-yellow-600 to-yellow-400" />
        <MetricCard label="Sessions" value={metrics.sessions} icon="🧘" color="from-blue-700 to-blue-400" />
        <MetricCard label="Growth" value={metrics.growth + '%'} icon="🌱" color="from-green-700 to-green-400" />
      </div>
      {/* தமில - AI Alerts */}
      {metrics.ai_alerts && metrics.ai_alerts.length > 0 && (
        <div className="mb-8">
          {metrics.ai_alerts.map((msg, i) => <AIAlert key={i} message={msg} />)}
        </div>
      )}
      {/* தமில - Revenue Trend Chart */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-xl font-bold mb-4">Revenue Trend</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={metrics.revenue_trend}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="revenue" stroke="#8b5cf6" strokeWidth={3} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      {/* தமில - User Acquisition Funnel */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-xl font-bold mb-4">User Acquisition Funnel</h2>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={metrics.funnel}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="stage" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="count" fill="#f59e42" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      {/* தமில - System Health */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-bold mb-2">System Health</h3>
          <div className="flex items-center mb-2">
            <span className="text-green-600 text-2xl mr-2">●</span>
            <span>API: {metrics.system_health.api === 'healthy' ? 'Healthy' : 'Issue'}</span>
          </div>
          <div className="flex items-center mb-2">
            <span className="text-green-600 text-2xl mr-2">●</span>
            <span>Database: {metrics.system_health.db === 'healthy' ? 'Healthy' : 'Issue'}</span>
          </div>
          <div className="flex items-center">
            <span className="text-green-600 text-2xl mr-2">●</span>
            <span>Stripe: {metrics.system_health.stripe === 'healthy' ? 'Healthy' : 'Issue'}</span>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-6 flex flex-col items-center justify-center">
          <span className="text-5xl mb-2">🕉️</span>
          <div className="text-lg font-bold text-purple-700">Spiritual Platform Operational</div>
        </div>
      </div>
    </div>
  );
} 