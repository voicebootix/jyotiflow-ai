// தமில - அமைப்புகள்
import { useEffect, useState } from 'react';
import spiritualAPI from '../../lib/api';
import Loader from '../ui/Loader';

export default function Settings() {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [services, setServices] = useState([]);
  const [servicesLoading, setServicesLoading] = useState(true);

  useEffect(() => {
    spiritualAPI.getAdminSettings().then(setSettings).finally(() => setLoading(false));
    // Fetch dynamic services
    spiritualAPI.request('/api/admin/service-types').then(data => {
      setServices(data);
      setServicesLoading(false);
    });
  }, []);

  if (loading) return <Loader message="அமைப்புகள் ஏற்றப்படுகிறது..." />;
  if (!settings) return <div className="text-gray-600">No settings available.</div>;

  const updateService = (id, changes) => {
    setServicesLoading(true);
    spiritualAPI.request(`/api/admin/service-types/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(changes)
    }).then(updated => {
      setServices(services.map(s => s.id === id ? updated : s));
      setServicesLoading(false);
    });
  };

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Settings & Configuration</h2>
      {/* Render settings form, AI config, integrations, health, security */}
      <pre className="bg-white p-4 rounded">{JSON.stringify(settings, null, 2)}</pre>
      <div className="mt-8">
        <h3 className="text-lg font-bold mb-2">Service Pricing & Controls</h3>
        {servicesLoading ? <Loader message="சேவைகள் ஏற்றப்படுகிறது..." /> : (
          <div>
            {services.map(service => (
              <div key={service.id} className="mb-4 p-4 border rounded bg-white">
                <div className="font-semibold mb-2">{service.name}</div>
                <div className="flex flex-wrap gap-4 items-center">
                  <label>Price ($)
                    <input type="number" value={service.price_usd} onChange={e => updateService(service.id, { price_usd: +e.target.value })} className="ml-2 border px-2 py-1 rounded w-24" />
                  </label>
                  <label>Credits
                    <input type="number" value={service.credits_required} onChange={e => updateService(service.id, { credits_required: +e.target.value })} className="ml-2 border px-2 py-1 rounded w-20" />
                  </label>
                  <label>Duration (min)
                    <input type="number" value={service.duration_minutes} onChange={e => updateService(service.id, { duration_minutes: +e.target.value })} className="ml-2 border px-2 py-1 rounded w-20" />
                  </label>
                  <button onClick={() => updateService(service.id, { enabled: !service.enabled })} className={`px-4 py-1 rounded ${service.enabled ? 'bg-green-500 text-white' : 'bg-gray-300 text-gray-700'}`}>{service.enabled ? 'Enabled' : 'Disabled'}</button>
                </div>
                <div className="text-gray-500 text-sm mt-1">{service.description}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
} 