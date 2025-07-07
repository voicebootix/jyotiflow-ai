import React from 'react';
import { Loader2, Heart, Sparkles, Clock } from 'lucide-react';

const LoadingState = ({ 
  type = 'default', 
  message = 'Loading divine blessings...', 
  size = 'default',
  showSpinner = true 
}) => {
  const getLoadingContent = () => {
    switch (type) {
      case 'spiritual':
        return (
          <div className="text-center space-y-4">
            <div className="flex justify-center">
              <Heart className="animate-pulse text-red-500" size={size === 'large' ? 48 : 32} />
            </div>
            <p className="text-gray-600 font-medium">{message}</p>
            <div className="flex justify-center space-x-1">
              <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
          </div>
        );
        
      case 'avatar':
        return (
          <div className="text-center space-y-4">
            <div className="flex justify-center">
              <Sparkles className="animate-spin text-yellow-500" size={size === 'large' ? 48 : 32} />
            </div>
            <p className="text-gray-600 font-medium">{message}</p>
            <div className="text-sm text-gray-500">
              Creating your personalized avatar video...
            </div>
          </div>
        );
        
      case 'birth-chart':
        return (
          <div className="text-center space-y-4">
            <div className="flex justify-center">
              <div className="relative">
                <div className="w-12 h-12 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin"></div>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-xs font-bold text-purple-600">📊</span>
                </div>
              </div>
            </div>
            <p className="text-gray-600 font-medium">{message}</p>
            <div className="text-sm text-gray-500">
              Calculating your cosmic blueprint...
            </div>
          </div>
        );
        
      case 'live-chat':
        return (
          <div className="text-center space-y-4">
            <div className="flex justify-center">
              <Clock className="animate-pulse text-blue-500" size={size === 'large' ? 48 : 32} />
            </div>
            <p className="text-gray-600 font-medium">{message}</p>
            <div className="text-sm text-gray-500">
              Connecting you with divine guidance...
            </div>
          </div>
        );
        
      default:
        return (
          <div className="text-center space-y-4">
            {showSpinner && (
              <div className="flex justify-center">
                <Loader2 className="animate-spin text-purple-600" size={size === 'large' ? 48 : 32} />
              </div>
            )}
            <p className="text-gray-600 font-medium">{message}</p>
          </div>
        );
    }
  };

  const getSizeClasses = () => {
    switch (size) {
      case 'small':
        return 'p-4';
      case 'large':
        return 'p-12';
      default:
        return 'p-8';
    }
  };

  return (
    <div className={`bg-white rounded-lg shadow-lg ${getSizeClasses()}`}>
      {getLoadingContent()}
    </div>
  );
};

// Specialized loading components for common use cases
export const SpiritualLoading = ({ message, size }) => (
  <LoadingState type="spiritual" message={message} size={size} />
);

export const AvatarLoading = ({ message, size }) => (
  <LoadingState type="avatar" message={message} size={size} />
);

export const BirthChartLoading = ({ message, size }) => (
  <LoadingState type="birth-chart" message={message} size={size} />
);

export const LiveChatLoading = ({ message, size }) => (
  <LoadingState type="live-chat" message={message} size={size} />
);

export default LoadingState; 