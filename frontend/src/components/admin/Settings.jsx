// தமில - அமைப்புகள்
import { useEffect, useState } from 'react';
import api from '../../lib/api';
import Loader from '../ui/Loader';

export default function Settings() {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getAdminSettings().then(setSettings).finally(() => setLoading(false));
  }, []);

  if (loading) return <Loader message="அமைப்புகள் ஏற்றப்படுகிறது..." />;

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Settings & Configuration</h2>
      {/* Render settings form, AI config, integrations, health, security */}
      <pre className="bg-white p-4 rounded">{JSON.stringify(settings, null, 2)}</pre>
    </div>
  );
} 