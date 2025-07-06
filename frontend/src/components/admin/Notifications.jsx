import React, { useState } from 'react';
import spiritualAPI from '../../lib/api';
import Loader from '../ui/Loader.jsx';

const channelOptions = [
  { value: 'email', label: 'Email' },
  { value: 'sms', label: 'SMS' },
  { value: 'whatsapp', label: 'WhatsApp' },
  { value: 'push', label: 'Push Notification' },
];

export default function Notifications() {
  const [channel, setChannel] = useState('email');
  const [to, setTo] = useState('');
  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');
  const [deviceToken, setDeviceToken] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    const payload = { channel, to, subject, message };
    if (channel === 'push') payload.device_token = deviceToken;
    const res = await spiritualAPI.sendFollowupNotification(payload);
    setResult(res);
    setLoading(false);
  };

  const inputStyle = {
    width: '100%',
    padding: '8px 12px',
    borderRadius: '4px',
    border: '1px solid #ccc',
    fontSize: '14px',
    marginBottom: '12px'
  };

  return (
    <div style={{ maxWidth: 500, margin: '0 auto' }}>
      <h3>Send Follow-up / Reminder</h3>
      <form onSubmit={handleSubmit}>
        <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>Channel</label>
        <select value={channel} onChange={e => setChannel(e.target.value)} style={{ ...inputStyle }}>
          {channelOptions.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
        <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>
          {channel === 'email' ? 'Email' : channel === 'push' ? 'User Device Token' : 'Phone Number'}
        </label>
        <input 
          type="text"
          value={to} 
          onChange={e => setTo(e.target.value)} 
          required 
          placeholder={channel === 'email' ? 'user@email.com' : '+1234567890'}
          style={inputStyle}
        />
        {channel === 'push' && (
          <>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>Device Token</label>
            <input 
              type="text"
              value={deviceToken} 
              onChange={e => setDeviceToken(e.target.value)} 
              required 
              placeholder="Push device token"
              style={inputStyle}
            />
          </>
        )}
        {channel === 'email' || channel === 'push' ? (
          <>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>Subject</label>
            <input 
              type="text"
              value={subject} 
              onChange={e => setSubject(e.target.value)} 
              required
              style={inputStyle}
            />
          </>
        ) : null}
        <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>Message</label>
        <textarea 
          value={message} 
          onChange={e => setMessage(e.target.value)} 
          required 
          rows={4} 
          style={{ ...inputStyle, resize: 'vertical' }} 
        />
        <button 
          type="submit" 
          disabled={loading} 
          style={{ 
            marginTop: 16, 
            padding: '10px 20px', 
            backgroundColor: '#6366f1', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px', 
            cursor: loading ? 'not-allowed' : 'pointer',
            fontSize: '14px',
            fontWeight: '500'
          }}
        >
          {loading ? <Loader size={18} /> : 'Send Notification'}
        </button>
      </form>
      {result && (
        <div style={{ marginTop: 16, color: result.success ? 'green' : 'red' }}>
          {result.message}
        </div>
      )}
    </div>
  );
} 