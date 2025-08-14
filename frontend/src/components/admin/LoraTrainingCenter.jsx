import React, { useState, useCallback } from 'react';
import { Button } from '../ui/button';
import enhanced_api from '../../services/enhanced-api';
import { Loader2, CheckCircle, AlertTriangle, Upload, Rocket, BrainCircuit } from 'lucide-react';
import { useDropzone } from 'react-dropzone';

const LoraTrainingCenter = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  const [modelData, setModelData] = useState(null);
  const [zipFile, setZipFile] = useState(null);
  const [zipUploadUrl, setZipUploadUrl] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [trainingJob, setTrainingJob] = useState(null);

  const onDrop = useCallback(acceptedFiles => {
    setError(null); // Clear previous errors on a new drop attempt
    const file = acceptedFiles[0];
    
    // Loosened validation to only check for filename, as mime type can be inconsistent.
    if (file && file.name === 'swamiji_training_data.zip') {
      setZipFile(file);
    } else {
      setZipFile(null); // Clear any previously valid file if the new one is invalid
      setError('Invalid file. Please upload a ZIP file named "swamiji_training_data.zip".');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {'application/zip': ['.zip']},
    multiple: false
  });

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

  const handleUploadZip = async () => {
    if (!zipFile || !modelData) return;

    setIsLoading(true);
    setLoadingMessage('Step 2.1: Requesting secure upload URL from Replicate...');
    setError(null);
    setSuccess(null);

    try {
      // Get the signed URL from our backend
      const prepResponse = await enhanced_api.prepareTrainingUpload();
      if (!prepResponse?.success || !prepResponse.data?.upload_url) {
        throw new Error(prepResponse?.message || 'Failed to get upload URL.');
      }

      const { upload_url, serving_url } = prepResponse.data;
      setLoadingMessage('Step 2.2: Uploading ZIP file directly to Replicate...');
      
      // Use XMLHttpRequest to upload directly to the signed URL and track progress
      const xhr = new XMLHttpRequest();
      xhr.open('PUT', upload_url, true);
      xhr.setRequestHeader('Content-Type', 'application/zip');
      
      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const percentComplete = Math.round((event.loaded / event.total) * 100);
          setUploadProgress(percentComplete);
        }
      };

      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          setZipUploadUrl(serving_url);
          setSuccess('ZIP file uploaded to Replicate successfully!');
          setLoadingMessage('');
        } else {
          setError(`Upload failed. Status: ${xhr.status} ${xhr.statusText}`);
          setLoadingMessage('');
        }
        setIsLoading(false);
        setUploadProgress(0);
      };

      xhr.onerror = () => {
        setError('Network error during file upload.');
        setIsLoading(false);
        setUploadProgress(0);
      };

      xhr.send(zipFile);

    } catch (e) {
      setError(e.message || 'A client-side error occurred during upload preparation.');
      setIsLoading(false);
      setLoadingMessage('');
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

      {/* Step 2: Upload ZIP */}
      <div className={`border rounded-lg p-4 ${!modelData && 'opacity-50'}`}>
        <h4 className="font-semibold">Step 2: Upload `swamiji_training_data.zip`</h4>
        <p className="text-sm text-gray-500 mt-1">
            Upload the ZIP file containing 10-15 training images.
        </p>
        <div {...getRootProps()} className={`mt-3 border-2 border-dashed rounded-lg p-8 text-center cursor-pointer ${isDragActive ? 'border-purple-500 bg-purple-50' : 'border-gray-300'}`}>
            <input {...getInputProps()} disabled={!modelData || isLoading} />
            <Upload className="mx-auto h-10 w-10 text-gray-400" />
            {zipFile ? (
                <p className="mt-2 text-green-600">{zipFile.name} selected.</p>
            ) : (
                <p className="mt-2 text-sm text-gray-500">Drag 'n' drop 'swamiji_training_data.zip' here, or click to select.</p>
            )}
        </div>
        {zipFile && !zipUploadUrl && (
            <Button onClick={handleUploadZip} disabled={isLoading} className="mt-3">
                <Upload className="mr-2" /> Upload ZIP to Replicate
            </Button>
        )}
        {isLoading && uploadProgress > 0 && (
            <div className="w-full bg-gray-200 rounded-full h-2.5 mt-3">
                <div className="bg-purple-600 h-2.5 rounded-full" style={{ width: `${uploadProgress}%` }}></div>
            </div>
        )}
      </div>
      
       {/* Step 3: Start Training */}
      <div className={`border rounded-lg p-4 ${!zipUploadUrl && 'opacity-50'}`}>
        <h4 className="font-semibold">Step 3: Start Training</h4>
        <p className="text-sm text-gray-500 mt-1">
            This will start the LoRA training job on Replicate. It can take 15-30 minutes.
        </p>
         <Button disabled={!zipUploadUrl || isLoading} className="mt-3">
            <Rocket className="mr-2" /> Start Training Job
        </Button>
      </div>

    </div>
  );
};

export default LoraTrainingCenter;
