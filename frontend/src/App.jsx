import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useEffect } from 'react';
import './App.css';

// Import main components
import HomePage from './components/HomePage';
import SpiritualGuidance from './components/SpiritualGuidance';
import LiveChat from './components/LiveChat';
import Satsang from './components/Satsang';
import Profile from './components/Profile';
import AdminDashboard from './components/AdminDashboard';
import Login from './components/Login';
import Register from './components/Register';
import Navigation from './components/Navigation';

// Import new feature components
import AvatarGeneration from './components/AvatarGeneration';
import FollowUpCenter from './components/FollowUpCenter';
import BirthChart from './components/BirthChart';
import RealTimeBirthChart from './components/RealTimeBirthChart';
import PersonalizedRemedies from './components/PersonalizedRemedies';
import AgoraVideoCall from './components/AgoraVideoCall';

// Import about components
import SwamijiStory from './components/about/SwamijiStory';
import DigitalAshram from './components/about/DigitalAshram';
import FourPillars from './components/about/FourPillars';
import TamilHeritage from './components/about/TamilHeritage';

// Import admin components
import Overview from './components/admin/Overview';
import UserManagement from './components/admin/UserManagement';
import ContentManagement from './components/admin/ContentManagement';
import CreditPackages from './components/admin/CreditPackages';
import Donations from './components/admin/Donations';
import FollowUpManagement from './components/admin/FollowUpManagement';
import Notifications from './components/admin/Notifications';
import PricingConfig from './components/admin/PricingConfig';
import Products from './components/admin/Products';
import ProductForm from './components/admin/ProductForm';
import RevenueAnalytics from './components/admin/RevenueAnalytics';
import ServiceTypes from './components/admin/ServiceTypes';
import Settings from './components/admin/Settings';
import SocialContentManagement from './components/admin/SocialContentManagement';
import SocialMediaMarketing from './components/admin/SocialMediaMarketing';
import BusinessIntelligence from './components/admin/BusinessIntelligence';

// Import API client
import spiritualAPI from './lib/api';

// Import ProtectedRoute for authentication
import ProtectedRoute from './components/ProtectedRoute';

// Import ErrorBoundary for error handling
import ErrorBoundary from './components/ui/ErrorBoundary';

function App() {
  useEffect(() => {
    // Initialize platform on app load
    initializeSpiritualPlatform();
  }, []);

  const initializeSpiritualPlatform = async () => {
    try {
      // Load platform statistics
      await spiritualAPI.loadPlatformStats();
      
      // Track app initialization
      await spiritualAPI.trackSpiritualEngagement('app_initialized', {
        timestamp: new Date().toISOString(),
        user_agent: navigator.userAgent
      });
    } catch (error) {
      console.log('🕉️ Platform initialization blessed with patience:', error);
    }
  };

  return (
    <ErrorBoundary>
      <Router>
        <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-purple-800">
          {/* Digital Particles Background */}
          <div className="digital-particles">
            <div className="particle" style={{ left: '10%', animationDelay: '0s' }}></div>
            <div className="particle" style={{ left: '30%', animationDelay: '2s' }}></div>
            <div className="particle" style={{ left: '50%', animationDelay: '4s' }}></div>
            <div className="particle" style={{ left: '70%', animationDelay: '6s' }}></div>
            <div className="particle" style={{ left: '90%', animationDelay: '8s' }}></div>
          </div>

          {/* Navigation */}
          <Navigation />    
          
          {/* Main Content */}
          <main className="relative z-10">
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<HomePage />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              
              {/* About Routes */}
              <Route path="/about/swamiji" element={<SwamijiStory />} />
              <Route path="/about/digital-ashram" element={<DigitalAshram />} />
              <Route path="/about/four-pillars" element={<FourPillars />} />
              <Route path="/about/tamil-heritage" element={<TamilHeritage />} />
              
              {/* User Routes (require authentication) */}
              <Route path="/spiritual-guidance" element={
                <ProtectedRoute>
                  <SpiritualGuidance />
                </ProtectedRoute>
              } />
              <Route path="/live-chat" element={
                <ProtectedRoute>
                  <LiveChat />
                </ProtectedRoute>
              } />
              <Route path="/satsang" element={
                <ProtectedRoute>
                  <Satsang />
                </ProtectedRoute>
              } />
              <Route path="/profile" element={
                <ProtectedRoute>
                  <Profile />
                </ProtectedRoute>
              } />
              <Route path="/avatar-generation" element={
                <ProtectedRoute>
                  <AvatarGeneration />
                </ProtectedRoute>
              } />
              <Route path="/follow-up-center" element={
                <ProtectedRoute>
                  <FollowUpCenter />
                </ProtectedRoute>
              } />
              <Route path="/birth-chart" element={
                <ProtectedRoute>
                  <BirthChart />
                </ProtectedRoute>
              } />
              <Route path="/real-time-birth-chart" element={
                <ProtectedRoute>
                  <RealTimeBirthChart />
                </ProtectedRoute>
              } />
              <Route path="/personalized-remedies" element={
                <ProtectedRoute>
                  <PersonalizedRemedies />
                </ProtectedRoute>
              } />
              <Route path="/agora-video-call" element={
                <ProtectedRoute>
                  <AgoraVideoCall />
                </ProtectedRoute>
              } />
              
              {/* Admin Routes */}
              <Route path="/admin" element={
                <ProtectedRoute requireAdmin={true}>
                  <AdminDashboard />
                </ProtectedRoute>
              } />
              <Route path="/admin/overview" element={
                <ProtectedRoute requireAdmin={true}>
                  <Overview />
                </ProtectedRoute>
              } />
              <Route path="/admin/users" element={
                <ProtectedRoute requireAdmin={true}>
                  <UserManagement />
                </ProtectedRoute>
              } />
              <Route path="/admin/content" element={
                <ProtectedRoute requireAdmin={true}>
                  <ContentManagement />
                </ProtectedRoute>
              } />
              <Route path="/admin/credits" element={
                <ProtectedRoute requireAdmin={true}>
                  <CreditPackages />
                </ProtectedRoute>
              } />
              <Route path="/admin/donations" element={
                <ProtectedRoute requireAdmin={true}>
                  <Donations />
                </ProtectedRoute>
              } />
              <Route path="/admin/followup" element={
                <ProtectedRoute requireAdmin={true}>
                  <FollowUpManagement />
                </ProtectedRoute>
              } />
              <Route path="/admin/notifications" element={
                <ProtectedRoute requireAdmin={true}>
                  <Notifications />
                </ProtectedRoute>
              } />
              <Route path="/admin/pricing" element={
                <ProtectedRoute requireAdmin={true}>
                  <PricingConfig />
                </ProtectedRoute>
              } />
              <Route path="/admin/products" element={
                <ProtectedRoute requireAdmin={true}>
                  <Products />
                </ProtectedRoute>
              } />
              <Route path="/admin/products/new" element={
                <ProtectedRoute requireAdmin={true}>
                  <ProductForm />
                </ProtectedRoute>
              } />
              <Route path="/admin/products/edit/:id" element={
                <ProtectedRoute requireAdmin={true}>
                  <ProductForm />
                </ProtectedRoute>
              } />
              <Route path="/admin/analytics" element={
                <ProtectedRoute requireAdmin={true}>
                  <RevenueAnalytics />
                </ProtectedRoute>
              } />
              <Route path="/admin/services" element={
                <ProtectedRoute requireAdmin={true}>
                  <ServiceTypes />
                </ProtectedRoute>
              } />
              <Route path="/admin/settings" element={
                <ProtectedRoute requireAdmin={true}>
                  <Settings />
                </ProtectedRoute>
              } />
              <Route path="/admin/social-content" element={
                <ProtectedRoute requireAdmin={true}>
                  <SocialContentManagement />
                </ProtectedRoute>
              } />
              <Route path="/admin/social-marketing" element={
                <ProtectedRoute requireAdmin={true}>
                  <SocialMediaMarketing />
                </ProtectedRoute>
              } />
              <Route path="/admin/business-intelligence" element={
                <ProtectedRoute requireAdmin={true}>
                  <BusinessIntelligence />
                </ProtectedRoute>
              } />
            </Routes>
          </main>
        </div>
      </Router>
    </ErrorBoundary>
  );
}

export default App;

