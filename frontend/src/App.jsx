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
import BirthChart from './components/BirthChart';
import PersonalizedRemedies from './components/PersonalizedRemedies';
import AgoraVideoCall from './components/AgoraVideoCall';

// Import about components
import SwamijiStory from './components/about/SwamijiStory';
import DigitalAshram from './components/about/DigitalAshram';
import FourPillars from './components/about/FourPillars';
import TamilHeritage from './components/about/TamilHeritage';

// Import admin components (only needed for standalone routes)
import ProductForm from './components/admin/ProductForm';

// Import debug component
import AdminRoleTest from './components/AdminRoleTest';

// Import testing dashboard
import TestResultsDashboard from './components/TestResultsDashboard';

// Import API client
import spiritualAPI from './lib/api';

// Import ProtectedRoute for authentication
import ProtectedRoute from './components/ProtectedRoute';

// Import ErrorBoundary for error handling
import ErrorBoundary from './components/ui/ErrorBoundary';
import LanguageProvider from './contexts/LanguageContext';

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
      <LanguageProvider>
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
              
              {/* Spiritual Service Routes (Public - Browse freely, login required for actions) */}
              <Route path="/spiritual-guidance" element={<SpiritualGuidance />} />
              <Route path="/live-chat" element={<LiveChat />} />
              <Route path="/satsang" element={<Satsang />} />
              <Route path="/birth-chart" element={<BirthChart />} />
              <Route path="/personalized-remedies" element={<PersonalizedRemedies />} />
              
              {/* User-Specific Routes (require authentication) */}
              <Route path="/profile" element={
                <ProtectedRoute>
                  <Profile />
                </ProtectedRoute>
              } />
              <Route path="/agora-video-call" element={
                <ProtectedRoute>
                  <AgoraVideoCall />
                </ProtectedRoute>
              } />
              
              {/* Admin Routes - Simplified to prevent navigation conflicts */}
              <Route path="/admin" element={
                <ProtectedRoute requireAdmin={true}>
                  <AdminDashboard />
                </ProtectedRoute>
              } />
              
              {/* Keep essential standalone routes for product management */}
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
              
              {/* Testing Dashboard Route */}
              <Route path="/admin/testing" element={
                <ProtectedRoute requireAdmin={true}>
                  <TestResultsDashboard />
                </ProtectedRoute>
              } />
              
              {/* Temporary debug route */}
              <Route path="/debug-admin" element={<AdminRoleTest />} />
            </Routes>
          </main>
        </div>
      </Router>
      </LanguageProvider>
    </ErrorBoundary>
  );
}

export default App;

