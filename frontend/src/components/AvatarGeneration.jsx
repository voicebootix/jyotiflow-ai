import React, { useState, useEffect } from 'react';
import { Play, Pause, Download, Share2, Video, Clock, Star, Loader2 } from 'lucide-react';
import enhanced_api from '../services/enhanced-api';

const AvatarGeneration = () => {
  const [question, setQuestion] = useState('');
  const [serviceType, setServiceType] = useState('comprehensive');
  // Avatar style and voice tone are now admin-controlled, not user-selectable
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationStatus, setGenerationStatus] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [videoUrl, setVideoUrl] = useState(null);
  const [guidance, setGuidance] = useState('');
  const [generationTime, setGenerationTime] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [serviceTypes, setServiceTypes] = useState([]);
  const [birthDetails, setBirthDetails] = useState({
    birth_date: '',
    birth_time: '',
    birth_location: ''
  });

  useEffect(() => {
    fetchServiceTypes();
  }, []);

  useEffect(() => {
    let interval;
    if (sessionId && generationStatus === 'generating') {
      interval = setInterval(checkGenerationStatus, 5000); // Check every 5 seconds
    }
    return () => clearInterval(interval);
  }, [sessionId, generationStatus]);

  const fetchServiceTypes = async () => {
    try {
      const response = await enhanced_api.get('/service-types');
      if (response.data.success) {
        setServiceTypes(response.data.data.filter(service => 
          service.is_active && service.avatar_video_enabled
        ));
      }
    } catch (error) {
      console.error('Error fetching service types:', error);
    }
  };

  const generateAvatarVideo = async () => {
    if (!question.trim()) {
      alert('Please enter your spiritual question');
      return;
    }

    setIsGenerating(true);
    setGenerationStatus('generating');
    setVideoUrl(null);
    setGuidance('');

    try {
      const response = await enhanced_api.post('/avatar/generate-with-guidance', {
        question: question,
        service_type: serviceType,
        birth_details: birthDetails.birth_date ? birthDetails : null
      });

      if (response.data.success) {
        setSessionId(response.data.session_id);
        setGuidance(response.data.guidance_text);
        
        if (response.data.video_url) {
          // Video generated immediately
          setVideoUrl(response.data.video_url);
          setGenerationStatus('completed');
          setGenerationTime(response.data.generation_time);
          setIsGenerating(false);
        } else {
          // Video still generating, keep checking status
          setGenerationStatus('generating');
        }
      } else {
        throw new Error(response.data.error || 'Generation failed');
      }
    } catch (error) {
      console.error('Error generating avatar video:', error);
      setGenerationStatus('failed');
      setIsGenerating(false);
      alert('Failed to generate avatar video. Please try again.');
    }
  };

  const checkGenerationStatus = async () => {
    if (!sessionId) return;

    try {
      const response = await enhanced_api.get(`/avatar/status/${sessionId}`);
      const status = response.data.status;

      if (status === 'completed') {
        setVideoUrl(response.data.video_url);
        setGenerationStatus('completed');
        setGenerationTime(response.data.generation_time);
        setIsGenerating(false);
      } else if (status === 'failed') {
        setGenerationStatus('failed');
        setIsGenerating(false);
        alert('Avatar generation failed. Please try again.');
      }
      // If still generating, keep polling
    } catch (error) {
      console.error('Error checking generation status:', error);
    }
  };

  const handleVideoPlay = () => {
    setIsPlaying(true);
  };

  const handleVideoPause = () => {
    setIsPlaying(false);
  };

  const downloadVideo = () => {
    if (videoUrl) {
      const link = document.createElement('a');
      link.href = videoUrl;
      link.download = `swamiji-guidance-${sessionId}.mp4`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const shareVideo = async () => {
    if (navigator.share && videoUrl) {
      try {
        await navigator.share({
          title: 'Spiritual Guidance from Swami Jyotirananthan',
          text: 'Divine wisdom and blessings from JyotiFlow.ai',
          url: videoUrl
        });
      } catch (error) {
        console.log('Share failed:', error);
        // Fallback to copying URL
        navigator.clipboard.writeText(videoUrl);
        alert('Video URL copied to clipboard!');
      }
    } else {
      // Fallback for browsers without Web Share API
      navigator.clipboard.writeText(videoUrl);
      alert('Video URL copied to clipboard!');
    }
  };

  // Swamiji's appearance and voice are now automatically controlled by admin settings

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          🎭 Generate Avatar Guidance with Swami Jyotirananthan
        </h1>
        <p className="text-gray-600">
          Receive personalized spiritual guidance with AI-generated video from our beloved master
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column - Input Form */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Your Spiritual Question
              </label>
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask Swamiji about your spiritual journey, relationships, career, or any guidance you seek..."
                rows={4}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Service Type
              </label>
              <select
                value={serviceType}
                onChange={(e) => setServiceType(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                {serviceTypes.map(service => (
                  <option key={service.name} value={service.name}>
                    {service.display_name} ({service.credits_required} credits)
                  </option>
                ))}
              </select>
            </div>

            {/* Swamiji Appearance - Admin Controlled Notice */}
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-2">
                <span className="text-purple-600">🎭</span>
                <h3 className="font-medium text-purple-900">Swamiji's Authentic Presence</h3>
              </div>
              <p className="text-sm text-purple-800">
                Swami Jyotirananthan appears in his traditional form, automatically styled for today's spiritual theme and any special occasions. His appearance reflects authentic Tamil spiritual tradition.
              </p>
              <div className="mt-2 text-xs text-purple-600">
                Today: Traditional robes with temple background • Voice: Compassionate Tamil accent
              </div>
            </div>

            {/* Optional Birth Details */}
            <div className="border-t pt-4">
              <h3 className="font-medium text-gray-900 mb-3">
                Birth Details (Optional for Personalized Reading)
              </h3>
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Birth Date</label>
                  <input
                    type="date"
                    value={birthDetails.birth_date}
                    onChange={(e) => setBirthDetails(prev => ({...prev, birth_date: e.target.value}))}
                    className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Birth Time</label>
                  <input
                    type="time"
                    value={birthDetails.birth_time}
                    onChange={(e) => setBirthDetails(prev => ({...prev, birth_time: e.target.value}))}
                    className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Birth Location</label>
                  <input
                    type="text"
                    value={birthDetails.birth_location}
                    onChange={(e) => setBirthDetails(prev => ({...prev, birth_location: e.target.value}))}
                    placeholder="City, Country"
                    className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
                  />
                </div>
              </div>
            </div>

            <button
              onClick={generateAvatarVideo}
              disabled={isGenerating || !question.trim()}
              className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 text-white py-3 px-4 rounded-lg font-medium hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="animate-spin" size={16} />
                  <span>Generating Avatar Video...</span>
                </>
              ) : (
                <>
                  <Video size={16} />
                  <span>Generate Avatar Guidance</span>
                </>
              )}
            </button>
          </div>

          {/* Right Column - Video Player & Status */}
          <div className="space-y-4">
            {generationStatus === 'generating' && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-center space-x-2">
                  <Loader2 className="animate-spin text-blue-600" size={20} />
                  <span className="text-blue-800">
                    Swamiji is preparing your personalized guidance...
                  </span>
                </div>
                <div className="mt-2 text-sm text-blue-600">
                  This may take 2-5 minutes. You'll see the video when it's ready.
                </div>
              </div>
            )}

            {guidance && (
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                <h3 className="font-medium text-purple-900 mb-2">Spiritual Guidance</h3>
                <div className="text-sm text-purple-800 whitespace-pre-wrap">
                  {guidance}
                </div>
              </div>
            )}

            {videoUrl && (
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-medium text-gray-900">Avatar Video</h3>
                  {generationTime && (
                    <div className="flex items-center text-sm text-gray-500">
                      <Clock size={14} className="mr-1" />
                      Generated in {generationTime.toFixed(1)}s
                    </div>
                  )}
                </div>
                
                <video
                  controls
                  className="w-full rounded-lg"
                  onPlay={handleVideoPlay}
                  onPause={handleVideoPause}
                >
                  <source src={videoUrl} type="video/mp4" />
                  Your browser does not support the video tag.
                </video>

                <div className="flex justify-center space-x-3 mt-4">
                  <button
                    onClick={downloadVideo}
                    className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                  >
                    <Download size={16} />
                    <span>Download</span>
                  </button>
                  <button
                    onClick={shareVideo}
                    className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    <Share2 size={16} />
                    <span>Share</span>
                  </button>
                </div>
              </div>
            )}

            {generationStatus === 'failed' && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="text-red-800">
                  Avatar generation failed. Please try again or contact support.
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Information Section */}
      <div className="bg-gradient-to-r from-purple-100 to-indigo-100 rounded-lg p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          🕉️ About Avatar Guidance
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <h3 className="font-medium text-purple-900 mb-2">Real AI Technology</h3>
            <p className="text-gray-700">
              Powered by D-ID video generation and ElevenLabs voice synthesis for authentic Swamiji experience.
            </p>
          </div>
          <div>
            <h3 className="font-medium text-purple-900 mb-2">Personalized Guidance</h3>
            <p className="text-gray-700">
              Each response is uniquely generated based on your question and spiritual profile.
            </p>
          </div>
          <div>
            <h3 className="font-medium text-purple-900 mb-2">Tamil Tradition</h3>
            <p className="text-gray-700">
              Rooted in authentic Tamil spiritual wisdom and Vedantic principles.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AvatarGeneration;