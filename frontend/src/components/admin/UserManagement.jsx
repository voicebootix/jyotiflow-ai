// தமில - பயனர் மேலாண்மை
import { useEffect, useState } from 'react';
import spiritualAPI from '../../lib/api';

export default function UserManagement() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    spiritualAPI.getAdminUsers().then(setUsers).finally(() => setLoading(false));
  }, []);

  if (loading) return <div>Loading...</div>;
  if (!users || users.length === 0) return <div>No users available.</div>;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">User & Subscription Management</h2>
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
      {/* Add: Advanced search, subscription, credit history, support tools */}
    </div>
  );
} 