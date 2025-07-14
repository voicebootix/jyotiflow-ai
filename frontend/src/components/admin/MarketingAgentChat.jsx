import React, { useState, useEffect, useRef } from 'react';
import enhanced_api from '../../services/enhanced-api';

const MarketingAgentChat = () => {
  const [messages, setMessages] = useState([
    { 
      sender: 'agent', 
      text: '🤖 **AI Marketing Director** at your service! I can help you with:\n\n' +
            '• **Market Analysis** - Analyze your target audience and competitors\n' +
            '• **Content Strategy** - Generate content calendars and campaigns\n' +
            '• **Performance Reports** - Track metrics and ROI\n' +
            '• **Platform Optimization** - Improve engagement across social media\n' +
            '• **Campaign Management** - Create and manage marketing campaigns\n\n' +
            'What would you like to work on today?'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    
    const userMsg = { sender: 'user', text: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      console.log('Sending message to AI Marketing Director:', input);
      
      // Use the proper sendAgentMessage method from enhanced-api
      const response = await enhanced_api.sendAgentMessage(input);
      
      console.log('AI Marketing Director response:', response);
      
      // Handle the StandardResponse format from the backend
      let responseText = '';
      
      if (response && response.success) {
        // Extract the message from the data object
        responseText = response.data?.message || 
                      response.data?.reply || 
                      response.message || 
                      'Response received successfully';
      } else if (response && response.success === false) {
        // Handle error responses
        responseText = response.message || 
                      response.data?.error || 
                      'The AI Marketing Director encountered an error';
      } else {
        // Handle unexpected response format
        responseText = 'Invalid response format received';
      }
      
      console.log('Processed response text:', responseText);
      
      setMessages(prev => [...prev, { 
        sender: 'agent', 
        text: responseText
      }]);
      
    } catch (error) {
      console.error('AI Marketing Director chat error:', error);
      console.error('Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      });
      
      let errorMessage = '⚠️ Error: Could not reach the AI Marketing Director. Please try again.';
      
      // More specific error messages based on error type
      if (error.response) {
        const status = error.response.status;
        const errorData = error.response.data;
        
        if (status === 401) {
          errorMessage = '⚠️ Authentication error. Please refresh the page and log in again.';
        } else if (status === 403) {
          errorMessage = '⚠️ Access denied. Admin privileges required for AI Marketing Director.';
        } else if (status === 404) {
          errorMessage = '⚠️ AI Marketing Director service not found. Please contact support.';
        } else if (status === 500) {
          errorMessage = '⚠️ Server error. The AI Marketing Director is temporarily unavailable.';
        } else if (errorData?.message) {
          errorMessage = `⚠️ Error: ${errorData.message}`;
        } else if (errorData?.detail) {
          errorMessage = `⚠️ Error: ${errorData.detail}`;
        }
      } else if (error.request) {
        errorMessage = '⚠️ Network error. Please check your connection and try again.';
      } else if (error.message) {
        errorMessage = `⚠️ Error: ${error.message}`;
      }
      
      setMessages(prev => [...prev, { 
        sender: 'agent', 
        text: errorMessage
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatMessage = (text) => {
    return text.split('\n').map((line, index) => {
      // Handle bold text
      const boldRegex = /\*\*(.*?)\*\*/g;
      const parts = line.split(boldRegex);
      
      return (
        <span key={index}>
          {parts.map((part, i) => 
            i % 2 === 1 ? <strong key={i}>{part}</strong> : part
          )}
          {index < text.split('\n').length - 1 && <br />}
        </span>
      );
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 max-w-4xl mx-auto">
      <h3 className="text-lg font-semibold">AI Marketing Director</h3>
      <div className="bg-gray-50 rounded-lg p-4 h-80 overflow-y-auto mb-4">
        {messages.map((msg, index) => (
          <div key={index} className={`mb-4 ${msg.sender === 'user' ? 'text-right' : 'text-left'}`}>
            <div className={`inline-block p-3 rounded-lg max-w-xs md:max-w-md ${
              msg.sender === 'user' 
                ? 'bg-blue-500 text-white' 
                : 'bg-white border'
            }`}>
              <div className="whitespace-pre-wrap">
                {formatMessage(msg.text)}
              </div>
            </div>
          </div>
        ))}
        {loading && (
          <div className="text-left mb-4">
            <div className="inline-block p-3 rounded-lg bg-gray-200">
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500 mr-2"></div>
                AI Marketing Director is thinking...
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Give instructions to the AI Marketing Director... (e.g., 'Show market analysis', 'Generate content plan')"
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={loading}
        />
        <button
          onClick={sendMessage}
          disabled={loading || !input.trim()}
          className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? 'Sending...' : 'Send'}
        </button>
      </div>
      
      <div className="mt-4 text-sm text-gray-600">
        <p><strong>💡 Pro Tips:</strong></p>
        <ul className="list-disc list-inside mt-2 space-y-1">
          <li>Ask for specific market insights: "Analyze spiritual guidance market trends"</li>
          <li>Request content strategies: "Create content calendar for Instagram"</li>
          <li>Get performance reports: "Show last week's engagement metrics"</li>
          <li>Campaign optimization: "Improve Facebook ad performance"</li>
        </ul>
      </div>
    </div>
  );
};

export default MarketingAgentChat; 