import { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Menu, X, User, LogOut, ChevronDown } from 'lucide-react';
import spiritualAPI from '../lib/api';

const Navigation = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userProfile, setUserProfile] = useState(null);
  const [showAboutDropdown, setShowAboutDropdown] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    checkAuthStatus();
    
    // Listen for authentication state changes
    const handleAuthChange = (event) => {
      console.log('Auth state changed:', event.detail);
      checkAuthStatus();
    };
    
    window.addEventListener('auth-state-changed', handleAuthChange);
    
    return () => {
      window.removeEventListener('auth-state-changed', handleAuthChange);
    };
  }, []);

  const checkAuthStatus = async () => {
    try {
      if (spiritualAPI.isAuthenticated && spiritualAPI.isAuthenticated()) {
        setIsAuthenticated(true);
        if (spiritualAPI.getUserProfile) {
          const profile = await spiritualAPI.getUserProfile();
          if (profile && profile.success) {
            setUserProfile(profile.data);
          }
        }
      }
    } catch (error) {
      console.log('🕉️ Profile loading blessed with patience:', error);
    }
  };

  const handleLogout = () => {
    try {
      spiritualAPI.logout();
      setIsAuthenticated(false);
      setUserProfile(null);
      
      // Use React Router for navigation
      navigate('/', { replace: true });
      
    } catch (error) {
      console.log('Logout blessed with patience:', error);
      localStorage.removeItem('jyotiflow_token');
      localStorage.removeItem('jyotiflow_user');
      navigate('/', { replace: true });
    }
  };

  const navItems = [
    { path: '/', label: '🏠 Home', icon: '🏠' },
    { path: '/spiritual-guidance', label: '🕉️ Spiritual Guidance', icon: '🕉️' },
    { path: '/live-chat', label: '📹 Live Chat', icon: '📹' },
    { path: '/satsang', label: '🙏 Satsang', icon: '🙏' },
    { path: '/profile', label: '👤 Profile', icon: '👤', authRequired: true }
  ];

  const aboutItems = [
    { path: '/about/swamiji', label: "Swamiji's Story" },
    { path: '/about/digital-ashram', label: 'The Digital Ashram' },
    { path: '/about/four-pillars', label: 'Four Sacred Pillars' },
    { path: '/about/tamil-heritage', label: 'Tamil Heritage' }
  ];

  const isActivePath = (path) => {
    return location.pathname === path;
  };

  return (
    <nav className="sacred-nav fixed top-0 left-0 right-0 z-50 bg-gray-900/95 backdrop-blur-sm border-b border-gray-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <span className="text-2xl">🕉️</span>
            <span className="text-xl font-bold text-white">JyotiFlow.ai</span>
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
                  >
                    <span className="mr-1">{item.icon}</span>
                    {item.label}
                  </Link>
                );
              })}

              {/* About Dropdown */}
              <div className="relative">
                <button
                  onClick={() => setShowAboutDropdown(!showAboutDropdown)}
                  onMouseEnter={() => setShowAboutDropdown(true)}
                  className="flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium text-gray-300 hover:text-white hover:bg-gray-700 transition-all duration-300"
                >
                  <span>About Swamiji</span>
                  <ChevronDown className="h-4 w-4" />
                </button>
                
                {showAboutDropdown && (
                  <div 
                    className="absolute top-full left-0 mt-2 w-64 bg-gray-800 rounded-lg shadow-lg border border-gray-600 z-50"
                    onMouseLeave={() => setShowAboutDropdown(false)}
                  >
                    <div className="py-2">
                      {aboutItems.map((item) => (
                        <Link
                          key={item.path}
                          to={item.path}
                          className="block px-4 py-2 text-gray-300 hover:bg-gray-700 hover:text-white transition-colors"
                          onClick={() => setShowAboutDropdown(false)}
                        >
                          {item.label}
                        </Link>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Auth Section */}
          <div className="hidden md:block">
            {isAuthenticated ? (
              <div className="flex items-center space-x-4">
                {userProfile && (
                  <span className="text-gray-300 text-sm">
                    Welcome, {userProfile.name || userProfile.email || 'Divine Soul'}
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
                  className="bg-gradient-to-r from-orange-500 to-red-500 text-white px-4 py-2 rounded-full text-sm font-semibold hover:from-orange-600 hover:to-red-600 transition-all duration-300"
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
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-gray-900/95 backdrop-blur-sm">
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
                  onClick={() => setIsOpen(false)}
                >
                  <span className="mr-2">{item.icon}</span>
                  {item.label}
                </Link>
              );
            })}

            {/* Mobile About Section */}
            <div className="border-t border-gray-700 pt-4">
              <div className="px-3 py-2 text-gray-400 text-sm font-medium">About Swamiji</div>
              {aboutItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className="block px-6 py-2 text-gray-300 hover:text-white hover:bg-gray-700 rounded-md"
                  onClick={() => setIsOpen(false)}
                >
                  {item.label}
                </Link>
              ))}
            </div>
            
            {/* Mobile Auth */}
            <div className="border-t border-gray-700 pt-4">
              {isAuthenticated ? (
                <div className="space-y-2">
                  {userProfile && (
                    <div className="px-3 py-2 text-gray-300 text-sm">
                      Welcome, {userProfile.name || userProfile.email || 'Divine Soul'}
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
                    className="block px-3 py-2 bg-gradient-to-r from-orange-500 to-red-500 text-white text-center rounded-md font-semibold"
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



