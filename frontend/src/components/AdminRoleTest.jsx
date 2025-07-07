import React, { useState, useEffect } from 'react';
import spiritualAPI from '../lib/api';

const AdminRoleTest = () => {
  const [debugInfo, setDebugInfo] = useState({});

  useEffect(() => {
    checkAdminStatus();
  }, []);

  const checkAdminStatus = async () => {
    const info = {
      isAuthenticated: spiritualAPI.isAuthenticated(),
      localStorageToken: !!localStorage.getItem('jyotiflow_token'),
      localStorageUser: localStorage.getItem('jyotiflow_user'),
    };

    try {
      const profile = await spiritualAPI.getUserProfile();
      info.apiProfile = profile;
      info.apiUserRole = profile?.data?.role;
    } catch (error) {
      info.apiError = error.message;
    }

    const storedUser = localStorage.getItem('jyotiflow_user');
    if (storedUser) {
      try {
        const user = JSON.parse(storedUser);
        info.storedUserRole = user.role;
        info.storedUser = user;
      } catch (error) {
        info.storedUserError = error.message;
      }
    }

    setDebugInfo(info);
  };

  const forceAdminRole = () => {
    const user = JSON.parse(localStorage.getItem('jyotiflow_user') || '{}');
    user.role = 'admin';
    localStorage.setItem('jyotiflow_user', JSON.stringify(user));
    checkAdminStatus();
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-4">🔍 Admin Role Debug</h2>
      
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="p-4 bg-gray-100 rounded">
            <h3 className="font-semibold">Authentication Status</h3>
            <p>Is Authenticated: {debugInfo.isAuthenticated ? '✅ Yes' : '❌ No'}</p>
            <p>Has Token: {debugInfo.localStorageToken ? '✅ Yes' : '❌ No'}</p>
          </div>
          
          <div className="p-4 bg-gray-100 rounded">
            <h3 className="font-semibold">Role Information</h3>
            <p>Stored Role: {debugInfo.storedUserRole || 'None'}</p>
            <p>API Role: {debugInfo.apiUserRole || 'None'}</p>
          </div>
        </div>

        <div className="p-4 bg-blue-50 rounded">
          <h3 className="font-semibold">Actions</h3>
          <button 
            onClick={forceAdminRole}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            Force Admin Role
          </button>
          <button 
            onClick={checkAdminStatus}
            className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 ml-2"
          >
            Refresh Debug Info
          </button>
        </div>

        <div className="p-4 bg-yellow-50 rounded">
          <h3 className="font-semibold">Raw Debug Data</h3>
          <pre className="text-xs overflow-auto">
            {JSON.stringify(debugInfo, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  );
};

export default AdminRoleTest; 