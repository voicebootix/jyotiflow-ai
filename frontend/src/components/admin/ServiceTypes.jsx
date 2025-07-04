import { useState, useEffect } from 'react';
import { Plus, Edit, Trash2, Save, X, Eye, EyeOff } from 'lucide-react';
import spiritualAPI from '../../lib/api';

const ServiceTypes = () => {
  const [serviceTypes, setServiceTypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    display_name: '',
    description: '',
    credits_required: 1,
    duration_minutes: 5,
    price_usd: 0,
    service_category: 'guidance',
    avatar_video_enabled: false,
    live_chat_enabled: false,
    icon: '🔮',
    color_gradient: 'from-purple-500 to-indigo-600',
    is_active: true
  });

  useEffect(() => {
    fetchServiceTypes();
  }, []);

  const fetchServiceTypes = async () => {
    try {
      const response = await spiritualAPI.getServiceTypes();
      setServiceTypes(Array.isArray(response) ? response : []);
    } catch (error) {
      console.error('Error fetching service types:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('DEBUG editingId:', editingId, typeof editingId);
    try {
      if (editingId && typeof editingId === 'string' && editingId !== 'service-types') {
        // For updates, send the same payload structure
        const updatePayload = {
          name: formData.name,
          display_name: formData.display_name,
          description: formData.description,
          credits_required: Number(formData.credits_required),
          duration_minutes: Number(formData.duration_minutes),
          price_usd: Number(formData.price_usd),
          service_category: formData.service_category,
          enabled: Boolean(formData.is_active),
          is_active: Boolean(formData.is_active),
          avatar_video_enabled: Boolean(formData.avatar_video_enabled),
          live_chat_enabled: Boolean(formData.live_chat_enabled),
          icon: formData.icon,
          color_gradient: formData.color_gradient
        };
        await spiritualAPI.updateServiceType(editingId, updatePayload);
      } else {
        // Map only the DB fields for backend, add both enabled and is_active for compatibility
        const payload = {
          name: formData.name,
          display_name: formData.display_name,
          description: formData.description,
          credits_required: Number(formData.credits_required),
          duration_minutes: Number(formData.duration_minutes),
          price_usd: Number(formData.price_usd),
          service_category: formData.service_category,
          enabled: Boolean(formData.is_active),
          is_active: Boolean(formData.is_active),
          avatar_video_enabled: Boolean(formData.avatar_video_enabled),
          live_chat_enabled: Boolean(formData.live_chat_enabled),
          icon: formData.icon,
          color_gradient: formData.color_gradient
        };
        await spiritualAPI.createServiceType(payload);
      }
      fetchServiceTypes();
      resetForm();
    } catch (error) {
      console.error('Error saving service type:', error);
    }
  };

  const handleEdit = (serviceType) => {
    setEditingId(serviceType.id);
    setFormData({
      name: serviceType.name,
      display_name: serviceType.display_name,
      description: serviceType.description,
      credits_required: serviceType.credits_required,
      duration_minutes: serviceType.duration_minutes,
      price_usd: serviceType.price_usd,
      service_category: serviceType.service_category,
      avatar_video_enabled: serviceType.avatar_video_enabled,
      live_chat_enabled: serviceType.live_chat_enabled,
      icon: serviceType.icon,
      color_gradient: serviceType.color_gradient,
      is_active: serviceType.is_active
    });
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to disable this service type?')) {
      try {
        await spiritualAPI.deleteServiceType(id);
        fetchServiceTypes();
      } catch (error) {
        console.error('Error deleting service type:', error);
      }
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      display_name: '',
      description: '',
      credits_required: 1,
      duration_minutes: 5,
      price_usd: 0,
      service_category: 'guidance',
      avatar_video_enabled: false,
      live_chat_enabled: false,
      icon: '🔮',
      color_gradient: 'from-purple-500 to-indigo-600',
      is_active: true
    });
    setEditingId(null); // Always reset editingId
    setShowForm(false);
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : type === 'number' ? parseFloat(value) : value
    }));
  };

  if (loading) {
    return <div className="text-center py-8">Loading divine services...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Service Types Management</h2>
          <p className="text-gray-600">Manage dynamic service offerings and pricing</p>
        </div>
        <button
          onClick={() => {
            setShowForm(true);
            setEditingId(null); // Always reset editingId for new service
          }}
          className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors flex items-center space-x-2"
        >
          <Plus size={16} />
          <span>Add Service</span>
        </button>
      </div>

      {/* Service Types List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Service
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Credits
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Duration
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Price
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Features
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {serviceTypes.map((service) => (
                <tr key={service.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className="text-2xl mr-3">{service.icon}</span>
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {service.display_name}
                        </div>
                        <div className="text-sm text-gray-500">{service.name}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {service.credits_required} credits
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {service.duration_minutes} min
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${service.price_usd}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div className="flex space-x-2">
                      {service.avatar_video_enabled && (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          Video
                        </span>
                      )}
                      {service.live_chat_enabled && (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          Live Chat
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      service.is_active 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {service.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleEdit(service)}
                        className="text-indigo-600 hover:text-indigo-900"
                      >
                        <Edit size={16} />
                      </button>
                      <button
                        onClick={() => handleDelete(service.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add/Edit Form */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium">
                {editingId ? 'Edit Service Type' : 'Add New Service Type'}
              </h3>
              <button onClick={resetForm} className="text-gray-400 hover:text-gray-600">
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Service Name</label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-purple-500 focus:border-purple-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Display Name</label>
                  <input
                    type="text"
                    name="display_name"
                    value={formData.display_name}
                    onChange={handleInputChange}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-purple-500 focus:border-purple-500"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Description</label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  rows={3}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-purple-500 focus:border-purple-500"
                />
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Credits Required</label>
                  <input
                    type="number"
                    name="credits_required"
                    value={formData.credits_required}
                    onChange={handleInputChange}
                    min="1"
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-purple-500 focus:border-purple-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Duration (minutes)</label>
                  <input
                    type="number"
                    name="duration_minutes"
                    value={formData.duration_minutes}
                    onChange={handleInputChange}
                    min="1"
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-purple-500 focus:border-purple-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Price (USD)</label>
                  <input
                    type="number"
                    name="price_usd"
                    value={formData.price_usd}
                    onChange={handleInputChange}
                    min="0"
                    step="0.01"
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-purple-500 focus:border-purple-500"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Service Category</label>
                  <select
                    name="service_category"
                    value={formData.service_category}
                    onChange={handleInputChange}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-purple-500 focus:border-purple-500"
                  >
                    <option value="guidance">Spiritual Guidance</option>
                    <option value="astrology">Astrology</option>
                    <option value="meditation">Meditation</option>
                    <option value="healing">Healing</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Icon</label>
                  <input
                    type="text"
                    name="icon"
                    value={formData.icon}
                    onChange={handleInputChange}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-purple-500 focus:border-purple-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Color Gradient</label>
                  <input
                    type="text"
                    name="color_gradient"
                    value={formData.color_gradient}
                    onChange={handleInputChange}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-purple-500 focus:border-purple-500"
                  />
                </div>
              </div>

              <div className="flex space-x-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    name="avatar_video_enabled"
                    checked={formData.avatar_video_enabled}
                    onChange={handleInputChange}
                    className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Avatar Video Enabled</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    name="live_chat_enabled"
                    checked={formData.live_chat_enabled}
                    onChange={handleInputChange}
                    className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Live Chat Enabled</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    name="is_active"
                    checked={formData.is_active}
                    onChange={handleInputChange}
                    className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Active</span>
                </label>
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
                  <span>{editingId ? 'Update' : 'Create'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ServiceTypes; 