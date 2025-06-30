// தமில - பயனர் மேலாண்மை
import { useEffect, useState } from 'react';
import spiritualAPI from '../../lib/api';
import Loader from '../ui/Loader';
import { Table } from '../ui/table';

export default function UserManagement() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    spiritualAPI.getAdminUsers().then(setUsers).finally(() => setLoading(false));
  }, []);

  if (loading) return <Loader message="பயனர் தரவு ஏற்றப்படுகிறது..." />;
  if (!users || users.length === 0) return <div>No users available.</div>;

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">User & Subscription Management</h2>
      <Table
        columns={[
          { label: 'Email', key: 'email' },
          { label: 'Role', key: 'role' },
          { label: 'Credits', key: 'credits' },
          { label: 'Subscription', key: 'subscription' }
        ]}
        data={users}
      />
      {/* Add: Advanced search, subscription, credit history, support tools */}
    </div>
  );
} 