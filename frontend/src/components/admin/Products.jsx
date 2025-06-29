import { useEffect, useState } from 'react';
import api from '../../lib/api';
import Loader from '../ui/Loader';
import Table from '../ui/table';
import ProductForm from './ProductForm';

// தமில - தயாரிப்பு மேலாண்மை
export default function Products() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editProduct, setEditProduct] = useState(null);

  useEffect(() => { fetchProducts(); }, []);

  function fetchProducts() {
    setLoading(true);
    api.getAdminProducts().then(data => {
      setProducts(data);
      setLoading(false);
    });
  }

  function handleEdit(product) {
    setEditProduct(product);
    setShowForm(true);
  }

  function handleCreate() {
    setEditProduct(null);
    setShowForm(true);
  }

  function handleFormClose(refresh) {
    setShowForm(false);
    setEditProduct(null);
    if (refresh) fetchProducts();
  }

  async function handleDelete(productId) {
    if (window.confirm("Are you sure you want to delete this product?")) {
      await api.deleteAdminProduct(productId);
      fetchProducts();
    }
  }

  async function handleStripeSync() {
    await api.syncStripeProducts();
    fetchProducts();
  }

  if (loading) return <Loader message="தயவு செய்து காத்திருக்கவும்..." />;

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">Products & SKU Management</h2>
        <div>
          <button className="bg-yellow-500 text-white px-4 py-2 rounded mr-2" onClick={handleStripeSync}>Sync Stripe</button>
          <button className="bg-purple-700 text-white px-4 py-2 rounded" onClick={handleCreate}>+ Create Product</button>
        </div>
      </div>
      <Table
        columns={[
          { label: 'SKU', key: 'sku_code' },
          { label: 'Name', key: 'name' },
          { label: 'Price', key: 'price' },
          { label: 'Credits', key: 'credits_allocated' },
          { label: 'Active', key: 'is_active', render: row => row.is_active ? "Yes" : "No" },
          { label: 'Actions', key: 'actions', render: (row) => (
            <div>
              <button className="text-blue-600 mr-2" onClick={() => handleEdit(row)}>Edit</button>
              <button className="text-red-600" onClick={() => handleDelete(row.id)}>Delete</button>
            </div>
          )}
        ]}
        data={products}
      />
      {showForm && (
        <ProductForm
          product={editProduct}
          onClose={handleFormClose}
        />
      )}
      {/* Add: AI pricing, analytics */}
    </div>
  );
} 