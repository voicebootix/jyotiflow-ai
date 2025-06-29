// தமில - உள்ளடக்க மேலாண்மை
import { useEffect, useState } from 'react';
import api from '../../lib/api';
import Loader from '../ui/Loader';
import { Table } from '../ui/table';

export default function ContentManagement() {
  const [content, setContent] = useState([]);
  const [satsangs, setSatsangs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.getAdminContent(), api.getAdminSatsangs()])
      .then(([content, satsangs]) => {
        setContent(content);
        setSatsangs(satsangs);
        setLoading(false);
      });
  }, []);

  if (loading) return <Loader message="உள்ளடக்க தரவு ஏற்றப்படுகிறது..." />;

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Content Management</h2>
      <div className="mb-8">
        <h3 className="font-bold mb-2">Social Content Queue</h3>
        <Table
          columns={[
            { label: 'Platform', key: 'platform' },
            { label: 'Type', key: 'content_type' },
            { label: 'Text', key: 'content_text' },
            { label: 'Scheduled', key: 'scheduled_at' },
            { label: 'Status', key: 'status' }
          ]}
          data={content}
        />
      </div>
      <div>
        <h3 className="font-bold mb-2">Satsang Events</h3>
        <Table
          columns={[
            { label: 'Title', key: 'title' },
            { label: 'Date', key: 'event_date' },
            { label: 'Attendees', key: 'current_attendees' },
            { label: 'Status', key: 'status' }
          ]}
          data={satsangs}
        />
      </div>
    </div>
  );
} 