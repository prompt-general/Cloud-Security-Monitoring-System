import React, { useState, useEffect } from 'react';
import axios from 'axios';

type Log = {
  timestamp: string;
  event_type: string;
  cloud_provider: string;
  status: string;
  source_ip?: string;
  resource?: string;
};

type Props = {
  userId: string;
};

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export default function UserActivityTimeline({ userId }: Props) {
  const [logs, setLogs] = useState<Log[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!userId) return;
    const fetchLogs = async () => {
      setLoading(true);
      try {
        const res = await axios.get(`${API_BASE}/logs?user_id=${userId}&limit=50`);
        setLogs(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchLogs();
  }, [userId]);

  if (!userId) return null;
  
  return (
    <div className="mt-8 bg-white shadow rounded-lg p-4">
      <h2 className="text-xl font-semibold mb-3">Activity Timeline: {userId}</h2>
      {loading && <div>Loading...</div>}
      {!loading && logs.length === 0 && <div>No activity found.</div>}
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {logs.map((log, idx) => (
          <div key={idx} className="border-l-4 border-gray-300 pl-3 py-1">
            <div className="text-sm text-gray-500">{new Date(log.timestamp).toLocaleString()}</div>
            <div className="font-mono text-sm">
              {log.event_type} · {log.cloud_provider} · {log.status}
              {log.source_ip && ` · IP: ${log.source_ip}`}
              {log.resource && ` · Resource: ${log.resource}`}
            </div>
          </div>
        ))}
      </div>
    </div>
	);
}
