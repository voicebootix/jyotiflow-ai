import React, { useState, useEffect } from 'react';
import { 
  Upload, Eye, Download, Settings, Wand2, CheckCircle, 
  AlertTriangle, Play, Pause, RotateCcw, Save, Star 
} from 'lucide-react';
import enhanced_api from '../../services/enhanced-api';
import { useNotification } from '../../hooks/useNotification';

const SwamjiAvatarPreview = () => {
  const [uploadedImage, setUploadedImage] = useState(null);
  const [voices, setVoices] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [approvedConfig, setApprovedConfig] = useState(null);
  
  const [previewImage, setPreviewImage] = useState(null);
  const [promptText, setPromptText] = useState('');
  const [finalVideo, setFinalVideo] = useState(null);
  const [isGeneratingVideo, setIsGeneratingVideo] = useState(false);
  
  const { addNotification } = useNotification();

  useEffect(() => {
    fetchCurrentConfiguration();
  }, []);

  // REFRESH.MD: FIX - Add useEffect to revoke object URLs and prevent memory leaks.
  useEffect(() => {
    // This is the cleanup function that will be called when the component unmounts
    // or when the previewImage state changes.
    return () => {
      if (previewImage && previewImage.startsWith('blob:')) {
        URL.revokeObjectURL(previewImage);
      }
    };
  }, [previewImage]); // Dependency array ensures this runs when previewImage changes.

  const fetchCurrentConfiguration = async () => {
    try {
      // REFRESH.MD: FIX - Corrected method name from getSwamjiAvatarConfig to getSwamijiAvatarConfig
      const response = await enhanced_api.getSwamijiAvatarConfig();
      if (response.success && response.data) {
        setApprovedConfig(response.data);
        if (response.data.image_url) {
            setUploadedImage(response.data.image_url);
        }
        // REFRESH.MD: FIX - Added safety check for non-empty voices array
        if (response.data.voices && Array.isArray(response.data.voices) && response.data.voices.length > 0) {
            setVoices(response.data.voices);
            const defaultVoice = response.data.voices.find(v => v.gender === 'male');
            if (defaultVoice) {
                setSelectedVoice(defaultVoice.id);
            } else {
                setSelectedVoice(response.data.voices[0].id); // Fallback to the first voice
            }
        }
      } else {
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
      // Corrected method name here as well for consistency, assuming it was a typo in multiple places
      const response = await enhanced_api.uploadSwamjiImage(formData);
      
      if (response && response.success && response.data?.image_url) {
        setUploadedImage(response.data.image_url);
        addNotification('success', '✅ Swamiji photo uploaded successfully!');
      } else {
        const errorMessage = response?.message || 'Unknown error occurred';
        console.error('Error uploading image:', errorMessage);
        addNotification('error', `❌ Failed to upload image: ${errorMessage}`);
      }
    } catch (error) {
      console.error('Error uploading image:', error);
      addNotification('error', '❌ Failed to upload image. A network error occurred.');
    }
  };

  const generateImagePreview = async (customPrompt = null) => {
    if (!uploadedImage) {
      addNotification('error', 'Please upload Swamiji\'s photo first');
      return;
    }
    try {
      setIsGenerating(true);
      
      // REFRESH.MD: FIX - Revoke previous object URL before creating a new one
      if (previewImage && previewImage.startsWith('blob:')) {
        URL.revokeObjectURL(previewImage);
      }
      setPreviewImage(null); 
      setFinalVideo(null);

      const response = await enhanced_api.generateImagePreview({
        custom_prompt: customPrompt || promptText || "A divine, photorealistic image of a spiritual master giving a blessing, with a serene background.",
      });

      if (response.success && response.blob) {
        const imageUrl = URL.createObjectURL(response.blob);
        setPreviewImage(imageUrl);
        setPromptText(customPrompt || promptText || "A divine, photorealistic image of a spiritual master giving a blessing, with a serene background.");
        addNotification('success', '✅ Image preview generated!');
      } else {
        const errorMessage = response?.message || 'Failed to generate image preview.';
        addNotification('error', `❌ ${errorMessage}`);
      }
    } catch (error) {
      addNotification('error', '❌ An unexpected error occurred during image generation.');
    } finally {
      setIsGenerating(false);
    }
  };

  const generateVideoFromPreview = async () => {
    if (!previewImage) {
      addNotification('error', 'Please generate an image preview first.');
      return;
    }
    if (!selectedVoice) {
      addNotification('error', 'A voice must be selected to generate the video.');
      return;
    }
    try {
      setIsGeneratingVideo(true);
      setFinalVideo(null);

      const response = await enhanced_api.generateVideoFromPreview({
        image_url: previewImage,
        voice_id: selectedVoice,
        sample_text: "வணக்கம், அன்பு ஆத்மாக்களே. இந்த தெய்வீக ஆன்மீக வழிகாட்டுதலுக்கு உங்களை வரவேற்கிறோம். அமைதியும் ஞானமும் எப்போதும் உங்களுடன் இருக்கட்டும். ஓம் நமசிவாய."
      });

      if (response.success && response.data) {
        setFinalVideo(response.data);
        addNotification('success', '✅ Video generated successfully!');
      } else {
        const errorMessage = response?.message || 'Failed to generate video.';
        addNotification('error', `❌ ${errorMessage}`);
      }
    } catch (error) {
      addNotification('error', '❌ An unexpected error occurred while generating the video.');
    } finally {
      setIsGeneratingVideo(false);
    }
  };

  const approveConfiguration = async () => {
    if (!uploadedImage || !finalVideo) {
      addNotification('error', 'Please generate a video preview first');
      return;
    }
    try {
      const response = await enhanced_api.approveSwamijiAvatar({
        image_url: uploadedImage,
        video_url: finalVideo.video_url,
        prompt: promptText,
      });

      if (response.success) {
        setApprovedConfig(response.data.configuration);
        addNotification('success', '✅ Swamiji avatar configuration approved!');
      } else {
        const errorMessage = response?.message || 'Failed to approve configuration.';
        addNotification('error', `❌ ${errorMessage}`);
      }
    } catch (error) {
      console.error('Error approving configuration:', error);
      addNotification('error', '❌ An unexpected error occurred while approving.');
    }
  };

  const downloadVideo = () => {
    if (finalVideo?.video_url) {
      window.open(finalVideo.video_url, '_blank');
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
              <button
                onClick={() => generateImagePreview()}
                disabled={!uploadedImage || isGenerating}
                className="w-full bg-purple-600 text-white px-4 py-3 rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center justify-center space-x-2 text-base"
              >
                <Star size={18} />
                <span>Generate Daily Image Preview</span>
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

        {/* Right Panel - Interactive Preview and Generation */}
        <div className="space-y-6">
          {/* Interactive Image Preview */}
          {previewImage && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <Eye className="mr-2" size={20} />
                Image Preview
              </h3>
              <div className="space-y-4">
                <div className="bg-gray-100 rounded-lg p-4 text-center">
                  <img 
                    src={previewImage} 
                    alt="Generated Preview" 
                    className="mx-auto max-w-full h-64 rounded-lg object-contain"
                  />
                </div>
                <div>
                  <label htmlFor="prompt-text" className="block text-sm font-medium text-gray-700 mb-1">
                    Generated Prompt
                  </label>
                  <textarea
                    id="prompt-text"
                    value={promptText}
                    onChange={(e) => setPromptText(e.target.value)}
                    rows={4}
                    className="w-full border border-gray-300 rounded-lg p-2 text-sm"
                  />
                </div>
                <button
                  onClick={() => generateImagePreview(promptText)}
                  disabled={isGenerating}
                  className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center space-x-2"
                >
                  <RotateCcw size={16} />
                  <span>Regenerate Image</span>
                </button>
              </div>
            </div>
          )}

          {/* Video Generation & Final Preview */}
          {previewImage && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-green-900 mb-4 flex items-center">
                <Play className="mr-2" size={20} />
                Step 2: Generate Video
              </h3>
              <div className="space-y-4">
                <p className="text-green-800">
                  If you are happy with the image preview, generate the final video.
                </p>
                <button
                  onClick={generateVideoFromPreview}
                  disabled={isGeneratingVideo}
                  className="w-full bg-green-600 text-white px-4 py-3 rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center justify-center space-x-2"
                >
                  <CheckCircle size={18} />
                  <span>Confirm & Generate Video</span>
                </button>
                {isGeneratingVideo && (
                  <div className="text-center py-4">
                    <div className="animate-spin mx-auto h-8 w-8 border-4 border-green-500 border-t-transparent rounded-full"></div>
                    <p className="mt-2 text-gray-600">Generating video...</p>
                  </div>
                )}
              </div>
            </div>
          )}
          
          {finalVideo && (
            <div className="bg-white rounded-lg shadow p-6">
               <h3 className="text-lg font-semibold mb-4 text-purple-800">Final Video Preview</h3>
                <video 
                    src={finalVideo.video_url}
                    controls
                    className="mx-auto max-w-full h-64 rounded-lg"
                    poster={previewImage}
                  >
                    Your browser does not support video playback.
                </video>
                 <div className="mt-4 flex justify-end space-x-3">
                    <button
                        onClick={downloadVideo}
                        className="flex items-center px-3 py-2 text-purple-600 hover:bg-purple-50 rounded-lg"
                      >
                        <Download size={16} className="mr-2" />
                        Download
                    </button>
                    <button
                        onClick={approveConfiguration}
                        className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 flex items-center space-x-2"
                      >
                        <Save size={16} />
                        <span>Approve Final Avatar</span>
                    </button>
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
