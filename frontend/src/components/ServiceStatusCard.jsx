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

  return (
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
            <CardTitle id={`${testType}-title`} className="text-sm font-medium">
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
            {lastResult.success_rate && (
              <div className="flex justify-between">
                <span>Success Rate:</span>
                <span className="font-medium">
                  {lastResult.success_rate.toFixed(1)}%
                </span>
              </div>
            )}
            {lastResult.accessible_endpoints && (
              <div className="flex justify-between">
                <span>Endpoints:</span>
                <span className="font-medium">
                  {lastResult.accessible_endpoints}/{lastResult.total_endpoints}
                </span>
              </div>
            )}
            {lastResult.avg_response_time_ms && (
              <div className="flex justify-between">
                <span>Avg Response:</span>
                <span className="font-medium">
                  {lastResult.avg_response_time_ms.toFixed(0)}ms
                </span>
              </div>
            )}

            {/* Admin Services specific: Show individual endpoint results */}
            {testType === "admin_services" && lastResult.endpoint_results && (
              <div className="mt-2 space-y-1">
                <div className="text-xs font-medium text-gray-700 mb-1">
                  Endpoint Results:
                </div>
                {Object.entries(lastResult.endpoint_results).map(
                  ([key, result], index) => (
                    <div
                      key={index}
                      className="flex justify-between items-center"
                    >
                      <span
                        className="text-xs truncate"
                        title={result.business_function || key}
                      >
                        {result.business_function || key}:
                      </span>
                      <div className="flex items-center gap-1">
                        {result.endpoint_accessible ? (
                          <CheckCircle className="h-3 w-3 text-green-500" />
                        ) : (
                          <XCircle className="h-3 w-3 text-red-500" />
                        )}
                        <span className="text-xs">{result.status_code}</span>
                        {result.response_time_ms && (
                          <span className="text-xs text-gray-500">
                            ({result.response_time_ms}ms)
                          </span>
                        )}
                      </div>
                    </div>
                  )
                )}
              </div>
            )}

            {/* Show endpoints tested for Admin Services */}
            {testType === "admin_services" && lastResult.endpoints_tested && (
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

            {/* Show API endpoint test results */}
            {(testType === "api" || testType === "api_endpoints") &&
              lastResult.results && (
                <div className="mt-2">
                  <div className="text-xs font-medium text-gray-700 mb-1">
                    Tested 4 API endpoints:
                  </div>
                  <div className="text-xs text-gray-600 space-y-1">
                    {Object.entries(lastResult.results).map(
                      ([testName, result], i) => (
                        <div
                          key={i}
                          className="flex items-center justify-between"
                        >
                          <span className="truncate">
                            {result.http_status_code === 200
                              ? "✅"
                              : result.http_status_code === 401
                              ? "🔒"
                              : result.http_status_code
                              ? "❌"
                              : "⏳"}
                            {testName
                              .replace("test_", "")
                              .replace("_endpoint", "")
                              .replace("_", " ")}
                          </span>
                          <span className="text-gray-500 ml-2">
                            {result.http_status_code || "..."}
                          </span>
                        </div>
                      )
                    )}
                  </div>
                </div>
              )}
          </div>
        )}

        {error && (
          <Alert className="py-2" role="alert">
            <AlertTriangle className="h-3 w-3" />
            <AlertDescription className="text-xs">{error}</AlertDescription>
          </Alert>
        )}

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
      </CardContent>
    </Card>
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
