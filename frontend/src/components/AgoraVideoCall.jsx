import React, { useState, useEffect, useRef } from 'react';
import { Video, VideoOff, Mic, MicOff, Phone, PhoneOff, Users, Settings, Volume2, VolumeX } from 'lucide-react';

// Agora SDK integration (production would use real Agora SDK)
const AgoraVideoCall = ({ 
    sessionData, 
    onEndCall, 
    onError 
}) => {
    const [isConnected, setIsConnected] = useState(false);
    const [isVideoEnabled, setIsVideoEnabled] = useState(true);
    const [isAudioEnabled, setIsAudioEnabled] = useState(true);
    const [isSpeakerEnabled, setIsSpeakerEnabled] = useState(true);
    const [participants, setParticipants] = useState([]);
    const [connectionStatus, setConnectionStatus] = useState('connecting');
    const [callDuration, setCallDuration] = useState(0);
    const [remoteVideoVisible, setRemoteVideoVisible] = useState(false);
    
    const localVideoRef = useRef(null);
    const remoteVideoRef = useRef(null);
    const connectionTimerRef = useRef(null);
    const durationTimerRef = useRef(null);
    
    // Initialize Agora connection
    useEffect(() => {
        if (!sessionData || !sessionData.agora_app_id) {
            onError('Invalid session data');
            return;
        }
        
        initializeAgoraConnection();
        
        return () => {
            cleanup();
        };
    }, [sessionData]);
    
    const initializeAgoraConnection = async () => {
        try {
            setConnectionStatus('connecting');
            
            // Simulate Agora connection process
            await simulateAgoraConnection();
            
            setConnectionStatus('connected');
            setIsConnected(true);
            
            // Start call duration timer
            durationTimerRef.current = setInterval(() => {
                setCallDuration(prev => prev + 1);
            }, 1000);
            
            // Simulate remote video after 2 seconds
            setTimeout(() => {
                setRemoteVideoVisible(true);
                setParticipants([
                    {
                        uid: 'swamiji',
                        name: 'Swamiji',
                        isVideoEnabled: true,
                        isAudioEnabled: true
                    }
                ]);
            }, 2000);
            
        } catch (error) {
            console.error('Agora connection failed:', error);
            setConnectionStatus('failed');
            onError('Connection to divine guidance failed');
        }
    };
    
    const simulateAgoraConnection = async () => {
        // Simulate connection process
        return new Promise((resolve, reject) => {
            // Simulate real Agora connection steps
            setTimeout(() => {
                if (sessionData.agora_token && sessionData.agora_channel) {
                    resolve();
                } else {
                    reject(new Error('Invalid credentials'));
                }
            }, 1500);
        });
    };
    
    const cleanup = () => {
        if (durationTimerRef.current) {
            clearInterval(durationTimerRef.current);
        }
        if (connectionTimerRef.current) {
            clearInterval(connectionTimerRef.current);
        }
        // In production, clean up Agora client
    };
    
    const toggleVideo = () => {
        setIsVideoEnabled(!isVideoEnabled);
        // In production, toggle local video stream
    };
    
    const toggleAudio = () => {
        setIsAudioEnabled(!isAudioEnabled);
        // In production, toggle local audio stream
    };
    
    const toggleSpeaker = () => {
        setIsSpeakerEnabled(!isSpeakerEnabled);
        // In production, toggle speaker/earpiece
    };
    
    const endCall = async () => {
        try {
            setConnectionStatus('ending');
            
            // Call parent's end call handler
            await onEndCall();
            
            cleanup();
            
        } catch (error) {
            console.error('End call failed:', error);
            onError('Failed to end call properly');
        }
    };
    
    const formatDuration = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };
    
    const renderConnectionStatus = () => {
        switch (connectionStatus) {
            case 'connecting':
                return (
                    <div className="flex flex-col items-center justify-center h-64 bg-gradient-to-br from-orange-50 to-red-50 rounded-lg">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mb-4"></div>
                        <p className="text-orange-600 font-medium">दिव्य मार्गदर्शन से जुड़ रहे हैं...</p>
                        <p className="text-sm text-gray-500 mt-2">Connecting to divine guidance...</p>
                    </div>
                );
            case 'failed':
                return (
                    <div className="flex flex-col items-center justify-center h-64 bg-red-50 rounded-lg">
                        <div className="text-red-500 mb-4">
                            <PhoneOff size={48} />
                        </div>
                        <p className="text-red-600 font-medium">कनेक्शन असफल</p>
                        <p className="text-sm text-gray-500 mt-2">Connection failed</p>
                        <button 
                            onClick={() => initializeAgoraConnection()}
                            className="mt-4 px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
                        >
                            फिर से कोशिश करें
                        </button>
                    </div>
                );
            case 'ending':
                return (
                    <div className="flex flex-col items-center justify-center h-64 bg-gray-50 rounded-lg">
                        <div className="animate-pulse text-gray-500 mb-4">
                            <PhoneOff size={48} />
                        </div>
                        <p className="text-gray-600 font-medium">सेशन समाप्त हो रहा है...</p>
                        <p className="text-sm text-gray-500 mt-2">Ending session...</p>
                    </div>
                );
            default:
                return null;
        }
    };
    
    if (!isConnected) {
        return (
            <div className="w-full max-w-4xl mx-auto p-6">
                <div className="bg-white rounded-lg shadow-xl p-6">
                    <div className="mb-4">
                        <h2 className="text-xl font-bold text-gray-900">Live Divine Guidance</h2>
                        <p className="text-sm text-gray-600">
                            Channel: {sessionData?.agora_channel || 'Unknown'}
                        </p>
                    </div>
                    {renderConnectionStatus()}
                </div>
            </div>
        );
    }
    
    return (
        <div className="w-full max-w-6xl mx-auto p-4">
            <div className="bg-white rounded-lg shadow-xl overflow-hidden">
                {/* Header */}
                <div className="bg-gradient-to-r from-orange-500 to-red-500 text-white p-4">
                    <div className="flex justify-between items-center">
                        <div>
                            <h2 className="text-lg font-bold">Live Divine Guidance</h2>
                            <p className="text-sm opacity-90">
                                Session: {sessionData?.session_id?.slice(0, 8)}...
                            </p>
                        </div>
                        <div className="flex items-center space-x-4">
                            <div className="flex items-center space-x-2">
                                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                                <span className="text-sm">Live</span>
                            </div>
                            <div className="text-sm">
                                {formatDuration(callDuration)}
                            </div>
                        </div>
                    </div>
                </div>
                
                {/* Video Container */}
                <div className="relative bg-black" style={{ height: '500px' }}>
                    {/* Remote Video (Swamiji) */}
                    <div className="absolute inset-0 flex items-center justify-center">
                        {remoteVideoVisible ? (
                            <div className="w-full h-full bg-gradient-to-br from-orange-400 to-red-500 flex items-center justify-center">
                                <div className="text-center text-white">
                                    <div className="w-32 h-32 bg-white bg-opacity-20 rounded-full flex items-center justify-center mb-4 mx-auto">
                                        <Users size={48} className="text-white" />
                                    </div>
                                    <h3 className="text-xl font-bold mb-2">Swamiji</h3>
                                    <p className="text-sm opacity-90">
                                        आपका दिव्य मार्गदर्शन यहाँ है
                                    </p>
                                </div>
                            </div>
                        ) : (
                            <div className="text-gray-400 text-center">
                                <Users size={48} className="mx-auto mb-4" />
                                <p>Waiting for divine guidance...</p>
                            </div>
                        )}
                    </div>
                    
                    {/* Local Video (User) */}
                    <div className="absolute top-4 right-4 w-48 h-36 bg-gray-800 rounded-lg overflow-hidden shadow-lg">
                        {isVideoEnabled ? (
                            <div className="w-full h-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center">
                                <div className="text-white text-center">
                                    <div className="w-16 h-16 bg-white bg-opacity-20 rounded-full flex items-center justify-center mb-2 mx-auto">
                                        <Video size={24} />
                                    </div>
                                    <p className="text-xs">You</p>
                                </div>
                            </div>
                        ) : (
                            <div className="w-full h-full bg-gray-700 flex items-center justify-center">
                                <div className="text-gray-400 text-center">
                                    <VideoOff size={24} className="mx-auto mb-2" />
                                    <p className="text-xs">Video Off</p>
                                </div>
                            </div>
                        )}
                    </div>
                    
                    {/* Participants List */}
                    <div className="absolute top-4 left-4 bg-black bg-opacity-50 rounded-lg p-2">
                        <div className="flex items-center space-x-2 text-white text-sm">
                            <Users size={16} />
                            <span>{participants.length + 1} participants</span>
                        </div>
                    </div>
                </div>
                
                {/* Controls */}
                <div className="bg-gray-50 p-4">
                    <div className="flex justify-center space-x-4">
                        {/* Video Toggle */}
                        <button
                            onClick={toggleVideo}
                            className={`p-3 rounded-full transition-colors ${
                                isVideoEnabled 
                                    ? 'bg-gray-200 hover:bg-gray-300 text-gray-700' 
                                    : 'bg-red-500 hover:bg-red-600 text-white'
                            }`}
                        >
                            {isVideoEnabled ? <Video size={20} /> : <VideoOff size={20} />}
                        </button>
                        
                        {/* Audio Toggle */}
                        <button
                            onClick={toggleAudio}
                            className={`p-3 rounded-full transition-colors ${
                                isAudioEnabled 
                                    ? 'bg-gray-200 hover:bg-gray-300 text-gray-700' 
                                    : 'bg-red-500 hover:bg-red-600 text-white'
                            }`}
                        >
                            {isAudioEnabled ? <Mic size={20} /> : <MicOff size={20} />}
                        </button>
                        
                        {/* Speaker Toggle */}
                        <button
                            onClick={toggleSpeaker}
                            className={`p-3 rounded-full transition-colors ${
                                isSpeakerEnabled 
                                    ? 'bg-gray-200 hover:bg-gray-300 text-gray-700' 
                                    : 'bg-gray-400 hover:bg-gray-500 text-white'
                            }`}
                        >
                            {isSpeakerEnabled ? <Volume2 size={20} /> : <VolumeX size={20} />}
                        </button>
                        
                        {/* End Call */}
                        <button
                            onClick={endCall}
                            className="p-3 rounded-full bg-red-500 hover:bg-red-600 text-white transition-colors"
                        >
                            <PhoneOff size={20} />
                        </button>
                        
                        {/* Settings */}
                        <button className="p-3 rounded-full bg-gray-200 hover:bg-gray-300 text-gray-700 transition-colors">
                            <Settings size={20} />
                        </button>
                    </div>
                    
                    {/* Session Info */}
                    <div className="mt-4 text-center text-sm text-gray-600">
                        <div className="flex justify-center space-x-6">
                            <div>
                                <span className="font-medium">Session Type:</span> {sessionData?.session_type}
                            </div>
                            <div>
                                <span className="font-medium">Duration:</span> {formatDuration(callDuration)}
                            </div>
                            <div>
                                <span className="font-medium">Quality:</span> 
                                <span className="text-green-600 ml-1">HD</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AgoraVideoCall;