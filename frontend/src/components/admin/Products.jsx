import { useEffect, useState } from 'react';
import spiritualAPI from '../../lib/api';
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
    spiritualAPI.getAdminProducts().then(response => {
      if (response && response.success && response.data) {
        // Handle the new API response format
        if (response.data.products) {
          setProducts(response.data.products);
        } else if (Array.isArray(response.data)) {
          setProducts(response.data);
        } else {
          setProducts([]);
        }
      } else if (Array.isArray(response)) {
        // Handle legacy response format
        setProducts(response);
      } else {
        console.error('Invalid products response:', response);
        setProducts([]);
      }
      setLoading(false);
    }).catch(error => {
      console.error('Error fetching products:', error);
      setProducts([]);
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
      await spiritualAPI.deleteAdminProduct(productId);
      fetchProducts();
    }
  }

  async function handleStripeSync() {
    await spiritualAPI.syncStripeProducts();
    fetchProducts();
  }

  if (loading) return <div>Loading...</div>;
  if (!products || !Array.isArray(products) || products.length === 0) return <div>No products available.</div>;

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">Products & SKU Management</h2>
        <div>
          <button className="bg-yellow-500 text-white px-4 py-2 rounded mr-2" onClick={handleStripeSync}>Sync Stripe</button>
          <button className="bg-purple-700 text-white px-4 py-2 rounded" onClick={handleCreate}>+ Create Product</button>
        </div>
      </div>
      <table>
        <thead>
          <tr>
            <th>SKU</th>
            <th>Name</th>
            <th>Price</th>
            <th>Credits</th>
            <th>Active</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {products.map(row => (
            <tr key={row.id}>
              <td>{row.sku_code}</td>
              <td>{row.name}</td>
              <td>{row.price}</td>
              <td>{row.credits_allocated}</td>
              <td>{row.is_active ? "Yes" : "No"}</td>
              <td>
                <button onClick={() => handleEdit(row)}>Edit</button>
                <button onClick={() => handleDelete(row.id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {showForm && (
        <ProductForm
          product={editProduct}
          onClose={handleFormClose}
        />
      )}
    </div>
  );
} 