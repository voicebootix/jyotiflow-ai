import { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Eye, EyeOff, Loader } from 'lucide-react';
import spiritualAPI from '../lib/api';
import { useLanguage } from '../contexts/LanguageContext';

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isAdmin, setIsAdmin] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { t } = useLanguage();

  useEffect(() => {
    const searchParams = new URLSearchParams(location.search);
    setIsAdmin(searchParams.get('admin') === 'true');
  }, [location]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      console.log('🕉️ Attempting login with:', formData.email);
      const response = await spiritualAPI.login(formData.email, formData.password);
      
      if (response.success) {
        console.log('✅ Login successful:', response);
        
        // Role-based redirect logic
        const userRole = response.user?.role || 'user';
        const searchParams = new URLSearchParams(location.search);
        const redirect = searchParams.get('redirect');
        
        let redirectPath;
        if (redirect) {
          // Use specified redirect path
          redirectPath = redirect;
        } else {
          // Default redirect based on user role
          redirectPath = userRole === 'admin' ? '/admin' : '/profile';
        }
        
        console.log(`🚀 Redirecting ${userRole} to:`, redirectPath);
        navigate(redirectPath, { replace: true });
      } else {
        setError(response.message || t('loginError'));
        console.log('❌ Login failed:', response.message);
      }
    } catch (error) {
      console.error('🔴 Login error:', error);
      setError(t('networkError'));
    } finally {
      setLoading(false);
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-purple-800 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Logo/Header */}
        <div className="text-center mb-8">
          <div className="w-20 h-20 mx-auto mb-4 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center">
            <span className="text-3xl">🕉️</span>
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">
            {isAdmin ? t('adminLogin', 'Admin Login') : t('login')}
          </h1>
          <p className="text-gray-300">
            {t('welcomeBack', 'Welcome back to your spiritual journey')}
          </p>
        </div>

        {/* Login Form */}
        <div className="bg-white rounded-xl p-8 shadow-2xl">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email Field */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                {t('email')}
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all"
                placeholder={t('emailPlaceholder', 'Enter your email')}
                required
              />
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                {t('password')}
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all pr-12"
                  placeholder={t('passwordPlaceholder', 'Enter your password')}
                  required
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={togglePasswordVisibility}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-orange-500 to-red-600 text-white py-3 px-4 rounded-lg font-semibold hover:from-orange-600 hover:to-red-700 transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:transform-none flex items-center justify-center"
            >
              {loading ? (
                <>
                  <Loader className="animate-spin h-5 w-5 mr-2" />
                  {t('signingIn', 'Signing In...')}
                </>
              ) : (
                t('signIn')
              )}
            </button>
          </form>

          {/* Quick Admin Access */}
          {!isAdmin && (
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h3 className="text-sm font-semibold text-gray-700 mb-2">
                {t('quickAccess', 'Quick Access')}:
              </h3>
              <div className="space-y-2 text-sm">
                <div>
                  <strong>{t('adminAccess', 'Admin')}:</strong> admin@jyotiflow.ai / {t('anyPassword', 'any password')}
                </div>
                <div>
                  <strong>{t('userAccess', 'User')}:</strong> user@jyotiflow.ai / {t('anyPassword', 'any password')}
                </div>
              </div>
            </div>
          )}

          {/* Register Link */}
          <div className="mt-6 text-center">
            <p className="text-gray-600">
              {t('noAccount', "Don't have an account?")}{' '}
              <Link
                to="/register"
                className="text-orange-600 hover:text-orange-700 font-semibold"
              >
                {t('registerHere', 'Register here')}
              </Link>
            </p>
          </div>

          {/* Back to Home */}
          <div className="mt-4 text-center">
            <Link
              to="/"
              className="text-gray-500 hover:text-gray-700 text-sm"
            >
              ← {t('backToHome', 'Back to Home')}
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;

