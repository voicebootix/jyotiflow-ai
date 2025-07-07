import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Crown, X } from 'lucide-react';
import spiritualAPI from '../lib/api';

const AdminRedirect = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [showAdminBanner, setShowAdminBanner] = useState(false);

  useEffect(() => {
    const checkAndRedirect = async () => {
      const isAuthenticated = spiritualAPI.isAuthenticated();
      
      if (isAuthenticated) {
        const storedUser = localStorage.getItem('jyotiflow_user');
        if (storedUser) {
          try {
            const user = JSON.parse(storedUser);
            if (user.role === 'admin') {
              // Show admin banner on user services pages
              const userServicePaths = [
                '/spiritual-guidance', '/birth-chart', '/remedies', 
                '/live-chat', '/satsang', '/profile', '/follow-ups'
              ];
              
              if (userServicePaths.some(path => location.pathname.startsWith(path))) {
                setShowAdminBanner(true);
              }
              
              // Only redirect from home page to admin dashboard
              if (location.pathname === '/' || location.pathname === '/home') {
                console.log('👑 Admin user detected, redirecting to admin dashboard');
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

  const goToAdminDashboard = () => {
    navigate('/admin');
  };

  const dismissBanner = () => {
    setShowAdminBanner(false);
  };

  if (!showAdminBanner) return null;

  return (
    <div className="fixed top-0 left-0 right-0 bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-4 py-2 z-50 shadow-lg">
      <div className="flex items-center justify-between max-w-7xl mx-auto">
        <div className="flex items-center space-x-2">
          <Crown size={20} />
          <span className="font-medium">Admin Testing Mode</span>
          <span className="text-purple-200 text-sm">
            You're viewing the user experience. Testing all features as admin.
          </span>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={goToAdminDashboard}
            className="bg-white/20 hover:bg-white/30 px-3 py-1 rounded-lg text-sm font-medium transition-colors"
          >
            Go to Admin Dashboard
          </button>
          <button
            onClick={dismissBanner}
            className="text-white/70 hover:text-white transition-colors"
          >
            <X size={18} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default AdminRedirect; 