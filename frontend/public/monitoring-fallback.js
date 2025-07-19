
// WebSocket fallback for monitoring system
function createMonitoringWebSocket() {
    const maxRetries = 5;
    let retryCount = 0;
    let ws = null;
    
    function connect() {
        try {
            // Get API URL from configuration, with fallback
            // Try import.meta.env first (for Vite processed files), then window, then default
            const apiUrl = (typeof import !== 'undefined' && import.meta && import.meta.env && import.meta.env.VITE_API_URL) ||
                          window.VITE_API_URL || 
                          'https://jyotiflow-ai.onrender.com';
            
            const backendUrl = new URL(apiUrl);
            const wsProtocol = backendUrl.protocol === 'https:' ? 'wss:' : 'ws:';
            
            // Get WebSocket URL with similar fallback pattern
            const wsUrl = (typeof import !== 'undefined' && import.meta && import.meta.env && import.meta.env.VITE_WS_URL) ||
                         (typeof window !== 'undefined' && window.MONITORING_WS_URL) ||
                         (typeof process !== 'undefined' && process.env.MONITORING_WS_URL) ||
                         `${wsProtocol}//${backendUrl.host}/api/monitoring/ws`;
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = function() {
                console.log('🔌 Monitoring WebSocket connected');
                retryCount = 0;
            };
            
            ws.onmessage = function(event) {
                try {
                    const data = JSON.parse(event.data);
                    // Handle monitoring data
                    updateMonitoringDashboard(data);
                } catch (e) {
                    console.warn('📡 Invalid monitoring data:', e);
                }
            };
            
            ws.onerror = function(error) {
                console.warn('📡 Monitoring WebSocket error (graceful fallback active)');
                // Don't log excessive errors - use HTTP polling as fallback
                startHttpPollingFallback();
            };
            
            ws.onclose = function() {
                if (retryCount < maxRetries) {
                    retryCount++;
                    setTimeout(connect, Math.min(1000 * Math.pow(2, retryCount), 30000));
                } else {
                    console.log('📡 Monitoring WebSocket failed - using HTTP polling');
                    startHttpPollingFallback();
                }
            };
            
        } catch (e) {
            console.warn('📡 WebSocket not supported - using HTTP polling');
            startHttpPollingFallback();
        }
    }
    
    function startHttpPollingFallback() {
        // Poll monitoring endpoint every 30 seconds as fallback
        setInterval(async () => {
            try {
                const apiUrl = (typeof import !== 'undefined' && import.meta && import.meta.env && import.meta.env.VITE_API_URL) ||
                              window.VITE_API_URL || 
                              'https://jyotiflow-ai.onrender.com';
                const response = await fetch(`${apiUrl}/api/monitoring/dashboard`);
                const data = await response.json();
                updateMonitoringDashboard(data);
            } catch (e) {
                console.warn('📡 Monitoring HTTP polling failed:', e);
            }
        }, 30000);
    }
    
    function updateMonitoringDashboard(data) {
        // Update dashboard UI with monitoring data
        // This function should be implemented by the frontend
        console.log('📊 Monitoring data:', data);
    }
    
    connect();
    return ws;
}

// Initialize monitoring with fallback
if (typeof window !== 'undefined') {
    window.monitoringWS = createMonitoringWebSocket();
}
