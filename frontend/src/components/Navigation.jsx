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
        console.log('🕉️ Profile loading blessed with patience:', profileError);
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
    { to: '/follow-up-center', label: t('followUps'), icon: '📧' },
  ];

  const adminLinks = [
    { to: '/admin', label: t('adminDashboard'), icon: '👑' },
    { to: '/admin/overview', label: t('overview'), icon: '📊' },
    { to: '/admin/users', label: t('users'), icon: '👥' },
    { to: '/admin/analytics', label: t('analytics'), icon: '📈' },
    { to: '/admin/social-marketing', label: t('socialMedia', 'Social Media'), icon: '📱' },
    { to: '/admin/pricing', label: t('pricing'), icon: '💰' },
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

  return (
    <nav className="w-full bg-black text-white shadow-md sticky top-0 z-50 flex items-center px-4 py-2">
      {/* Logo */}
      <div className="flex items-center mr-4">
        <img src="/favicon.ico" alt="JyotiFlow Logo" className="h-8 w-8 mr-2" />
        <span className="font-bold text-xl">JyotiFlow.ai</span>
      </div>
      {/* Nav Items */}
      <div className="flex-1 flex items-center space-x-2">
        {navLinks.map(link => (
          <Link
            key={link.to}
            to={link.to}
            className={`px-4 py-2 rounded-full font-semibold transition-all ${location.pathname === link.to ? 'bg-yellow-500 text-black' : 'hover:bg-gray-800'}`}
          >
            {link.icon} {link.label}
          </Link>
        ))}
        {isAuthenticated && (
          <Link to="/profile" className={`px-4 py-2 rounded-full font-semibold transition-all ${location.pathname === '/profile' ? 'bg-yellow-500 text-black' : 'hover:bg-gray-800'}`}>
            👤 {t('profile')}
          </Link>
        )}
        {isAuthenticated && userProfile?.role === 'admin' && (
          <Link to="/admin" className={`px-4 py-2 rounded-full font-semibold transition-all ${location.pathname === '/admin' ? 'bg-yellow-500 text-black' : 'hover:bg-gray-800'}`}>
            👑 {t('adminDashboard')}
          </Link>
        )}
        {/* User dropdown or Sign In */}
        {isAuthenticated ? (
          <div className="relative group">
            <button className="px-4 py-2 rounded-full font-semibold hover:bg-gray-800 transition-all flex items-center">
              <span className="mr-2">{userProfile?.name || t('user', 'User')}</span>
              <ChevronDown size={16} />
            </button>
            <div className="absolute right-0 mt-2 w-48 bg-white text-black rounded shadow-lg opacity-0 group-hover:opacity-100 group-focus:opacity-100 transition-opacity z-50">
              <Link to="/profile" className="block px-4 py-2 hover:bg-gray-100">👤 {t('profile')}</Link>
              <Link to="/follow-up-center" className="block px-4 py-2 hover:bg-gray-100">📧 {t('followUps')}</Link>
              {userProfile?.role === 'admin' && (
                <>
                  <div className="border-t border-gray-200 my-1"></div>
                  <div className="px-4 py-1 text-xs font-semibold text-gray-500 uppercase">{t('admin', 'Admin')}</div>
                  <Link to="/admin" className="block px-4 py-2 hover:bg-gray-100">👑 {t('adminDashboard', 'Dashboard')}</Link>
                  <Link to="/admin/users" className="block px-4 py-2 hover:bg-gray-100">👥 {t('users')}</Link>
                  <Link to="/admin/analytics" className="block px-4 py-2 hover:bg-gray-100">📈 {t('analytics')}</Link>
                  <Link to="/admin/social-marketing" className="block px-4 py-2 hover:bg-gray-100">📱 {t('socialMedia', 'Social Media')}</Link>
                  <Link to="/admin/pricing" className="block px-4 py-2 hover:bg-gray-100">💰 {t('pricing')}</Link>
                </>
              )}
              <div className="border-t border-gray-200 my-1"></div>
              <button onClick={handleLogout} className="block w-full text-left px-4 py-2 hover:bg-gray-100 text-red-600">🚪 {t('logout')}</button>
            </div>
          </div>
        ) : (
          <Link to="/login" className="px-4 py-2 rounded-full font-semibold hover:bg-gray-800 transition-all">
            {t('signIn')}
          </Link>
        )}
        <Link to="/register" className="ml-2 px-6 py-2 rounded-full font-bold bg-gradient-to-r from-orange-400 to-red-500 text-white hover:from-orange-500 hover:to-red-600 transition-all">
          {t('joinSacredJourney', 'Join Sacred Journey')}
        </Link>
      </div>
      {/* Language Selector - Replace the old select with LanguageSelector component */}
      <div style={{ marginLeft: 'auto', marginRight: 16 }}>
        <LanguageSelector />
      </div>
    </nav>
  );
};

export default Navigation;



