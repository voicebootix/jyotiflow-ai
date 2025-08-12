import React from "react";
import PropTypes from "prop-types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Play, RefreshCw, Download } from "lucide-react";

const TestExecutionPanel = ({
  onExecuteTests,
  onRefreshData,
  onDownloadReport,
  executingTests,
  isLoading,
}) => {
  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Test Execution Panel</span>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={onRefreshData}
              disabled={isLoading}
            >
              <RefreshCw
                className={`h-4 w-4 mr-1 ${isLoading ? "animate-spin" : ""}`}
              />
              Refresh
            </Button>
            <Button variant="outline" size="sm" onClick={onDownloadReport}>
              <Download className="h-4 w-4 mr-1" />
              Export
            </Button>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Button
            onClick={() => onExecuteTests("database")}
            disabled={executingTests}
            className="w-full"
            aria-label="Execute database tests from database configuration"
            aria-busy={executingTests}
            aria-disabled={executingTests}
          >
            {executingTests ? (
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Play className="h-4 w-4 mr-2" />
            )}
            Run Database Tests
          </Button>

          <Button
            onClick={() => onExecuteTests("api")}
            disabled={executingTests}
            variant="outline"
            className="w-full"
            aria-label="Execute API tests from database configuration"
            aria-busy={executingTests}
            aria-disabled={executingTests}
          >
            {executingTests ? (
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Play className="h-4 w-4 mr-2" />
            )}
            Run API Tests
          </Button>

          <Button
            onClick={() => onExecuteTests("all")}
            disabled={executingTests}
            variant="secondary"
            className="w-full"
            aria-label="Execute complete test suite including unit, integration, and end-to-end tests"
            aria-busy={executingTests}
            aria-disabled={executingTests}
          >
            {executingTests ? (
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Play className="h-4 w-4 mr-2" />
            )}
            Run All Tests
          </Button>
        </div>

        <div
          id="test-execution-status"
          className="mt-4 flex items-center justify-between"
          role="status"
          aria-live="polite"
        >
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600">Test Status:</span>
            <Badge variant={executingTests ? "default" : "secondary"}>
              {executingTests ? "Running" : "Idle"}
            </Badge>
          </div>

          <div className="text-sm text-gray-500">
            {executingTests
              ? "Please wait while tests are executing..."
              : "Ready to execute tests"}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

TestExecutionPanel.propTypes = {
  onExecuteTests: PropTypes.func.isRequired,
  onRefreshData: PropTypes.func.isRequired,
  onDownloadReport: PropTypes.func.isRequired,
  executingTests: PropTypes.bool,
  isLoading: PropTypes.bool,
};

TestExecutionPanel.defaultProps = {
  executingTests: false,
  isLoading: false,
};

export default TestExecutionPanel;
