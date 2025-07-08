import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, TrendingUp, Target, Globe } from 'lucide-react';
import enhanced_api from '../../services/enhanced-api';

const MarketingAgentChat = () => {
  const [messages, setMessages] = useState([
    { 
      sender: 'agent', 
      text: '🤖 **AI Marketing Director** at your service! I can help you with:\n\n' +
            '• **Market Analysis** - "Show market analysis"\n' +
            '• **Performance Reports** - "Show performance report"\n' +
            '• **Content Strategy** - "Generate content plan"\n' +
            '• **Campaign Control** - "Enable campaign"\n' +
            '• **Platform Optimization** - "Optimize YouTube"\n' +
            '• **World Domination** - "Execute world domination"\n\n' +
            'Type "help" for all commands, or ask me anything!'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
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
      const response = await enhanced_api.post('/admin/social-marketing/agent-chat', { 
        message: input 
      });
      
      if (response.data.success) {
        setMessages(prev => [...prev, { 
          sender: 'agent', 
          text: response.data.data.reply 
        }]);
      } else {
        setMessages(prev => [...prev, { 
          sender: 'agent', 
          text: '⚠️ Error: Could not get response from agent.' 
        }]);
      }
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, { 
        sender: 'agent', 
        text: '⚠️ Error: Could not reach the AI Marketing Director. Please try again.' 
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
    // Convert markdown-style formatting to HTML
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br>')
      .replace(/•/g, '• ');
  };

  return (
    <div className="bg-white rounded-lg shadow-lg border border-gray-200 mb-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-4 rounded-t-lg">
        <div className="flex items-center space-x-3">
          <div className="bg-white/20 p-2 rounded-full">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-semibold">AI Marketing Director</h3>
            <p className="text-sm text-purple-100">Strategic marketing intelligence & automation</p>
          </div>
          <div className="ml-auto flex space-x-2">
            <div className="bg-white/20 px-2 py-1 rounded text-xs flex items-center">
              <Sparkles className="w-3 h-3 mr-1" />
              AI-Powered
            </div>
            <div className="bg-white/20 px-2 py-1 rounded text-xs flex items-center">
              <Globe className="w-3 h-3 mr-1" />
              Global
            </div>
          </div>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="h-80 overflow-y-auto p-4 bg-gray-50">
        {messages.map((msg, idx) => (
          <div key={idx} className={`mb-4 flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
              msg.sender === 'user' 
                ? 'bg-purple-600 text-white' 
                : 'bg-white border border-gray-200 text-gray-800'
            }`}>
              <div className="flex items-start space-x-2">
                {msg.sender === 'agent' && (
                  <Bot className="w-4 h-4 text-purple-600 mt-0.5 flex-shrink-0" />
                )}
                <div 
                  className="text-sm leading-relaxed"
                  dangerouslySetInnerHTML={{ __html: formatMessage(msg.text) }}
                />
                {msg.sender === 'user' && (
                  <User className="w-4 h-4 text-purple-200 mt-0.5 flex-shrink-0" />
                )}
              </div>
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="flex justify-start mb-4">
            <div className="bg-white border border-gray-200 text-gray-800 px-4 py-3 rounded-lg">
              <div className="flex items-center space-x-2">
                <Bot className="w-4 h-4 text-purple-600" />
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={chatEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex items-end space-x-3">
          <div className="flex-1">
            <textarea
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              rows={2}
              placeholder="Give instructions to the AI Marketing Director... (e.g., 'Show market analysis', 'Generate content plan')"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
            />
          </div>
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
          >
            <Send className="w-4 h-4" />
            <span className="hidden sm:inline">Send</span>
          </button>
        </div>
        
        {/* Quick Commands */}
        <div className="mt-3 flex flex-wrap gap-2">
          {[
            { text: 'Market Analysis', icon: TrendingUp },
            { text: 'Performance Report', icon: Target },
            { text: 'Generate Content', icon: Sparkles },
            { text: 'Enable Campaign', icon: Globe }
          ].map((cmd, idx) => (
            <button
              key={idx}
              onClick={() => setInput(cmd.text)}
              className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 px-2 py-1 rounded flex items-center space-x-1 transition-colors"
            >
              <cmd.icon className="w-3 h-3" />
              <span>{cmd.text}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default MarketingAgentChat; 