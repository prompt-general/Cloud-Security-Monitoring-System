import React from 'react';
import { formatDistanceToNow } from 'date-fns';
import { AlertItem } from "../App";

const severityColors: Record<string, string> = {
  low: 'bg-green-100 text-green-800',
  medium: 'bg-yellow-100 text-yellow-800',
  high: 'bg-red-100 text-red-800',
  critical: 'bg-purple-100 text-purple-800'
};

type Props = {
  alerts: AlertItem[];
  loading: boolean;
  onAcknowledge: (alertId: string) => void;
};

export default function AlertTable({ alerts, loading, onAcknowledge }: Props) {
  if (loading) return <div className="text-center py-8">Loading alerts...</div>;
  if (alerts.length === 0) return <div className="text-center py-8">No alerts found.</div>;

  return (
    <div className="bg-white shadow rounded-lg overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Time</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reason</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Risk Score</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Severity</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {alerts.map(alert => (
            <tr key={alert.alert_id || alert.id} className={alert.acknowledged ? 'bg-gray-50' : ''}>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {formatDistanceToNow(new Date(alert.timestamp), { addSuffix: true })}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {alert.user_id}
              </td>
              <td className="px-6 py-4 text-sm text-gray-700">{alert.reason}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm">
                {(alert.risk_score * 100).toFixed(0)}%
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`px-2 py-1 text-xs rounded-full ${severityColors[alert.severity] || 'bg-gray-100 text-gray-800'}`}>
                  {alert.severity}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {!alert.acknowledged ? (
                  <button
                    onClick={() => onAcknowledge(alert.alert_id || alert.id || '')}
                    className="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    Acknowledge
                  </button>
                ) : (
                  <span className="text-gray-400 text-sm">Acknowledged</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
	);
}
