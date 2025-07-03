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
    <nav className="w-full bg-black text-white shadow-md sticky top-0 z-50 flex items-center px-4 py-2">
      {/* Logo */}
      <div className="flex items-center mr-4">
        <img src="/favicon.ico" alt="JyotiFlow Logo" className="h-8 w-8 mr-2" />
        <span className="font-bold text-xl">JyotiFlow.ai</span>
      </div>
      {/* Nav Items */}
      <div className="flex-1 flex items-center space-x-2">
        <Link to="/" className="px-4 py-2 rounded-full font-semibold bg-yellow-500 text-black hover:bg-yellow-600 transition-all">
          🏠 Home
        </Link>
        <Link to="/spiritual-guidance" className="px-4 py-2 rounded-full font-semibold hover:bg-gray-800 transition-all">
          🕉️ Spiritual Guidance
        </Link>
        <Link to="/live-chat" className="px-4 py-2 rounded-full font-semibold hover:bg-gray-800 transition-all">
          🗨️ Live Chat
        </Link>
        <Link to="/satsang" className="px-4 py-2 rounded-full font-semibold hover:bg-gray-800 transition-all">
          🙏 Satsang
        </Link>
        {isAuthenticated && (
          <Link to="/profile" className="px-4 py-2 rounded-full font-semibold hover:bg-gray-800 transition-all">
            👤 Profile
          </Link>
        )}
        {/* User dropdown or Sign In */}
        {isAuthenticated ? (
          <div className="relative group">
            <button className="px-4 py-2 rounded-full font-semibold hover:bg-gray-800 transition-all flex items-center">
              <span className="mr-2">{userProfile?.name || 'User'}</span>
              <ChevronDown size={16} />
            </button>
            <div className="absolute right-0 mt-2 w-40 bg-white text-black rounded shadow-lg opacity-0 group-hover:opacity-100 group-focus:opacity-100 transition-opacity z-50">
              <Link to="/profile" className="block px-4 py-2 hover:bg-gray-100">Profile</Link>
              <button onClick={handleLogout} className="block w-full text-left px-4 py-2 hover:bg-gray-100">Logout</button>
            </div>
          </div>
        ) : (
          <Link to="/login" className="px-4 py-2 rounded-full font-semibold hover:bg-gray-800 transition-all">
            Sign In
          </Link>
        )}
        <Link to="/register" className="ml-2 px-6 py-2 rounded-full font-bold bg-gradient-to-r from-orange-400 to-red-500 text-white hover:from-orange-500 hover:to-red-600 transition-all">
          Join Sacred Journey
        </Link>
      </div>
      {/* Language Selector */}
      <div style={{ marginLeft: 'auto', marginRight: 16 }}>
        <select value={language} onChange={handleLanguageChange} style={{ padding: 4, borderRadius: 4, minWidth: 90 }}>
          <option value="en">English</option>
          <option value="ta">தமிழ்</option>
          <option value="hi">हिन्दी</option>
        </select>
      </div>
    </nav>
  );
};

export default Navigation;



