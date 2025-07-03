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
  const [language, setLanguage] = useState(localStorage.getItem('jyotiflow_language') || 'en');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

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

  useEffect(() => {
    localStorage.setItem('jyotiflow_language', language);
  }, [language]);

  const checkAuthStatus = async () => {
  try {
    if (spiritualAPI.isAuthenticated && spiritualAPI.isAuthenticated()) {
      setIsAuthenticated(true);
      try {
        const profile = await spiritualAPI.getUserProfile();
        if (profile && profile.success) {
          setUserProfile(profile.data);
        }
      } catch (profileError) {
        console.log('🕉️ Profile loading blessed with patience:', profileError);
        // Still keep user authenticated even if profile fails
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
      
      // Use React Router for navigation
      navigate('/', { replace: true });
      
    } catch (error) {
      console.log('Logout blessed with patience:', error);
      localStorage.removeItem('jyotiflow_token');
      localStorage.removeItem('jyotiflow_user');
      navigate('/', { replace: true });
    }
  };

  const handleLanguageChange = (e) => {
    setLanguage(e.target.value);
    localStorage.setItem('jyotiflow_language', e.target.value);
    window.location.reload();
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
    <nav className="w-full bg-black text-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto flex items-center px-4 py-2">
        {/* Logo */}
        <div className="flex items-center mr-4">
          <img src="/favicon.ico" alt="JyotiFlow Logo" className="h-8 w-8 mr-2" />
          <span className="font-bold text-xl">JyotiFlow.ai</span>
        </div>
        {/* Desktop Nav */}
        <div className="hidden md:flex flex-1 items-center space-x-2">
          <button className="px-4 py-2 rounded-full font-semibold bg-yellow-500 text-black hover:bg-yellow-600 transition-all">
            🏠 Home
          </button>
          <button className="px-4 py-2 rounded-full font-semibold hover:bg-gray-800 transition-all">
            🕉️ Spiritual Guidance
          </button>
          <button className="px-4 py-2 rounded-full font-semibold hover:bg-gray-800 transition-all">
            🗨️ Live Chat
          </button>
          <button className="px-4 py-2 rounded-full font-semibold hover:bg-gray-800 transition-all">
            🙏 Satsang
          </button>
          <button className="px-4 py-2 rounded-full font-semibold hover:bg-gray-800 transition-all">
            About Swamiji
          </button>
          <button className="px-4 py-2 rounded-full font-semibold hover:bg-gray-800 transition-all">
            Sign In
          </button>
          <button className="ml-2 px-6 py-2 rounded-full font-bold bg-gradient-to-r from-orange-400 to-red-500 text-white hover:from-orange-500 hover:to-red-600 transition-all">
            Join Sacred Journey
          </button>
        </div>
        {/* Language Selector (Desktop) */}
        <div className="hidden md:flex ml-auto">
          <select
            value={language}
            onChange={handleLanguageChange}
            className="min-w-[110px] px-3 py-1 rounded-md bg-gray-900 text-white border border-gray-700 focus:outline-none focus:ring-2 focus:ring-yellow-400"
            style={{ appearance: 'none', fontWeight: 500 }}
          >
            <option value="en">English</option>
            <option value="ta">தமிழ்</option>
            <option value="hi">हिन्दी</option>
          </select>
        </div>
        {/* Mobile Hamburger */}
        <div className="md:hidden ml-auto flex items-center">
          <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)} className="focus:outline-none">
            <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </div>
      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-black px-4 pb-4 pt-2 space-y-2 flex flex-col">
          <button className="w-full text-left px-4 py-2 rounded-full font-semibold bg-yellow-500 text-black hover:bg-yellow-600 transition-all">
            🏠 Home
          </button>
          <button className="w-full text-left px-4 py-2 rounded-full font-semibold hover:bg-gray-800 transition-all">
            🕉️ Spiritual Guidance
          </button>
          <button className="w-full text-left px-4 py-2 rounded-full font-semibold hover:bg-gray-800 transition-all">
            🗨️ Live Chat
          </button>
          <button className="w-full text-left px-4 py-2 rounded-full font-semibold hover:bg-gray-800 transition-all">
            🙏 Satsang
          </button>
          <button className="w-full text-left px-4 py-2 rounded-full font-semibold hover:bg-gray-800 transition-all">
            About Swamiji
          </button>
          <button className="w-full text-left px-4 py-2 rounded-full font-semibold hover:bg-gray-800 transition-all">
            Sign In
          </button>
          <button className="w-full text-left mt-2 px-6 py-2 rounded-full font-bold bg-gradient-to-r from-orange-400 to-red-500 text-white hover:from-orange-500 hover:to-red-600 transition-all">
            Join Sacred Journey
          </button>
          <div className="w-full mt-2">
            <select
              value={language}
              onChange={handleLanguageChange}
              className="w-full px-3 py-2 rounded-md bg-gray-900 text-white border border-gray-700 focus:outline-none focus:ring-2 focus:ring-yellow-400"
              style={{ appearance: 'none', fontWeight: 500 }}
            >
              <option value="en">English</option>
              <option value="ta">தமிழ்</option>
              <option value="hi">हिन्दी</option>
            </select>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navigation;



