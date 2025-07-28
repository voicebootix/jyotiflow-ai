import React, { useState, useEffect } from 'react';
import { 
  Upload, Eye, Download, Settings, Wand2, CheckCircle, 
  AlertTriangle, Play, Pause, RotateCcw, Save, Star 
} from 'lucide-react';
import enhanced_api from '../../services/enhanced-api';
import { useNotification } from '../../hooks/useNotification';

const SwamjiAvatarPreview = () => {
  const [uploadedImage, setUploadedImage] = useState(null);
  // REFRESH.MD: Removed avatarPreviews and selectedStyle states as they are no longer needed.
  const [voices, setVoices] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [approvedConfig, setApprovedConfig] = useState(null);
  const [currentSample, setCurrentSample] = useState(null);
  const { addNotification } = useNotification();

  // REFRESH.MD: Removed the hardcoded avatarStyles object. The theme is now dynamic from the backend.

  useEffect(() => {
    fetchCurrentConfiguration();
  }, []);

  const fetchCurrentConfiguration = async () => {
    try {
      const response = await enhanced_api.getSwamjiAvatarConfig();
      if (response.success && response.data) {
        setApprovedConfig(response.data);
        if (response.data.image_url) {
            setUploadedImage(response.data.image_url);
        }
        if (response.data.voices && response.data.voices.length > 0) {
            setVoices(response.data.voices);
            // REFRESH.MD: Default to the first available male voice for better suitability.
            const defaultVoice = response.data.voices.find(v => v.gender === 'male');
            if (defaultVoice) {
                setSelectedVoice(defaultVoice.id);
            } else {
                setSelectedVoice(response.data.voices[0].id); // Fallback to the first voice if no male voice is found
            }
        }
      } else {
        // If no config is found, ensure we don't show a broken image
        setUploadedImage(null);
      }
    } catch (error) {
      console.error('Error fetching avatar config:', error);
      setUploadedImage(null);
    }
  };

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('image', file);

    try {
      // Use the dedicated upload function
      const response = await enhanced_api.uploadSwamjiImage(formData);
      
      // REFRESH.MD: Check nested properties safely to avoid runtime errors
      if (response && response.success && response.data?.image_url) {
        setUploadedImage(response.data.image_url);
        addNotification('success', '✅ Swamiji photo uploaded successfully!');
      } else {
        // Provide more specific feedback
        const errorMessage = response?.message || 'Unknown error occurred';
        console.error('Error uploading image:', errorMessage);
        addNotification('error', `❌ Failed to upload image: ${errorMessage}`);
      }
    } catch (error) {
      console.error('Error uploading image:', error);
      addNotification('error', '❌ Failed to upload image. A network error occurred.');
    }
  };

  const generatePreviewSample = async () => {
    if (!uploadedImage) {
      addNotification('error', 'Please upload Swamiji\'s photo first');
      return;
    }

    // CORE.MD: Add validation to ensure a voice is selected before proceeding.
    if (!selectedVoice) {
        addNotification('error', 'Voice configuration not loaded. Please refresh the page.');
        return;
    }

    try {
      setIsGenerating(true);
      // REFRESH.MD: Removed the 'style' parameter as the backend now handles daily themes.
      const response = await enhanced_api.generateAvatarPreview({
        voice_id: selectedVoice,
        // CORE.MD: Standardized the sample_text to use consistent Tamil script to avoid TTS errors.
        sample_text: "வணக்கம், அன்பு ஆத்மாக்களே. இந்த தெய்வீக ஆன்மீக வழிகாட்டுதலுக்கு உங்களை வரவேற்கிறோம். அமைதியும் ஞானமும் எப்போதும் உங்களுடன் இருக்கட்டும். ஓம் நமசிவாய."
      });

      if (response.success && response.data?.preview) {
        // REFRESH.MD: Directly set the current sample, removing the old style-based object.
        setCurrentSample(response.data.preview);
        addNotification('success', '✅ Daily preview generated successfully!');
      } else {
        const errorMessage = response?.message || 'Failed to generate preview.';
        console.error('Error generating preview:', errorMessage);
        addNotification('error', `❌ ${errorMessage}`);
      }
    } catch (error) {
      console.error('Error generating preview:', error);
      addNotification('error', '❌ An unexpected error occurred while generating the preview.');
    } finally {
      setIsGenerating(false);
    }
  };

  // REFRESH.MD: Removed generateAllPreviews as it's replaced by the single daily theme generation.

  const approveConfiguration = async () => {
    // REFRESH.MD: Updated the check to use currentSample instead of avatarPreviews.
    if (!uploadedImage || !currentSample) {
      addNotification('error', 'Please upload photo and generate a preview first');
      return;
    }

    try {
      // CORE.MD: The approval logic might need backend changes later, for now, we send the current sample.
      const response = await enhanced_api.approveSwamjiAvatar({
        image_url: uploadedImage,
        previews: { daily: currentSample },
        approved_styles: ['daily'],
        default_style: 'daily'
      });

      if (response.success) {
        setApprovedConfig(response.data.configuration);
        addNotification('success', '✅ Swamiji avatar configuration approved! All future content will use this appearance.');
      }
    } catch (error) {
      console.error('Error approving configuration:', error);
      addNotification('error', '❌ Failed to approve configuration.');
    }
  };

  const downloadPreview = () => {
    if (currentSample?.video_url) {
      window.open(currentSample.video_url, '_blank');
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
              {/* REFRESH.MD: Replaced two buttons with a single daily theme generation button. */}
              <button
                onClick={generatePreviewSample}
                disabled={!uploadedImage || isGenerating}
                className="w-full bg-purple-600 text-white px-4 py-3 rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center justify-center space-x-2 text-base"
              >
                <Star size={18} />
                <span>Generate Daily Avatar Preview</span>
              </button>

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
          {/* REFRESH.MD: The entire Style Selection panel is removed as themes are now automatic. */}

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
                    onClick={downloadPreview}
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
          {currentSample && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-green-900 mb-4 flex items-center">
                <CheckCircle className="mr-2" size={20} />
                Approve Avatar Configuration
              </h3>
              
              <div className="space-y-4">
                <p className="text-green-800">
                  A new daily theme has been generated.
                  Once approved, this appearance will be used for ALL social media content for today.
                </p>
                
                <div className="flex items-center justify-between">
                  <div className="text-sm text-green-700">
                    <p>✅ Preview generated successfully.</p>
                    <p>✅ Theme: Daily Dynamic Theme</p>
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