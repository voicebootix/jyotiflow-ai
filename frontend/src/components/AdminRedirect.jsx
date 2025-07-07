import React, { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import spiritualAPI from '../lib/api';

const AdminRedirect = () => {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const checkAndRedirect = async () => {
      const isAuthenticated = spiritualAPI.isAuthenticated();
      
      if (isAuthenticated) {
        // Check if user is admin
        const storedUser = localStorage.getItem('jyotiflow_user');
        if (storedUser) {
          try {
            const user = JSON.parse(storedUser);
            console.log('🔍 AdminRedirect - User role:', user.role);
            if (user.role === 'admin') {
              // Only redirect if not already on an admin page
              if (!location.pathname.startsWith('/admin') && location.pathname !== '/debug-admin') {
                console.log('👑 Admin user detected, redirecting to admin dashboard from:', location.pathname);
                navigate('/admin', { replace: true });
              }
            }
          } catch (error) {
            console.log('Error parsing stored user:', error);
          }
        }
      }
    };

    checkAndRedirect();
  }, [location.pathname, navigate]);

  return null; // This component doesn't render anything
};

export default AdminRedirect; 