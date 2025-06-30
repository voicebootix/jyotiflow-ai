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
      console.log('subscriptionPlans:', plansRes?.data || []); // Debug log
    })
    .finally(() => setLoading(false));
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">User & Subscription Management</h2>
      
      {/* Subscription Plans */}
      <section className="mt-8">
        <h2 className="text-xl font-bold mb-2">Subscription Plans</h2>
        {subscriptionPlans.length === 0 ? (
          <div className="text-gray-500">No subscription plans found.</div>
        ) : (
          <ul className="space-y-4">
            {subscriptionPlans.map(plan => (
              <li key={plan.id} className="border p-4 rounded">
                <div className="font-semibold">{plan.name} <span className="text-sm text-gray-500">(₹{plan.monthly_price})</span></div>
                <div className="text-gray-700 mb-1">{plan.description}</div>
                <div className="text-xs text-gray-600 mb-1">Credits/month: {plan.credits_per_month}</div>
                <div className="mt-2">
                  <span className="font-medium">Features:</span>
                  <ul className="ml-4 list-disc">
                    {plan.features && Object.entries(plan.features).map(([feature, enabled]) => (
                      <li key={feature} className={enabled ? 'text-green-600' : 'text-gray-400'}>
                        {enabled ? '✓' : '✗'} {feature.replace('_', ' ')}
                      </li>
                    ))}
                  </ul>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

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