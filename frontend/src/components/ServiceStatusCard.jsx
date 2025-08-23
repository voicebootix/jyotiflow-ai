import React, { useState } from "react";
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
  Clock,
  Eye,
  X,
} from "lucide-react";

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "https://jyotiflow-ai.onrender.com";

/**
 * ServiceStatusCard component for displaying and testing individual service status
 *
 * @param {Object} props - Component props
 * @param {string} props.title - Service title
 * @param {string} props.description - Service description
 * @param {string} props.endpoint - API endpoint for testing
 * @param {string} props.testType - Type of test to execute
 * @param {string} props.icon - Icon emoji to display
 * @param {string} props.priority - Service priority (critical, high, medium, low)
 * @returns {JSX.Element} ServiceStatusCard component
 */
const ServiceStatusCard = ({
  title,
  description,
  endpoint,
  testType,
  icon,
  priority = "medium",
}) => {
  const [status, setStatus] = useState("idle");
  const [loading, setLoading] = useState(false);
  const [lastResult, setLastResult] = useState(null);
  const [error, setError] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

  /**
   * Triggers a test for the service
   * @async
   * @function triggerTest
   * @returns {Promise<void>}
   */
  const triggerTest = async () => {
    setLoading(true);
    setError(null);
    setStatus("running");

    try {
      // Enhanced API endpoint test execution with proper configuration
      const requestBody = {
        test_type:
          testType === "api" || testType === "api_endpoints"
            ? "integration"
            : testType,
        test_suite:
          testType === "api" || testType === "api_endpoints"
            ? "api_endpoints"
            : testType, // Map both api and api_endpoints to correct suite
        environment: import.meta.env.VITE_APP_ENV || "production",
        triggered_by: "frontend_button",
      };

      console.log(`🧪 Triggering test for ${title}:`, requestBody);

      const response = await fetch(
        `${API_BASE_URL}/api/monitoring/test-execute`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Test-Run": "true",
            "X-Test-Environment": requestBody.environment,
            "User-Agent": "JyotiFlow-Frontend/1.0",
          },
          body: JSON.stringify(requestBody),
        }
      );

      if (response.ok) {
        const data = await response.json();

        // FIXED: Update individual card status based on actual test results
        if (data.status === "success") {
          const testResult = data.data;
          if (testResult && testResult.status) {
            setStatus(testResult.status); // 'passed', 'failed', 'partial'
            setLastResult(testResult);
          } else {
            setStatus("completed");
            setLastResult(data.data || data);
          }
        } else {
          setError(data.message || "Test execution failed");
          setStatus("failed");
        }
      } else {
        const errorMessage = `Test failed with status ${response.status}`;
        setError(errorMessage);
        setStatus("failed");
      }
    } catch (err) {
      const errorMessage = `Test execution failed: ${err.message}`;
      setError(errorMessage);
      setStatus("failed");
    } finally {
      setLoading(false);
    }
  };

  /**
   * Gets the appropriate status icon based on current status
   * @returns {JSX.Element} Status icon component
   */
  const getStatusIcon = () => {
    switch (status) {
      case "running":
        return (
          <RefreshCw
            className="h-4 w-4 animate-spin text-blue-500"
            aria-label="Test running"
          />
        );
      case "completed":
        return (
          <CheckCircle
            className="h-4 w-4 text-green-500"
            aria-label="Test completed successfully"
          />
        );
      case "failed":
        return (
          <XCircle className="h-4 w-4 text-red-500" aria-label="Test failed" />
        );
      default:
        return (
          <Clock className="h-4 w-4 text-gray-400" aria-label="Test idle" />
        );
    }
  };

  /**
   * Gets the appropriate badge styling based on priority
   * @returns {JSX.Element} Priority badge component
   */
  const getStatusBadge = () => {
    const priorityConfig = {
      critical: {
        className: "bg-red-100 text-red-800",
        label: "Critical priority",
      },
      high: {
        className: "bg-orange-100 text-orange-800",
        label: "High priority",
      },
      medium: {
        className: "bg-yellow-100 text-yellow-800",
        label: "Medium priority",
      },
      low: { className: "bg-gray-100 text-gray-800", label: "Low priority" },
    };

    const config = priorityConfig[priority] || priorityConfig.medium;

    return (
      <Badge className={config.className} aria-label={config.label}>
        {(priority || "medium").toUpperCase()}
      </Badge>
    );
  };

  /**
   * Helper functions for safe value display with proper null/undefined checks
   */
  const isDef = (value) => value !== null && value !== undefined;

  const fmtPct = (value, decimals = 1) => {
    if (!isDef(value)) return "N/A";
    const num = Number(value);
    return Number.isFinite(num) ? `${num.toFixed(decimals)}%` : "N/A";
  };

  const fmtMs = (value, decimals = 0) => {
    if (!isDef(value)) return "N/A";
    const num = Number(value);
    return Number.isFinite(num) ? `${num.toFixed(decimals)}ms` : "N/A";
  };

  const fmtNum = (value) => {
    if (!isDef(value)) return "N/A";
    const num = Number(value);
    return Number.isFinite(num) ? num.toString() : "N/A";
  };

  return (
    <>
      <Card
        className="h-full"
        role="region"
        aria-labelledby={`${testType}-title`}
      >
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-lg" role="img" aria-label={`${title} icon`}>
                {icon}
              </span>
              <CardTitle
                id={`${testType}-title`}
                className="text-sm font-medium"
              >
                {title}
              </CardTitle>
            </div>
            <div className="flex items-center gap-2">
              {getStatusIcon()}
              {getStatusBadge()}
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-xs text-gray-600">{description}</p>

          {lastResult && (
            <div
              className="text-xs space-y-1"
              role="region"
              aria-label="Test results"
            >
              <div className="flex justify-between">
                <span>Status:</span>
                <Badge
                  className={
                    lastResult.status === "passed"
                      ? "bg-green-100 text-green-800"
                      : "bg-red-100 text-red-800"
                  }
                >
                  {lastResult.status}
                </Badge>
              </div>
              {isDef(lastResult.success_rate) && (
                <div className="flex justify-between">
                  <span>Success Rate:</span>
                  <span className="font-medium">
                    {fmtPct(lastResult.success_rate)}
                  </span>
                </div>
              )}
              {isDef(lastResult.accessible_endpoints) && (
                <div className="flex justify-between">
                  <span>Endpoints:</span>
                  <span className="font-medium">
                    {fmtNum(lastResult.accessible_endpoints)}/
                    {fmtNum(lastResult.total_endpoints)}
                  </span>
                </div>
              )}
              {isDef(lastResult.avg_response_time_ms) && (
                <div className="flex justify-between">
                  <span>Avg Response:</span>
                  <span className="font-medium">
                    {fmtMs(lastResult.avg_response_time_ms)}
                  </span>
                </div>
              )}

              {/* Show individual endpoint results for ALL test suites */}
              {lastResult.endpoint_results && (
                <div className="mt-2 space-y-1">
                  <div className="text-xs font-medium text-gray-700 mb-1">
                    Endpoint Results:
                  </div>
                  {Object.entries(lastResult.endpoint_results).map(
                    ([key, result], index) => (
                      <div key={index} className="space-y-1">
                        <div className="flex justify-between items-center">
                          <span
                            className="text-xs truncate"
                            title={result.business_function || key}
                          >
                            {result.business_function || key}:
                          </span>
                          <div className="flex items-center gap-1">
                            {result.status === "passed" ? (
                              <CheckCircle className="h-3 w-3 text-green-500" />
                            ) : (
                              <XCircle className="h-3 w-3 text-red-500" />
                            )}
                            <span
                              className={`text-xs ${
                                result.details?.status_code >= 200 &&
                                result.details?.status_code < 300
                                  ? "text-green-600"
                                  : result.details?.status_code >= 400
                                  ? "text-red-600"
                                  : "text-yellow-600"
                              }`}
                            >
                              {result.details?.status_code ||
                                result.status_code}
                            </span>
                            {isDef(
                              result.response_time_ms ||
                                result.details?.response_time_ms
                            ) && (
                              <span className="text-xs text-gray-500">
                                (
                                {fmtMs(
                                  result.response_time_ms ||
                                    result.details?.response_time_ms
                                )}
                                )
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Show brief problem indication */}
                        {result.status === "failed" &&
                          (result.problem_type || result.error_type) && (
                            <div className="text-xs text-red-600 ml-2">
                              ⚠️{" "}
                              {(
                                result.problem_type || result.error_type
                              ).replace(/_/g, " ")}
                            </div>
                          )}

                        {/* Show success reason briefly */}
                        {result.status === "passed" &&
                          (result.status_code === 401 ||
                            result.details?.status_code === 401) && (
                            <div className="text-xs text-green-600 ml-2">
                              ✅ Auth required (expected)
                            </div>
                          )}
                        {result.status === "passed" &&
                          (result.status_code === 200 ||
                            result.details?.status_code === 200) && (
                            <div className="text-xs text-green-600 ml-2">
                              ✅ Working correctly
                            </div>
                          )}
                        {result.status === "passed" &&
                          (result.status_code === 403 ||
                            result.details?.status_code === 403) && (
                            <div className="text-xs text-green-600 ml-2">
                              ✅ Access forbidden (expected)
                            </div>
                          )}
                      </div>
                    )
                  )}
                </div>
              )}

              {/* Show endpoints tested for ALL test suites */}
              {lastResult.endpoints_tested && (
                <div className="mt-2">
                  <div className="text-xs font-medium text-gray-700 mb-1">
                    Tested {lastResult.endpoints_tested.length} endpoints:
                  </div>
                  <div className="text-xs text-gray-600">
                    {lastResult.endpoints_tested.map((ep, i) => (
                      <div
                        key={i}
                        className="truncate"
                        title={`${ep.method} ${ep.endpoint}`}
                      >
                        • {ep.business_function}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Show test execution errors */}
          {error && (
            <Alert className="py-2" role="alert">
              <AlertTriangle className="h-3 w-3" />
              <AlertDescription className="text-xs">{error}</AlertDescription>
            </Alert>
          )}

          {/* Show problems summary for failed tests - ALL test suites */}
          {lastResult && lastResult.failed_tests > 0 && (
            <Alert className="py-2 border-orange-200 bg-orange-50" role="alert">
              <AlertTriangle className="h-3 w-3 text-orange-600" />
              <AlertDescription className="text-xs text-orange-800">
                <strong>Issues Found:</strong> {lastResult.failed_tests}{" "}
                endpoint(s) have problems. Click "View Details" to see specific
                issues and fix suggestions.
              </AlertDescription>
            </Alert>
          )}

          <div className="space-y-2">
            <Button
              size="sm"
              onClick={triggerTest}
              disabled={loading}
              className="w-full text-xs"
              aria-label={`Run test for ${title}`}
            >
              {loading ? (
                <RefreshCw
                  className="h-3 w-3 animate-spin mr-1"
                  aria-hidden="true"
                />
              ) : (
                <Play className="h-3 w-3 mr-1" aria-hidden="true" />
              )}
              {loading ? "Testing..." : "Run Test"}
            </Button>

            {/* View Details Button - only show if we have test results */}
            {(lastResult || error) && (
              <Button
                size="sm"
                variant="outline"
                onClick={() => setShowDetailModal(true)}
                className="w-full text-xs"
                aria-label={`View details for ${title}`}
              >
                <Eye className="h-3 w-3 mr-1" aria-hidden="true" />
                View Details
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Detailed Results Modal */}
      {showDetailModal && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          role="dialog"
          aria-modal="true"
          aria-labelledby="detail-modal-title"
          onClick={(e) => {
            if (e.target === e.currentTarget) {
              setShowDetailModal(false);
            }
          }}
        >
          <Card className="max-w-4xl w-full max-h-[80vh] overflow-y-auto">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle
                id="detail-modal-title"
                className="flex items-center gap-2"
              >
                {icon} {title} - Test Results
              </CardTitle>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowDetailModal(false)}
                aria-label="Close modal"
              >
                <X className="h-4 w-4" />
              </Button>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Overall Status */}
                <div className="flex items-center gap-2">
                  <span className="font-semibold">Overall Status:</span>
                  {getStatusIcon()}
                  <Badge
                    variant={
                      status === "completed" || status === "passed"
                        ? "default"
                        : status === "failed"
                        ? "destructive"
                        : status === "running"
                        ? "secondary"
                        : "outline"
                    }
                  >
                    {status}
                  </Badge>
                </div>

                {/* Test Summary */}
                {lastResult && (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-gray-50 rounded-lg">
                    <div>
                      <div className="text-sm font-medium text-gray-600">
                        Total Tests
                      </div>
                      <div className="text-lg font-semibold">
                        {isDef(lastResult.total_tests)
                          ? fmtNum(lastResult.total_tests)
                          : 0}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-600">
                        Passed
                      </div>
                      <div className="text-lg font-semibold text-green-600">
                        {isDef(lastResult.passed_tests)
                          ? fmtNum(lastResult.passed_tests)
                          : 0}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-600">
                        Failed
                      </div>
                      <div className="text-lg font-semibold text-red-600">
                        {isDef(lastResult.failed_tests)
                          ? fmtNum(lastResult.failed_tests)
                          : 0}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-600">
                        Success Rate
                      </div>
                      <div className="text-lg font-semibold">
                        {isDef(lastResult.success_rate)
                          ? fmtPct(lastResult.success_rate)
                          : "0%"}
                      </div>
                    </div>
                  </div>
                )}

                {/* Detailed Endpoint Results for ALL test suites */}
                {lastResult && lastResult.results && (
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">
                      Endpoint Test Results
                    </h3>

                    {/* Show individual test results */}
                    {lastResult.results &&
                      Object.entries(lastResult.results).map(
                        ([testName, result]) => (
                          <Card
                            key={testName}
                            className="border-l-4 border-l-gray-300"
                          >
                            <CardContent className="pt-4">
                              <div className="flex items-start justify-between">
                                <div className="flex-1">
                                  <div className="flex items-center gap-2 mb-2">
                                    {result.status === "passed" ? (
                                      <CheckCircle className="h-4 w-4 text-green-500" />
                                    ) : (
                                      <XCircle className="h-4 w-4 text-red-500" />
                                    )}
                                    <h4 className="font-medium">
                                      {result.business_function || testName}
                                    </h4>
                                    <Badge
                                      variant={
                                        result.status === "passed"
                                          ? "default"
                                          : "destructive"
                                      }
                                    >
                                      {result.status}
                                    </Badge>
                                  </div>

                                  {/* Test Details */}
                                  {result.details && (
                                    <div className="space-y-2 text-sm">
                                      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                                        <div>
                                          <span className="font-medium">
                                            Method:
                                          </span>{" "}
                                          {result.details.method}
                                        </div>
                                        <div>
                                          <span className="font-medium">
                                            Status Code:
                                          </span>
                                          <span
                                            className={`ml-1 ${
                                              result.details.status_code >=
                                                200 &&
                                              result.details.status_code < 300
                                                ? "text-green-600"
                                                : result.details.status_code >=
                                                  400
                                                ? "text-red-600"
                                                : "text-yellow-600"
                                            }`}
                                          >
                                            {result.details.status_code}
                                          </span>
                                        </div>
                                        <div>
                                          <span className="font-medium">
                                            Response Time:
                                          </span>{" "}
                                          {fmtMs(
                                            result.details.response_time_ms
                                          )}
                                        </div>
                                        <div>
                                          <span className="font-medium">
                                            Endpoint:
                                          </span>{" "}
                                          {result.details.endpoint}
                                        </div>
                                      </div>

                                      <div>
                                        <span className="font-medium">
                                          Full URL:
                                        </span>
                                        <code className="ml-1 text-xs bg-gray-100 px-1 py-0.5 rounded">
                                          {result.details.url}
                                        </code>
                                      </div>

                                      {/* Show success reasons for passed tests */}
                                      {result.status === "passed" &&
                                        result.success_reason && (
                                          <Alert className="mt-2 border-green-200 bg-green-50">
                                            <CheckCircle className="h-4 w-4 text-green-600" />
                                            <AlertDescription className="text-green-800">
                                              <strong>Success:</strong>{" "}
                                              {result.success_reason}
                                            </AlertDescription>
                                          </Alert>
                                        )}

                                      {/* Show detailed error information for failed tests */}
                                      {result.status === "failed" &&
                                        (result.error ||
                                          result.server_response) && (
                                          <div className="mt-2 space-y-2">
                                            <Alert className="border-red-200 bg-red-50">
                                              <AlertTriangle className="h-4 w-4 text-red-600" />
                                              <AlertDescription className="text-red-800">
                                                <div className="space-y-2">
                                                  <div>
                                                    <strong>Problem:</strong>{" "}
                                                    {result.server_response ||
                                                      result.error}
                                                  </div>

                                                  {result.fix_suggestion && (
                                                    <div className="text-sm">
                                                      <strong>
                                                        💡 How to Fix:
                                                      </strong>{" "}
                                                      {result.fix_suggestion}
                                                    </div>
                                                  )}

                                                  {(result.problem_type ||
                                                    result.error_type) && (
                                                    <div className="text-xs">
                                                      <strong>
                                                        Issue Type:
                                                      </strong>{" "}
                                                      <code className="bg-red-100 px-1 py-0.5 rounded">
                                                        {result.problem_type ||
                                                          result.error_type}
                                                      </code>
                                                    </div>
                                                  )}

                                                  {(result.endpoint_url ||
                                                    result.details
                                                      ?.endpoint) && (
                                                    <div className="text-xs">
                                                      <strong>Endpoint:</strong>{" "}
                                                      <code className="bg-gray-100 px-1 py-0.5 rounded">
                                                        {result.method ||
                                                          result.details
                                                            ?.method}{" "}
                                                        {result.endpoint_url ||
                                                          result.details
                                                            ?.endpoint}
                                                      </code>
                                                    </div>
                                                  )}
                                                </div>
                                              </AlertDescription>
                                            </Alert>
                                          </div>
                                        )}

                                      {/* Show error details for endpoint_accessible:false tests */}
                                      {result.endpoint_accessible === false &&
                                        !result.status && (
                                          <div className="mt-2">
                                            <Alert className="border-red-200 bg-red-50">
                                              <AlertTriangle className="h-4 w-4 text-red-600" />
                                              <AlertDescription className="text-red-800 text-xs">
                                                <div className="space-y-1">
                                                  <div>
                                                    <strong>Issue:</strong>{" "}
                                                    {result.server_response ||
                                                      result.error ||
                                                      "Endpoint not accessible"}
                                                  </div>
                                                  {result.error_type && (
                                                    <div>
                                                      <strong>Type:</strong>{" "}
                                                      {result.error_type.replace(
                                                        /_/g,
                                                        " "
                                                      )}
                                                    </div>
                                                  )}
                                                  {result.endpoint_url && (
                                                    <div>
                                                      <strong>URL:</strong>{" "}
                                                      {result.method}{" "}
                                                      {result.endpoint_url}
                                                    </div>
                                                  )}
                                                </div>
                                              </AlertDescription>
                                            </Alert>
                                          </div>
                                        )}
                                    </div>
                                  )}
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        )
                      )}
                  </div>
                )}

                {/* General Error Display */}
                {error && (
                  <Alert>
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>
                      <strong>Test Execution Error:</strong> {error}
                    </AlertDescription>
                  </Alert>
                )}

                {/* Raw Result Data (for debugging) */}
                {lastResult && (
                  <details className="mt-4">
                    <summary className="cursor-pointer text-sm font-medium text-gray-600">
                      Raw Test Data (Debug)
                    </summary>
                    <pre className="mt-2 text-xs bg-gray-100 p-3 rounded overflow-x-auto">
                      {JSON.stringify(lastResult, null, 2)}
                    </pre>
                  </details>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </>
  );
};

ServiceStatusCard.propTypes = {
  /** Service title */
  title: PropTypes.string.isRequired,
  /** Service description */
  description: PropTypes.string.isRequired,
  /** API endpoint for testing */
  endpoint: PropTypes.string.isRequired,
  /** Type of test to execute */
  testType: PropTypes.string.isRequired,
  /** Icon emoji to display */
  icon: PropTypes.string.isRequired,
  /** Service priority level */
  priority: PropTypes.oneOf(["critical", "high", "medium", "low"]),
};

ServiceStatusCard.defaultProps = {
  priority: "medium",
};

export default ServiceStatusCard;
