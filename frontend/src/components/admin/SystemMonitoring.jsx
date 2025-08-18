import React, { useState, useEffect, useRef } from "react";
import {
  Activity,
  AlertCircle,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  TrendingUp,
  TrendingDown,
  RefreshCw,
  Wifi,
  WifiOff,
  Database,
  Brain,
  Mic,
  Video,
  Share2,
  Search,
  BarChart3,
  Info,
  ChevronRight,
  ChevronDown,
} from "lucide-react";
import spiritualAPI from "../../lib/api";

const SystemMonitoring = () => {
  const API_BASE_URL =
    import.meta.env.VITE_API_URL || "https://jyotiflow-ai.onrender.com";
  const [monitoringData, setMonitoringData] = useState(null);
  const [selectedSession, setSelectedSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [wsConnected, setWsConnected] = useState(false);
  const [expandedSections, setExpandedSections] = useState({
    integrations: true,
    recentIssues: true,
    activeSessions: false,
  });
  const wsRef = useRef(null);

  // Integration icons mapping
  const integrationIcons = {
    // Core Services
    prokerala: Database,
    rag_knowledge: Brain,
    openai_guidance: Brain,
    elevenlabs_voice: Mic,
    did_avatar: Video,
    social_media: Share2,

    // Platform Integrations
    facebook: Share2,
    instagram: Share2,
    youtube: Video,
    tiktok: Video,
    twitter: Share2,
    linkedin: Share2,

    // API Services
    openai: Brain,
    elevenlabs: Mic,
    did: Video,
    stripe: Database,
    sendgrid: Database,
    twilio: Database,

    // Service Types
    comprehensive_reading: Brain,
    birth_chart_analysis: BarChart3,
    spiritual_guidance: Search,
    avatar_consultation: Video,
    daily_wisdom: Info,
  };
  

  // Status color mapping
  const statusColors = {
    healthy: "text-green-600 bg-green-100",
    warning: "text-yellow-600 bg-yellow-100",
    degraded: "text-yellow-600 bg-yellow-100",
    error: "text-red-600 bg-red-100",
    critical: "text-red-600 bg-red-100",
    not_configured: "text-orange-600 bg-orange-100",
    partial: "text-yellow-600 bg-yellow-100",
    unused: "text-blue-600 bg-blue-100",
    disabled: "text-gray-600 bg-gray-100",
    low_usage: "text-yellow-600 bg-yellow-100",
    unknown: "text-gray-600 bg-gray-100",
  };

  // Connect to WebSocket for real-time updates
  useEffect(() => {
    connectWebSocket();
    fetchMonitoringData();

    // Refresh data every 30 seconds
    const interval = setInterval(fetchMonitoringData, 30000);

    return () => {
      clearInterval(interval);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    try {
      const backendUrl = new URL(API_BASE_URL);
      const wsProtocol = backendUrl.protocol === "https:" ? "wss:" : "ws:";
      const wsUrl = `${wsProtocol}//${backendUrl.host}/api/monitoring/ws`;
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        setWsConnected(true);
        console.log("Monitoring WebSocket connected");
      };

      wsRef.current.onmessage = (event) => {
        const update = JSON.parse(event.data);
        handleRealtimeUpdate(update);
      };

      wsRef.current.onclose = () => {
        setWsConnected(false);
        // Reconnect after 5 seconds
        setTimeout(connectWebSocket, 5000);
      };

      wsRef.current.onerror = (error) => {
        console.error("WebSocket error:", error);
        setWsConnected(false);
      };
    } catch (error) {
      console.error("Failed to connect WebSocket:", error);
    }
  };

  const fetchMonitoringData = async () => {
    try {
      console.log("🔄 Fetching monitoring data...");
      const response = await spiritualAPI.request("/api/monitoring/dashboard");
      console.log("📊 Raw monitoring response:", response);

      // Handle StandardResponse format - extract data and normalize structure
      if (response && response.success && response.data) {
        console.log("🔍 Raw system_health:", response.data.system_health);
        console.log(
          "🔍 Raw integration_points:",
          response.data.system_health?.integration_points
        );

        const normalizedData = {
          ...response.data,
          status: response.data.system_health?.system_status || "healthy",
          integrations: response.data.system_health?.integration_points || {},
          recent_issues: response.data.system_health?.recent_issues || [],
          metrics: response.data.metrics || {
            success_rates: {},
            avg_response_times: {},
          },
        };
        console.log("✅ Normalized monitoring data:", normalizedData);
        console.log(
          "🎯 Final integrations object:",
          normalizedData.integrations
        );
        console.log(
          "📊 Integration count:",
          Object.keys(normalizedData.integrations).length
        );
        setMonitoringData(normalizedData);
      } else {
        // Fallback for direct response format - check if direct format has integrations
        console.log("📋 Using direct response format");
        if (response?.integrations) {
          console.log("🎯 Direct format integrations:", response.integrations);
        }
        setMonitoringData(response);
      }
      setLoading(false);
    } catch (error) {
      console.error("❌ Failed to fetch monitoring data:", error);

      // Show error state instead of mock data
      const errorData = {
        status: "error",
        integrations: {},
        recent_issues: [
          {
            type: "api_error",
            message: "Failed to fetch monitoring data",
            timestamp: new Date().toISOString(),
          },
        ],
        active_sessions: 0,
        error: error.message,
      };
      console.log("⚠️ Using error state:", errorData);
      setMonitoringData(errorData);
      setLoading(false);
    }
  };

  const fetchSessionDetails = async (sessionId) => {
    try {
      const response = await spiritualAPI.request(
        `/api/monitoring/session/${sessionId}`
      );
      setSelectedSession(response);
    } catch (error) {
      console.error("Failed to fetch session details:", error);
    }
  };

  const handleRealtimeUpdate = (update) => {
    setMonitoringData((prev) => {
      if (!prev) return prev;

      // Update based on the type of update
      switch (update.type) {
        case "integration_status":
          return {
            ...prev,
            integrations: {
              ...prev.integrations,
              [update.integration]: update.data,
            },
          };

        case "new_issue":
          return {
            ...prev,
            recent_issues: [update.data, ...(prev.recent_issues || [])].slice(
              0,
              10
            ),
          };

        case "session_update":
          return {
            ...prev,
            active_sessions: update.data.active_sessions,
          };

        default:
          return prev;
      }
    });
  };

  const toggleSection = (section) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  const formatLatency = (ms) => {
    if (!ms) return "N/A";
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return "N/A";
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="animate-spin text-purple-600" size={32} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with System Status */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <Activity className="text-purple-600" size={28} />
            <h2 className="text-2xl font-bold text-gray-800">
              System Monitoring
            </h2>
            <div
              className={`flex items-center space-x-1 px-3 py-1 rounded-full ${
                wsConnected ? "bg-green-100" : "bg-red-100"
              }`}
            >
              {wsConnected ? (
                <>
                  <Wifi className="text-green-600" size={16} />
                  <span className="text-sm text-green-600">Live</span>
                </>
              ) : (
                <>
                  <WifiOff className="text-red-600" size={16} />
                  <span className="text-sm text-red-600">Offline</span>
                </>
              )}
            </div>
          </div>
          <button
            onClick={fetchMonitoringData}
            className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            <RefreshCw size={16} />
            <span>Refresh</span>
          </button>
        </div>

        {/* Overall System Status */}
        <div
          className={`flex items-center justify-center p-4 rounded-lg ${
            monitoringData?.status === "healthy"
              ? "bg-green-50"
              : monitoringData?.status === "degraded"
              ? "bg-yellow-50"
              : "bg-red-50"
          }`}
        >
          {monitoringData?.status === "healthy" ? (
            <CheckCircle className="text-green-600 mr-2" size={24} />
          ) : monitoringData?.status === "degraded" ? (
            <AlertCircle className="text-yellow-600 mr-2" size={24} />
          ) : (
            <XCircle className="text-red-600 mr-2" size={24} />
          )}
          <span
            className={`text-lg font-semibold ${
              monitoringData?.status === "healthy"
                ? "text-green-700"
                : monitoringData?.status === "degraded"
                ? "text-yellow-700"
                : "text-red-700"
            }`}
          >
            System Status:{" "}
            {String(monitoringData?.status || "unknown").toUpperCase()}
          </span>
        </div>
      </div>

      {/* Integration Health Grid */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div
          className="flex items-center justify-between cursor-pointer"
          onClick={() => toggleSection("integrations")}
        >
          <h3 className="text-lg font-semibold text-gray-800 flex items-center">
            {expandedSections.integrations ? (
              <ChevronDown size={20} />
            ) : (
              <ChevronRight size={20} />
            )}
            <span className="ml-2">Integration Health</span>
          </h3>
        </div>

        {expandedSections.integrations && (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-4">
            {(() => {
              console.log("🔧 Rendering integrations section");
              console.log(
                "🔧 monitoringData?.integrations:",
                monitoringData?.integrations
              );
              const entries = Object.entries(
                monitoringData?.integrations || {}
              );
              console.log("🔧 Integration entries:", entries);
              return entries;
            })().map(([key, data]) => {
              console.log(`🔧 Processing integration: ${key}`, data);

              // Safety check for data structure
              if (!data || typeof data !== "object") {
                console.warn(`❌ Invalid integration data for ${key}:`, data);
                return null;
              }

              const Icon = integrationIcons[key] || Activity;
              const statusClass =
                statusColors[data.status] || statusColors.unknown;

              return (
                <div
                  key={key}
                  className="border rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <Icon className="text-purple-600" size={20} />
                      <span className="font-medium capitalize">
                        {key.replace("_", " ")}
                      </span>
                    </div>
                    <span
                      className={`px-2 py-1 rounded-full text-xs ${statusClass}`}
                    >
                      {data.status || "unknown"}
                    </span>
                  </div>

                  {/* Integration-specific details */}
                  <div className="text-sm text-gray-600 space-y-1">
                    {/* Integration Type */}
                    {data.type && (
                      <div className="flex items-center justify-between">
                        <span>Type:</span>
                        <span className="font-medium capitalize">
                          {data.type}
                        </span>
                      </div>
                    )}

                    {/* Configuration Status for Platform Integrations */}
                    {data.type === "platform" && (
                      <div className="flex items-center justify-between">
                        <span>Configured:</span>
                        <span
                          className={`font-medium ${
                            data.configured ? "text-green-600" : "text-red-600"
                          }`}
                        >
                          {data.configured ? "✓" : "✗"}
                        </span>
                      </div>
                    )}

                    {/* Usage Count for Service Integrations */}
                    {data.type === "service" &&
                      data.usage_count !== undefined && (
                        <div className="flex items-center justify-between">
                          <span>Usage (30d):</span>
                          <span className="font-mono">{data.usage_count}</span>
                        </div>
                      )}

                    {/* Success Rate */}
                    {data.success_rate !== undefined &&
                      data.success_rate > 0 && (
                        <div className="flex items-center justify-between">
                          <span>Success Rate:</span>
                          <span
                            className={`font-mono ${
                              data.success_rate >= 90
                                ? "text-green-600"
                                : data.success_rate >= 70
                                ? "text-yellow-600"
                                : "text-red-600"
                            }`}
                          >
                            {data.success_rate}%
                          </span>
                        </div>
                      )}

                    {/* Response Time */}
                    {data.latency_ms && data.latency_ms > 0 && (
                      <div className="flex items-center justify-between">
                        <span>Latency:</span>
                        <span className="font-mono">
                          {formatLatency(data.latency_ms)}
                        </span>
                      </div>
                    )}

                    {/* Total Validations */}
                    {data.total_validations !== undefined &&
                      data.total_validations > 0 && (
                        <div className="flex items-center justify-between">
                          <span>Validations (24h):</span>
                          <span className="font-mono">
                            {data.total_validations}
                          </span>
                        </div>
                      )}

                    {/* Last Used/Updated */}
                    {(data.last_used || data.last_check) && (
                      <div className="flex items-center justify-between">
                        <span>Last Used:</span>
                        <span className="font-mono text-xs">
                          {formatTimestamp(data.last_used || data.last_check)}
                        </span>
                      </div>
                    )}

                    {/* Status-specific information */}
                    {data.status === "not_configured" && (
                      <div className="mt-2 p-2 bg-yellow-50 rounded text-xs text-yellow-700">
                        ⚠️ Integration not configured. Check platform settings.
                      </div>
                    )}

                    {data.status === "unused" && (
                      <div className="mt-2 p-2 bg-blue-50 rounded text-xs text-blue-700">
                        ℹ️ Service enabled but not used recently.
                      </div>
                    )}

                    {data.status === "disabled" && (
                      <div className="mt-2 p-2 bg-gray-50 rounded text-xs text-gray-700">
                        🔒 Service is disabled.
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Recent Issues */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div
          className="flex items-center justify-between cursor-pointer"
          onClick={() => toggleSection("recentIssues")}
        >
          <h3 className="text-lg font-semibold text-gray-800 flex items-center">
            {expandedSections.recentIssues ? (
              <ChevronDown size={20} />
            ) : (
              <ChevronRight size={20} />
            )}
            <span className="ml-2">Recent Issues</span>
            {monitoringData?.recent_issues?.length > 0 && (
              <span className="ml-2 px-2 py-1 bg-red-100 text-red-600 text-xs rounded-full">
                {monitoringData.recent_issues.length}
              </span>
            )}
          </h3>
        </div>

        {expandedSections.recentIssues && (
          <div className="mt-4 space-y-3">
            {monitoringData?.recent_issues?.length > 0 ? (
              monitoringData.recent_issues.map((issue, index) => (
                <div
                  key={index}
                  className="border-l-4 border-red-400 pl-4 py-2"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <AlertCircle className="text-red-500" size={16} />
                        <span className="font-medium text-gray-800">
                          {issue.type}
                        </span>
                        <span className="text-xs text-gray-500">
                          {formatTimestamp(issue.timestamp)}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">
                        {issue.message}
                      </p>
                      {issue.session_id && (
                        <button
                          onClick={() => fetchSessionDetails(issue.session_id)}
                          className="text-xs text-purple-600 hover:underline mt-1"
                        >
                          View Session Details →
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                <CheckCircle className="mx-auto mb-2" size={32} />
                <p>No recent issues detected</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Success Rate */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            Success Rate (24h)
          </h3>
          <div className="space-y-3">
            {Object.entries(monitoringData?.metrics?.success_rates || {}).map(
              ([integration, rate]) => (
                <div
                  key={integration}
                  className="flex items-center justify-between"
                >
                  <span className="capitalize">
                    {integration.replace("_", " ")}
                  </span>
                  <div className="flex items-center space-x-2">
                    <div className="w-32 bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          rate >= 95
                            ? "bg-green-500"
                            : rate >= 80
                            ? "bg-yellow-500"
                            : "bg-red-500"
                        }`}
                        style={{ width: `${rate}%` }}
                      />
                    </div>
                    <span className="text-sm font-mono w-12 text-right">
                      {rate}%
                    </span>
                  </div>
                </div>
              )
            )}
          </div>
        </div>

        {/* Average Response Times */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            Avg Response Time
          </h3>
          <div className="space-y-3">
            {Object.entries(
              monitoringData?.metrics?.avg_response_times || {}
            ).map(([integration, time]) => (
              <div
                key={integration}
                className="flex items-center justify-between"
              >
                <span className="capitalize">
                  {integration.replace("_", " ")}
                </span>
                <span
                  className={`font-mono ${
                    time > 5000
                      ? "text-red-600"
                      : time > 2000
                      ? "text-yellow-600"
                      : "text-green-600"
                  }`}
                >
                  {formatLatency(time)}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Session Details Modal */}
      {selectedSession && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-semibold">
                  Session Details: {selectedSession.session_id}
                </h3>
                <button
                  onClick={() => setSelectedSession(null)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <XCircle size={24} />
                </button>
              </div>

              {/* Session timeline and details */}
              <div className="space-y-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-semibold mb-2">Session Info</h4>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>User ID: {selectedSession.user_id}</div>
                    <div>
                      Started: {formatTimestamp(selectedSession.started_at)}
                    </div>
                    <div>
                      Status:{" "}
                      <span className={statusColors[selectedSession.status]}>
                        {selectedSession.status}
                      </span>
                    </div>
                    <div>
                      Duration: {formatLatency(selectedSession.duration_ms)}
                    </div>
                  </div>
                </div>

                {/* Integration flow */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-semibold mb-2">Integration Flow</h4>
                  <div className="space-y-2">
                    {selectedSession.integrations?.map((integration, index) => (
                      <div
                        key={index}
                        className="flex items-center space-x-3 text-sm"
                      >
                        <span
                          className={`w-6 h-6 rounded-full flex items-center justify-center text-white text-xs ${
                            integration.status === "success"
                              ? "bg-green-500"
                              : "bg-red-500"
                          }`}
                        >
                          {index + 1}
                        </span>
                        <span className="font-medium">{integration.name}</span>
                        <span className="text-gray-500">
                          {formatLatency(integration.duration_ms)}
                        </span>
                        {integration.error && (
                          <span className="text-red-600 text-xs">
                            {integration.error}
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Validation results */}
                {selectedSession.validations && (
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="font-semibold mb-2">Validation Results</h4>
                    <div className="space-y-2 text-sm">
                      {selectedSession.validations.rag_relevance && (
                        <div>
                          RAG Relevance:{" "}
                          <span
                            className={
                              selectedSession.validations.rag_relevance >= 65
                                ? "text-green-600"
                                : "text-red-600"
                            }
                          >
                            {selectedSession.validations.rag_relevance}%
                          </span>
                        </div>
                      )}
                      {selectedSession.validations.context_preserved !==
                        undefined && (
                        <div>
                          Context Preserved:{" "}
                          <span
                            className={
                              selectedSession.validations.context_preserved
                                ? "text-green-600"
                                : "text-red-600"
                            }
                          >
                            {selectedSession.validations.context_preserved
                              ? "Yes"
                              : "No"}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SystemMonitoring;
