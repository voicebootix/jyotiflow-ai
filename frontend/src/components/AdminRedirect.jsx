import React, { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import spiritualAPI from '../lib/api';

const AdminRedirect = () => {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const checkAndRedirect = async () => {
      // Only redirect if we're on the home page or profile page
      if (location.pathname === '/' || location.pathname === '/profile') {
        const isAuthenticated = spiritualAPI.isAuthenticated();
        
        if (isAuthenticated) {
          // Check if user is admin
          const storedUser = localStorage.getItem('jyotiflow_user');
          if (storedUser) {
            try {
              const user = JSON.parse(storedUser);
              if (user.role === 'admin') {
                console.log('👑 Admin user detected, redirecting to admin dashboard');
                navigate('/admin', { replace: true });
              }
            } catch (error) {
              console.log('Error parsing stored user:', error);
            }
          }
        }
      }
    };

    checkAndRedirect();
  }, [location.pathname, navigate]);

  return null; // This component doesn't render anything
};

export default AdminRedirect; 