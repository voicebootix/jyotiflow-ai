import { useEffect, useState } from 'react';
import spiritualAPI from '../../lib/api';

const CreditPackages = () => {
  const [packages, setPackages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({ name: '', credits_amount: '', bonus_credits: '', price_usd: '' });

  useEffect(() => {
    const fetchPackages = async () => {
      setLoading(true);
      const data = await spiritualAPI.getCreditPackages();
      setPackages(data || []);
      setLoading(false);
    };
    fetchPackages();
  }, []);

  const handleEditClick = (pkg) => {
    setEditingId(pkg.id);
    setEditForm({
      name: pkg.name,
      credits_amount: pkg.credits_amount,
      bonus_credits: pkg.bonus_credits,
      price_usd: pkg.price_usd,
    });
  };

  const handleEditChange = (e) => {
    setEditForm({ ...editForm, [e.target.name]: e.target.value });
  };

  const handleEditSave = async (id) => {
    await spiritualAPI.updateCreditPackage(id, {
      name: editForm.name,
      credits_amount: Number(editForm.credits_amount),
      bonus_credits: Number(editForm.bonus_credits),
      price_usd: Number(editForm.price_usd),
    });
    // Refresh list
    const data = await spiritualAPI.getCreditPackages();
    setPackages(data || []);
    setEditingId(null);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this package?')) {
      await spiritualAPI.deleteCreditPackage(id);
      const data = await spiritualAPI.getCreditPackages();
      setPackages(data || []);
    }
  };

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
            <th className="px-4 py-2 border">Actions</th>
          </tr>
        </thead>
        <tbody>
          {packages.map(pkg => (
            <tr key={pkg.id}>
              {editingId === pkg.id ? (
                <>
                  <td className="px-2 py-2 border">
                    <input name="name" value={editForm.name} onChange={handleEditChange} className="border px-2 py-1 w-full" />
                  </td>
                  <td className="px-2 py-2 border">
                    <input name="credits_amount" type="number" value={editForm.credits_amount} onChange={handleEditChange} className="border px-2 py-1 w-full" />
                  </td>
                  <td className="px-2 py-2 border">
                    <input name="bonus_credits" type="number" value={editForm.bonus_credits} onChange={handleEditChange} className="border px-2 py-1 w-full" />
                  </td>
                  <td className="px-2 py-2 border">
                    <input name="price_usd" type="number" value={editForm.price_usd} onChange={handleEditChange} className="border px-2 py-1 w-full" />
                  </td>
                  <td className="px-2 py-2 border">{pkg.enabled ? 'Active' : 'Inactive'}</td>
                  <td className="px-2 py-2 border">
                    <button onClick={() => handleEditSave(pkg.id)} className="btn btn-sm btn-success mr-2">Save</button>
                    <button onClick={() => setEditingId(null)} className="btn btn-sm btn-secondary">Cancel</button>
                  </td>
                </>
              ) : (
                <>
                  <td className="px-4 py-2 border">{pkg.name}</td>
                  <td className="px-4 py-2 border">{pkg.name} ({pkg.credits_amount})</td>
                  <td className="px-4 py-2 border">{pkg.bonus_credits}</td>
                  <td className="px-4 py-2 border">${pkg.price_usd}</td>
                  <td className="px-4 py-2 border">{pkg.enabled ? 'Active' : 'Inactive'}</td>
                  <td className="px-4 py-2 border">
                    <button onClick={() => handleEditClick(pkg)} className="btn btn-sm btn-primary mr-2">Edit</button>
                    <button onClick={() => handleDelete(pkg.id)} className="btn btn-sm btn-danger">Delete</button>
                  </td>
                </>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default CreditPackages; 