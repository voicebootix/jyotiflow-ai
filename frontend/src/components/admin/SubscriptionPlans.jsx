import React, { useEffect, useState } from "react";
import {
  CreditCard,
  Star,
  Users,
  Calendar,
  DollarSign,
  CheckCircle,
  Edit,
  Plus,
  Trash2,
  Crown,
  Zap,
} from "lucide-react";
import spiritualAPI from "../../lib/api";

const SubscriptionPlans = () => {
  const [subscriptionPlans, setSubscriptionPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingPlan, setEditingPlan] = useState(null);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    fetchSubscriptionPlans();
  }, []);

  const fetchSubscriptionPlans = async () => {
    try {
      setLoading(true);
      const response = await spiritualAPI.getAdminSubscriptionPlans();

      // Handle response format - the API returns an array directly
      if (Array.isArray(response)) {
        setSubscriptionPlans(response);
      } else if (response && response.data && Array.isArray(response.data)) {
        setSubscriptionPlans(response.data);
      } else {
        console.error("Invalid subscription plans response:", response);
        setSubscriptionPlans([]);
      }
    } catch (error) {
      console.error("Error fetching subscription plans:", error);
      setSubscriptionPlans([]);
    } finally {
      setLoading(false);
    }
  };

  const getPlanIcon = (planId) => {
    if (planId?.includes("basic")) return Users;
    if (planId?.includes("premium")) return Star;
    if (planId?.includes("divine")) return Crown;
    return CreditCard;
  };

  const getPlanColor = (planId) => {
    if (planId?.includes("basic"))
      return "text-blue-600 bg-blue-50 border-blue-200";
    if (planId?.includes("premium"))
      return "text-purple-600 bg-purple-50 border-purple-200";
    if (planId?.includes("divine"))
      return "text-yellow-600 bg-yellow-50 border-yellow-200";
    return "text-gray-600 bg-gray-50 border-gray-200";
  };

  const formatPrice = (price, billingPeriod) => {
    return `$${price}${billingPeriod === "monthly" ? "/month" : "/year"}`;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            💳 Subscription Plans
          </h1>
          <p className="text-gray-600 mt-2">
            Manage pricing plans and subscription offerings
          </p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors flex items-center space-x-2"
        >
          <Plus size={16} />
          <span>Add New Plan</span>
        </button>
      </div>

      {/* Plans Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {subscriptionPlans.map((plan) => {
          const Icon = getPlanIcon(plan.plan_id);
          const colorClasses = getPlanColor(plan.plan_id);

          return (
            <div
              key={plan.id}
              className={`border-2 rounded-xl p-6 transition-all hover:shadow-lg ${colorClasses}`}
            >
              {/* Plan Header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <Icon className="w-8 h-8" />
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">
                      {plan.name}
                    </h3>
                    <p className="text-sm text-gray-600">{plan.description}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setEditingPlan(plan)}
                    className="p-2 text-gray-400 hover:text-purple-600 transition-colors"
                  >
                    <Edit size={16} />
                  </button>
                  <button className="p-2 text-gray-400 hover:text-red-600 transition-colors">
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>

              {/* Pricing */}
              <div className="mb-6">
                <div className="flex items-baseline space-x-2">
                  <span className="text-3xl font-bold text-gray-900">
                    ${plan.price_usd}
                  </span>
                  <span className="text-gray-600">
                    /{plan.billing_period === "monthly" ? "month" : "year"}
                  </span>
                </div>
                <div className="flex items-center space-x-4 mt-2 text-sm text-gray-600">
                  <div className="flex items-center space-x-1">
                    <Zap size={14} />
                    <span>{plan.credits_per_period} credits</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Calendar size={14} />
                    <span>{plan.billing_period}</span>
                  </div>
                </div>
              </div>

              {/* Features */}
              <div className="space-y-3 mb-6">
                <h4 className="font-semibold text-gray-900">Features:</h4>
                <ul className="space-y-2">
                  {plan.features &&
                    plan.features.map((feature, index) => (
                      <li key={index} className="flex items-start space-x-2">
                        <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                        <span className="text-sm text-gray-700">{feature}</span>
                      </li>
                    ))}
                </ul>
              </div>

              {/* Plan Details */}
              <div className="space-y-2 text-xs text-gray-500 border-t pt-4">
                <div className="flex justify-between">
                  <span>Plan ID:</span>
                  <span className="font-mono">{plan.plan_id}</span>
                </div>
                <div className="flex justify-between">
                  <span>Status:</span>
                  <span
                    className={`px-2 py-1 rounded-full ${
                      plan.is_active
                        ? "bg-green-100 text-green-800"
                        : "bg-red-100 text-red-800"
                    }`}
                  >
                    {plan.is_active ? "Active" : "Inactive"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Created:</span>
                  <span>{formatDate(plan.created_at)}</span>
                </div>
                {plan.stripe_product_id && (
                  <div className="flex justify-between">
                    <span>Stripe Product:</span>
                    <span className="font-mono text-blue-600">
                      {plan.stripe_product_id}
                    </span>
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div className="mt-4 pt-4 border-t">
                <div className="flex space-x-2">
                  <button className="flex-1 bg-white border border-gray-300 text-gray-700 px-3 py-2 rounded-lg text-sm hover:bg-gray-50 transition-colors">
                    View Details
                  </button>
                  <button className="flex-1 bg-purple-600 text-white px-3 py-2 rounded-lg text-sm hover:bg-purple-700 transition-colors">
                    Edit Plan
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Summary Stats */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <CreditCard className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-gray-900">
                {subscriptionPlans.length}
              </h3>
              <p className="text-sm text-gray-600">Total Plans</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-gray-900">
                {subscriptionPlans.filter((plan) => plan.is_active).length}
              </h3>
              <p className="text-sm text-gray-600">Active Plans</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <DollarSign className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-gray-900">
                ${Math.min(...subscriptionPlans.map((p) => p.price_usd))} - $
                {Math.max(...subscriptionPlans.map((p) => p.price_usd))}
              </h3>
              <p className="text-sm text-gray-600">Price Range</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <Zap className="w-6 h-6 text-yellow-600" />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-gray-900">
                {subscriptionPlans.reduce(
                  (sum, plan) => sum + plan.credits_per_period,
                  0
                )}
              </h3>
              <p className="text-sm text-gray-600">Total Credits</p>
            </div>
          </div>
        </div>
      </div>

      {/* Empty State */}
      {subscriptionPlans.length === 0 && (
        <div className="text-center py-12">
          <CreditCard className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            No Subscription Plans
          </h3>
          <p className="text-gray-600 mb-4">
            Create your first subscription plan to get started.
          </p>
          <button
            onClick={() => setShowForm(true)}
            className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition-colors"
          >
            Create First Plan
          </button>
        </div>
      )}
    </div>
  );
};

export default SubscriptionPlans;
