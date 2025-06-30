// தமில - பயனர் மேலாண்மை
import { useEffect, useState } from 'react';
import spiritualAPI from '../../lib/api';

export default function UserManagement() {
  const [users, setUsers] = useState([]);
  const [subscriptionPlans, setSubscriptionPlans] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      spiritualAPI.getAdminUsers(),
      spiritualAPI.getAdminSubscriptionPlans()
    ])
    .then(([usersRes, plansRes]) => {
      setUsers(usersRes.data || []);
      setSubscriptionPlans(plansRes?.data || []);
    })
    .finally(() => setLoading(false));
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">User & Subscription Management</h2>
      
      {/* Subscription Plans */}
      <div className="mb-8">
        <h3 className="text-xl font-semibold mb-4">Subscription Plans</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {subscriptionPlans.map(plan => (
            <div key={plan.id} className="border rounded-lg p-4 bg-white shadow">
              <h4 className="font-bold text-lg">{plan.name}</h4>
              <p className="text-gray-600 text-sm mb-2">{plan.description}</p>
              <div className="text-2xl font-bold text-green-600">₹{plan.monthly_price}</div>
              <div className="text-sm text-gray-500">{plan.credits_per_month} credits/month</div>
              <div className="mt-2">
                {plan.features && Object.entries(plan.features).map(([feature, enabled]) => (
                  <div key={feature} className={`text-xs ${enabled ? 'text-green-600' : 'text-gray-400'}`}>
                    {enabled ? '✓' : '✗'} {feature.replace('_', ' ')}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Users Table */}
      <div>
        <h3 className="text-xl font-semibold mb-4">Users</h3>
        {!Array.isArray(users) || users.length === 0 ? (
          <div>No users available.</div>
        ) : (
          <table className="min-w-full bg-white border">
            <thead>
              <tr>
                <th className="border px-4 py-2">ID</th>
                <th className="border px-4 py-2">Email</th>
                <th className="border px-4 py-2">Name</th>
                <th className="border px-4 py-2">Role</th>
                <th className="border px-4 py-2">Credits</th>
                <th className="border px-4 py-2">Created At</th>
              </tr>
            </thead>
            <tbody>
              {users.map(user => (
                <tr key={user.id}>
                  <td className="border px-4 py-2">{user.id}</td>
                  <td className="border px-4 py-2">{user.email}</td>
                  <td className="border px-4 py-2">{user.full_name || user.name}</td>
                  <td className="border px-4 py-2">{user.role}</td>
                  <td className="border px-4 py-2">{user.credits}</td>
                  <td className="border px-4 py-2">{user.created_at}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
      
      {/* Add: Advanced search, subscription, credit history, support tools */}
    </div>
  );
} 