// தமில - தயாரிப்பு உருவாக்க/திருத்தம்
import { useState } from 'react';
import spiritualAPI from '../../lib/api';

export default function ProductForm({ product, onClose }) {
  const [form, setForm] = useState(product || {
    sku_code: '', name: '', description: '', price: '', credits_allocated: '', is_active: true
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  function handleChange(e) {
    const { name, value, type, checked } = e.target;
    setForm(f => ({ ...f, [name]: type === 'checkbox' ? checked : value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      if (product) {
        await spiritualAPI.updateAdminProduct(product.id, form);
      } else {
        await spiritualAPI.createAdminProduct(form);
      }
      onClose(true);
    } catch (err) {
      setError('Error: ' + (err.message || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <form className="bg-white rounded-lg p-8 w-full max-w-lg shadow" onSubmit={handleSubmit}>
        <h3 className="text-xl font-bold mb-4">{product ? "Edit Product" : "Create Product"}</h3>
        {error && <div className="text-red-600 mb-2">{error}</div>}
        <div className="mb-2">
          <label className="block">SKU Code</label>
          <input name="sku_code" value={form.sku_code} onChange={handleChange} className="w-full border p-2 rounded" required disabled={!!product} />
        </div>
        <div className="mb-2">
          <label className="block">Name</label>
          <input name="name" value={form.name} onChange={handleChange} className="w-full border p-2 rounded" required />
        </div>
        <div className="mb-2">
          <label className="block">Description</label>
          <textarea name="description" value={form.description} onChange={handleChange} className="w-full border p-2 rounded" />
        </div>
        <div className="mb-2">
          <label className="block">Price ($)</label>
          <input name="price" type="number" value={form.price} onChange={handleChange} className="w-full border p-2 rounded" required />
        </div>
        <div className="mb-2">
          <label className="block">Credits Allocated</label>
          <input name="credits_allocated" type="number" value={form.credits_allocated} onChange={handleChange} className="w-full border p-2 rounded" required />
        </div>
        <div className="mb-4">
          <label className="inline-flex items-center">
            <input name="is_active" type="checkbox" checked={form.is_active} onChange={handleChange} />
            <span className="ml-2">Active</span>
          </label>
        </div>
        <div className="flex justify-end">
          <button type="button" className="mr-2 px-4 py-2 rounded bg-gray-200" onClick={() => onClose(false)}>Cancel</button>
          <button type="submit" className="px-4 py-2 rounded bg-purple-700 text-white" disabled={loading}>
            {loading ? "Saving..." : "Save"}
          </button>
        </div>
      </form>
    </div>
  );
} 