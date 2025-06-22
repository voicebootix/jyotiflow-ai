import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X, User, LogOut } from 'lucide-react';
import spiritualAPI from '../lib/api';

const Navigation = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userProfile, setUserProfile] = useState(null);
  const location = useLocation();

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    if (spiritualAPI.isAuthenticated()) {
      setIsAuthenticated(true);
      try {
        const profile = await spiritualAPI.getUserProfile();
        if (profile && profile.success) {
          setUserProfile(profile.data);
        }
      } catch (error) {
        console.log('Profile loading blessed with patience:', error);
      }
    }
  };

  const handleLogout = () => {
    spiritualAPI.clearAuth();
    setIsAuthenticated(false);
    setUserProfile(null);
    window.location.href = '/';
  };

  const navItems = [
    { path: '/', label: '🏠 Home', icon: '🏠' },
    { path: '/spiritual-guidance', label: '🕉️ Spiritual Guidance', icon: '🕉️' },
    { path: '/live-chat', label: '📹 Live Chat', icon: '📹' },
    { path: '/satsang', label: '🙏 Satsang', icon: '🙏' },
    { path: '/profile', label: '👤 Profile', icon: '👤', authRequired: true }
  ];

  const isActivePath = (path) => {
    return location.pathname === path;
  };

  return (
    <nav className="sacred-nav fixed top-0 left-0 right-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <span className="om-symbol">🕉️</span>
            <span className="divine-text text-xl font-bold">JyotiFlow.ai</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-4">
              {navItems.map((item) => {
                if (item.authRequired && !isAuthenticated) return null;
                
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-all duration-300 ${
                      isActivePath(item.path)
                        ? 'bg-gradient-to-r from-yellow-400 to-orange-400 text-white shadow-lg'
                        : 'text-gray-300 hover:text-white hover:bg-gray-700'
                    }`}
                    onClick={() => spiritualAPI.trackSpiritualEngagement('navigation_click', { page: item.path })}
                  >
                    <span className="mr-1">{item.icon}</span>
                    {item.label.replace(/^[🏠🕉️📹🙏👤]\s/, '')}
                  </Link>
                );
              })}
            </div>
          </div>

          {/* Auth Section */}
          <div className="hidden md:block">
            {isAuthenticated ? (
              <div className="flex items-center space-x-4">
                {userProfile && (
                  <span className="text-gray-300 text-sm">
                    Welcome, {userProfile.name || 'Divine Soul'}
                  </span>
                )}
                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-1 text-gray-300 hover:text-white transition-colors"
                >
                  <LogOut size={16} />
                  <span>Logout</span>
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-4">
                <Link
                  to="/login"
                  className="text-gray-300 hover:text-white transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="divine-button text-sm"
                >
                  Join Sacred Journey
                </Link>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="text-gray-300 hover:text-white focus:outline-none focus:text-white"
            >
              {isOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      {isOpen && (
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-gray-900 bg-opacity-95">
            {navItems.map((item) => {
              if (item.authRequired && !isAuthenticated) return null;
              
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`block px-3 py-2 rounded-md text-base font-medium transition-all duration-300 ${
                    isActivePath(item.path)
                      ? 'bg-gradient-to-r from-yellow-400 to-orange-400 text-white'
                      : 'text-gray-300 hover:text-white hover:bg-gray-700'
                  }`}
                  onClick={() => {
                    setIsOpen(false);
                    spiritualAPI.trackSpiritualEngagement('mobile_navigation_click', { page: item.path });
                  }}
                >
                  {item.label}
                </Link>
              );
            })}
            
            {/* Mobile Auth */}
            <div className="border-t border-gray-700 pt-4">
              {isAuthenticated ? (
                <div className="space-y-2">
                  {userProfile && (
                    <div className="px-3 py-2 text-gray-300 text-sm">
                      Welcome, {userProfile.name || 'Divine Soul'}
                    </div>
                  )}
                  <button
                    onClick={handleLogout}
                    className="block w-full text-left px-3 py-2 text-gray-300 hover:text-white hover:bg-gray-700 rounded-md"
                  >
                    <LogOut size={16} className="inline mr-2" />
                    Logout
                  </button>
                </div>
              ) : (
                <div className="space-y-2">
                  <Link
                    to="/login"
                    className="block px-3 py-2 text-gray-300 hover:text-white hover:bg-gray-700 rounded-md"
                    onClick={() => setIsOpen(false)}
                  >
                    Sign In
                  </Link>
                  <Link
                    to="/register"
                    className="block px-3 py-2 divine-button text-center"
                    onClick={() => setIsOpen(false)}
                  >
                    Join Sacred Journey
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navigation;

