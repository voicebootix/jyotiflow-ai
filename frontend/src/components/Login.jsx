import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { Eye, EyeOff, Mail, Lock, LogIn, Crown, User } from 'lucide-react';
import spiritualAPI from '../lib/api';

export default function Login() {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    setIsAdmin(searchParams.get('admin') === 'true');
  }, [searchParams]);

  useEffect(() => {
    const redirectTo = isAdmin ? '/admin' : '/profile';
    
    if (spiritualAPI.isAuthenticated()) {
      navigate(redirectTo);
    }
  }, [searchParams, isAdmin, navigate]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const result = await spiritualAPI.login(formData.email, formData.password);

      if (result.success) {
        // Check if user is admin from backend response or email
        const userIsAdmin = result.user?.role === 'admin' || 
                           result.user?.email === 'admin@jyotiflow.ai' ||
                           formData.email === 'admin@jyotiflow.ai' ||
                           isAdmin; // fallback to URL parameter
        
        // Redirect based on actual user role
        const redirectTo = userIsAdmin ? '/admin' : '/profile';
        console.log('Login successful, user:', result.user, 'redirecting to:', redirectTo);
        navigate(redirectTo);
      } else {
        // Login failed
        setError(result.message || 'Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      setError('Network error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    try {
      // Implement Google Sign-In
      console.log('Google Sign-In not implemented yet');
    } catch (error) {
      setError('Google Sign-In failed');
    }
  };

  const handleRegisterRedirect = () => {
    navigate('/register');
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <div className={`bg-gradient-to-r ${isAdmin ? 'from-red-600 to-purple-600' : 'from-blue-600 to-indigo-600'} py-16`}>
        <div className="max-w-md mx-auto text-center px-4">
          <Link to="/" className="inline-block mb-6">
            <img 
              src="/api/placeholder/120/120" 
              alt="JyotiFlow" 
              className="mx-auto h-20 w-20 rounded-full bg-white/20 backdrop-blur-sm p-4"
            />
          </Link>
          <div className="text-6xl mb-4">{isAdmin ? '👑' : '🔐'}</div>
          <h1 className="text-4xl font-bold text-white mb-2">
            {isAdmin ? 'Admin Portal' : 'Sacred Sign In'}
          </h1>
          <p className="text-blue-100 text-lg">
            {isAdmin
              ? 'Access the divine administration dashboard'
              : 'Continue your spiritual journey'}
          </p>
        </div>
      </div>

      {/* Login Form */}
      <div className="flex-1 bg-gray-50 py-12">
        <div className="max-w-md mx-auto bg-white rounded-2xl shadow-xl p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Mail className="inline w-4 h-4 mr-2" />
                Email Address
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder={isAdmin ? "admin@jyotiflow.ai" : "your@email.com"}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Lock className="inline w-4 h-4 mr-2" />
                Password
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent pr-12"
                  placeholder="Enter your password"
                  required
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeOff className="h-5 w-5 text-gray-400" /> : <Eye className="h-5 w-5 text-gray-400" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className={`w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white ${
                isAdmin
                  ? 'bg-purple-600 hover:bg-purple-700 focus:ring-purple-500'
                  : 'bg-blue-600 hover:bg-blue-700 focus:ring-blue-500'
              } focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200`}
            >
              {loading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              ) : (
                <>
                  <LogIn className="w-5 h-5 mr-2" />
                  <span>{isAdmin ? 'Access Admin Portal' : 'Sign In to Sacred Journey'}</span>
                </>
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              {!isAdmin && (
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white text-gray-500">Or continue with</span>
                </div>
              )}
            </div>

            {!isAdmin && (
              <button
                onClick={handleGoogleSignIn}
                className="mt-4 w-full flex justify-center py-3 px-4 border border-gray-300 rounded-lg shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
              >
                <img className="w-5 h-5 mr-2" src="https://www.google.com/favicon.ico" alt="Google" />
                Sign in with Google
              </button>
            )}

            <div className="mt-6 text-center">
              <Link
                to={isAdmin ? "/login" : "/login?admin=true"}
                className="text-sm text-blue-600 hover:text-blue-500 font-medium"
              >
                {isAdmin ? 'User Login' : 'Admin Login'}
              </Link>
            </div>
          </div>

          {/* Demo Credentials */}
          <div className="mt-8 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <h3 className="text-sm font-medium text-yellow-800 mb-2">Demo Credentials:</h3>
            {isAdmin && <div><strong>Admin:</strong> admin@jyotiflow.ai / admin123</div>}
            <div><strong>User:</strong> user@jyotiflow.ai / user123</div>
          </div>

          {!isAdmin && (
            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600">
                Don't have an account?{' '}
                <button
                  onClick={handleRegisterRedirect}
                  className="font-medium text-blue-600 hover:text-blue-500"
                >
                  Create your spiritual journey
                </button>
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

