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
      // FIXED: Send specific test suite name for individual test execution
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          test_type: testType,
          test_suite: testType, // FIXED: Add test_suite parameter for specific execution
          environment: "production",
          triggered_by: "individual_card",
        }),
      });

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
        {priority.toUpperCase()}
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
