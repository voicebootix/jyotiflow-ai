import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import spiritualAPI from '../lib/api';

const ProtectedRoute = ({ children, requireAdmin = false }) => {
  const location = useLocation();
  
  // 🔥 ADMIN ACCESS RESTRICTIONS REMOVED 🔥
  // No authentication required - direct access to admin dashboard
  console.log('� ProtectedRoute BYPASS - Direct access granted to:', location.pathname);
  
  // Return children directly without any authentication or admin checks
  return children;
};

export default ProtectedRoute; 