import React from 'react';
import { Alert, AlertDescription } from './alert';
import { Button } from './button';
import { RefreshCw, Home, ArrowLeft } from 'lucide-react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
    
    // Log error to console for debugging
    console.error('🕉️ JyotiFlow Error Boundary caught an error:', error, errorInfo);
    
    // Track error for analytics (if available)
    if (window.spiritualAPI && window.spiritualAPI.trackSpiritualEngagement) {
      try {
        window.spiritualAPI.trackSpiritualEngagement('error_boundary_caught', {
          error: error.message,
          stack: error.stack,
          component: errorInfo.componentStack,
          timestamp: new Date().toISOString()
        });
      } catch (trackingError) {
        console.log('Error tracking failed:', trackingError);
      }
    }
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  handleGoBack = () => {
    window.history.back();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-purple-800 flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-white rounded-lg shadow-xl p-8 text-center">
            <div className="text-6xl mb-4">🕉️</div>
            <h1 className="text-2xl font-bold text-gray-900 mb-4">
              Divine Blessings Amidst Challenges
            </h1>
            <p className="text-gray-600 mb-6">
              Even the most sacred paths encounter obstacles. This is a temporary pause in your spiritual journey.
            </p>
            
            <Alert className="mb-6">
              <AlertDescription>
                <strong>Error:</strong> {this.state.error?.message || 'An unexpected error occurred'}
              </AlertDescription>
            </Alert>
            
            <div className="space-y-3">
              <Button 
                onClick={this.handleRetry}
                className="w-full bg-purple-600 hover:bg-purple-700"
              >
                <RefreshCw size={16} className="mr-2" />
                Try Again
              </Button>
              
              <Button 
                onClick={this.handleGoBack}
                variant="outline"
                className="w-full"
              >
                <ArrowLeft size={16} className="mr-2" />
                Go Back
              </Button>
              
              <Button 
                onClick={this.handleGoHome}
                variant="outline"
                className="w-full"
              >
                <Home size={16} className="mr-2" />
                Return Home
              </Button>
            </div>
            
            <div className="mt-6 text-xs text-gray-500">
              <p>If this error persists, please contact our support team.</p>
              <p className="mt-2">Error ID: {Date.now()}</p>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary; 