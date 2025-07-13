import { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Menu, X, User, LogOut, ChevronDown } from 'lucide-react';
import spiritualAPI from '../lib/api';
import { useLanguage } from '../contexts/LanguageContext';
import LanguageSelector from './LanguageSelector';

const Navigation = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userProfile, setUserProfile] = useState(null);
  const [showAboutDropdown, setShowAboutDropdown] = useState(false);
  const [showUserDropdown, setShowUserDropdown] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { t } = useLanguage();

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

  // Close mobile menu when route changes
  useEffect(() => {
    setIsOpen(false);
    setShowAboutDropdown(false);
    setShowUserDropdown(false);
  }, [location.pathname]);

  const checkAuthStatus = async () => {
    try {
      if (spiritualAPI.isAuthenticated && spiritualAPI.isAuthenticated()) {
        setIsAuthenticated(true);
        try {
          const profile = await spiritualAPI.getUserProfile();
          console.log('🔍 User profile loaded:', profile); // Debug log
          if (profile && profile.success) {
            setUserProfile(profile.data);
            console.log('👤 User role:', profile.data?.role); // Debug log
          } else {
            // Fallback: try to get user from localStorage
            const storedUser = localStorage.getItem('jyotiflow_user');
            if (storedUser) {
              const user = JSON.parse(storedUser);
              setUserProfile(user);
              console.log('👤 Fallback user role:', user?.role); // Debug log
            }
          }
        } catch (profileError) {
          console.log('Profile loading blessed with patience:', profileError);
          // Fallback: try to get user from localStorage
          const storedUser = localStorage.getItem('jyotiflow_user');
          if (storedUser) {
            const user = JSON.parse(storedUser);
            setUserProfile(user);
            console.log('👤 Fallback user role (error case):', user?.role); // Debug log
          }
        }
      } else {
        setIsAuthenticated(false);
        setUserProfile(null);
      }
    } catch (error) {
      console.log('🕉️ Auth check blessed with patience:', error);
      setIsAuthenticated(false);
      setUserProfile(null);
    }
  };

  const handleLogout = () => {
    try {
      spiritualAPI.logout();
      setIsAuthenticated(false);
      setUserProfile(null);
      setIsOpen(false);
      setShowUserDropdown(false);
      
      // Use React Router for navigation
      navigate('/', { replace: true });
      
    } catch (error) {
      console.log('Logout blessed with patience:', error);
      localStorage.removeItem('jyotiflow_token');
      localStorage.removeItem('jyotiflow_user');
      navigate('/', { replace: true });
    }
  };

  const navLinks = [
    { to: '/', label: t('home'), icon: '🏠' },
    { to: '/spiritual-guidance', label: t('spiritualGuidance'), icon: '🕉️' },
    { to: '/live-chat', label: t('liveChat'), icon: '🗨️' },
    { to: '/satsang', label: t('satsang'), icon: '🙏' },
    { to: '/birth-chart', label: t('birthChart'), icon: '📊' },
    { to: '/personalized-remedies', label: t('remedies'), icon: '💊' },
  ];

  const aboutItems = [
    { path: '/about/swamiji', label: t('swamijiStory', "Swamiji's Story") },
    { path: '/about/digital-ashram', label: t('digitalAshram', 'The Digital Ashram') },
    { path: '/about/four-pillars', label: t('fourPillars', 'Four Sacred Pillars') },
    { path: '/about/tamil-heritage', label: t('tamilHeritage', 'Tamil Heritage') }
  ];

  const isActivePath = (path) => {
    return location.pathname === path;
  };

  const toggleMobileMenu = () => {
    setIsOpen(!isOpen);
  };

  const handleAboutDropdown = () => {
    setShowAboutDropdown(!showAboutDropdown);
  };

  const handleUserDropdown = () => {
    setShowUserDropdown(!showUserDropdown);
  };

  return (
    <nav className="w-full bg-black text-white shadow-md sticky top-0 z-50">
      <div className="flex items-center justify-between px-4 py-2">
        {/* Logo */}
        <div className="flex items-center">
          <img src="/favicon.ico" alt="JyotiFlow Logo" className="h-8 w-8 mr-2" />
          <span className="font-bold text-xl">JyotiFlow.ai</span>
        </div>

        {/* Desktop Navigation */}
        <div className="hidden lg:flex items-center space-x-2 flex-1 justify-center">
          {navLinks.map(link => (
            <Link
              key={link.to}
              to={link.to}
              className={`px-4 py-2 rounded-full font-semibold transition-all text-sm whitespace-nowrap ${
                location.pathname === link.to 
                  ? 'bg-yellow-500 text-black' 
                  : 'hover:bg-gray-800'
              }`}
            >
              {link.icon} {link.label}
            </Link>
          ))}
          
          {/* About Dropdown */}
          <div className="relative">
            <button
              onClick={handleAboutDropdown}
              className="px-4 py-2 rounded-full font-semibold transition-all text-sm hover:bg-gray-800 flex items-center"
            >
              📖 {t('about', 'About')} <ChevronDown size={16} className="ml-1" />
            </button>
            {showAboutDropdown && (
              <div className="absolute top-full left-0 mt-2 w-48 bg-white text-black rounded shadow-lg z-50">
                {aboutItems.map(item => (
                  <Link
                    key={item.path}
                    to={item.path}
                    className="block px-4 py-2 hover:bg-gray-100"
                    onClick={() => setShowAboutDropdown(false)}
                  >
                    {item.label}
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Desktop User Actions */}
        <div className="hidden lg:flex items-center space-x-2">
          {isAuthenticated && (
            <Link 
              to="/profile" 
              className={`px-4 py-2 rounded-full font-semibold transition-all text-sm ${
                location.pathname === '/profile' 
                  ? 'bg-yellow-500 text-black' 
                  : 'hover:bg-gray-800'
              }`}
            >
              👤 {t('profile')}
            </Link>
          )}
          
          {isAuthenticated && userProfile?.role === 'admin' && (
            <Link 
              to="/admin" 
              className={`px-4 py-2 rounded-full font-semibold transition-all text-sm ${
                location.pathname === '/admin' 
                  ? 'bg-yellow-500 text-black' 
                  : 'hover:bg-gray-800'
              }`}
            >
              👑 {t('adminDashboard')}
            </Link>
          )}

          {/* User Dropdown */}
          {isAuthenticated ? (
            <div className="relative">
              <button 
                onClick={handleUserDropdown}
                className="px-4 py-2 rounded-full font-semibold hover:bg-gray-800 transition-all flex items-center text-sm"
              >
                <span className="mr-2">{userProfile?.name || t('user', 'User')}</span>
                <ChevronDown size={16} />
              </button>
              {showUserDropdown && (
                <div className="absolute right-0 mt-2 w-48 bg-white text-black rounded shadow-lg z-50">
                  <Link 
                    to="/profile" 
                    className="block px-4 py-2 hover:bg-gray-100"
                    onClick={() => setShowUserDropdown(false)}
                  >
                    👤 {t('profile')}
                  </Link>
                  <Link 
                    to="/profile?tab=sessions" 
                    className="block px-4 py-2 hover:bg-gray-100"
                    onClick={() => setShowUserDropdown(false)}
                  >
                    📧 {t('followUps')}
                  </Link>
                  {userProfile?.role === 'admin' && (
                    <>
                      <div className="border-t border-gray-200 my-1"></div>
                      <div className="px-4 py-1 text-xs font-semibold text-gray-500 uppercase">{t('admin', 'Admin')}</div>
                      <Link 
                        to="/admin" 
                        className="block px-4 py-2 hover:bg-gray-100"
                        onClick={() => setShowUserDropdown(false)}
                      >
                        👑 {t('adminDashboard', 'Admin Dashboard')}
                      </Link>
                    </>
                  )}
                  <div className="border-t border-gray-200 my-1"></div>
                  <button 
                    onClick={handleLogout} 
                    className="block w-full text-left px-4 py-2 hover:bg-gray-100 text-red-600"
                  >
                    🚪 {t('logout')}
                  </button>
                </div>
              )}
            </div>
          ) : (
            <Link 
              to="/login" 
              className="px-4 py-2 rounded-full font-semibold hover:bg-gray-800 transition-all text-sm"
            >
              {t('signIn')}
            </Link>
          )}
          
          <Link 
            to="/register" 
            className="px-6 py-2 rounded-full font-bold bg-gradient-to-r from-orange-400 to-red-500 text-white hover:from-orange-500 hover:to-red-600 transition-all text-sm"
          >
            {t('joinSacredJourney', 'Join Sacred Journey')}
          </Link>

          {/* Language Selector */}
          <LanguageSelector />
        </div>

        {/* Mobile Menu Toggle */}
        <button
          className="lg:hidden p-2 rounded-md hover:bg-gray-800 transition-all"
          onClick={toggleMobileMenu}
          aria-label="Toggle mobile menu"
        >
          {isOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile Menu */}
      {isOpen && (
        <div className="lg:hidden bg-black border-t border-gray-800">
          <div className="px-4 py-2 space-y-1">
            {/* Main Navigation Links */}
            {navLinks.map(link => (
              <Link
                key={link.to}
                to={link.to}
                className={`block px-4 py-3 rounded-lg font-semibold transition-all ${
                  location.pathname === link.to 
                    ? 'bg-yellow-500 text-black' 
                    : 'hover:bg-gray-800'
                }`}
                onClick={() => setIsOpen(false)}
              >
                {link.icon} {link.label}
              </Link>
            ))}

            {/* About Section */}
            <div className="border-t border-gray-700 pt-2 mt-2">
              <div className="px-4 py-2 text-sm font-semibold text-gray-400 uppercase">
                📖 {t('about', 'About')}
              </div>
              {aboutItems.map(item => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`block px-4 py-3 rounded-lg font-semibold transition-all ${
                    location.pathname === item.path 
                      ? 'bg-yellow-500 text-black' 
                      : 'hover:bg-gray-800'
                  }`}
                  onClick={() => setIsOpen(false)}
                >
                  {item.label}
                </Link>
              ))}
            </div>

            {/* User Actions */}
            <div className="border-t border-gray-700 pt-2 mt-2">
              {isAuthenticated ? (
                <>
                  <Link
                    to="/profile"
                    className={`block px-4 py-3 rounded-lg font-semibold transition-all ${
                      location.pathname === '/profile' 
                        ? 'bg-yellow-500 text-black' 
                        : 'hover:bg-gray-800'
                    }`}
                    onClick={() => setIsOpen(false)}
                  >
                    👤 {t('profile')}
                  </Link>
                  <Link
                    to="/profile?tab=sessions"
                    className="block px-4 py-3 rounded-lg font-semibold transition-all hover:bg-gray-800"
                    onClick={() => setIsOpen(false)}
                  >
                    📧 {t('followUps')}
                  </Link>
                  {userProfile?.role === 'admin' && (
                    <>
                      <div className="px-4 py-2 text-sm font-semibold text-gray-400 uppercase">
                        👑 {t('admin', 'Admin')}
                      </div>
                      <Link
                        to="/admin"
                        className={`block px-4 py-3 rounded-lg font-semibold transition-all ${
                          location.pathname === '/admin' 
                            ? 'bg-yellow-500 text-black' 
                            : 'hover:bg-gray-800'
                        }`}
                        onClick={() => setIsOpen(false)}
                      >
                        👑 {t('adminDashboard', 'Admin Dashboard')}
                      </Link>
                    </>
                  )}
                  <button
                    onClick={handleLogout}
                    className="block w-full text-left px-4 py-3 rounded-lg font-semibold hover:bg-gray-800 text-red-400 transition-all"
                  >
                    🚪 {t('logout')}
                  </button>
                </>
              ) : (
                <>
                  <Link
                    to="/login"
                    className="block px-4 py-3 rounded-lg font-semibold transition-all hover:bg-gray-800"
                    onClick={() => setIsOpen(false)}
                  >
                    {t('signIn')}
                  </Link>
                  <Link
                    to="/register"
                    className="block px-4 py-3 rounded-lg font-bold bg-gradient-to-r from-orange-400 to-red-500 text-white hover:from-orange-500 hover:to-red-600 transition-all text-center"
                    onClick={() => setIsOpen(false)}
                  >
                    {t('joinSacredJourney', 'Join Sacred Journey')}
                  </Link>
                </>
              )}
            </div>

            {/* Language Selector */}
            <div className="border-t border-gray-700 pt-2 mt-2">
              <div className="px-4 py-2 text-sm font-semibold text-gray-400 uppercase">
                🌐 {t('language', 'Language')}
              </div>
              <div className="px-4 py-2">
                <LanguageSelector />
              </div>
            </div>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navigation;



