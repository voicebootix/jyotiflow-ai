import { useState, useEffect } from 'react';
import { Plus, Edit, Trash2, Save, X, Send, Calendar, BarChart2 } from 'lucide-react';
import spiritualAPI from '../../lib/api';

const contentTypes = [
  { value: 'daily_wisdom', label: 'Daily Wisdom' },
  { value: 'satsang_highlight', label: 'Satsang Highlight' },
  { value: 'spiritual_teaching', label: 'Spiritual Teaching' },
];

const platforms = [
  'instagram', 'twitter', 'facebook', 'youtube', 'linkedin'
];

const SocialContentManagement = () => {
  const [queue, setQueue] = useState([]);
  const [published, setPublished] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    platform: 'instagram',
    content_type: 'daily_wisdom',
    content_text: '',
    media_url: '',
    scheduled_at: '',
    status: 'draft'
  });
  const [editingId, setEditingId] = useState(null);

  useEffect(() => {
    fetchContent();
  }, []);

  const fetchContent = async () => {
    setLoading(true);
    try {
      const data = await spiritualAPI.getAdminSocialContent();
      if (Array.isArray(data)) {
        setQueue(data.filter(c => c.status === 'draft' || c.status === 'scheduled'));
        setPublished(data.filter(c => c.status === 'published'));
      } else {
        setQueue([]);
        setPublished([]);
      }
    } catch (e) {
      setQueue([]);
      setPublished([]);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        await spiritualAPI.updateAdminSocialContent(editingId, formData);
      } else {
        await spiritualAPI.createAdminSocialContent(formData);
      }
      fetchContent();
      resetForm();
    } catch (e) {
      // handle error
    }
  };

  const handleEdit = (content) => {
    setEditingId(content.id);
    setFormData({
      platform: content.platform,
      content_type: content.content_type,
      content_text: content.content_text,
      media_url: content.media_url,
      scheduled_at: content.scheduled_at || '',
      status: content.status
    });
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this content?')) {
      await spiritualAPI.deleteAdminSocialContent(id);
      fetchContent();
    }
  };

  const resetForm = () => {
    setFormData({
      platform: 'instagram',
      content_type: 'daily_wisdom',
      content_text: '',
      media_url: '',
      scheduled_at: '',
      status: 'draft'
    });
    setEditingId(null);
    setShowForm(false);
  };

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Social Content Management</h2>
          <p className="text-gray-600">Manage, schedule, and publish posts to social media platforms</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 flex items-center space-x-2"
        >
          <Plus size={16} />
          <span>New Post</span>
        </button>
      </div>

      {/* Queue Section */}
      <div>
        <h3 className="font-bold mb-2">Content Queue</h3>
        {queue.length === 0 ? (
          <div className="text-gray-500">No queued content.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2">Type</th>
                  <th className="px-4 py-2">Platform</th>
                  <th className="px-4 py-2">Content</th>
                  <th className="px-4 py-2">Scheduled At</th>
                  <th className="px-4 py-2">Status</th>
                  <th className="px-4 py-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {queue.map((c) => (
                  <tr key={c.id} className="hover:bg-gray-50">
                    <td className="px-4 py-2">{c.content_type}</td>
                    <td className="px-4 py-2">{c.platform}</td>
                    <td className="px-4 py-2 max-w-xs truncate">{c.content_text}</td>
                    <td className="px-4 py-2">{c.scheduled_at ? new Date(c.scheduled_at).toLocaleString() : '-'}</td>
                    <td className="px-4 py-2">{c.status}</td>
                    <td className="px-4 py-2">
                      <button onClick={() => handleEdit(c)} className="text-indigo-600 hover:text-indigo-900 mr-2"><Edit size={16} /></button>
                      <button onClick={() => handleDelete(c.id)} className="text-red-600 hover:text-red-900"><Trash2 size={16} /></button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Published Section */}
      <div>
        <h3 className="font-bold mb-2 mt-8">Published Content</h3>
        {published.length === 0 ? (
          <div className="text-gray-500">No published content.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2">Type</th>
                  <th className="px-4 py-2">Platform</th>
                  <th className="px-4 py-2">Content</th>
                  <th className="px-4 py-2">Published At</th>
                  <th className="px-4 py-2">Performance</th>
                  <th className="px-4 py-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {published.map((c) => (
                  <tr key={c.id} className="hover:bg-gray-50">
                    <td className="px-4 py-2">{c.content_type}</td>
                    <td className="px-4 py-2">{c.platform}</td>
                    <td className="px-4 py-2 max-w-xs truncate">{c.content_text}</td>
                    <td className="px-4 py-2">{c.published_at ? new Date(c.published_at).toLocaleString() : '-'}</td>
                    <td className="px-4 py-2">
                      {c.engagement_metrics ? (
                        <span>
                          <BarChart2 size={14} className="inline mr-1" />
                          {c.engagement_metrics.likes || 0} Likes, {c.engagement_metrics.shares || 0} Shares
                        </span>
                      ) : '-'}
                    </td>
                    <td className="px-4 py-2">
                      <button onClick={() => handleEdit(c)} className="text-indigo-600 hover:text-indigo-900 mr-2"><Edit size={16} /></button>
                      <button onClick={() => handleDelete(c.id)} className="text-red-600 hover:text-red-900"><Trash2 size={16} /></button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Create/Edit Form */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium">
                {editingId ? 'Edit Social Content' : 'Create New Social Content'}
              </h3>
              <button onClick={resetForm} className="text-gray-400 hover:text-gray-600">
                <X size={20} />
              </button>
            </div>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Platform</label>
                <select
                  name="platform"
                  value={formData.platform}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  {platforms.map(p => <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Content Type</label>
                <select
                  name="content_type"
                  value={formData.content_type}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  {contentTypes.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Content Text</label>
                <textarea
                  name="content_text"
                  value={formData.content_text}
                  onChange={handleInputChange}
                  rows={3}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Media URL</label>
                <input
                  type="text"
                  name="media_url"
                  value={formData.media_url}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Scheduled At</label>
                <input
                  type="datetime-local"
                  name="scheduled_at"
                  value={formData.scheduled_at}
                  onChange={handleInputChange}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
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

export default SocialContentManagement; 