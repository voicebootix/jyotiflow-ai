import { useState, useEffect } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Mail, Lock, Eye, EyeOff, Loader } from 'lucide-react';
import spiritualAPI from '../lib/api';


const Login = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    // Check if this is admin login
    setIsAdmin(searchParams.get('admin') === 'true');
    
    // Track login page visit
    spiritualAPI.trackSpiritualEngagement('login_visit', {
      admin_login: isAdmin,
      referrer: searchParams.get('from') || document.referrer
    });

    // Redirect if already authenticated using React Router
    if (spiritualAPI.isAuthenticated()) {
      const redirectTo = isAdmin ? '/admin' : '/profile';
      navigate(redirectTo, { replace: true });
    }
  }, [searchParams, isAdmin, navigate]);

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError(''); // Clear error when user types
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      // Track login attempt
      await spiritualAPI.trackSpiritualEngagement('login_attempt', {
        admin_login: isAdmin,
        email: formData.email
      });

      // Attempt login
      const result = await spiritualAPI.login(formData.email, formData.password);
      
      if (result && result.success) {
        // Track successful login
        await spiritualAPI.trackSpiritualEngagement('login_success', {
          admin_login: isAdmin,
          user_id: result.user?.id
        });

        // Use React Router for navigation instead of window.location
        const redirectTo = searchParams.get('redirect');
        if (redirectTo === 'admin') {
          console.log('Redirecting to /admin (redirect param)');
          navigate('/admin', { replace: true });
        } else if (isAdmin) {
          console.log('Redirecting to /admin (isAdmin)');
          navigate('/admin', { replace: true });
        } else if (result.user?.role === 'admin') {
          console.log('Redirecting to /admin (user role is admin)');
          navigate('/admin', { replace: true });
        } else if (redirectTo) {
          console.log('Redirecting to', redirectTo);
          navigate(redirectTo.startsWith('/') ? redirectTo : `/${redirectTo}`, { replace: true });
        } else {
          console.log('Redirecting to /profile (default)');
          navigate('/profile', { replace: true });
        }
      } else {
        setError(result?.message || 'Invalid email or password. Please try again.');
        
        // Track failed login
        await spiritualAPI.trackSpiritualEngagement('login_failed', {
          admin_login: isAdmin,
          error: result?.message || 'Invalid credentials'
        });
      }
    } catch (error) {
      console.error('Login encountered divine turbulence:', error);
      setError('Connection to divine servers temporarily unavailable. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="pt-16 min-h-screen">
      {/* Header */}
      <div className={`bg-gradient-to-r ${isAdmin ? 'from-red-600 to-purple-600' : 'from-blue-600 to-indigo-600'} py-16`}>
        <div className="max-w-md mx-auto px-4 text-center">
          <Link 
            to="/" 
            className="inline-flex items-center text-white hover:text-gray-200 mb-6 transition-colors"
          >
            <ArrowLeft size={20} className="mr-2" />
            Back to Home
          </Link>
          
          <div className="text-6xl mb-4">{isAdmin ? '👑' : '🔐'}</div>
          <h1 className="text-4xl font-bold text-white mb-4">
            {isAdmin ? 'Admin Portal' : 'Sacred Sign In'}
          </h1>
          <p className="text-xl text-white opacity-90">
            {isAdmin 
              ? 'Access the divine administration dashboard'
              : 'Welcome back to your spiritual journey'
            }
          </p>
        </div>
      </div>

      {/* Login Form */}
      <div className="py-16 px-4">
        <div className="max-w-md mx-auto">
          <div className="sacred-card p-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Error Message */}
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                  {error}
                </div>
              )}

              {/* Email Field */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    placeholder={isAdmin ? "admin@jyotiflow.ai" : "your@email.com"}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                    required
                  />
                </div>
              </div>

              {/* Password Field */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                  <input
                    type={showPassword ? "text" : "password"}
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    placeholder="Enter your password"
                    className="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                  </button>
                </div>
              </div>

              {/* Remember Me & Forgot Password */}
              <div className="flex items-center justify-between">
                <label className="flex items-center">
                  <input type="checkbox" className="mr-2 rounded" />
                  <span className="text-sm text-gray-600">Remember me</span>
                </label>
                <Link 
                  to="/forgot-password" 
                  className="text-sm text-yellow-600 hover:text-yellow-800 transition-colors"
                >
                  Forgot password?
                </Link>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isLoading}
                className={`w-full flex items-center justify-center space-x-2 py-3 px-4 rounded-lg font-semibold transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed ${
                  isAdmin 
                    ? 'bg-gradient-to-r from-red-600 to-purple-600 text-white hover:from-red-700 hover:to-purple-700'
                    : 'divine-button'
                }`}
              >
                {isLoading ? (
                  <>
                    <Loader className="animate-spin" size={20} />
                    <span>Authenticating...</span>
                  </>
                ) : (
                  <span>{isAdmin ? 'Access Admin Portal' : 'Sign In to Sacred Journey'}</span>
                )}
              </button>
            </form>

            {/* Divider */}
            <div className="my-8 flex items-center">
              <div className="flex-1 border-t border-gray-300"></div>
              <span className="px-4 text-gray-500 text-sm">or</span>
              <div className="flex-1 border-t border-gray-300"></div>
            </div>

            {/* Sign Up Link */}
            {!isAdmin && (
              <div className="text-center">
                <p className="text-gray-600 mb-4">
                  New to your spiritual journey?
                </p>
                <Link 
                  to="/register" 
                  className="bg-transparent border-2 border-yellow-500 text-yellow-600 hover:bg-yellow-500 hover:text-white transition-all duration-300 px-6 py-3 rounded-lg font-semibold inline-block"
                >
                  Create Sacred Account
                </Link>
              </div>
            )}

            {/* Admin/User Toggle */}
            <div className="mt-8 text-center">
              <Link 
                to={isAdmin ? "/login" : "/login?admin=true"}
                className="text-sm text-gray-500 hover:text-gray-700 transition-colors"
              >
                {isAdmin ? 'User Login' : 'Admin Login'}
              </Link>
            </div>
          </div>

          {/* Demo Credentials */}
          {process.env.NODE_ENV === 'development' && (
            <div className="mt-6 sacred-card p-4">
              <h3 className="font-semibold text-gray-800 mb-2">Demo Credentials:</h3>
              <div className="text-sm text-gray-600 space-y-1">
                <div><strong>User:</strong> demo@jyotiflow.ai / demo123</div>
                {isAdmin && <div><strong>Admin:</strong> admin@jyotiflow.ai / admin123</div>}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Features Section */}
      {!isAdmin && (
        <div className="py-16 bg-gradient-to-br from-purple-900 to-blue-900">
          <div className="max-w-4xl mx-auto px-4">
            <h2 className="text-3xl font-bold text-center text-white mb-12">
              <span className="divine-text">Why Join Our Sacred Community?</span>
            </h2>
            
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center sacred-card p-6">
                <div className="text-4xl mb-4">🎯</div>
                <h3 className="text-lg font-bold text-gray-800 mb-3">Personalized Guidance</h3>
                <p className="text-gray-600 text-sm">
                  Receive spiritual guidance tailored to your unique birth chart and life journey
                </p>
              </div>
              
              <div className="text-center sacred-card p-6">
                <div className="text-4xl mb-4">🤝</div>
                <h3 className="text-lg font-bold text-gray-800 mb-3">Sacred Community</h3>
                <p className="text-gray-600 text-sm">
                  Connect with thousands of spiritual seekers on similar journeys worldwide
                </p>
              </div>
              
              <div className="text-center sacred-card p-6">
                <div className="text-4xl mb-4">🌟</div>
                <h3 className="text-lg font-bold text-gray-800 mb-3">Advanced Features</h3>
                <p className="text-gray-600 text-sm">
                  Access AI avatar videos, live sessions, and exclusive satsang gatherings
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Login;

