import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Badge } from '../ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../ui/dialog';
import { Switch } from '../ui/switch';
import { Alert, AlertDescription } from '../ui/alert';
import { Loader } from '../ui/Loader';
import spiritualAPI from '../../lib/api';

const FollowUpManagement = () => {
  const [activeTab, setActiveTab] = useState('templates');
  const [templates, setTemplates] = useState([]);
  const [schedules, setSchedules] = useState([]);
  const [analytics, setAnalytics] = useState({});
  const [settings, setSettings] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Template form state
  const [templateForm, setTemplateForm] = useState({
    name: '',
    tamil_name: '',
    description: '',
    template_type: 'session_followup',
    channel: 'email',
    subject: '',
    content: '',
    tamil_content: '',
    credits_cost: 5,
    is_active: true
  });
  
  // Settings form state
  const [settingsForm, setSettingsForm] = useState({
    auto_followup_enabled: true,
    default_credits_cost: 5,
    max_followups_per_session: 3,
    min_interval_hours: 24,
    max_interval_days: 30,
    enable_credit_charging: true
  });

  useEffect(() => {
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    setLoading(true);
    setError('');
    try {
      switch (activeTab) {
        case 'templates':
          const templatesData = await spiritualAPI.get('/api/followup/admin/templates');
          if (templatesData.success) {
            setTemplates(templatesData.data || []);
          }
          break;
        case 'schedules':
          const schedulesData = await spiritualAPI.get('/api/followup/admin/schedules');
          if (schedulesData.success) {
            setSchedules(schedulesData.data || []);
          }
          break;
        case 'analytics':
          const analyticsData = await spiritualAPI.get('/api/followup/admin/analytics');
          if (analyticsData.success) {
            setAnalytics(analyticsData.data || {});
          }
          break;
        case 'settings':
          const settingsData = await spiritualAPI.get('/api/followup/admin/settings');
          if (settingsData.success) {
            setSettings(settingsData.data || {});
            setSettingsForm(settingsData.data || {});
          }
          break;
      }
    } catch (err) {
      setError('Failed to load data: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTemplate = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await spiritualAPI.post('/api/followup/admin/templates', templateForm);
      if (response.success) {
        setSuccess('Template created successfully!');
        setTemplateForm({
          name: '',
          tamil_name: '',
          description: '',
          template_type: 'session_followup',
          channel: 'email',
          subject: '',
          content: '',
          tamil_content: '',
          credits_cost: 5,
          is_active: true
        });
        loadData();
      } else {
        setError(response.message || 'Failed to create template');
      }
    } catch (err) {
      setError('Failed to create template: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateSettings = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await spiritualAPI.request('/api/followup/admin/settings', {
        method: 'PUT',
        body: JSON.stringify(settingsForm)
      });
      if (response.success) {
        setSuccess('Settings updated successfully!');
        setSettings(settingsForm);
      } else {
        setError(response.message || 'Failed to update settings');
      }
    } catch (err) {
      setError('Failed to update settings: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusColors = {
      pending: 'bg-yellow-100 text-yellow-800',
      sent: 'bg-blue-100 text-blue-800',
      delivered: 'bg-green-100 text-green-800',
      read: 'bg-purple-100 text-purple-800',
      failed: 'bg-red-100 text-red-800',
      cancelled: 'bg-gray-100 text-gray-800'
    };
    return (
      <Badge className={statusColors[status] || 'bg-gray-100 text-gray-800'}>
        {status}
      </Badge>
    );
  };

  const getChannelIcon = (channel) => {
    const icons = {
      email: '📧',
      sms: '📱',
      whatsapp: '💬',
      push: '🔔',
      in_app: '📱'
    };
    return icons[channel] || '📧';
  };

  if (loading) return <Loader />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Follow-up System Management</h1>
        <Badge variant="outline" className="text-sm">
          Internal Follow-up System
        </Badge>
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

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="templates">Templates</TabsTrigger>
          <TabsTrigger value="schedules">Schedules</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        <TabsContent value="templates" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Follow-up Templates</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="name">Template Name</Label>
                    <Input
                      id="name"
                      value={templateForm.name}
                      onChange={(e) => setTemplateForm({...templateForm, name: e.target.value})}
                      placeholder="Session Follow-up 1"
                    />
                  </div>
                  <div>
                    <Label htmlFor="tamil_name">Tamil Name</Label>
                    <Input
                      id="tamil_name"
                      value={templateForm.tamil_name}
                      onChange={(e) => setTemplateForm({...templateForm, tamil_name: e.target.value})}
                      placeholder="அமர்வு பின்தொடர்தல் 1"
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="description">Description</Label>
                  <Input
                    id="description"
                    value={templateForm.description}
                    onChange={(e) => setTemplateForm({...templateForm, description: e.target.value})}
                    placeholder="First follow-up after spiritual session"
                  />
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <Label htmlFor="template_type">Template Type</Label>
                    <Select
                      value={templateForm.template_type}
                      onValueChange={(value) => setTemplateForm({...templateForm, template_type: value})}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="session_followup">Session Follow-up</SelectItem>
                        <SelectItem value="reminder">Reminder</SelectItem>
                        <SelectItem value="check_in">Check-in</SelectItem>
                        <SelectItem value="offer">Offer</SelectItem>
                        <SelectItem value="support">Support</SelectItem>
                        <SelectItem value="custom">Custom</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="channel">Channel</Label>
                    <Select
                      value={templateForm.channel}
                      onValueChange={(value) => setTemplateForm({...templateForm, channel: value})}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="email">Email</SelectItem>
                        <SelectItem value="sms">SMS</SelectItem>
                        <SelectItem value="whatsapp">WhatsApp</SelectItem>
                        <SelectItem value="push">Push Notification</SelectItem>
                        <SelectItem value="in_app">In-App</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="credits_cost">Credits Cost</Label>
                    <Input
                      id="credits_cost"
                      type="number"
                      value={templateForm.credits_cost}
                      onChange={(e) => setTemplateForm({...templateForm, credits_cost: parseInt(e.target.value)})}
                      min="0"
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="subject">Subject (Email)</Label>
                  <Input
                    id="subject"
                    value={templateForm.subject}
                    onChange={(e) => setTemplateForm({...templateForm, subject: e.target.value})}
                    placeholder="How is your spiritual journey progressing? 🕉️"
                  />
                </div>

                <div>
                  <Label htmlFor="content">Content (English)</Label>
                  <Textarea
                    id="content"
                    value={templateForm.content}
                    onChange={(e) => setTemplateForm({...templateForm, content: e.target.value})}
                    placeholder="Dear {{user_name}}, Thank you for your recent spiritual consultation..."
                    rows={6}
                  />
                </div>

                <div>
                  <Label htmlFor="tamil_content">Content (Tamil)</Label>
                  <Textarea
                    id="tamil_content"
                    value={templateForm.tamil_content}
                    onChange={(e) => setTemplateForm({...templateForm, tamil_content: e.target.value})}
                    placeholder="அன்புள்ள {{user_name}}, உங்கள் சமீபத்திய ஆன்மீக ஆலோசனைக்கு நன்றி..."
                    rows={6}
                  />
                </div>

                <div className="flex items-center space-x-2">
                  <Switch
                    id="is_active"
                    checked={templateForm.is_active}
                    onCheckedChange={(checked) => setTemplateForm({...templateForm, is_active: checked})}
                  />
                  <Label htmlFor="is_active">Active</Label>
                </div>

                <Button onClick={handleCreateTemplate} disabled={loading}>
                  {loading ? 'Creating...' : 'Create Template'}
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Existing Templates</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Channel</TableHead>
                    <TableHead>Credits</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {templates.map((template) => (
                    <TableRow key={template.id}>
                      <TableCell>
                        <div>
                          <div className="font-medium">{template.name}</div>
                          {template.tamil_name && (
                            <div className="text-sm text-gray-500">{template.tamil_name}</div>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">{template.template_type}</Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center space-x-2">
                          <span>{getChannelIcon(template.channel)}</span>
                          <span>{template.channel}</span>
                        </div>
                      </TableCell>
                      <TableCell>{template.credits_cost}</TableCell>
                      <TableCell>
                        <Badge variant={template.is_active ? "default" : "secondary"}>
                          {template.is_active ? 'Active' : 'Inactive'}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="schedules" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Follow-up Schedules</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>User</TableHead>
                    <TableHead>Template</TableHead>
                    <TableHead>Channel</TableHead>
                    <TableHead>Scheduled</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Credits</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {schedules.map((schedule) => (
                    <TableRow key={schedule.id}>
                      <TableCell>
                        <div>
                          <div className="font-medium">{schedule.user_name || schedule.user_email}</div>
                          <div className="text-sm text-gray-500">{schedule.user_email}</div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <div className="font-medium">{schedule.template_name}</div>
                          {schedule.template_tamil_name && (
                            <div className="text-sm text-gray-500">{schedule.template_tamil_name}</div>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center space-x-2">
                          <span>{getChannelIcon(schedule.channel)}</span>
                          <span>{schedule.channel}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        {new Date(schedule.scheduled_at).toLocaleString()}
                      </TableCell>
                      <TableCell>
                        {getStatusBadge(schedule.status)}
                      </TableCell>
                      <TableCell>{schedule.credits_charged}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Delivery Statistics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span>Total Sent:</span>
                    <span className="font-bold">{analytics.total_sent || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Total Delivered:</span>
                    <span className="font-bold text-green-600">{analytics.total_delivered || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Total Read:</span>
                    <span className="font-bold text-blue-600">{analytics.total_read || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Total Failed:</span>
                    <span className="font-bold text-red-600">{analytics.total_failed || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Delivery Rate:</span>
                    <span className="font-bold">{(analytics.delivery_rate || 0).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Read Rate:</span>
                    <span className="font-bold">{(analytics.read_rate || 0).toFixed(1)}%</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Revenue & Credits</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span>Total Credits Charged:</span>
                    <span className="font-bold">{analytics.total_credits_charged || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Revenue Generated:</span>
                    <span className="font-bold text-green-600">${(analytics.total_revenue || 0).toFixed(2)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Top Templates</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Template</TableHead>
                    <TableHead>Total Sent</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {(analytics.top_templates || []).map((template, index) => (
                    <TableRow key={index}>
                      <TableCell>
                        <div>
                          <div className="font-medium">{template.name}</div>
                          {template.tamil_name && (
                            <div className="text-sm text-gray-500">{template.tamil_name}</div>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>{template.total_sent}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Follow-up System Settings</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="auto_followup">Auto Follow-up Enabled</Label>
                    <p className="text-sm text-gray-500">Automatically schedule follow-ups after sessions</p>
                  </div>
                  <Switch
                    id="auto_followup"
                    checked={settingsForm.auto_followup_enabled}
                    onCheckedChange={(checked) => setSettingsForm({...settingsForm, auto_followup_enabled: checked})}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="credit_charging">Credit Charging Enabled</Label>
                    <p className="text-sm text-gray-500">Charge credits for follow-up messages</p>
                  </div>
                  <Switch
                    id="credit_charging"
                    checked={settingsForm.enable_credit_charging}
                    onCheckedChange={(checked) => setSettingsForm({...settingsForm, enable_credit_charging: checked})}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="default_credits">Default Credits Cost</Label>
                    <Input
                      id="default_credits"
                      type="number"
                      value={settingsForm.default_credits_cost}
                      onChange={(e) => setSettingsForm({...settingsForm, default_credits_cost: parseInt(e.target.value)})}
                      min="0"
                    />
                  </div>

                  <div>
                    <Label htmlFor="max_followups">Max Follow-ups per Session</Label>
                    <Input
                      id="max_followups"
                      type="number"
                      value={settingsForm.max_followups_per_session}
                      onChange={(e) => setSettingsForm({...settingsForm, max_followups_per_session: parseInt(e.target.value)})}
                      min="1"
                      max="10"
                    />
                  </div>

                  <div>
                    <Label htmlFor="min_interval">Minimum Interval (Hours)</Label>
                    <Input
                      id="min_interval"
                      type="number"
                      value={settingsForm.min_interval_hours}
                      onChange={(e) => setSettingsForm({...settingsForm, min_interval_hours: parseInt(e.target.value)})}
                      min="1"
                    />
                  </div>

                  <div>
                    <Label htmlFor="max_interval">Maximum Interval (Days)</Label>
                    <Input
                      id="max_interval"
                      type="number"
                      value={settingsForm.max_interval_days}
                      onChange={(e) => setSettingsForm({...settingsForm, max_interval_days: parseInt(e.target.value)})}
                      min="1"
                    />
                  </div>
                </div>

                <Button onClick={handleUpdateSettings} disabled={loading}>
                  {loading ? 'Updating...' : 'Update Settings'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default FollowUpManagement; 