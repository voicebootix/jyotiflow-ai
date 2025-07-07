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
    is_active: true,
    // Enhanced features for comprehensive reading
    dynamic_pricing_enabled: false,
    knowledge_domains: [],
    persona_modes: [],
    comprehensive_reading_enabled: false,
    birth_chart_enabled: false,
    remedies_enabled: false,
    voice_enabled: false,
    video_enabled: false
  });

  const knowledgeDomainsOptions = [
    'vedic_astrology', 'western_astrology', 'tarot', 'numerology', 
    'palmistry', 'meditation', 'chakra_healing', 'gemstones', 
    'mantras', 'vastu_shastra', 'spiritual_guidance', 'life_coaching'
  ];

  const personaModesOptions = [
    'traditional_guru', 'modern_advisor', 'compassionate_healer', 
    'practical_guide', 'mystical_sage', 'scientific_astrologer'
  ];

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
          color_gradient: formData.color_gradient,
          // Enhanced features
          dynamic_pricing_enabled: Boolean(formData.dynamic_pricing_enabled),
          knowledge_domains: formData.knowledge_domains,
          persona_modes: formData.persona_modes,
          comprehensive_reading_enabled: Boolean(formData.comprehensive_reading_enabled),
          birth_chart_enabled: Boolean(formData.birth_chart_enabled),
          remedies_enabled: Boolean(formData.remedies_enabled),
          voice_enabled: Boolean(formData.voice_enabled),
          video_enabled: Boolean(formData.video_enabled)
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
          color_gradient: formData.color_gradient,
          // Enhanced features
          dynamic_pricing_enabled: Boolean(formData.dynamic_pricing_enabled),
          knowledge_domains: formData.knowledge_domains,
          persona_modes: formData.persona_modes,
          comprehensive_reading_enabled: Boolean(formData.comprehensive_reading_enabled),
          birth_chart_enabled: Boolean(formData.birth_chart_enabled),
          remedies_enabled: Boolean(formData.remedies_enabled),
          voice_enabled: Boolean(formData.voice_enabled),
          video_enabled: Boolean(formData.video_enabled)
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
      is_active: serviceType.is_active,
      // Enhanced features
      dynamic_pricing_enabled: serviceType.dynamic_pricing_enabled || false,
      knowledge_domains: serviceType.knowledge_domains || [],
      persona_modes: serviceType.persona_modes || [],
      comprehensive_reading_enabled: serviceType.comprehensive_reading_enabled || false,
      birth_chart_enabled: serviceType.birth_chart_enabled || false,
      remedies_enabled: serviceType.remedies_enabled || false,
      voice_enabled: serviceType.voice_enabled || false,
      video_enabled: serviceType.video_enabled || false
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
      is_active: true,
      // Enhanced features
      dynamic_pricing_enabled: false,
      knowledge_domains: [],
      persona_modes: [],
      comprehensive_reading_enabled: false,
      birth_chart_enabled: false,
      remedies_enabled: false,
      voice_enabled: false,
      video_enabled: false
    });
    setEditingId(null);
    setShowForm(false);
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : type === 'number' ? parseFloat(value) : value
    }));
  };

  const handleKnowledgeDomainToggle = (domain) => {
    setFormData(prev => ({
      ...prev,
      knowledge_domains: prev.knowledge_domains.includes(domain)
        ? prev.knowledge_domains.filter(d => d !== domain)
        : [...prev.knowledge_domains, domain]
    }));
  };

  const handlePersonaModeToggle = (mode) => {
    setFormData(prev => ({
      ...prev,
      persona_modes: prev.persona_modes.includes(mode)
        ? prev.persona_modes.filter(m => m !== mode)
        : [...prev.persona_modes, mode]
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
                  Enhanced
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
              {serviceTypes.filter(service => service.is_active).map((service) => (
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
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div className="flex space-x-1">
                      {service.dynamic_pricing_enabled && (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                          Smart Price
                        </span>
                      )}
                      {service.comprehensive_reading_enabled && (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                          Comprehensive
                        </span>
                      )}
                      {service.birth_chart_enabled && (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                          Birth Chart
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
                  <span className="ml-2 text-sm text-gray-700">Avatar Video</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    name="live_chat_enabled"
                    checked={formData.live_chat_enabled}
                    onChange={handleInputChange}
                    className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Live Chat</span>
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

              {/* Enhanced Features Section */}
              <div className="border-t pt-4">
                <h4 className="font-medium text-gray-900 mb-3">Enhanced Features</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        name="dynamic_pricing_enabled"
                        checked={formData.dynamic_pricing_enabled}
                        onChange={handleInputChange}
                        className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">Dynamic Pricing</span>
                    </label>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        name="comprehensive_reading_enabled"
                        checked={formData.comprehensive_reading_enabled}
                        onChange={handleInputChange}
                        className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">Comprehensive Reading</span>
                    </label>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        name="birth_chart_enabled"
                        checked={formData.birth_chart_enabled}
                        onChange={handleInputChange}
                        className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">Birth Chart Analysis</span>
                    </label>
                  </div>
                  <div className="space-y-2">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        name="remedies_enabled"
                        checked={formData.remedies_enabled}
                        onChange={handleInputChange}
                        className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">Personalized Remedies</span>
                    </label>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        name="voice_enabled"
                        checked={formData.voice_enabled}
                        onChange={handleInputChange}
                        className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">Voice Narration</span>
                    </label>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        name="video_enabled"
                        checked={formData.video_enabled}
                        onChange={handleInputChange}
                        className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">Video Generation</span>
                    </label>
                  </div>
                </div>
              </div>

              {/* Knowledge Domains */}
              <div className="border-t pt-4">
                <h4 className="font-medium text-gray-900 mb-3">Knowledge Domains</h4>
                <div className="grid grid-cols-3 gap-2">
                  {knowledgeDomainsOptions.map(domain => (
                    <label key={domain} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={formData.knowledge_domains.includes(domain)}
                        onChange={() => handleKnowledgeDomainToggle(domain)}
                        className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                      />
                      <span className="ml-2 text-xs text-gray-700 capitalize">
                        {domain.replace('_', ' ')}
                      </span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Persona Modes */}
              <div className="border-t pt-4">
                <h4 className="font-medium text-gray-900 mb-3">Persona Modes</h4>
                <div className="grid grid-cols-2 gap-2">
                  {personaModesOptions.map(mode => (
                    <label key={mode} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={formData.persona_modes.includes(mode)}
                        onChange={() => handlePersonaModeToggle(mode)}
                        className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                      />
                      <span className="ml-2 text-xs text-gray-700 capitalize">
                        {mode.replace('_', ' ')}
                      </span>
                    </label>
                  ))}
                </div>
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