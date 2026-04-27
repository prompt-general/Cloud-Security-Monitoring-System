import React, { useState, useEffect } from 'react';
import axios from 'axios';
import AlertTable from './components/AlertTable';
import UserActivityTimeline from './components/UserActivityTimeline';
import FilterBar from './components/FilterBar';

export type AlertItem = {
  id?: string;
  alert_id?: string;
  user_id: string;
  risk_score: number;
  severity: 'high' | 'medium' | 'low';
  reason: string;
  timestamp: string;
  acknowledged?: boolean;
  raw_log_ref?: string;
  rule_name?: string;
};

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

function App() {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [filteredAlerts, setFilteredAlerts] = useState<AlertItem[]>([]);
  const [selectedUser, setSelectedUser] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAlerts();
  }, []);

  useEffect(() => {
    let filtered = alerts;
    if (selectedUser) {
      filtered = filtered.filter(a => a.user_id === selectedUser);
    }
    if (severityFilter) {
      filtered = filtered.filter(a => a.severity === severityFilter);
    }
    setFilteredAlerts(filtered);
  }, [alerts, selectedUser, severityFilter]);

  const fetchAlerts = async () => {
    try {
      const res = await axios.get(`${API_BASE}/alerts?limit=200`);
      setAlerts(res.data);
      setFilteredAlerts(res.data);
    } catch (err) {
      console.error('Failed to fetch alerts', err);
      setLoading(false);
    } finally {
      setLoading(false);
    }
  };

  const acknowledgeAlert = async (alertId: string) => {
    try {
      await axios.patch(`${API_BASE}/alerts/${alertId}/acknowledge`);
      // update local state
      setAlerts(alerts.map(a => (a.id === alertId || a.alert_id === alertId) ? {...a, acknowledged: true} : a));
    } catch (err) {
      console.error('Failed to acknowledge', err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <h1 className="text-3xl font-bold mb-6">Cloud Security Monitor</h1>
      <FilterBar
        selectedUser={selectedUser}
        setSelectedUser={setSelectedUser}
        severityFilter={severityFilter}
        setSeverityFilter={setSeverityFilter}
        users={[...new Set(alerts.map(a => a.user_id))]}
      />
      <AlertTable 
        alerts={filteredAlerts} 
        loading={loading} 
        onAcknowledge={acknowledgeAlert}
      />
      {selectedUser && (
        <UserActivityTimeline userId={selectedUser} />
      )}
    </div>
  );
}

export default App;
