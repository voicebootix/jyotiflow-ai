import React, { useState } from 'react';
import spiritualAPI from '../../lib/api';
import Input from '../ui/input.jsx';
import { Label } from '../ui/label.jsx';
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
  const [subject, setSubject] = useState('JyotiFlow.ai Notification');
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

  return (
    <div style={{ maxWidth: 500, margin: '0 auto' }}>
      <h3>Send Follow-up / Reminder</h3>
      <form onSubmit={handleSubmit}>
        <Label>Channel</Label>
        <select value={channel} onChange={e => setChannel(e.target.value)} style={{ width: '100%', marginBottom: 12 }}>
          {channelOptions.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
        <Label>{channel === 'email' ? 'Email' : channel === 'push' ? 'User Device Token' : 'Phone Number'}</Label>
        <Input value={to} onChange={e => setTo(e.target.value)} required placeholder={channel === 'email' ? 'user@email.com' : '+1234567890'} />
        {channel === 'push' && (
          <>
            <Label>Device Token</Label>
            <Input value={deviceToken} onChange={e => setDeviceToken(e.target.value)} required placeholder="Push device token" />
          </>
        )}
        {channel === 'email' || channel === 'push' ? (
          <>
            <Label>Subject</Label>
            <Input value={subject} onChange={e => setSubject(e.target.value)} required />
          </>
        ) : null}
        <Label>Message</Label>
        <textarea value={message} onChange={e => setMessage(e.target.value)} required rows={4} style={{ width: '100%' }} />
        <button type="submit" disabled={loading} style={{ marginTop: 16 }}>
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