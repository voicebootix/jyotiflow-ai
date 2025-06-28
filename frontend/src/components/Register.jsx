import { useState, useEffect } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, User, Mail, Lock, Eye, EyeOff, Loader, Check } from 'lucide-react';
import spiritualAPI from '../lib/api';

const Register = () => {
  const navigate = useNavigate(); // ADD THIS LINE
  const [searchParams] = useSearchParams();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    birthDate: '',
    birthTime: '',
    birthLocation: '',
    agreeToTerms: false,
    subscribeNewsletter: true
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [step, setStep] = useState(1);
  const [welcomeService, setWelcomeService] = useState(null);
  
  useEffect(() => {
    // Check welcome parameters
    const service = searchParams.get('service');
    const welcome = searchParams.get('welcome');
    
    if (service) setWelcomeService(service);
    
    // Track registration page visit
    spiritualAPI.trackSpiritualEngagement('register_visit', {
      service: service,
      welcome: welcome,
      referrer: document.referrer
    });

    // Redirect if already authenticated
    if (spiritualAPI.isAuthenticated()) {
      navigate('/profile', { replace: true });
    }
  }, [searchParams]);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
    setError(''); // Clear error when user types
  };

  const validateStep1 = () => {
    if (!formData.name.trim()) {
      setError('Please enter your sacred name');
      return false;
    }
    if (!formData.email.trim()) {
      setError('Please enter your email address');
      return false;
    }
    if (!/\S+@\S+\.\S+/.test(formData.email)) {
      setError('Please enter a valid email address');
      return false;
    }
    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long');
      return false;
    }
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return false;
    }
    if (!formData.agreeToTerms) {
      setError('Please agree to the Terms of Service');
      return false;
    }
    return true;
  };

  const validateStep2 = () => {
    if (!formData.birthDate) {
      setError('Birth date is required for accurate spiritual guidance');
      return false;
    }
    if (!formData.birthTime) {
      setError('Birth time helps provide more precise guidance');
      return false;
    }
    if (!formData.birthLocation.trim()) {
      setError('Birth location is needed for astrological calculations');
      return false;
    }
    return true;
  };

  const handleStep1Submit = (e) => {
    e.preventDefault();
    if (validateStep1()) {
      setStep(2);
      spiritualAPI.trackSpiritualEngagement('register_step1_complete');
    }
  };

  const handleFinalSubmit = async (e) => {
    e.preventDefault();
    if (!validateStep2()) return;

    setIsLoading(true);
    setError('');

    try {
      // Track registration attempt
      await spiritualAPI.trackSpiritualEngagement('register_attempt', {
        service: welcomeService,
        has_birth_details: true
      });

      // Attempt registration
      // Use input type='date' and type='time' for correct format
      const formattedBirthDate = formData.birthDate; // Already YYYY-MM-DD
      let formattedBirthTime = formData.birthTime;
      if (formData.birthTime && /^\d{2}:\d{2}$/.test(formData.birthTime)) {
        formattedBirthTime = formData.birthTime + ':00';
      }
      const result = await spiritualAPI.register({
        name: formData.name,
        email: formData.email,
        password: formData.password,
        birth_date: formattedBirthDate,
        birth_time: formattedBirthTime,
        birth_location: formData.birthLocation
      });
      
      if (result && result.success) {
        // Track successful registration
        await spiritualAPI.trackSpiritualEngagement('register_success', {
          user_id: result.user?.id,
          service: welcomeService
        });

        // Auto-login after successful registration
        const loginResult = await spiritualAPI.login(formData.email, formData.password);
        
        if (loginResult && loginResult.success) {
          // Redirect based on welcome service or to profile
          const redirectTo = welcomeService 
            ? `/spiritual-guidance?service=${welcomeService}&welcome=true`
            : '/profile?welcome=true';
          
          navigate(redirectTo.startsWith('/') ? redirectTo : `/${redirectTo}`);
        } else {
          // Registration successful but login failed, redirect to login
          navigate('/login?message=Registration successful! Please sign in.');
        }
      } else {
        setError(result?.message || 'Registration failed. Please try again.');
        
        // Track failed registration
        await spiritualAPI.trackSpiritualEngagement('register_failed', {
          error: result?.message || 'Registration failed'
        });
      }
    } catch (error) {
      console.error('Registration encountered divine turbulence:', error);
      setError('Connection to divine servers temporarily unavailable. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const getWelcomeMessage = () => {
    const messages = {
      'live-chat': 'Join to access live video guidance with Swami Jyotirananthan',
      'satsang': 'Create your account to register for sacred community gatherings',
      'clarity': 'Begin your spiritual journey with personalized guidance',
      'love': 'Discover divine insights about love and relationships',
      'premium': 'Unlock premium features including AI avatar videos',
      'elite': 'Access the complete spiritual transformation experience'
    };
    
    return messages[welcomeService] || 'Welcome to your divine digital guidance journey';
  };

  return (
    <div className="pt-16 min-h-screen">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-blue-600 py-16">
        <div className="max-w-md mx-auto px-4 text-center">
          <Link 
            to="/" 
            className="inline-flex items-center text-white hover:text-gray-200 mb-6 transition-colors"
          >
            <ArrowLeft size={20} className="mr-2" />
            Back to Home
          </Link>
          
          <div className="text-6xl mb-4">🌟</div>
          <h1 className="text-4xl font-bold text-white mb-4">
            Join Sacred Journey
          </h1>
          <p className="text-xl text-white opacity-90">
            {welcomeService ? getWelcomeMessage() : 'Create your account for divine digital guidance'}
          </p>
        </div>
      </div>

      {/* Progress Indicator */}
      <div className="py-8 bg-black bg-opacity-50">
        <div className="max-w-md mx-auto px-4">
          <div className="flex items-center justify-center space-x-4">
            <div className={`flex items-center justify-center w-8 h-8 rounded-full ${
              step >= 1 ? 'bg-yellow-400 text-black' : 'bg-gray-600 text-white'
            }`}>
              {step > 1 ? <Check size={16} /> : '1'}
            </div>
            <div className={`h-1 w-16 ${step >= 2 ? 'bg-yellow-400' : 'bg-gray-600'}`}></div>
            <div className={`flex items-center justify-center w-8 h-8 rounded-full ${
              step >= 2 ? 'bg-yellow-400 text-black' : 'bg-gray-600 text-white'
            }`}>
              2
            </div>
          </div>
          <div className="flex justify-between mt-2 text-sm text-white">
            <span>Account Details</span>
            <span>Birth Information</span>
          </div>
        </div>
      </div>

      {/* Registration Form */}
      <div className="py-16 px-4">
        <div className="max-w-md mx-auto">
          <div className="sacred-card p-8">
            {step === 1 ? (
              /* Step 1: Account Details */
              <form onSubmit={handleStep1Submit} className="space-y-6">
                <div className="text-center mb-6">
                  <h2 className="text-2xl font-bold text-gray-800">Create Your Sacred Account</h2>
                  <p className="text-gray-600 mt-2">Step 1 of 2: Basic Information</p>
                </div>

                {/* Error Message */}
                {error && (
                  <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                    {error}
                  </div>
                )}

                {/* Name Field */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Full Name
                  </label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                    <input
                      type="text"
                      name="name"
                      value={formData.name}
                      onChange={handleInputChange}
                      placeholder="Your sacred name"
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                      required
                    />
                  </div>
                </div>

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
                      placeholder="your@email.com"
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
                      placeholder="Create a secure password"
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

                {/* Confirm Password Field */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Confirm Password
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                    <input
                      type={showConfirmPassword ? "text" : "password"}
                      name="confirmPassword"
                      value={formData.confirmPassword}
                      onChange={handleInputChange}
                      placeholder="Confirm your password"
                      className="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                    </button>
                  </div>
                </div>

                {/* Terms Agreement */}
                <div className="space-y-3">
                  <label className="flex items-start">
                    <input 
                      type="checkbox" 
                      name="agreeToTerms"
                      checked={formData.agreeToTerms}
                      onChange={handleInputChange}
                      className="mr-3 mt-1" 
                      required 
                    />
                    <span className="text-sm text-gray-600">
                      I agree to the <Link to="/terms" className="text-yellow-600 hover:text-yellow-800">Terms of Service</Link> and <Link to="/privacy" className="text-yellow-600 hover:text-yellow-800">Privacy Policy</Link>
                    </span>
                  </label>
                  
                  <label className="flex items-start">
                    <input 
                      type="checkbox" 
                      name="subscribeNewsletter"
                      checked={formData.subscribeNewsletter}
                      onChange={handleInputChange}
                      className="mr-3 mt-1" 
                    />
                    <span className="text-sm text-gray-600">
                      Subscribe to spiritual wisdom newsletter and satsang updates
                    </span>
                  </label>
                </div>

                {/* Continue Button */}
                <button
                  type="submit"
                  className="w-full divine-button py-3"
                >
                  Continue to Birth Details
                </button>
              </form>
            ) : (
              /* Step 2: Birth Information */
              <form onSubmit={handleFinalSubmit} className="space-y-6">
                <div className="text-center mb-6">
                  <h2 className="text-2xl font-bold text-gray-800">Birth Information</h2>
                  <p className="text-gray-600 mt-2">Step 2 of 2: For Accurate Spiritual Guidance</p>
                </div>

                {/* Error Message */}
                {error && (
                  <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                    {error}
                  </div>
                )}

                {/* Birth Details */}
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Birth Date
                    </label>
                    <input
                      type="date"
                      name="birthDate"
                      value={formData.birthDate}
                      onChange={handleInputChange}
                      className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Birth Time
                    </label>
                    <input
                      type="time"
                      name="birthTime"
                      value={formData.birthTime}
                      onChange={handleInputChange}
                      className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500"
                      required
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Exact time helps provide more accurate guidance
                    </p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Birth Location
                    </label>
                    <input
                      type="text"
                      name="birthLocation"
                      value={formData.birthLocation}
                      onChange={handleInputChange}
                      placeholder="City, State/Province, Country"
                      className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500"
                      required
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Used for astrological calculations and spiritual insights
                    </p>
                  </div>
                </div>

                {/* Privacy Note */}
                <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
                  <p className="text-sm text-blue-800">
                    🔒 Your birth information is kept completely private and secure. 
                    It's only used to provide accurate spiritual guidance and astrological insights.
                  </p>
                </div>

                {/* Action Buttons */}
                <div className="flex space-x-4">
                  <button
                    type="button"
                    onClick={() => setStep(1)}
                    className="flex-1 bg-gray-300 text-gray-700 py-3 rounded-lg font-semibold hover:bg-gray-400 transition-colors"
                  >
                    Back
                  </button>
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="flex-2 divine-button py-3 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                  >
                    {isLoading ? (
                      <>
                        <Loader className="animate-spin" size={20} />
                        <span>Creating Account...</span>
                      </>
                    ) : (
                      <span>Complete Sacred Registration</span>
                    )}
                  </button>
                </div>
              </form>
            )}

            {/* Sign In Link */}
            <div className="mt-8 text-center">
              <p className="text-gray-600 mb-4">
                Already have an account?
              </p>
              <Link 
                to="/login" 
                className="text-yellow-600 hover:text-yellow-800 font-semibold transition-colors"
              >
                Sign In to Your Journey
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;

