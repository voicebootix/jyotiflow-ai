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
        const storedUser = localStorage.getItem('jyotiflow_user');
        if (storedUser) {
          try {
            const user = JSON.parse(storedUser);
            if (user.role === 'admin') {
              // Only redirect from home page to admin dashboard
              if (location.pathname === '/' || location.pathname === '/home') {
                console.log('👑 Admin user detected, redirecting to admin dashboard');
                navigate('/admin', { replace: true });
              }
              // REMOVED: No more annoying banner on user service pages
            }
          } catch (error) {
            console.log('Error parsing stored user:', error);
          }
        }
      }
    };

    checkAndRedirect();
  }, [location.pathname, navigate]);

  // REMOVED: All banner-related code and state
  // No more showAdminBanner, dismissBanner, goToAdminDashboard functions
  // No more annoying testing mode banner
  
  return null; // Component now does nothing except redirect from home
};

export default AdminRedirect; 