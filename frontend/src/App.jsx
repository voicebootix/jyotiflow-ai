import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useEffect } from 'react';
import './App.css';

// Import components (to be created)
import HomePage from './components/HomePage';
import SpiritualGuidance from './components/SpiritualGuidance';
import LiveChat from './components/LiveChat';
import Satsang from './components/Satsang';
import Profile from './components/Profile';
import AdminDashboard from './components/AdminDashboard';
import Login from './components/Login';
import Register from './components/Register';
import Navigation from './components/Navigation';

import SwamijiStory from './components/about/SwamijiStory';
import DigitalAshram from './components/about/DigitalAshram';
import FourPillars from './components/about/FourPillars';
import TamilHeritage from './components/about/TamilHeritage';



// Import API client
import spiritualAPI from './lib/api';

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

        // In your main navigation component, add this dropdown
        <div className="relative group">
          <button className="flex items-center space-x-1 text-gray-700 hover:text-orange-600">
            <span>About Swamiji</span>
            <ChevronDown className="h-4 w-4" />
          </button>
          
          <div className="absolute top-full left-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
            <div className="py-2">
              <Link to="/about/swamiji" className="block px-4 py-2 text-gray-700 hover:bg-orange-50 hover:text-orange-600">
                Swamiji's Story
              </Link>
              <Link to="/about/digital-ashram" className="block px-4 py-2 text-gray-700 hover:bg-orange-50 hover:text-orange-600">
                The Digital Ashram
              </Link>
              <Link to="/about/four-pillars" className="block px-4 py-2 text-gray-700 hover:bg-orange-50 hover:text-orange-600">
                Four Sacred Pillars
              </Link>
              <Link to="/about/tamil-heritage" className="block px-4 py-2 text-gray-700 hover:bg-orange-50 hover:text-orange-600">
                Tamil Heritage
              </Link>
            </div>
          </div>
        </div>    

        {/* Main Content */}
        <main className="relative z-10">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/spiritual-guidance" element={<SpiritualGuidance />} />
            <Route path="/live-chat" element={<LiveChat />} />
            <Route path="/satsang" element={<Satsang />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            <Route path="/about/swamiji" element={<SwamijiStory />} />
            <Route path="/about/digital-ashram" element={<DigitalAshram />} />
            <Route path="/about/four-pillars" element={<FourPillars />} />
            <Route path="/about/tamil-heritage" element={<TamilHeritage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;

