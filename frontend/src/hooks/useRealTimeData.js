import { useState, useEffect, useCallback } from 'react';
import spiritualAPI from '../lib/api';

export const useRealTimeData = (refreshInterval = 30000) => {
  const [services, setServices] = useState([]);
  const [creditPackages, setCreditPackages] = useState([]);
  const [donationOptions, setDonationOptions] = useState([]);
  const [credits, setCredits] = useState(0);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastRefresh, setLastRefresh] = useState(new Date());
  const [error, setError] = useState(null);

  const loadData = useCallback(async () => {
    try {
      setError(null);
      
      // Load services
      const servicesData = await spiritualAPI.request('/api/admin/products/service-types');
      setServices(Array.isArray(servicesData) ? servicesData : []);

      // Load credit packages
      const packagesData = await spiritualAPI.request('/api/admin/products/credit-packages');
      setCreditPackages(Array.isArray(packagesData) ? packagesData : []);

      // Load donation options
      const donationsData = await spiritualAPI.request('/api/admin/products/donations');
      setDonationOptions(Array.isArray(donationsData) ? donationsData : []);

      // Load user credits if authenticated
      if (spiritualAPI.isAuthenticated()) {
        const creditsData = await spiritualAPI.getCreditBalance();
        if (creditsData && creditsData.success) {
          setCredits(creditsData.data.credits || 0);
        }
      }

      setLastRefresh(new Date());
    } catch (error) {
      console.log('Data loading blessed with patience:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const refreshData = useCallback(async () => {
    try {
      setRefreshing(true);
      setError(null);
      
      // Load services
      const servicesData = await spiritualAPI.request('/api/admin/products/service-types');
      setServices(Array.isArray(servicesData) ? servicesData : []);

      // Load credit packages
      const packagesData = await spiritualAPI.request('/api/admin/products/credit-packages');
      setCreditPackages(Array.isArray(packagesData) ? packagesData : []);

      // Load donation options
      const donationsData = await spiritualAPI.request('/api/admin/products/donations');
      setDonationOptions(Array.isArray(donationsData) ? donationsData : []);

      // Load user credits if authenticated
      if (spiritualAPI.isAuthenticated()) {
        const creditsData = await spiritualAPI.getCreditBalance();
        if (creditsData && creditsData.success) {
          setCredits(creditsData.data.credits || 0);
        }
      }

      setLastRefresh(new Date());
    } catch (error) {
      console.log('Real-time refresh blessed with patience:', error);
      setError(error.message);
    } finally {
      setRefreshing(false);
    }
  }, []);

  // Manual refresh function
  const handleManualRefresh = useCallback(async () => {
    await refreshData();
  }, [refreshData]);

  useEffect(() => {
    loadData();

    // Set up real-time refresh
    const interval = setInterval(() => {
      refreshData();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [loadData, refreshData, refreshInterval]);

  return {
    services,
    creditPackages,
    donationOptions,
    credits,
    loading,
    refreshing,
    lastRefresh,
    error,
    refreshData,
    handleManualRefresh,
    setCredits // Allow manual credit updates
  };
}; 