import React, { useState } from 'react';
import axios from 'axios';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Loader2, Star, Gift, Check } from "lucide-react";

const EnhancedRegistration = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    phone: '',
    birth_details: {
      date: '',
      time: '',
      location: '',
      timezone: 'Asia/Colombo'
    },
    spiritual_level: 'beginner',
    preferred_language: 'en'
  });

  const [registrationState, setRegistrationState] = useState({
    loading: false,
    success: false,
    error: null,
    welcomeProfile: null
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    if (name.startsWith('birth_')) {
      const fieldName = name.replace('birth_', '');
      setFormData(prev => ({
        ...prev,
        birth_details: {
          ...prev.birth_details,
          [fieldName]: value
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const handleSelectChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const validateForm = () => {
    const { name, email, password, confirmPassword, birth_details } = formData;
    
    if (!name || !email || !password || !confirmPassword) {
      return "Please fill in all required fields";
    }
    
    if (password !== confirmPassword) {
      return "Passwords do not match";
    }
    
    if (password.length < 8) {
      return "Password must be at least 8 characters";
    }
    
    if (!birth_details.date || !birth_details.time || !birth_details.location) {
      return "Please provide complete birth details for your chart";
    }
    
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const validationError = validateForm();
    if (validationError) {
      setRegistrationState(prev => ({
        ...prev,
        error: validationError
      }));
      return;
    }

    setRegistrationState(prev => ({
      ...prev,
      loading: true,
      error: null
    }));

    try {
      const response = await axios.post('/api/register', formData);
      
      setRegistrationState(prev => ({
        ...prev,
        loading: false,
        success: true,
        welcomeProfile: response.data.registration_welcome
      }));
      
    } catch (error) {
      setRegistrationState(prev => ({
        ...prev,
        loading: false,
        error: error.response?.data?.detail || 'Registration failed. Please try again.'
      }));
    }
  };

  const WelcomeProfile = ({ profile }) => {
    const { data_summary, reading_preview, value_proposition } = profile;
    
    return (
      <div className="space-y-6">
        <Card className="border-green-200 bg-green-50">
          <CardHeader>
            <CardTitle className="text-green-800 flex items-center gap-2">
              <Gift className="w-5 h-5" />
              வணக்கம்! Your Spiritual Journey Begins
            </CardTitle>
            <CardDescription className="text-green-700">
              Your personalized birth chart and AI reading by Swami Jyotirananthan are ready!
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-semibold mb-2">Your Astrological Profile</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Birth Nakshatra:</span>
                    <Badge variant="outline">{data_summary.nakshatra}</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span>Moon Sign:</span>
                    <Badge variant="outline">{data_summary.moon_sign}</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span>Sun Sign:</span>
                    <Badge variant="outline">{data_summary.sun_sign}</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span>Ascendant:</span>
                    <Badge variant="outline">{data_summary.ascendant}</Badge>
                  </div>
                </div>
              </div>
              
              <div>
                <h4 className="font-semibold mb-2">What You've Received</h4>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-green-600" />
                    <span className="text-sm">Complete Birth Chart</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-green-600" />
                    <span className="text-sm">AI Reading by Swamiji</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-green-600" />
                    <span className="text-sm">{data_summary.pdf_reports_count} Astrological Reports</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-green-600" />
                    <span className="text-sm">Spiritual Guidance</span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Star className="w-5 h-5 text-yellow-500" />
              Preview of Your Reading
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="p-4 bg-gray-50 rounded-lg">
                <h4 className="font-semibold mb-2">Swamiji's Introduction</h4>
                <p className="text-sm text-gray-700 italic">
                  {reading_preview.introduction}
                </p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <h4 className="font-semibold mb-2">Personality Insights</h4>
                  <ul className="text-sm space-y-1">
                    {reading_preview.personality_insights.map((insight, idx) => (
                      <li key={idx} className="text-gray-700">• {insight}</li>
                    ))}
                  </ul>
                </div>
                
                <div>
                  <h4 className="font-semibold mb-2">Spiritual Guidance</h4>
                  <ul className="text-sm space-y-1">
                    {reading_preview.spiritual_guidance.map((guidance, idx) => (
                      <li key={idx} className="text-gray-700">• {guidance}</li>
                    ))}
                  </ul>
                </div>
                
                <div>
                  <h4 className="font-semibold mb-2">Practical Advice</h4>
                  <ul className="text-sm space-y-1">
                    {reading_preview.practical_advice.map((advice, idx) => (
                      <li key={idx} className="text-gray-700">• {advice}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-blue-200 bg-blue-50">
          <CardHeader>
            <CardTitle className="text-blue-800">
              Value: {value_proposition.estimated_value} - FREE for you!
            </CardTitle>
            <CardDescription className="text-blue-700">
              Upgrade to premium for live spiritual guidance
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-semibold mb-2">What's Included (FREE)</h4>
                <ul className="text-sm space-y-1">
                  {value_proposition.includes.map((item, idx) => (
                    <li key={idx} className="flex items-center gap-2">
                      <Check className="w-4 h-4 text-green-600" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
              
              <div>
                <h4 className="font-semibold mb-2">Premium Benefits</h4>
                <ul className="text-sm space-y-1">
                  {value_proposition.upgrade_benefits.map((benefit, idx) => (
                    <li key={idx} className="flex items-center gap-2">
                      <Star className="w-4 h-4 text-yellow-500" />
                      {benefit}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
            
            <div className="mt-4 flex gap-2">
              <Button variant="outline" onClick={() => window.location.href = '/profile'}>
                View Full Profile
              </Button>
              <Button>
                Upgrade to Premium
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  };

  if (registrationState.success) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <WelcomeProfile profile={registrationState.welcomeProfile} />
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <Card>
        <CardHeader>
          <CardTitle>Join JyotiFlow - Get Your FREE Birth Chart & AI Reading</CardTitle>
          <CardDescription>
            Sign up and receive your complete Vedic birth chart with personalized AI reading by Swami Jyotirananthan (Worth $60-105)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Personal Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="name">Full Name *</Label>
                <Input
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div>
                <Label htmlFor="email">Email *</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="password">Password *</Label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div>
                <Label htmlFor="confirmPassword">Confirm Password *</Label>
                <Input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  required
                />
              </div>
            </div>

            <div>
              <Label htmlFor="phone">Phone (Optional)</Label>
              <Input
                id="phone"
                name="phone"
                value={formData.phone}
                onChange={handleInputChange}
              />
            </div>

            {/* Birth Details for Chart Generation */}
            <div className="border-t pt-4">
              <h3 className="text-lg font-semibold mb-3">Birth Details (Required for Chart)</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="birth_date">Birth Date *</Label>
                  <Input
                    id="birth_date"
                    name="birth_date"
                    type="date"
                    value={formData.birth_details.date}
                    onChange={handleInputChange}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="birth_time">Birth Time *</Label>
                  <Input
                    id="birth_time"
                    name="birth_time"
                    type="time"
                    value={formData.birth_details.time}
                    onChange={handleInputChange}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="birth_location">Birth Location *</Label>
                  <Input
                    id="birth_location"
                    name="birth_location"
                    placeholder="City, Country"
                    value={formData.birth_details.location}
                    onChange={handleInputChange}
                    required
                  />
                </div>
              </div>
            </div>

            {/* Preferences */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="spiritual_level">Spiritual Level</Label>
                <Select onValueChange={(value) => handleSelectChange('spiritual_level', value)} defaultValue="beginner">
                  <SelectTrigger>
                    <SelectValue placeholder="Select level" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="beginner">Beginner</SelectItem>
                    <SelectItem value="intermediate">Intermediate</SelectItem>
                    <SelectItem value="advanced">Advanced</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="preferred_language">Preferred Language</Label>
                <Select onValueChange={(value) => handleSelectChange('preferred_language', value)} defaultValue="en">
                  <SelectTrigger>
                    <SelectValue placeholder="Select language" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="en">English</SelectItem>
                    <SelectItem value="ta">Tamil</SelectItem>
                    <SelectItem value="hi">Hindi</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {registrationState.error && (
              <Alert className="border-red-200 bg-red-50">
                <AlertDescription className="text-red-700">
                  {registrationState.error}
                </AlertDescription>
              </Alert>
            )}

            <Button 
              type="submit" 
              className="w-full"
              disabled={registrationState.loading}
            >
              {registrationState.loading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Creating Your Account & Birth Chart...
                </>
              ) : (
                'Create Account & Get FREE Birth Chart'
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Compelling Hook Line */}
      <Card className="mt-6 bg-gradient-to-r from-orange-50 to-yellow-50 border-orange-200">
        <CardContent className="text-center py-6">
          <div className="flex flex-col items-center space-y-3">
            <div className="flex items-center gap-2 text-orange-800">
              <Star className="w-6 h-6 text-yellow-500" />
              <h3 className="text-xl font-bold">Get Your Complete Spiritual Report & Personal Reading from Swami Jyotirananthan</h3>
              <Star className="w-6 h-6 text-yellow-500" />
            </div>
            
            <p className="text-lg text-orange-700 font-semibold">
              Just Sign Up and You Get That FREE! 
            </p>
            
            <div className="flex flex-wrap justify-center gap-4 text-sm text-orange-600 mt-2">
              <div className="flex items-center gap-1">
                <Check className="w-4 h-4 text-green-600" />
                <span>Complete Vedic Birth Chart</span>
              </div>
              <div className="flex items-center gap-1">
                <Check className="w-4 h-4 text-green-600" />
                <span>Personal AI Reading by Swamiji</span>
              </div>
              <div className="flex items-center gap-1">
                <Check className="w-4 h-4 text-green-600" />
                <span>Spiritual Guidance & Remedies</span>
              </div>
              <div className="flex items-center gap-1">
                <Check className="w-4 h-4 text-green-600" />
                <span>Worth $60-105 USD</span>
              </div>
            </div>
            
            <Badge className="bg-orange-100 text-orange-800 text-base px-4 py-2 font-bold">
              🎁 100% FREE - No Credit Card Required
            </Badge>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default EnhancedRegistration;