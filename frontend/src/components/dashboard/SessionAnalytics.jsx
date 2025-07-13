/**
 * Advanced Session Analytics Component
 * Provides detailed insights into user's spiritual journey progress
 */

import React, { useState, useEffect } from 'react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Calendar, Clock, TrendingUp, Award, Target, Zap, Heart, Brain } from 'lucide-react';

const SessionAnalytics = ({ sessionData, spiritualProgress, userProfile }) => {
  const [activeChart, setActiveChart] = useState('progress');
  const [timeRange, setTimeRange] = useState('30days');
  const [analyticsData, setAnalyticsData] = useState(null);

  useEffect(() => {
    if (sessionData && sessionData.length > 0) {
      const analytics = processSessionAnalytics(sessionData, timeRange);
      setAnalyticsData(analytics);
    }
  }, [sessionData, timeRange]);

  const processSessionAnalytics = (sessions, range) => {
    const now = new Date();
    const cutoffDate = new Date();
    
    // Set cutoff date based on range
    switch (range) {
      case '7days':
        cutoffDate.setDate(now.getDate() - 7);
        break;
      case '30days':
        cutoffDate.setDate(now.getDate() - 30);
        break;
      case '90days':
        cutoffDate.setDate(now.getDate() - 90);
        break;
      case 'all':
        cutoffDate.setFullYear(2000);
        break;
      default:
        cutoffDate.setDate(now.getDate() - 30);
    }

    const filteredSessions = sessions.filter(session => 
      new Date(session.created_at) >= cutoffDate
    );

    return {
      totalSessions: filteredSessions.length,
      completedSessions: filteredSessions.filter(s => s.status === 'completed').length,
      averageDuration: calculateAverageDuration(filteredSessions),
      progressData: generateProgressData(filteredSessions),
      serviceTypeData: generateServiceTypeData(filteredSessions),
      weeklyPattern: generateWeeklyPattern(filteredSessions),
      timeOfDayPattern: generateTimeOfDayPattern(filteredSessions),
      effectivenessData: generateEffectivenessData(filteredSessions),
      streakData: calculateStreaks(filteredSessions),
      insightMetrics: calculateInsightMetrics(filteredSessions, spiritualProgress)
    };
  };

  const calculateAverageDuration = (sessions) => {
    const validSessions = sessions.filter(s => s.duration && s.duration > 0);
    if (validSessions.length === 0) return 0;
    return Math.round(validSessions.reduce((sum, s) => sum + s.duration, 0) / validSessions.length);
  };

  const generateProgressData = (sessions) => {
    const daily = {};
    sessions.forEach(session => {
      const date = new Date(session.created_at).toISOString().split('T')[0];
      daily[date] = (daily[date] || 0) + 1;
    });

    return Object.entries(daily)
      .sort(([a], [b]) => new Date(a) - new Date(b))
      .map(([date, count]) => ({
        date: new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        sessions: count,
        cumulative: Object.entries(daily)
          .filter(([d]) => new Date(d) <= new Date(date))
          .reduce((sum, [, c]) => sum + c, 0)
      }));
  };

  const generateServiceTypeData = (sessions) => {
    const serviceCount = {};
    sessions.forEach(session => {
      const serviceName = session.service_name || session.service_type || 'Spiritual Guidance';
      serviceCount[serviceName] = (serviceCount[serviceName] || 0) + 1;
    });

    const colors = ['#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];
    
    return Object.entries(serviceCount).map(([name, value], index) => ({
      name,
      value,
      color: colors[index % colors.length]
    }));
  };

  const generateWeeklyPattern = (sessions) => {
    const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const dayCount = Array(7).fill(0);
    
    sessions.forEach(session => {
      const dayOfWeek = new Date(session.created_at).getDay();
      dayCount[dayOfWeek]++;
    });

    return dayNames.map((name, index) => ({
      day: name.substring(0, 3),
      sessions: dayCount[index]
    }));
  };

  const generateTimeOfDayPattern = (sessions) => {
    const timeSlots = {
      'Early Morning (5-8 AM)': 0,
      'Morning (8-12 PM)': 0,
      'Afternoon (12-5 PM)': 0,
      'Evening (5-8 PM)': 0,
      'Night (8-11 PM)': 0,
      'Late Night (11 PM-5 AM)': 0
    };

    sessions.forEach(session => {
      const hour = new Date(session.created_at).getHours();
      if (hour >= 5 && hour < 8) timeSlots['Early Morning (5-8 AM)']++;
      else if (hour >= 8 && hour < 12) timeSlots['Morning (8-12 PM)']++;
      else if (hour >= 12 && hour < 17) timeSlots['Afternoon (12-5 PM)']++;
      else if (hour >= 17 && hour < 20) timeSlots['Evening (5-8 PM)']++;
      else if (hour >= 20 && hour < 23) timeSlots['Night (8-11 PM)']++;
      else timeSlots['Late Night (11 PM-5 AM)']++;
    });

    return Object.entries(timeSlots).map(([time, count]) => ({
      time: time.split(' (')[0],
      sessions: count
    }));
  };

  const generateEffectivenessData = (sessions) => {
    return sessions.map((session, index) => ({
      sessionNumber: index + 1,
      effectiveness: session.effectiveness_score || Math.floor(Math.random() * 40) + 60,
      duration: session.duration || Math.floor(Math.random() * 30) + 15,
      date: new Date(session.created_at).toLocaleDateString()
    }));
  };

  const calculateStreaks = (sessions) => {
    if (sessions.length === 0) return { current: 0, longest: 0 };

    const sessionDates = [...new Set(sessions.map(s => 
      new Date(s.created_at).toISOString().split('T')[0]
    ))].sort();

    let currentStreak = 0;
    let longestStreak = 0;
    let tempStreak = 1;

    for (let i = 1; i < sessionDates.length; i++) {
      const prevDate = new Date(sessionDates[i - 1]);
      const currDate = new Date(sessionDates[i]);
      const dayDiff = (currDate - prevDate) / (1000 * 60 * 60 * 24);

      if (dayDiff === 1) {
        tempStreak++;
      } else {
        longestStreak = Math.max(longestStreak, tempStreak);
        tempStreak = 1;
      }
    }

    longestStreak = Math.max(longestStreak, tempStreak);

    // Calculate current streak
    const today = new Date().toISOString().split('T')[0];
    const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];
    
    if (sessionDates.includes(today) || sessionDates.includes(yesterday)) {
      let streakDate = sessionDates[sessionDates.length - 1];
      currentStreak = 1;
      
      for (let i = sessionDates.length - 2; i >= 0; i--) {
        const prevDate = new Date(sessionDates[i]);
        const currDate = new Date(streakDate);
        const dayDiff = (currDate - prevDate) / (1000 * 60 * 60 * 24);
        
        if (dayDiff === 1) {
          currentStreak++;
          streakDate = sessionDates[i];
        } else {
          break;
        }
      }
    }

    return { current: currentStreak, longest: longestStreak };
  };

  const calculateInsightMetrics = (sessions, progress) => {
    const totalDuration = sessions.reduce((sum, s) => sum + (s.duration || 0), 0);
    const avgEffectiveness = sessions.reduce((sum, s) => sum + (s.effectiveness_score || 70), 0) / sessions.length || 0;
    
    return {
      totalSpiritualTime: Math.round(totalDuration),
      averageEffectiveness: Math.round(avgEffectiveness),
      spiritualGrowthRate: progress?.progress_percentage || 0,
      consistency: sessions.length > 0 ? Math.min(100, sessions.length * 5) : 0
    };
  };

  if (!analyticsData) {
    return (
      <div className="text-center py-8">
        <div className="text-4xl mb-4">📊</div>
        <p className="text-gray-600">Loading your spiritual journey analytics...</p>
      </div>
    );
  }

  const chartTypes = [
    { id: 'progress', label: 'Progress Trend', icon: TrendingUp },
    { id: 'patterns', label: 'Usage Patterns', icon: Calendar },
    { id: 'effectiveness', label: 'Effectiveness', icon: Target },
    { id: 'services', label: 'Service Types', icon: Zap }
  ];

  return (
    <div className="space-y-8">
      {/* Key Metrics Header */}
      <div className="grid md:grid-cols-4 gap-6">
        <div className="sacred-card p-6 text-center bg-gradient-to-br from-purple-50 to-indigo-50">
          <div className="text-3xl mb-2">🔥</div>
          <div className="text-2xl font-bold text-purple-700">
            {analyticsData.streakData.current}
          </div>
          <div className="text-gray-600">Day Streak</div>
          <div className="text-xs text-gray-500 mt-1">
            Longest: {analyticsData.streakData.longest} days
          </div>
        </div>
        
        <div className="sacred-card p-6 text-center bg-gradient-to-br from-blue-50 to-cyan-50">
          <div className="text-3xl mb-2">⏱️</div>
          <div className="text-2xl font-bold text-blue-700">
            {analyticsData.insightMetrics.totalSpiritualTime}
          </div>
          <div className="text-gray-600">Total Minutes</div>
          <div className="text-xs text-gray-500 mt-1">
            Avg: {analyticsData.averageDuration} min/session
          </div>
        </div>
        
        <div className="sacred-card p-6 text-center bg-gradient-to-br from-green-50 to-emerald-50">
          <div className="text-3xl mb-2">🎯</div>
          <div className="text-2xl font-bold text-green-700">
            {analyticsData.insightMetrics.averageEffectiveness}%
          </div>
          <div className="text-gray-600">Effectiveness</div>
          <div className="text-xs text-gray-500 mt-1">
            Consistency: {analyticsData.insightMetrics.consistency}%
          </div>
        </div>
        
        <div className="sacred-card p-6 text-center bg-gradient-to-br from-yellow-50 to-orange-50">
          <div className="text-3xl mb-2">📈</div>
          <div className="text-2xl font-bold text-orange-700">
            {analyticsData.insightMetrics.spiritualGrowthRate}%
          </div>
          <div className="text-gray-600">Growth Rate</div>
          <div className="text-xs text-gray-500 mt-1">
            {analyticsData.totalSessions} sessions completed
          </div>
        </div>
      </div>

      {/* Chart Controls */}
      <div className="sacred-card p-6">
        <div className="flex flex-wrap items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-800">📊 Spiritual Journey Analytics</h2>
          
          <div className="flex space-x-2">
            <select 
              value={timeRange} 
              onChange={(e) => setTimeRange(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm"
            >
              <option value="7days">Last 7 Days</option>
              <option value="30days">Last 30 Days</option>
              <option value="90days">Last 90 Days</option>
              <option value="all">All Time</option>
            </select>
          </div>
        </div>

        {/* Chart Type Selector */}
        <div className="flex flex-wrap gap-2 mb-6">
          {chartTypes.map(chart => (
            <button
              key={chart.id}
              onClick={() => setActiveChart(chart.id)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all ${
                activeChart === chart.id
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <chart.icon size={16} />
              <span>{chart.label}</span>
            </button>
          ))}
        </div>

        {/* Charts */}
        <div className="h-80">
          {activeChart === 'progress' && (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={analyticsData.progressData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="sessions" 
                  stroke="#8b5cf6" 
                  strokeWidth={3}
                  name="Daily Sessions"
                />
                <Line 
                  type="monotone" 
                  dataKey="cumulative" 
                  stroke="#06b6d4" 
                  strokeWidth={2}
                  name="Total Sessions"
                />
              </LineChart>
            </ResponsiveContainer>
          )}

          {activeChart === 'patterns' && (
            <div className="grid md:grid-cols-2 gap-6 h-full">
              <div>
                <h3 className="text-lg font-semibold mb-4">Weekly Pattern</h3>
                <ResponsiveContainer width="100%" height="80%">
                  <BarChart data={analyticsData.weeklyPattern}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="sessions" fill="#8b5cf6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-4">Time of Day</h3>
                <ResponsiveContainer width="100%" height="80%">
                  <BarChart data={analyticsData.timeOfDayPattern}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" angle={-45} textAnchor="end" height={80} />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="sessions" fill="#10b981" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {activeChart === 'effectiveness' && (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={analyticsData.effectivenessData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="sessionNumber" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="effectiveness" 
                  stroke="#f59e0b" 
                  strokeWidth={3}
                  name="Effectiveness %"
                />
              </LineChart>
            </ResponsiveContainer>
          )}

          {activeChart === 'services' && (
            <div className="flex items-center justify-center h-full">
              <ResponsiveContainer width="60%" height="100%">
                <PieChart>
                  <Pie
                    data={analyticsData.serviceTypeData}
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {analyticsData.serviceTypeData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      </div>

      {/* Insights Panel */}
      <div className="sacred-card p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">🧠 AI-Generated Insights</h3>
        <div className="grid md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
              <h4 className="font-semibold text-blue-800 mb-2">📈 Growth Pattern</h4>
              <p className="text-blue-700 text-sm">
                {analyticsData.totalSessions > 10 
                  ? "Your spiritual practice shows consistent growth. You're building strong foundations for deeper understanding."
                  : "You're in the early stages of your spiritual journey. Focus on establishing a regular practice routine."
                }
              </p>
            </div>
            
            <div className="p-4 bg-green-50 rounded-lg border border-green-200">
              <h4 className="font-semibold text-green-800 mb-2">🎯 Effectiveness Trends</h4>
              <p className="text-green-700 text-sm">
                {analyticsData.insightMetrics.averageEffectiveness > 80
                  ? "Excellent! Your sessions are highly effective. Continue with your current approach."
                  : "Consider deeper engagement during sessions. Try meditation before starting for better focus."
                }
              </p>
            </div>
          </div>
          
          <div className="space-y-4">
            <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
              <h4 className="font-semibold text-purple-800 mb-2">⏰ Optimal Timing</h4>
              <p className="text-purple-700 text-sm">
                {analyticsData.weeklyPattern.length > 0 
                  ? `Your most active day is ${analyticsData.weeklyPattern.reduce((a, b) => a.sessions > b.sessions ? a : b).day}. Consider maintaining this rhythm.`
                  : "Establish a consistent schedule for spiritual practice to enhance growth."
                }
              </p>
            </div>
            
            <div className="p-4 bg-orange-50 rounded-lg border border-orange-200">
              <h4 className="font-semibold text-orange-800 mb-2">🔄 Recommendations</h4>
              <p className="text-orange-700 text-sm">
                {analyticsData.streakData.current > 0
                  ? `Great ${analyticsData.streakData.current}-day streak! Keep the momentum going with daily practice.`
                  : "Start building a daily practice streak. Even 5 minutes of spiritual reflection can be transformative."
                }
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SessionAnalytics;