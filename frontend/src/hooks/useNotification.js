import { useState } from 'react';

/**
 * Custom hook for managing notifications
 * @param {number} defaultDuration - Default duration in milliseconds before auto-dismiss (default: 5000)
 * @returns {object} - Notification state and control functions
 */
export const useNotification = (defaultDuration = 5000) => {
  const [notification, setNotification] = useState(null);

  /**
   * Show a notification with optional custom duration
   * @param {string} message - The notification message
   * @param {string} type - The notification type ('success', 'error', 'info')
   * @param {number} duration - Custom duration in milliseconds (optional)
   */
  const showNotification = (message, type = 'info', duration = defaultDuration) => {
    setNotification({ message, type });
    
    if (duration > 0) {
      setTimeout(() => {
        setNotification(null);
      }, duration);
    }
  };

  /**
   * Clear the current notification immediately
   */
  const clearNotification = () => {
    setNotification(null);
  };

  return {
    notification,
    showNotification,
    clearNotification
  };
};

export default useNotification;