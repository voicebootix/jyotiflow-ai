import React, { useState } from 'react';
import { Button } from '../ui/button';
import enhanced_api from '../../services/enhanced-api';
import { Loader2, CheckCircle, AlertTriangle, Download } from 'lucide-react';

const MasterAvatarManager = () => {
  const [candidates, setCandidates] = useState([]);
  const [variations, setVariations] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleGenerateCandidates = async () => {
    setIsLoading(true);
    setLoadingMessage('Generating 10 new avatar candidates...');
    setError(null);
    setSuccess(null);
    setCandidates([]);
    setVariations([]); // Clear old variations
    try {
      const response = await enhanced_api.generateAvatarCandidates();
      // 🛡️ Robust response handling
      if (response?.success && Array.isArray(response?.data?.candidate_urls)) {
        setCandidates(response.data.candidate_urls);
      } else {
        setError(response?.message || 'Failed to generate candidates. Response was invalid.');
      }
    } catch (err) {
      setError('A critical client-side error occurred.');
      console.error("Error generating candidates:", err);
    }
    setIsLoading(false);
    setLoadingMessage('');
  };

  const handleSetMasterAvatar = async (imageUrl) => {
    setIsLoading(true);
    setLoadingMessage('Setting master avatar...');
    setError(null);
    setSuccess(null);
    setVariations([]); // Clear old variations

    try {
      // Step 1: Set the master avatar
      const setMasterResponse = await enhanced_api.setMasterAvatar({ image_url: imageUrl });
      
      if (!setMasterResponse?.success || !setMasterResponse?.data?.new_avatar_url) {
        setError(setMasterResponse?.message || 'Failed to set master avatar or did not receive a new URL.');
        setIsLoading(false);
        setLoadingMessage('');
        return;
      }
      
      const masterAvatarUrl = setMasterResponse.data.new_avatar_url;
      setSuccess(`Master avatar set to: ${masterAvatarUrl}. Now generating 20 training variations...`);
      setLoadingMessage('Master avatar set! Generating 20 training variations (this may take a minute)...');
      
      // Step 2: Generate training variations from the new master URL
      const variationsResponse = await enhanced_api.generateTrainingVariations({ image_url: masterAvatarUrl });

      if (variationsResponse?.success && Array.isArray(variationsResponse?.data?.variation_urls)) {
        setVariations(variationsResponse.data.variation_urls);
        setSuccess(`Successfully generated ${variationsResponse.data.variation_urls.length} training variations.`);
      } else {
        setError(variationsResponse?.message || 'Failed to generate training variations.');
      }

    } catch (err) {
      setError('A critical client-side error occurred during the process.');
      console.error("Error in master avatar process:", err);
    }
    
    setIsLoading(false);
    setLoadingMessage('');
  };

  return (
    <div className="bg-white rounded-lg shadow p-6 space-y-6">
      <div>
        <h3 className="text-lg font-semibold">Phase 1: Master Avatar Selection</h3>
        <p className="text-sm text-gray-600 mt-1">
          First, generate a set of AI-created avatars. Then, choose the one that best represents Swamiji to become the 'master' avatar for training.
        </p>
      </div>

      {error && (
        <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4" role="alert">
          <div className="flex">
            <div className="py-1"><AlertTriangle className="h-5 w-5 text-red-500 mr-3" /></div>
            <div>
              <p className="font-bold">Error</p>
              <p className="text-sm">{error}</p>
            </div>
          </div>
        </div>
      )}

      {success && (
        <div className="bg-green-100 border-l-4 border-green-500 text-green-700 p-4" role="alert">
          <div className="flex">
            <div className="py-1"><CheckCircle className="h-5 w-5 text-green-500 mr-3" /></div>
            <div>
              <p className="font-bold">Success</p>
              <p className="text-sm">{success}</p>
            </div>
          </div>
        </div>
      )}

      <div className="flex items-center">
        <Button onClick={handleGenerateCandidates} disabled={isLoading}>
          {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          {loadingMessage || 'Generate New Avatar Candidates'}
        </Button>
      </div>

      {candidates.length > 0 && (
        <div>
          <h4 className="font-semibold mb-4">Select the Best Avatar Candidate:</h4>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {candidates.map((url, index) => (
              <div key={index} className="border rounded-lg p-2 space-y-2 flex flex-col items-center">
                <img src={url} alt={`Candidate ${index + 1}`} className="w-full h-auto rounded" />
                <Button 
                  size="sm" 
                  variant="outline"
                  onClick={() => handleSetMasterAvatar(url)}
                  disabled={isLoading}
                >
                  Set as Master
                </Button>
              </div>
            ))}
          </div>
        </div>
      )}

      {variations.length > 0 && (
        <div className="pt-6 mt-6 border-t">
          <h3 className="text-lg font-semibold">Phase 2: Training Data Variations</h3>
          <p className="text-sm text-gray-600 mt-1">
            Here are 20 variations of your selected master avatar. Download the best 5-10 images to create your `swamiji_training_data.zip` file for LoRA training.
          </p>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4 mt-4">
            {variations.map((url, index) => (
              <div key={index} className="border rounded-lg p-2 space-y-2 flex flex-col items-center">
                <img src={url} alt={`Variation ${index + 1}`} className="w-full h-auto rounded" />
                <a 
                  href={url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  download={`swamiji_variation_${index + 1}.png`}
                  className="w-full"
                >
                  <Button size="sm" variant="ghost" className="w-full">
                    <Download className="mr-2 h-4 w-4" />
                    Download
                  </Button>
                </a>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default MasterAvatarManager;
