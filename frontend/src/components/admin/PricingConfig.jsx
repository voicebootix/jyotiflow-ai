import { useState, useEffect } from 'react';
import { Plus, Edit, Trash2, Save, X, Settings } from 'lucide-react';
import spiritualAPI from '../../lib/api';

const PricingConfig = () => {
  const [pricingConfig, setPricingConfig] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingKey, setEditingKey] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    config_key: '',
    config_value: '',
    config_type: 'string',
    description: ''
  });

  useEffect(() => {
    fetchPricingConfig();
  }, []);

  const fetchPricingConfig = async () => {
    try {
      const response = await spiritualAPI.getPricingConfig();
      // Fix: support { success, data } or array
      setPricingConfig(Array.isArray(response?.data) ? response.data : Array.isArray(response) ? response : []);
    } catch (error) {
      console.error('Error fetching pricing config:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingKey) {
        await spiritualAPI.updatePricingConfig(editingKey, formData);
      } else {
        await spiritualAPI.createPricingConfig(formData);
      }
      fetchPricingConfig();
      resetForm();
    } catch (error) {
      console.error('Error saving pricing config:', error);
    }
  };

  const handleEdit = (config) => {
    setEditingKey(config.config_key);
    setFormData({
      config_key: config.config_key,
      config_value: config.config_value,
      config_type: config.config_type,
      description: config.description
    });
    setShowForm(true);
  };

  const resetForm = () => {
    setFormData({
      config_key: '',
      config_value: '',
      config_type: 'string',
      description: ''
    });
    setEditingKey(null);
    setShowForm(false);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const getConfigValueDisplay = (config) => {
    switch (config.config_type) {
      case 'boolean':
        return config.config_value === 'true' ? 'Yes' : 'No';
      case 'number':
        return parseFloat(config.config_value).toFixed(2);
      case 'json':
        try {
          return JSON.stringify(JSON.parse(config.config_value), null, 2);
        } catch {
          return config.config_value;
        }
      default:
        return config.config_value;
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading pricing configuration...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Pricing Configuration</h2>
          <p className="text-gray-600">Manage dynamic pricing variables and business rules</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors flex items-center space-x-2"
        >
          <Plus size={16} />
          <span>Add Config</span>
        </button>
      </div>

      {/* Pricing Config List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Configuration Key
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Value
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Description
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {pricingConfig.map((config) => (
                <tr key={config.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {config.config_key}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900 max-w-xs truncate">
                      {getConfigValueDisplay(config)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {config.config_type}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-500 max-w-xs truncate">
                      {config.description}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => handleEdit(config)}
                      className="text-indigo-600 hover:text-indigo-900"
                    >
                      <Edit size={16} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Quick Setup Section */}
      <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Setup Templates</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg p-4 border border-purple-200">
            <h4 className="font-medium text-gray-900 mb-2">Cost Protection</h4>
            <p className="text-sm text-gray-600 mb-3">Set minimum profit margins and cost limits</p>
            <button className="text-sm text-purple-600 hover:text-purple-700">
              Configure →
            </button>
          </div>
          <div className="bg-white rounded-lg p-4 border border-purple-200">
            <h4 className="font-medium text-gray-900 mb-2">Session Limits</h4>
            <p className="text-sm text-gray-600 mb-3">Set maximum session durations and credit limits</p>
            <button className="text-sm text-purple-600 hover:text-purple-700">
              Configure →
            </button>
          </div>
          <div className="bg-white rounded-lg p-4 border border-purple-200">
            <h4 className="font-medium text-gray-900 mb-2">Revenue Streams</h4>
            <p className="text-sm text-gray-600 mb-3">Configure revenue percentages and bonuses</p>
            <button className="text-sm text-purple-600 hover:text-purple-700">
              Configure →
            </button>
          </div>
        </div>
      </div>

      {/* Add/Edit Form */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium">
                {editingKey ? 'Edit Configuration' : 'Add New Configuration'}
              </h3>
              <button onClick={resetForm} className="text-gray-400 hover:text-gray-600">
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Configuration Key</label>
                <input
                  type="text"
                  name="config_key"
                  value={formData.config_key}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-purple-500 focus:border-purple-500"
                  required
                  disabled={!!editingKey}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Value</label>
                <textarea
                  name="config_value"
                  value={formData.config_value}
                  onChange={handleInputChange}
                  rows={3}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-purple-500 focus:border-purple-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Type</label>
                <select
                  name="config_type"
                  value={formData.config_type}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-purple-500 focus:border-purple-500"
                >
                  <option value="string">String</option>
                  <option value="number">Number</option>
                  <option value="boolean">Boolean</option>
                  <option value="json">JSON</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Description</label>
                <input
                  type="text"
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-purple-500 focus:border-purple-500"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={resetForm}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-purple-600 text-white rounded-md text-sm font-medium hover:bg-purple-700 flex items-center space-x-2"
                >
                  <Save size={16} />
                  <span>{editingKey ? 'Update' : 'Create'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default PricingConfig; 