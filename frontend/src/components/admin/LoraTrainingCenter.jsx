import React, { useState, useCallback, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Upload, Rocket, CheckCircle, XCircle, Loader2, BrainCircuit } from 'lucide-react';
import enhanced_api from '@/services/enhanced-api'; // Corrected: removed curly braces for default import
// Dropzone is no longer needed with the new URL-based flow
// import { useDropzone } from 'react-dropzone';

const LoraTrainingCenter = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [modelData, setModelData] = useState(null);
  const [trainingDataUrl, setTrainingDataUrl] = useState(''); // State for the public URL
  const [trainingJob, setTrainingJob] = useState(null);
  
  const handleCreateModel = async () => {
    setIsLoading(true);
    setLoadingMessage('Step 1: Creating model placeholder on Replicate...');
    setError(null);
    setSuccess(null);
    try {
      const response = await enhanced_api.createLoraModel({ owner: 'voicebootix' });
      if (response?.success) {
        setModelData(response.data);
        setSuccess(response.message);
      } else {
        setError(response?.message || 'Failed to create model.');
      }
    } catch (e) {
      setError('A client-side error occurred.');
    }
    setIsLoading(false);
    setLoadingMessage('');
  };
  
  const handleStartTraining = async () => {
    if (!modelData) {
      setError("Model must be created first (Step 1).");
      return;
    }

    const trimmedUrl = trainingDataUrl.trim();
    if (!trimmedUrl) {
      setError("Please provide a public URL for the training data ZIP file.");
      return;
    }

    try {
      const url = new URL(trimmedUrl);
      if (url.protocol !== 'https:' || !url.pathname.toLowerCase().endsWith('.zip')) {
        setError("Invalid URL. Please provide a public HTTPS URL that points directly to a .zip file.");
        return;
      }
    } catch (e) {
      setError("Invalid URL format. Please enter a full and valid URL (e.g., https://...).");
      return;
    }
    
    setIsLoading(true);
    setLoadingMessage("Starting the training job on Replicate...");
    setError(null);
    setSuccess(null);

    try {
      const payload = {
        model_owner: modelData.owner,
        model_name: modelData.name,
        training_data_url: trimmedUrl
      };

      const response = await enhanced_api.startTrainingJob(payload);
      
      if (response?.success) {
        setTrainingJob(response.data);
        setSuccess(`Training job started successfully! Job ID: ${response.data.id}`);
      } else {
        throw new Error(response?.message || "Failed to start training job.");
      }

    } catch (e) {
      setError(e.message || "An error occurred while starting the training job.");
    } finally {
      setIsLoading(false);
      setLoadingMessage("");
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6 space-y-6">
      <div>
        <h3 className="text-lg font-semibold flex items-center"><BrainCircuit className="mr-2" /> LoRA Model Training Center</h3>
        <p className="text-sm text-gray-600 mt-1">
          Follow these steps to train a new LoRA model for Swamiji's avatar.
        </p>
      </div>

      {error && (
        <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4" role="alert">
          <p className="font-bold">Error</p>
          <p>{error}</p>
        </div>
      )}
      {success && (
        <div className="bg-green-100 border-l-4 border-green-500 text-green-700 p-4" role="alert">
          <p className="font-bold">Success</p>
          <p>{success}</p>
        </div>
      )}
      {loadingMessage && (
        <div className="flex items-center space-x-2 text-purple-600">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span>{loadingMessage}</span>
        </div>
      )}

      {/* Step 1: Create Model */}
      <div className="border rounded-lg p-4">
        <h4 className="font-semibold">Step 1: Create Replicate Model</h4>
        <p className="text-sm text-gray-500 mt-1">
          Create a private model on Replicate named 'swamiji-lora-model' under the 'voicebootix' account. This only needs to be done once.
        </p>
        <Button onClick={handleCreateModel} disabled={isLoading || modelData} className="mt-3">
          {modelData ? <><CheckCircle className="mr-2"/> Model Exists/Created</> : 'Create Model'}
        </Button>
        {modelData && <pre className="mt-2 text-xs bg-gray-100 p-2 rounded">{JSON.stringify(modelData, null, 2)}</pre>}
      </div>

      {/* Step 2: Provide Training Data URL */}
      <div className={`border rounded-lg p-4 ${!modelData && 'opacity-50'}`}>
        <h4 className="font-semibold">Step 2: Provide Training Data URL</h4>
        <p className="text-sm text-gray-500 mt-1">
          Upload your `swamiji_training_data.zip` to a public host (like Google Drive or S3) and paste the direct download URL below.
        </p>
        <Input
          type="url"
          placeholder="https://example.com/path/to/swamiji_training_data.zip"
          value={trainingDataUrl}
          onChange={(e) => setTrainingDataUrl(e.target.value)}
          disabled={!modelData || isLoading}
          className="mt-3"
        />
      </div>
      
      {/* Step 3: Start Training */}
      <div className={`border rounded-lg p-4 ${!trainingDataUrl && 'opacity-50'}`}>
        <h4 className="font-semibold">Step 3: Start Training</h4>
        <p className="text-sm text-gray-500 mt-1">
            This will start the LoRA training job on Replicate. It can take 15-30 minutes.
        </p>
         <Button onClick={handleStartTraining} disabled={!trainingDataUrl || isLoading} className="mt-3">
            <Rocket className="mr-2" /> Start Training Job
        </Button>
      </div>

      {trainingJob && (
        <div className="border rounded-lg p-4 mt-4 bg-gray-50">
          <h4 className="font-semibold text-green-700">Training Job Details</h4>
          <p className="text-sm text-gray-600 mt-2">
            View your training progress on Replicate:
          </p>
          <a href={`https://replicate.com/trainings/${trainingJob.id}`} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline break-all">
            {`https://replicate.com/trainings/${trainingJob.id}`}
          </a>
          <pre className="text-xs bg-gray-900 text-white p-3 rounded-md mt-2 overflow-x-auto">
            {JSON.stringify(trainingJob, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

export default LoraTrainingCenter;
