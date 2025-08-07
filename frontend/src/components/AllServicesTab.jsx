import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Play,
  RefreshCw,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Activity,
  Target,
} from "lucide-react";
import spiritualAPI from "../lib/api";
import ServiceStatusCard from "./ServiceStatusCard";

/**
 * Configuration for all services organized by category
 * @constant {Array}
 */
const ALL_SERVICES_CONFIG = [
  // Core Platform Services
  {
    category: "Core Platform",
    services: [
      {
        title: "Database Tests",
        testType: "database",
        icon: "🗄️",
        priority: "critical",
        description: "Core database operations and data integrity",
      },
      {
        title: "API Tests",
        testType: "api",
        icon: "🔌",
        priority: "critical",
        description: "REST API endpoint functionality",
      },
      {
        title: "Integration Tests",
        testType: "integration",
        icon: "🔗",
        priority: "high",
        description: "End-to-end workflow validation",
      },
      {
        title: "Performance Tests",
        testType: "performance",
        icon: "⚡",
        priority: "high",
        description: "Load and scalability testing",
      },
      {
        title: "Security Tests",
        testType: "security",
        icon: "🔒",
        priority: "critical",
        description: "Vulnerability protection validation",
      },
      {
        title: "Auto-Healing Tests",
        testType: "auto_healing",
        icon: "🔄",
        priority: "high",
        description: "Self-recovery mechanism testing",
      },
    ],
  },
  // Revenue-Critical Services
  {
    category: "Revenue Critical",
    services: [
      {
        title: "Credit & Payment Tests",
        testType: "credit_payment",
        icon: "💳",
        priority: "critical",
        description: "Revenue processing and transactions",
      },
      {
        title: "Spiritual Services Tests",
        testType: "spiritual_services",
        icon: "🕉️",
        priority: "critical",
        description: "Core business logic and AI services",
      },
      {
        title: "Avatar Generation Tests",
        testType: "avatar_generation",
        icon: "🎭",
        priority: "high",
        description: "Video creation and spiritual avatars",
      },
    ],
  },
  // Communication Services
  {
    category: "Communication",
    services: [
      {
        title: "Live Audio/Video Tests",
        testType: "live_audio_video",
        icon: "📹",
        priority: "critical",
        description: "Live consultation and WebRTC",
      },
      {
        title: "Social Media Tests",
        testType: "social_media",
        icon: "📱",
        priority: "high",
        description: "Marketing automation and content",
      },
    ],
  },
  // User Experience Services
  {
    category: "User Experience",
    services: [
      {
        title: "User Management Tests",
        testType: "user_management",
        icon: "👤",
        priority: "critical",
        description: "Authentication and profile management",
      },
      {
        title: "Community Services Tests",
        testType: "community_services",
        icon: "🤝",
        priority: "medium",
        description: "Follow-up systems and engagement",
      },
      {
        title: "Notification Services Tests",
        testType: "notification_services",
        icon: "🔔",
        priority: "medium",
        description: "Alerts and user communication",
      },
    ],
  },
  // Business Management Services
  {
    category: "Business Management",
    services: [
      {
        title: "Admin Services Tests",
        testType: "admin_services",
        icon: "⚙️",
        priority: "high",
        description: "Dashboard, settings, and management",
      },
      {
        title: "Analytics & Monitoring Tests",
        testType: "analytics_monitoring",
        icon: "📊",
        priority: "high",
        description: "Business intelligence and tracking",
      },
    ],
  },
];

/**
 * AllServicesTab component for displaying and testing all services
 *
 * @returns {JSX.Element} AllServicesTab component
 */
const AllServicesTab = () => {
  const [globalStatus, setGlobalStatus] = useState("idle");
  const [loading, setLoading] = useState(false);
  const [testResults, setTestResults] = useState({});
  const [error, setError] = useState(null);

  /**
   * Runs tests for all services
   * @async
   * @function runAllTests
   * @returns {Promise<void>}
   */
  const runAllTests = async () => {
    setLoading(true);
    setGlobalStatus("running");
    setError(null);
    const results = {};

    try {
      // FIXED: Execute all test suites individually and track results
      for (const category of ALL_SERVICES_CONFIG) {
        for (const service of category.services) {
          try {
            // FIXED: Send test_suite parameter for individual execution
            const response = await spiritualAPI.post(
              "/api/monitoring/test-execute",
              {
                test_type: service.testType,
                test_suite: service.testType, // FIXED: Specify individual test suite
                environment: "production",
                triggered_by: "all_services_tab",
              }
            );

            if (response && response.status === "success") {
              results[service.testType] = {
                status: "passed",
                data: response.data || response,
              };
            } else {
              results[service.testType] = {
                status: "failed",
                error: response?.message || "Unknown error",
              };
            }
          } catch (error) {
            results[service.testType] = {
              status: "failed",
              error: error.message,
            };
          }
        }
      }

      setTestResults(results);
      setGlobalStatus("completed");

      // FIXED: Calculate and display individual test results
      const passedTests = Object.values(results).filter(
        (r) => r.status === "passed"
      ).length;
      const totalTests = Object.keys(results).length;

      console.log(
        `All Services Test Results: ${passedTests}/${totalTests} passed`
      );
    } catch (error) {
      setError(`Failed to run all tests: ${error.message}`);
      setGlobalStatus("failed");
    } finally {
      setLoading(false);
    }
  };

  /**
   * Calculates overall statistics for all services
   * @returns {Object} Statistics object with counts and metrics
   */
  const getOverallStats = () => {
    const totalServices = ALL_SERVICES_CONFIG.reduce(
      (sum, category) => sum + category.services.length,
      0
    );
    const completedTests = Object.keys(testResults).length;
    const passedTests = Object.values(testResults).filter(
      (result) => result.status === "passed"
    ).length;
    const failedTests = Object.values(testResults).filter(
      (result) => result.status === "failed"
    ).length;

    return { totalServices, completedTests, passedTests, failedTests };
  };

  const stats = getOverallStats();

  return (
    <div className="space-y-6" role="main" aria-label="All Services Test Suite">
      {/* Overall Status Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5" aria-hidden="true" />
              All Services Test Suite
            </CardTitle>
            <Button
              onClick={runAllTests}
              disabled={loading}
              className="flex items-center gap-2"
              aria-label="Run tests for all services"
            >
              {loading ? (
                <RefreshCw
                  className="h-4 w-4 animate-spin"
                  aria-hidden="true"
                />
              ) : (
                <Play className="h-4 w-4" aria-hidden="true" />
              )}
              {loading ? "Running All Tests..." : "Run All Tests"}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div
            className="grid grid-cols-2 md:grid-cols-4 gap-4"
            role="region"
            aria-label="Test statistics"
          >
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {stats.totalServices}
              </div>
              <div className="text-sm text-gray-600">Total Services</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {stats.passedTests}
              </div>
              <div className="text-sm text-gray-600">Passed Tests</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">
                {stats.failedTests}
              </div>
              <div className="text-sm text-gray-600">Failed Tests</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-600">
                {stats.completedTests}
              </div>
              <div className="text-sm text-gray-600">Completed</div>
            </div>
          </div>

          {stats.completedTests > 0 && (
            <div
              className="mt-4"
              role="region"
              aria-label="Success rate progress"
            >
              <div className="flex justify-between text-sm mb-2">
                <span>Overall Success Rate</span>
                <span className="font-medium">
                  {stats.completedTests > 0
                    ? (
                        (stats.passedTests / stats.completedTests) *
                        100
                      ).toFixed(1)
                    : 0}
                  %
                </span>
              </div>
              <div
                className="w-full bg-gray-200 rounded-full h-2"
                role="progressbar"
                aria-valuenow={
                  stats.completedTests > 0
                    ? (stats.passedTests / stats.completedTests) * 100
                    : 0
                }
                aria-valuemin="0"
                aria-valuemax="100"
              >
                <div
                  className="bg-green-500 h-2 rounded-full transition-all duration-300"
                  style={{
                    width: `${
                      stats.completedTests > 0
                        ? (stats.passedTests / stats.completedTests) * 100
                        : 0
                    }%`,
                  }}
                ></div>
              </div>
            </div>
          )}

          {error && (
            <Alert className="mt-4" role="alert">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Service Categories */}
      {ALL_SERVICES_CONFIG.map((category, categoryIndex) => (
        <Card key={categoryIndex}>
          <CardHeader>
            <CardTitle className="text-lg">
              {category.category} Services
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {category.services.map((service, serviceIndex) => (
                <ServiceStatusCard
                  key={`${category.category}-${serviceIndex}`}
                  title={service.title}
                  description={service.description}
                  endpoint="/api/monitoring/test-execute"
                  testType={service.testType}
                  icon={service.icon}
                  priority={service.priority}
                />
              ))}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

export default AllServicesTab;
