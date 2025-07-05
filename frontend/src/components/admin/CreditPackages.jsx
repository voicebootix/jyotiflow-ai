import { useEffect, useState } from 'react';
import spiritualAPI from '../../lib/api';

const CreditPackages = () => {
  const [packages, setPackages] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPackages = async () => {
      setLoading(true);
      const data = await spiritualAPI.getCreditPackages();
      setPackages(data || []);
      setLoading(false);
    };
    fetchPackages();
  }, []);

  if (loading) return <div>Loading credit packages...</div>;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Credit Packages</h2>
      <table className="min-w-full bg-white border">
        <thead>
          <tr>
            <th className="px-4 py-2 border">Name</th>
            <th className="px-4 py-2 border">Credits</th>
            <th className="px-4 py-2 border">Bonus</th>
            <th className="px-4 py-2 border">Price ($)</th>
            <th className="px-4 py-2 border">Status</th>
          </tr>
        </thead>
        <tbody>
          {packages.map(pkg => (
            <tr key={pkg.id}>
              <td className="px-4 py-2 border">{pkg.name}</td>
              <td className="px-4 py-2 border">{pkg.credits_amount}</td>
              <td className="px-4 py-2 border">{pkg.bonus_credits}</td>
              <td className="px-4 py-2 border">${pkg.price_usd}</td>
              <td className="px-4 py-2 border">{pkg.enabled ? 'Active' : 'Inactive'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default CreditPackages; 