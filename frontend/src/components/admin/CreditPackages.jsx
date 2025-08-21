import { useEffect, useState } from "react";
import {
  Plus,
  Edit,
  Trash2,
  Save,
  X,
  Eye,
  EyeOff,
  DollarSign,
  Gift,
} from "lucide-react";
import spiritualAPI from "../../lib/api";

const CreditPackages = () => {
  const [packages, setPackages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    credits_amount: "",
    price_usd: "",
    bonus_credits: "",
    description: "",
    enabled: true,
  });

  useEffect(() => {
    fetchPackages();
  }, []);

  const fetchPackages = async () => {
    try {
      setLoading(true);
      const data = await spiritualAPI.getAdminCreditPackages();
      console.log("Credit packages data:", data); // Debug log
      setPackages(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Error fetching credit packages:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        // Update existing package
        await spiritualAPI.updateCreditPackage(editingId, {
          name: formData.name,
          credits_amount: Number(formData.credits_amount),
          price_usd: Number(formData.price_usd),
          bonus_credits: Number(formData.bonus_credits),
          description: formData.description,
          enabled: formData.enabled,
        });
      } else {
        // Create new package
        await spiritualAPI.createCreditPackage({
          name: formData.name,
          credits_amount: Number(formData.credits_amount),
          price_usd: Number(formData.price_usd),
          bonus_credits: Number(formData.bonus_credits),
          description: formData.description,
          enabled: formData.enabled,
        });
      }
      fetchPackages();
      resetForm();
    } catch (error) {
      console.error("Error saving credit package:", error);
      alert("Error saving credit package. Please try again.");
    }
  };

  const handleEdit = (pkg) => {
    setEditingId(pkg.id);
    setFormData({
      name: pkg.name,
      credits_amount: pkg.credits_amount || pkg.credits,
      price_usd: pkg.price_usd,
      bonus_credits: pkg.bonus_credits || 0,
      description: pkg.description || "",
      enabled: pkg.enabled !== false,
    });
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (
      window.confirm(
        "Are you sure you want to delete this credit package? This action cannot be undone."
      )
    ) {
      try {
        await spiritualAPI.deleteCreditPackage(id);
        fetchPackages();
      } catch (error) {
        console.error("Error deleting credit package:", error);
        alert("Error deleting credit package. Please try again.");
      }
    }
  };

  const handleToggleStatus = async (id, currentStatus) => {
    try {
      await spiritualAPI.updateCreditPackage(id, {
        enabled: !currentStatus,
      });
      fetchPackages();
    } catch (error) {
      console.error("Error updating package status:", error);
      alert("Error updating package status. Please try again.");
    }
  };

  const resetForm = () => {
    setFormData({
      name: "",
      credits_amount: "",
      price_usd: "",
      bonus_credits: "",
      description: "",
      enabled: true,
    });
    setEditingId(null);
    setShowForm(false);
  };

  const createNewPackage = () => {
    setEditingId(null);
    setFormData({
      name: "",
      credits_amount: "",
      price_usd: "",
      bonus_credits: "",
      description: "",
      enabled: true,
    });
    setShowForm(true);
  };

  if (loading)
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
        <span className="ml-2">Loading credit packages...</span>
      </div>
    );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Credit Packages</h2>
          <p className="text-gray-600">
            Manage credit packages that users can purchase
          </p>
        </div>
        <button
          onClick={createNewPackage}
          className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>Add Package</span>
        </button>
      </div>

      {/* Create/Edit Form */}
      {showForm && (
        <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              {editingId ? "Edit Credit Package" : "Create New Credit Package"}
            </h3>
            <button
              onClick={resetForm}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Package Name *
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  required
                  placeholder="e.g., Starter Pack"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Credits Amount *
                </label>
                <input
                  type="number"
                  name="credits_amount"
                  value={formData.credits_amount}
                  onChange={handleInputChange}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  required
                  min="1"
                  placeholder="e.g., 10"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Price (USD) *
                </label>
                <div className="relative">
                  <DollarSign className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
                  <input
                    type="number"
                    name="price_usd"
                    value={formData.price_usd}
                    onChange={handleInputChange}
                    className="w-full border border-gray-300 rounded-md pl-10 pr-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    required
                    min="0"
                    step="0.01"
                    placeholder="e.g., 9.99"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Bonus Credits
                </label>
                <div className="relative">
                  <Gift className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
                  <input
                    type="number"
                    name="bonus_credits"
                    value={formData.bonus_credits}
                    onChange={handleInputChange}
                    className="w-full border border-gray-300 rounded-md pl-10 pr-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    min="0"
                    placeholder="e.g., 2"
                  />
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                rows={3}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="Describe the package benefits..."
              />
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                name="enabled"
                checked={formData.enabled}
                onChange={handleInputChange}
                className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
              />
              <label className="ml-2 text-sm text-gray-700">
                Enable this package for users
              </label>
            </div>

            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={resetForm}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors"
              >
                {editingId ? "Update Package" : "Create Package"}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Packages List */}
      <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            Available Packages ({packages.length})
          </h3>
        </div>

        {packages.length === 0 ? (
          <div className="p-8 text-center">
            <Gift className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">
              No credit packages
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              Get started by creating your first credit package.
            </p>
            <div className="mt-6">
              <button
                onClick={createNewPackage}
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-purple-600 hover:bg-purple-700"
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Package
              </button>
            </div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Package
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Credits
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Price
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
                {packages.map((pkg) => (
                  <tr key={pkg.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {pkg.name}
                        </div>
                        {pkg.description && (
                          <div className="text-sm text-gray-500">
                            {pkg.description}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {pkg.credits_amount || pkg.credits} credits
                      </div>
                      {pkg.bonus_credits > 0 && (
                        <div className="text-sm text-green-600">
                          +{pkg.bonus_credits} bonus
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        ${pkg.price_usd}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <button
                        onClick={() => handleToggleStatus(pkg.id, pkg.enabled)}
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          pkg.enabled
                            ? "bg-green-100 text-green-800"
                            : "bg-red-100 text-red-800"
                        }`}
                      >
                        {pkg.enabled ? (
                          <>
                            <Eye className="w-3 h-3 mr-1" />
                            Active
                          </>
                        ) : (
                          <>
                            <EyeOff className="w-3 h-3 mr-1" />
                            Inactive
                          </>
                        )}
                      </button>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleEdit(pkg)}
                          className="text-purple-600 hover:text-purple-900"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(pkg.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default CreditPackages;
