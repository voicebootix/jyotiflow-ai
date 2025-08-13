import React, { useState } from 'react';
import { Button } from '../ui/button';
import enhanced_api from '../../services/enhanced-api';
import { Loader2, CheckCircle, AlertTriangle } from 'lucide-react';

const MasterAvatarManager = () => {
  const [candidates, setCandidates] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleGenerateCandidates = async () => {
    setIsLoading(true);
    setError(null);
    setSuccess(null);
    setCandidates([]);
    try {
      const response = await enhanced_api.generateAvatarCandidates();
      if (response.data.success) {
        setCandidates(response.data.data.candidate_urls || []);
      } else {
        setError('Failed to generate candidates. Please check the logs.');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'An unexpected error occurred.');
      console.error("Error generating candidates:", err);
    }
    setIsLoading(false);
  };

  const handleSetMasterAvatar = async (imageUrl) => {
    setIsLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const response = await enhanced_api.setMasterAvatar({ image_url: imageUrl });
      if (response.data.success) {
        setSuccess(`Successfully set new master avatar! New URL: ${response.data.data.new_avatar_url}`);
        // Optionally, you can refresh the main avatar preview here if needed
      } else {
        setError('Failed to set master avatar. Please try again.');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'An unexpected error occurred while setting the master avatar.');
      console.error("Error setting master avatar:", err);
    }
    setIsLoading(false);
  };

  return (
    <div className="bg-white rounded-lg shadow p-6 space-y-6">
      <div>
        <h3 className="text-lg font-semibold">Master Avatar Selection (for LoRA Training)</h3>
        <p className="text-sm text-gray-600 mt-1">
          Generate a set of AI-created avatars. Choose the one that best represents Swamiji. This selected avatar will be used as the 'master' image to train a LoRA model for consistent face generation.
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
          Generate New Avatar Candidates
        </Button>
      </div>

      {candidates.length > 0 && (
        <div>
          <h4 className="font-semibold mb-4">Select the Best Avatar:</h4>
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
    </div>
  );
};

export default MasterAvatarManager;
