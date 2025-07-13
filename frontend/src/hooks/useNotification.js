import { useState, useRef, useEffect, useCallback } from 'react';

/**
 * Custom hook for managing notifications with proper timeout management
 * @param {number} defaultDuration - Default duration in milliseconds before auto-dismiss (default: 5000)
 * @returns {object} - Notification state and control functions
 */
export const useNotification = (defaultDuration = 5000) => {
  const [notification, setNotification] = useState(null);
  const timeoutRef = useRef(null);

  /**
   * Clear any existing timeout to prevent memory leaks and race conditions
   */
  const clearExistingTimeout = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  }, []);

  /**
   * Show a notification with optional custom duration
   * @param {string} message - The notification message
   * @param {string} type - The notification type ('success', 'error', 'info')
   * @param {number} duration - Custom duration in milliseconds (optional)
   */
  const showNotification = useCallback((message, type = 'info', duration = defaultDuration) => {
    // Clear any existing timeout to prevent overlapping dismissals
    clearExistingTimeout();
    
    setNotification({ message, type });
    
    if (duration > 0) {
      timeoutRef.current = setTimeout(() => {
        setNotification(null);
        timeoutRef.current = null;
      }, duration);
    }
  }, [defaultDuration, clearExistingTimeout]);

  /**
   * Clear the current notification immediately and cancel any pending timeout
   */
  const clearNotification = useCallback(() => {
    clearExistingTimeout();
    setNotification(null);
  }, [clearExistingTimeout]);

  /**
   * Cleanup timeout on unmount to prevent memory leaks
   */
  useEffect(() => {
    return () => {
      clearExistingTimeout();
    };
  }, [clearExistingTimeout]);

  return {
    notification,
    showNotification,
    clearNotification
  };
};

export default useNotification;