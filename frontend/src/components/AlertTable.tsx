import { AlertItem } from "../App";
import RiskBadge from "./RiskBadge";

type Props = {
  alerts: AlertItem[];
  loading: boolean;
  onAcknowledge: (alertId: string) => void;
};

export default function AlertTable({ alerts, loading, onAcknowledge }: Props) {
  if (loading) {
    return <div className="bg-white p-6 rounded-lg shadow">Loading alerts...</div>;
  }

  if (alerts.length === 0) {
    return <div className="bg-white p-6 rounded-lg shadow">No alerts found.</div>;
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <table className="w-full">
        <thead className="bg-gray-50 border-b">
          <tr>
            <th className="px-6 py-3 text-left text-sm font-semibold">User</th>
            <th className="px-6 py-3 text-left text-sm font-semibold">Reason</th>
            <th className="px-6 py-3 text-left text-sm font-semibold">Score</th>
            <th className="px-6 py-3 text-left text-sm font-semibold">Severity</th>
            <th className="px-6 py-3 text-left text-sm font-semibold">Time</th>
            <th className="px-6 py-3 text-left text-sm font-semibold">Action</th>
          </tr>
        </thead>
        <tbody className="divide-y">
          {alerts.map((alert) => (
            <tr key={alert.alert_id || alert.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 text-sm">{alert.user_id}</td>
              <td className="px-6 py-4 text-sm">{alert.reason}</td>
              <td className="px-6 py-4 text-sm">{alert.risk_score.toFixed(2)}</td>
              <td className="px-6 py-4 text-sm">
                <RiskBadge severity={alert.severity} />
              </td>
              <td className="px-6 py-4 text-sm">
                {new Date(alert.timestamp).toLocaleString()}
              </td>
              <td className="px-6 py-4 text-sm">
                {!alert.acknowledged ? (
                  <button
                    onClick={() => onAcknowledge(alert.alert_id || alert.id || '')}
                    className="px-3 py-1 bg-blue-500 text-white rounded text-xs hover:bg-blue-600"
                  >
                    Acknowledge
                  </button>
                ) : (
                  <span className="text-gray-500">Acknowledged</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
	);
}
