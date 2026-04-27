import { AlertItem } from "../services/api";
import RiskBadge from "./RiskBadge";

type Props = {
	alerts: AlertItem[];
};

export default function AlertTable({ alerts }: Props) {
	if (alerts.length === 0) {
		return <p>No alerts found.</p>;
	}

	return (
		<table>
			<thead>
				<tr>
					<th>User</th>
					<th>Reason</th>
					<th>Score</th>
					<th>Severity</th>
				</tr>
			</thead>
			<tbody>
				{alerts.map((alert) => (
					<tr key={alert.alert_id}>
						<td>{alert.user_id}</td>
						<td>{alert.reason}</td>
						<td>{alert.risk_score.toFixed(2)}</td>
						<td>
							<RiskBadge severity={alert.severity} />
						</td>
					</tr>
				))}
			</tbody>
		</table>
	);
}
