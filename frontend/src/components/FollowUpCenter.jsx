import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Alert, AlertDescription } from './ui/alert';
import Loader from './ui/Loader';
import { Calendar, Clock, Mail, MessageSquare, Smartphone, Bell } from 'lucide-react';
import spiritualAPI from '../lib/api';

const FollowUpCenter = () => {
  const [followups, setFollowups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    loadFollowups();
  }, []);

  const loadFollowups = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await spiritualAPI.get('/api/followup/my-followups');
      if (response.success) {
        setFollowups(response.data || []);
      } else {
        setError(response.message || 'Failed to load follow-ups');
      }
    } catch (err) {
      setError('Failed to load follow-ups: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCancelFollowup = async (followupId) => {
    try {
      const response = await spiritualAPI.post(`/api/followup/cancel/${followupId}`);
      if (response.success) {
        setSuccess('Follow-up cancelled successfully!');
        loadFollowups(); // Reload the list
      } else {
        setError(response.message || 'Failed to cancel follow-up');
      }
    } catch (err) {
      setError('Failed to cancel follow-up: ' + err.message);
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      pending: { color: 'bg-yellow-100 text-yellow-800', label: 'Scheduled' },
      sent: { color: 'bg-blue-100 text-blue-800', label: 'Sent' },
      delivered: { color: 'bg-green-100 text-green-800', label: 'Delivered' },
      read: { color: 'bg-purple-100 text-purple-800', label: 'Read' },
      failed: { color: 'bg-red-100 text-red-800', label: 'Failed' },
      cancelled: { color: 'bg-gray-100 text-gray-800', label: 'Cancelled' }
    };
    
    const config = statusConfig[status] || statusConfig.pending;
    return (
      <Badge className={config.color}>
        {config.label}
      </Badge>
    );
  };

  const getChannelIcon = (channel) => {
    const icons = {
      email: <Mail size={16} />,
      sms: <Smartphone size={16} />,
      whatsapp: <MessageSquare size={16} />,
      push: <Bell size={16} />,
      in_app: <Smartphone size={16} />
    };
    return icons[channel] || <Mail size={16} />;
  };

  const getChannelLabel = (channel) => {
    const labels = {
      email: 'Email',
      sms: 'SMS',
      whatsapp: 'WhatsApp',
      push: 'Push Notification',
      in_app: 'In-App'
    };
    return labels[channel] || 'Email';
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) return <Loader />;

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <div className="text-center space-y-4">
        <div className="text-4xl">🕉️</div>
        <h1 className="text-3xl font-bold text-gray-900">Follow-up Center</h1>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Stay connected with your spiritual journey through personalized follow-ups. 
          View your scheduled messages and manage your spiritual guidance preferences.
        </p>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert>
          <AlertDescription>{success}</AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Calendar className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Total Follow-ups</p>
                <p className="text-2xl font-bold text-gray-900">{followups.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <Clock className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Scheduled</p>
                <p className="text-2xl font-bold text-gray-900">
                  {followups.filter(f => f.status === 'pending').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Mail className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Delivered</p>
                <p className="text-2xl font-bold text-gray-900">
                  {followups.filter(f => f.status === 'delivered' || f.status === 'read').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <span>Your Follow-ups</span>
            <Badge variant="outline">{followups.length}</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {followups.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">📭</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Follow-ups Yet</h3>
              <p className="text-gray-600 mb-6">
                You don't have any scheduled follow-ups at the moment. 
                Follow-ups are automatically scheduled after your spiritual sessions.
              </p>
              <Button onClick={() => window.history.back()}>
                Back to Sessions
              </Button>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Template</TableHead>
                  <TableHead>Channel</TableHead>
                  <TableHead>Scheduled For</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Credits</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {followups.map((followup) => (
                  <TableRow key={followup.id}>
                    <TableCell>
                      <div>
                        <div className="font-medium">{followup.template_name}</div>
                        {followup.template_tamil_name && (
                          <div className="text-sm text-gray-500">{followup.template_tamil_name}</div>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        {getChannelIcon(followup.channel)}
                        <span className="text-sm">{getChannelLabel(followup.channel)}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">
                        {formatDate(followup.scheduled_at)}
                      </div>
                    </TableCell>
                    <TableCell>
                      {getStatusBadge(followup.status)}
                    </TableCell>
                    <TableCell>
                      <span className="text-sm font-medium">{followup.credits_charged}</span>
                    </TableCell>
                    <TableCell>
                      {followup.status === 'pending' && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleCancelFollowup(followup.id)}
                          className="text-red-600 hover:text-red-700"
                        >
                          Cancel
                        </Button>
                      )}
                      {followup.status === 'sent' && (
                        <Badge variant="outline" className="text-green-600">
                          Sent
                        </Badge>
                      )}
                      {followup.status === 'delivered' && (
                        <Badge variant="outline" className="text-blue-600">
                          Delivered
                        </Badge>
                      )}
                      {followup.status === 'read' && (
                        <Badge variant="outline" className="text-purple-600">
                          Read
                        </Badge>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>About Follow-ups</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">🕉️ Spiritual Guidance</h4>
              <p className="text-sm text-gray-600">
                Follow-ups help you stay connected with your spiritual journey by providing 
                personalized guidance, reminders, and support after your sessions.
              </p>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2">💳 Credit System</h4>
              <p className="text-sm text-gray-600">
                Each follow-up message costs a small amount of credits. This helps maintain 
                the quality of our spiritual guidance services.
              </p>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2">📱 Multiple Channels</h4>
              <p className="text-sm text-gray-600">
                Receive follow-ups via email, SMS, WhatsApp, or push notifications. 
                Choose your preferred communication method.
              </p>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2">⚡ Automatic Scheduling</h4>
              <p className="text-sm text-gray-600">
                Follow-ups are automatically scheduled after your spiritual sessions 
                to ensure continuous guidance and support.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default FollowUpCenter; 