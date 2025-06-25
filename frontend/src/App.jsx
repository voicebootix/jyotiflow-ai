import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useState, useEffect } from 'react';
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
        
        {/* Main Content */}
        <main className="relative z-10">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/spiritual-guidance" component={<SpiritualGuidance />} />
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

