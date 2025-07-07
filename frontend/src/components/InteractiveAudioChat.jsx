import React, { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Video, VideoOff, Phone, PhoneOff, Volume2, VolumeX, Settings } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';
import spiritualAPI from '../lib/api';

const InteractiveAudioChat = ({ onClose, serviceType = 'audio_guidance' }) => {
  const { t, currentLanguage } = useLanguage();
  const [isCallActive, setIsCallActive] = useState(false);
  const [isAudioEnabled, setIsAudioEnabled] = useState(false);
  const [isVideoEnabled, setIsVideoEnabled] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [conversation, setConversation] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [audioLevel, setAudioLevel] = useState(0);
  
  const mediaStreamRef = useRef(null);
  const peerConnectionRef = useRef(null);
  const recognitionRef = useRef(null);
  const synthesisRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);

  useEffect(() => {
    initializeWebRTC();
    initializeSpeechRecognition();
    initializeSpeechSynthesis();
    
    return () => {
      cleanup();
    };
  }, []);

  const initializeWebRTC = async () => {
    try {
      // Initialize peer connection
      peerConnectionRef.current = new RTCPeerConnection({
        iceServers: [
          { urls: 'stun:stun.l.google.com:19302' },
          { urls: 'stun:stun1.l.google.com:19302' }
        ]
      });

      // Handle connection state changes
      peerConnectionRef.current.onconnectionstatechange = () => {
        setConnectionStatus(peerConnectionRef.current.connectionState);
      };

    } catch (error) {
      console.error('WebRTC initialization error:', error);
    }
  };

  const initializeSpeechRecognition = () => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = getLanguageCode(currentLanguage);

      recognitionRef.current.onstart = () => {
        setIsListening(true);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current.onresult = (event) => {
        const result = event.results[event.results.length - 1];
        if (result.isFinal) {
          const transcript = result[0].transcript;
          handleUserSpeech(transcript);
        }
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };
    }
  };

  const initializeSpeechSynthesis = () => {
    if ('speechSynthesis' in window) {
      synthesisRef.current = window.speechSynthesis;
    }
  };

  const getLanguageCode = (lang) => {
    const langCodes = {
      'en': 'en-US',
      'ta': 'ta-IN',
      'hi': 'hi-IN'
    };
    return langCodes[lang] || 'en-US';
  };

  const getVoiceForLanguage = (lang) => {
    const voices = synthesisRef.current?.getVoices() || [];
    
    // Prefer specific voices for each language
    const voicePreferences = {
      'en': ['Google UK English Male', 'Microsoft David - English (United States)', 'en-US'],
      'ta': ['Google தமிழ்', 'Microsoft Tamil', 'ta-IN'],
      'hi': ['Google हिन्दी', 'Microsoft Hindi', 'hi-IN']
    };

    const preferences = voicePreferences[lang] || voicePreferences['en'];
    
    for (const preference of preferences) {
      const voice = voices.find(v => 
        v.name.includes(preference) || v.lang.includes(preference)
      );
      if (voice) return voice;
    }

    // Fallback to default voice
    return voices[0];
  };

  const startCall = async () => {
    try {
      setConnectionStatus('connecting');
      
      // Request media permissions
      const constraints = {
        audio: true,
        video: serviceType.includes('video')
      };

      mediaStreamRef.current = await navigator.mediaDevices.getUserMedia(constraints);
      
      // Set up audio level monitoring
      if (mediaStreamRef.current.getAudioTracks().length > 0) {
        setupAudioLevelMonitoring();
      }

      setIsCallActive(true);
      setIsAudioEnabled(true);
      if (serviceType.includes('video')) {
        setIsVideoEnabled(true);
      }
      
      setConnectionStatus('connected');
      
      // Start the conversation
      startConversation();
      
    } catch (error) {
      console.error('Error starting call:', error);
      setConnectionStatus('failed');
      alert(t('microphoneAccessError', 'Please allow microphone access to use voice chat'));
    }
  };

  const setupAudioLevelMonitoring = () => {
    if (!mediaStreamRef.current) return;

    audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
    analyserRef.current = audioContextRef.current.createAnalyser();
    
    const source = audioContextRef.current.createMediaStreamSource(mediaStreamRef.current);
    source.connect(analyserRef.current);
    
    analyserRef.current.fftSize = 256;
    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
    
    const updateAudioLevel = () => {
      if (!analyserRef.current) return;
      
      analyserRef.current.getByteFrequencyData(dataArray);
      const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
      setAudioLevel(Math.min(100, (average / 128) * 100));
      
      if (isCallActive) {
        requestAnimationFrame(updateAudioLevel);
      }
    };
    
    updateAudioLevel();
  };

  const startConversation = () => {
    // Welcome message
    const welcomeMessage = getWelcomeMessage();
    speakText(welcomeMessage);
    
    setConversation([{
      type: 'ai',
      text: welcomeMessage,
      timestamp: new Date()
    }]);

    // Start listening after welcome message
    setTimeout(() => {
      startListening();
    }, 3000);
  };

  const getWelcomeMessage = () => {
    const messages = {
      'en': "🕉️ Om Namah Shivaya. I am Swami Jyotirananthan. Welcome to our sacred conversation. Please share what is in your heart, and I will guide you with divine wisdom.",
      'ta': "🕉️ ஓம் நமஃ சிவாய. நான் ஸ்வாமி ஜ்யோதிரானந்தன். எங்கள் புனித உரையாடலுக்கு வரவேற்கிறேன். உங்கள் இதயத்தில் உள்ளதை பகிர்ந்து கொள்ளுங்கள், தெய்வீக ஞானத்துடன் உங்களுக்கு வழிகாட்டுவேன்.",
      'hi': "🕉️ ॐ नमः शिवाय। मैं स्वामी ज्योतिरानंदन हूं। हमारी पवित्र बातचीत में आपका स्वागत है। कृपया अपने हृदय की बात साझा करें, और मैं दिव्य ज्ञान के साथ आपका मार्गदर्शन करूंगा।"
    };
    return messages[currentLanguage] || messages['en'];
  };

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      recognitionRef.current.start();
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
    }
  };

  const handleUserSpeech = async (transcript) => {
    if (!transcript.trim()) return;

    // Add user message to conversation
    setConversation(prev => [...prev, {
      type: 'user',
      text: transcript,
      timestamp: new Date()
    }]);

    // Stop listening while processing
    stopListening();

    try {
      // Get AI response
      const response = await getAIResponse(transcript);
      
      // Add AI response to conversation
      setConversation(prev => [...prev, {
        type: 'ai',
        text: response,
        timestamp: new Date()
      }]);

      // Speak the response
      await speakText(response);

      // Resume listening after speaking
      setTimeout(() => {
        if (isCallActive) {
          startListening();
        }
      }, 1000);

    } catch (error) {
      console.error('Error processing speech:', error);
      const errorMessage = t('processingError', 'I apologize, I had trouble understanding. Please try again.');
      speakText(errorMessage);
      
      setTimeout(() => {
        if (isCallActive) {
          startListening();
        }
      }, 2000);
    }
  };

  const getAIResponse = async (userInput) => {
    try {
      const response = await spiritualAPI.post('/api/spiritual/interactive-guidance', {
        message: userInput,
        language: currentLanguage,
        conversation_context: conversation.slice(-6), // Last 6 messages for context
        service_type: serviceType
      });

      if (response.success) {
        return response.data.guidance;
      } else {
        throw new Error('AI response failed');
      }
    } catch (error) {
      console.error('AI response error:', error);
      
      // Fallback response
      const fallbacks = {
        'en': "I understand your concern. Please give me a moment to reflect on this deeply. Sometimes the divine speaks through silence before offering wisdom.",
        'ta': "உங்கள் கவலையை நான் புரிந்துகொள்கிறேன். இதைப் பற்றி ஆழமாக சிந்திக்க எனக்கு ஒரு கணம் கொடுங்கள். சில நேரங்களில் தெய்வம் ஞானத்தை வழங்குவதற்கு முன் மௌனத்தின் மூலம் பேசுகிறது.",
        'hi': "मैं आपकी चिंता समझता हूं। कृपया मुझे इस पर गहराई से विचार करने के लिए एक क्षण दें। कभी-कभी ईश्वर ज्ञान देने से पहले मौन के माध्यम से बोलता है।"
      };
      
      return fallbacks[currentLanguage] || fallbacks['en'];
    }
  };

  const speakText = (text) => {
    return new Promise((resolve) => {
      if (!synthesisRef.current) {
        resolve();
        return;
      }

      // Cancel any ongoing speech
      synthesisRef.current.cancel();

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.voice = getVoiceForLanguage(currentLanguage);
      utterance.rate = 0.9;
      utterance.pitch = 1.0;
      utterance.volume = 0.8;

      utterance.onstart = () => {
        setIsSpeaking(true);
      };

      utterance.onend = () => {
        setIsSpeaking(false);
        resolve();
      };

      utterance.onerror = (error) => {
        console.error('Speech synthesis error:', error);
        setIsSpeaking(false);
        resolve();
      };

      synthesisRef.current.speak(utterance);
    });
  };

  const endCall = () => {
    cleanup();
    setIsCallActive(false);
    setConnectionStatus('disconnected');
    if (onClose) onClose();
  };

  const toggleAudio = () => {
    if (mediaStreamRef.current) {
      const audioTracks = mediaStreamRef.current.getAudioTracks();
      audioTracks.forEach(track => {
        track.enabled = !isAudioEnabled;
      });
      setIsAudioEnabled(!isAudioEnabled);
      
      if (!isAudioEnabled) {
        startListening();
      } else {
        stopListening();
      }
    }
  };

  const toggleVideo = () => {
    if (mediaStreamRef.current) {
      const videoTracks = mediaStreamRef.current.getVideoTracks();
      videoTracks.forEach(track => {
        track.enabled = !isVideoEnabled;
      });
      setIsVideoEnabled(!isVideoEnabled);
    }
  };

  const cleanup = () => {
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(track => track.stop());
    }
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    if (synthesisRef.current) {
      synthesisRef.current.cancel();
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
    }
    if (peerConnectionRef.current) {
      peerConnectionRef.current.close();
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-4xl h-full max-h-[90vh] flex flex-col">
        
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white p-4 rounded-t-lg">
          <h2 className="text-xl font-bold text-center">
            🕉️ {t('interactiveChat', 'Interactive Chat with Swami Jyotirananthan')}
          </h2>
          <div className="text-center text-sm opacity-90 mt-1">
            {connectionStatus === 'connected' ? t('connected', 'Connected') : 
             connectionStatus === 'connecting' ? t('connecting', 'Connecting...') : 
             t('disconnected', 'Disconnected')}
          </div>
        </div>

        {/* Conversation Area */}
        <div className="flex-1 p-4 overflow-y-auto bg-gray-50">
          <div className="space-y-4">
            {conversation.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    message.type === 'user'
                      ? 'bg-purple-600 text-white'
                      : 'bg-white text-gray-800 shadow'
                  }`}
                >
                  <p className="text-sm">{message.text}</p>
                  <p className="text-xs opacity-70 mt-1">
                    {message.timestamp.toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}
            
            {isSpeaking && (
              <div className="flex justify-start">
                <div className="bg-yellow-100 text-yellow-800 px-4 py-2 rounded-lg max-w-xs">
                  <div className="flex items-center space-x-2">
                    <Volume2 size={16} className="animate-pulse" />
                    <span className="text-sm">{t('swamijIsSpeaking', 'Swamiji is speaking...')}</span>
                  </div>
                </div>
              </div>
            )}
            
            {isListening && (
              <div className="flex justify-end">
                <div className="bg-blue-100 text-blue-800 px-4 py-2 rounded-lg max-w-xs">
                  <div className="flex items-center space-x-2">
                    <Mic size={16} className="animate-pulse" />
                    <span className="text-sm">{t('listening', 'Listening...')}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Audio Level Indicator */}
        {isCallActive && (
          <div className="px-4 py-2 bg-gray-100">
            <div className="flex items-center space-x-2">
              <Mic size={16} className="text-gray-600" />
              <div className="flex-1 bg-gray-300 rounded-full h-2">
                <div
                  className="bg-green-500 h-2 rounded-full transition-all duration-200"
                  style={{ width: `${audioLevel}%` }}
                />
              </div>
              <span className="text-xs text-gray-600">{Math.round(audioLevel)}%</span>
            </div>
          </div>
        )}

        {/* Controls */}
        <div className="p-4 bg-white border-t border-gray-200 rounded-b-lg">
          <div className="flex justify-center space-x-4">
            {!isCallActive ? (
              <button
                onClick={startCall}
                className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-medium flex items-center space-x-2"
              >
                <Phone size={20} />
                <span>{t('startCall', 'Start Call')}</span>
              </button>
            ) : (
              <>
                <button
                  onClick={toggleAudio}
                  className={`px-4 py-3 rounded-lg font-medium flex items-center space-x-2 ${
                    isAudioEnabled 
                      ? 'bg-gray-200 text-gray-700 hover:bg-gray-300' 
                      : 'bg-red-600 text-white hover:bg-red-700'
                  }`}
                >
                  {isAudioEnabled ? <Mic size={20} /> : <MicOff size={20} />}
                </button>
                
                {serviceType.includes('video') && (
                  <button
                    onClick={toggleVideo}
                    className={`px-4 py-3 rounded-lg font-medium flex items-center space-x-2 ${
                      isVideoEnabled 
                        ? 'bg-gray-200 text-gray-700 hover:bg-gray-300' 
                        : 'bg-red-600 text-white hover:bg-red-700'
                    }`}
                  >
                    {isVideoEnabled ? <Video size={20} /> : <VideoOff size={20} />}
                  </button>
                )}
                
                <button
                  onClick={endCall}
                  className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg font-medium flex items-center space-x-2"
                >
                  <PhoneOff size={20} />
                  <span>{t('endCall', 'End Call')}</span>
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default InteractiveAudioChat;