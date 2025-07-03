import { useEffect, useState } from 'react';
import spiritualAPI from '../../lib/api';

export default function Donations() {
  const [donations, setDonations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({
    name: '',
    tamil_name: '',
    price_usd: '',
    icon: '',
    description: '',
    enabled: true
  });

  const loadDonations = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await spiritualAPI.request('/api/admin/products/donations');
      setDonations(Array.isArray(data) ? data : []);
    } catch (e) {
      setError('தானங்கள் ஏற்ற முடியவில்லை.');
    }
    setLoading(false);
  };

  useEffect(() => {
    loadDonations();
  }, []);

  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleAdd = () => {
    setForm({ name: '', tamil_name: '', price_usd: '', icon: '', description: '', enabled: true });
    setEditing(null);
    setShowForm(true);
  };

  const handleEdit = donation => {
    setForm({ ...donation });
    setEditing(donation.id);
    setShowForm(true);
  };

  const handleDelete = async id => {
    if (!window.confirm('இந்த தானத்தை நீக்க விரும்புகிறீர்களா?')) return;
    await spiritualAPI.request(`/api/admin/products/donations/${id}`, { method: 'DELETE' });
    loadDonations();
  };

  const handleSubmit = async e => {
    e.preventDefault();
    if (editing) {
      await spiritualAPI.request(`/api/admin/products/donations/${editing}`, {
        method: 'PUT',
        body: JSON.stringify(form),
        headers: { 'Content-Type': 'application/json' }
      });
    } else {
      await spiritualAPI.request('/api/admin/products/donations', {
        method: 'POST',
        body: JSON.stringify(form),
        headers: { 'Content-Type': 'application/json' }
      });
    }
    setShowForm(false);
    loadDonations();
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">தானங்கள் / Donations</h2>
        <button onClick={handleAdd} className="bg-green-600 text-white px-4 py-2 rounded">+ புதிய தானம்</button>
      </div>
      {loading ? (
        <div>தானங்கள் ஏற்றப்படுகிறது...</div>
      ) : error ? (
        <div className="text-red-600">{error}</div>
      ) : (
        <table className="min-w-full bg-white border">
          <thead>
            <tr>
              <th className="p-2 border">Icon</th>
              <th className="p-2 border">Name</th>
              <th className="p-2 border">Tamil Name</th>
              <th className="p-2 border">Price ($)</th>
              <th className="p-2 border">Description</th>
              <th className="p-2 border">Enabled</th>
              <th className="p-2 border">Actions</th>
            </tr>
          </thead>
          <tbody>
            {donations.map(donation => (
              <tr key={donation.id} className={!donation.enabled ? 'opacity-50' : ''}>
                <td className="p-2 border text-2xl">{donation.icon}</td>
                <td className="p-2 border">{donation.name}</td>
                <td className="p-2 border">{donation.tamil_name}</td>
                <td className="p-2 border">${donation.price_usd}</td>
                <td className="p-2 border">{donation.description}</td>
                <td className="p-2 border">{donation.enabled ? '✔️' : '❌'}</td>
                <td className="p-2 border">
                  <button onClick={() => handleEdit(donation)} className="text-blue-600 mr-2">Edit</button>
                  <button onClick={() => handleDelete(donation.id)} className="text-red-600">Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
          <form onSubmit={handleSubmit} className="bg-white p-8 rounded shadow-lg w-full max-w-md">
            <h3 className="text-xl font-bold mb-4">{editing ? 'தானம் திருத்து / Edit Donation' : 'புதிய தானம் / New Donation'}</h3>
            <div className="mb-3">
              <label className="block mb-1">Icon (Emoji)</label>
              <input name="icon" value={form.icon} onChange={handleChange} className="w-full border p-2 rounded" maxLength={2} />
            </div>
            <div className="mb-3">
              <label className="block mb-1">Name (English)</label>
              <input name="name" value={form.name} onChange={handleChange} className="w-full border p-2 rounded" required />
            </div>
            <div className="mb-3">
              <label className="block mb-1">Tamil Name</label>
              <input name="tamil_name" value={form.tamil_name} onChange={handleChange} className="w-full border p-2 rounded" required />
            </div>
            <div className="mb-3">
              <label className="block mb-1">Price ($)</label>
              <input name="price_usd" value={form.price_usd} onChange={handleChange} className="w-full border p-2 rounded" type="number" step="0.01" required />
            </div>
            <div className="mb-3">
              <label className="block mb-1">Description</label>
              <input name="description" value={form.description} onChange={handleChange} className="w-full border p-2 rounded" />
            </div>
            <div className="mb-3 flex items-center">
              <input type="checkbox" name="enabled" checked={form.enabled} onChange={e => setForm({ ...form, enabled: e.target.checked })} className="mr-2" />
              <span>Enabled</span>
            </div>
            <div className="flex justify-end space-x-2 mt-4">
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 bg-gray-300 rounded">Cancel</button>
              <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded">{editing ? 'Update' : 'Add'}</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
} 