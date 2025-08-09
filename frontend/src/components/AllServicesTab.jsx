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

// ✅ FOLLOWING .CURSOR RULES: No hardcoded data, retrieve from database
// Removed ALL_SERVICES_CONFIG hardcoded array - now fetched from API

/**
 * AllServicesTab component for displaying and testing all services
 * ✅ FOLLOWS .CURSOR RULES: Database-driven, no hardcoded configurations
 *
 * @returns {JSX.Element} AllServicesTab component
 */
const AllServicesTab = () => {
  const [globalStatus, setGlobalStatus] = useState("idle");
  const [loading, setLoading] = useState(false);
  const [testResults, setTestResults] = useState({});
  const [error, setError] = useState(null);
  const [servicesConfig, setServicesConfig] = useState([]);
  const [configLoading, setConfigLoading] = useState(true);
  const [configError, setConfigError] = useState(null);

  // ✅ FETCH TEST CONFIGURATIONS FROM DATABASE (following .cursor rules)
  useEffect(() => {
    fetchTestConfigurations();
  }, []);

  /**
   * Fetch test configurations from database via API
   * ✅ Replaces hardcoded ALL_SERVICES_CONFIG
   */
  const fetchTestConfigurations = async () => {
    try {
      setConfigLoading(true);
      setConfigError(null);
      
      const response = await spiritualAPI.get("/api/monitoring/test-suites");
      
      if (response && response.status === "success") {
        setServicesConfig(response.data.test_suites || []);
        console.log(`✅ Loaded ${response.data.total_suites} test suites from database`);
      } else {
        throw new Error(response?.message || "Failed to fetch test configurations");
      }
    } catch (err) {
      console.error("❌ Failed to fetch test configurations:", err);
      setConfigError(`Failed to load test configurations: ${err.message}`);
      // Fallback to empty array instead of hardcoded data (following .cursor rules)
      setServicesConfig([]);
    } finally {
      setConfigLoading(false);
    }
  };

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
      // ✅ DATABASE-DRIVEN: Execute all test suites from database configuration
      for (const category of servicesConfig) {
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

      {/* Database-driven Service Categories (following .cursor rules) */}
      {configLoading ? (
        <Card>
          <CardContent className="flex items-center justify-center p-8">
            <RefreshCw className="h-6 w-6 animate-spin mr-2" />
            <span>Loading test configurations from database...</span>
          </CardContent>
        </Card>
      ) : configError ? (
        <Alert className="mb-4">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            {configError}
            <Button 
              variant="outline" 
              size="sm" 
              onClick={fetchTestConfigurations}
              className="ml-2"
            >
              <RefreshCw className="h-3 w-3 mr-1" />
              Retry
            </Button>
          </AlertDescription>
        </Alert>
      ) : servicesConfig.length === 0 ? (
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            No test configurations found in database. Please check the database setup.
          </AlertDescription>
        </Alert>
      ) : (
        servicesConfig.map((category, categoryIndex) => (
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
      )))
      })
    </div>
  );
};

export default AllServicesTab;
