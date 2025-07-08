import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import spiritualAPI from '../lib/api';

const ProtectedRoute = ({ children, requireAdmin = false }) => {
  const location = useLocation();
  const isAuthenticated = spiritualAPI.isAuthenticated && spiritualAPI.isAuthenticated();
  
  console.log('🔒 ProtectedRoute check:', { 
    isAuthenticated, 
    requireAdmin, 
    pathname: location.pathname 
  });
  
  if (!isAuthenticated) {
    // Redirect to login if not authenticated
    console.log('🔒 Redirecting to login - not authenticated');
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requireAdmin) {
    // Check if user is admin - try multiple sources
    const storedUser = JSON.parse(localStorage.getItem('jyotiflow_user') || '{}');
    console.log('🔒 Admin check - stored user:', storedUser);
    
    if (storedUser.role !== 'admin') {
      // Redirect to home if not admin
      console.log('🔒 Redirecting to home - not admin');
      return <Navigate to="/" replace />;
    }
    
    console.log('🔒 Admin access granted');
  }

  return children;
};

export default ProtectedRoute; 