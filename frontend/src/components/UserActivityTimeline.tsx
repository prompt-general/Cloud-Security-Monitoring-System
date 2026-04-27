import { useEffect, useState } from 'react';
import axios from 'axios';

type Activity = {
  timestamp: string;
  description: string;
};

type Props = {
  userId: string;
};

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export default function UserActivityTimeline({ userId }: Props) {
  const [activity, setActivity] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchActivity = async () => {
      try {
        const res = await axios.get(`${API_BASE}/logs?user_id=${userId}&limit=50`);
        const activities = res.data.map((log: any) => ({
          timestamp: log.timestamp,
          description: `${log.event_type} from ${log.source_ip || 'unknown'} (${log.status})`
        }));
        setActivity(activities);
      } catch (err) {
        console.error('Failed to fetch activity', err);
      } finally {
        setLoading(false);
      }
    };

    if (userId) {
      fetchActivity();
    }
  }, [userId]);

  if (loading) {
    return <div className="bg-white p-6 rounded-lg shadow">Loading activity...</div>;
  }

  return (
    <div className="bg-white rounded-lg shadow p-6 mt-6">
      <h2 className="text-xl font-bold mb-4">Activity for {userId}</h2>
      {activity.length === 0 ? (
        <p className="text-gray-500">No activity found.</p>
      ) : (
        <ul className="space-y-3">
          {activity.map((item, idx) => (
            <li key={idx} className="border-l-2 border-blue-300 pl-4 py-2">
              <div className="text-sm font-semibold">
                {new Date(item.timestamp).toLocaleString()}
              </div>
              <div className="text-sm text-gray-600">{item.description}</div>
            </li>
          ))}
        </ul>
      )}
    </div>
	);
}
