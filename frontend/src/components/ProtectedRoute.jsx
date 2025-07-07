import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import spiritualAPI from '../lib/api';

const ProtectedRoute = ({ children, requireAdmin = false }) => {
  const location = useLocation();
  const isAuthenticated = spiritualAPI.isAuthenticated && spiritualAPI.isAuthenticated();
  
  if (!isAuthenticated) {
    // Redirect to login if not authenticated
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requireAdmin) {
    // Check if user is admin
    const user = JSON.parse(localStorage.getItem('jyotiflow_user') || '{}');
    if (user.role !== 'admin') {
      // Redirect to home if not admin
      return <Navigate to="/" replace />;
    }
  }

  return children;
};

export default ProtectedRoute; 