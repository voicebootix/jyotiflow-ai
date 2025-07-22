import React, { useState, useEffect } from 'react';
import { 
  Upload, Eye, Download, Settings, Wand2, CheckCircle, 
  AlertTriangle, Play, Pause, RotateCcw, Save, Star 
} from 'lucide-react';
import enhanced_api from '../../services/enhanced-api';

const SwamjiAvatarPreview = () => {
  const [uploadedImage, setUploadedImage] = useState(null);
  const [avatarPreviews, setAvatarPreviews] = useState({});
  const [selectedStyle, setSelectedStyle] = useState('traditional');
  const [isGenerating, setIsGenerating] = useState(false);
  const [approvedConfig, setApprovedConfig] = useState(null);
  const [currentSample, setCurrentSample] = useState(null);

  const avatarStyles = {
    traditional: {
      name: 'Traditional Spiritual',
      background: '#8B4513',
      description: 'Classic spiritual robes with warm brown background',
      icon: '🕉️',
      voiceTone: 'wise'
    },
    modern: {
      name: 'Modern Spiritual',
      background: '#2F4F4F',
      description: 'Contemporary spiritual attire with elegant gray background',
      icon: '✨',
      voiceTone: 'compassionate'
    },
    festival: {
      name: 'Festival Celebration',
      background: '#FF6347',
      description: 'Festive attire with vibrant celebration background',
      icon: '🎉',
      voiceTone: 'joyful'
    },
    meditation: {
      name: 'Meditation Master',
      background: '#4682B4',
      description: 'Serene meditation robes with peaceful blue background',
      icon: '🧘‍♂️',
      voiceTone: 'gentle'
    }
  };

  useEffect(() => {
    fetchCurrentConfiguration();
  }, []);

  const fetchCurrentConfiguration = async () => {
    try {
      const response = await enhanced_api.get('/api/admin/social-marketing/swamiji-avatar-config');
      if (response.data.success) {
        setApprovedConfig(response.data.data);
        if (response.data.data.image_url) {
          setUploadedImage(response.data.data.image_url);
        }
      }
    } catch (error) {
      console.error('Error fetching avatar config:', error);
    }
  };

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('swamiji_image', file);

    try {
      // Use the dedicated upload function
      const response = await enhanced_api.uploadSwamjiImage(formData);
      
      // REFRESH.MD: Check nested properties safely to avoid runtime errors
      if (response && response.success && response.data?.image_url) {
        setUploadedImage(response.data.image_url);
        alert('✅ Swamiji photo uploaded successfully!');
      } else {
        // Provide more specific feedback
        const errorMessage = response?.message || 'Unknown error occurred';
        console.error('Error uploading image:', errorMessage);
        alert(`❌ Failed to upload image: ${errorMessage}`);
      }
    } catch (error) {
      console.error('Error uploading image:', error);
      alert('❌ Failed to upload image');
    }
  };

  const generatePreviewSample = async (style) => {
    if (!uploadedImage) {
      alert('Please upload Swamiji\'s photo first');
      return;
    }

    try {
      setIsGenerating(true);
      const response = await enhanced_api.post('/api/admin/social-marketing/generate-avatar-preview', {
        style: style,
        sample_text: "Namaste, beloved souls. Welcome to this divine spiritual guidance. May peace and wisdom be with you always. Om Namah Shivaya."
      });

      if (response.data.success) {
        setAvatarPreviews(prev => ({
          ...prev,
          [style]: response.data.preview
        }));
        setCurrentSample(response.data.preview);
        alert('✅ Preview generated successfully!');
      }
    } catch (error) {
      console.error('Error generating preview:', error);
      alert('❌ Failed to generate preview');
    } finally {
      setIsGenerating(false);
    }
  };

  const generateAllPreviews = async () => {
    if (!uploadedImage) {
      alert('Please upload Swamiji\'s photo first');
      return;
    }

    setIsGenerating(true);
    
    for (const style of Object.keys(avatarStyles)) {
      await generatePreviewSample(style);
      // Small delay between generations
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
    
    setIsGenerating(false);
  };

  const approveConfiguration = async () => {
    if (!uploadedImage || Object.keys(avatarPreviews).length === 0) {
      alert('Please upload photo and generate previews first');
      return;
    }

    try {
      const response = await enhanced_api.post('/api/admin/social-marketing/approve-swamiji-avatar', {
        image_url: uploadedImage,
        previews: avatarPreviews,
        approved_styles: Object.keys(avatarPreviews),
        default_style: selectedStyle
      });

      if (response.data.success) {
        setApprovedConfig(response.data.configuration);
        alert('✅ Swamiji avatar configuration approved! All future content will use this appearance.');
      }
    } catch (error) {
      console.error('Error approving configuration:', error);
      alert('❌ Failed to approve configuration');
    }
  };

  const downloadPreview = (style) => {
    const preview = avatarPreviews[style];
    if (preview?.video_url) {
      window.open(preview.video_url, '_blank');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold mb-2">🎭 Swamiji Avatar Configuration</h2>
            <p className="text-purple-100">
              Upload Swamiji's photo and preview how he'll appear in all social media content
            </p>
          </div>
          <div className="text-right">
            {approvedConfig ? (
              <div className="flex items-center text-green-300">
                <CheckCircle className="mr-2" size={20} />
                <span>Avatar Approved</span>
              </div>
            ) : (
              <div className="flex items-center text-yellow-300">
                <AlertTriangle className="mr-2" size={20} />
                <span>Awaiting Approval</span>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Panel - Upload & Configuration */}
        <div className="space-y-6">
          {/* Image Upload */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <Upload className="mr-2" size={20} />
              Upload Swamiji's Photo
            </h3>
            
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              {uploadedImage ? (
                <div className="space-y-4">
                  <img 
                    src={uploadedImage} 
                    alt="Swamiji" 
                    className="mx-auto h-32 w-32 object-cover rounded-full border-4 border-purple-500"
                  />
                  <p className="text-green-600 font-medium">✅ Swamiji's photo uploaded</p>
                  <label className="inline-flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg cursor-pointer hover:bg-purple-700">
                    <Upload size={16} className="mr-2" />
                    Change Photo
                    <input type="file" className="hidden" accept="image/*" onChange={handleImageUpload} />
                  </label>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="mx-auto h-20 w-20 rounded-full bg-gray-200 flex items-center justify-center">
                    <Upload size={24} className="text-gray-400" />
                  </div>
                  <p className="text-gray-600">Upload a clear, front-facing photo of Swamiji</p>
                  <label className="inline-flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg cursor-pointer hover:bg-purple-700">
                    <Upload size={16} className="mr-2" />
                    Upload Photo
                    <input type="file" className="hidden" accept="image/*" onChange={handleImageUpload} />
                  </label>
                </div>
              )}
            </div>

            <div className="mt-4 p-4 bg-blue-50 rounded-lg">
              <h4 className="font-medium text-blue-900 mb-2">📸 Photo Guidelines:</h4>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• Clear, high-resolution image (minimum 512x512px)</li>
                <li>• Front-facing, well-lit photo</li>
                <li>• Neutral expression for best results</li>
                <li>• Traditional spiritual attire preferred</li>
              </ul>
            </div>
          </div>

          {/* Preview Generation */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <Wand2 className="mr-2" size={20} />
              Generate Avatar Previews
            </h3>
            
            <div className="space-y-4">
              <div className="flex space-x-3">
                <button
                  onClick={() => generatePreviewSample(selectedStyle)}
                  disabled={!uploadedImage || isGenerating}
                  className="flex-1 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center justify-center space-x-2"
                >
                  <Wand2 size={16} />
                  <span>Generate Selected Style</span>
                </button>
                <button
                  onClick={generateAllPreviews}
                  disabled={!uploadedImage || isGenerating}
                  className="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center justify-center space-x-2"
                >
                  <Star size={16} />
                  <span>Generate All Styles</span>
                </button>
              </div>

              {isGenerating && (
                <div className="text-center py-4">
                  <div className="animate-spin mx-auto h-8 w-8 border-4 border-purple-500 border-t-transparent rounded-full"></div>
                  <p className="mt-2 text-gray-600">Generating Swamiji avatar preview...</p>
                </div>
              )}

              <div className="p-4 bg-yellow-50 rounded-lg">
                <p className="text-sm text-yellow-800">
                  💰 Cost: ~$1-2 per preview generation. Generate samples to see how Swamiji will appear before approving.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Panel - Style Selection & Previews */}
        <div className="space-y-6">
          {/* Style Selection */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">🎨 Avatar Styles</h3>
            
            <div className="grid grid-cols-2 gap-3">
              {Object.entries(avatarStyles).map(([key, style]) => (
                <button
                  key={key}
                  onClick={() => setSelectedStyle(key)}
                  className={`p-4 rounded-lg border-2 text-left transition-all ${
                    selectedStyle === key 
                      ? 'border-purple-500 bg-purple-50' 
                      : 'border-gray-200 hover:border-purple-300'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-2xl">{style.icon}</span>
                    <div 
                      className="w-6 h-6 rounded-full border-2 border-white shadow"
                      style={{ backgroundColor: style.background }}
                    ></div>
                  </div>
                  <h4 className="font-medium text-gray-900">{style.name}</h4>
                  <p className="text-xs text-gray-600 mt-1">{style.description}</p>
                  {avatarPreviews[key] && (
                    <div className="mt-2 flex items-center text-green-600 text-xs">
                      <CheckCircle size={12} className="mr-1" />
                      Preview Ready
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Preview Display */}
          {currentSample && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <Eye className="mr-2" size={20} />
                Avatar Preview
              </h3>
              
              <div className="space-y-4">
                <div className="bg-gray-100 rounded-lg p-4 text-center">
                  <video 
                    src={currentSample.video_url}
                    controls
                    className="mx-auto max-w-full h-64 rounded-lg"
                    poster={currentSample.thumbnail_url}
                  >
                    Your browser does not support video playback.
                  </video>
                </div>
                
                <div className="flex justify-between items-center">
                  <div className="text-sm text-gray-600">
                    <p>Duration: {currentSample.duration || '~30s'}</p>
                    <p>Quality: {currentSample.quality || 'High'}</p>
                  </div>
                  <button
                    onClick={() => downloadPreview(selectedStyle)}
                    className="flex items-center px-3 py-2 text-purple-600 hover:bg-purple-50 rounded-lg"
                  >
                    <Download size={16} className="mr-2" />
                    Download
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Approval Section */}
          {Object.keys(avatarPreviews).length > 0 && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-green-900 mb-4 flex items-center">
                <CheckCircle className="mr-2" size={20} />
                Approve Avatar Configuration
              </h3>
              
              <div className="space-y-4">
                <p className="text-green-800">
                  You have generated {Object.keys(avatarPreviews).length} avatar style(s). 
                  Once approved, this appearance will be used for ALL social media content.
                </p>
                
                <div className="flex items-center justify-between">
                  <div className="text-sm text-green-700">
                    <p>✅ Previews generated: {Object.keys(avatarPreviews).length}/4</p>
                    <p>✅ Default style: {avatarStyles[selectedStyle].name}</p>
                  </div>
                  <button
                    onClick={approveConfiguration}
                    disabled={approvedConfig !== null}
                    className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center space-x-2"
                  >
                    <Save size={16} />
                    <span>{approvedConfig ? 'Approved' : 'Approve & Save'}</span>
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Status Summary */}
      {approvedConfig && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-green-900 mb-4">✅ Avatar Configuration Active</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl mb-2">🎭</div>
              <div className="font-medium">Avatar Ready</div>
              <div className="text-sm text-gray-600">Swamiji appearance configured</div>
            </div>
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl mb-2">🚀</div>
              <div className="font-medium">Auto-Generation Active</div>
              <div className="text-sm text-gray-600">Content will use approved avatar</div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-2xl mb-2">🎯</div>
              <div className="font-medium">Consistent Branding</div>
              <div className="text-sm text-gray-600">Same appearance across all platforms</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SwamjiAvatarPreview;