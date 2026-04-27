import { useMemo, useState } from "react";
import AlertTable from "../components/AlertTable";
import UserActivityTimeline from "../components/UserActivityTimeline";
import { useAlerts } from "../hooks/useAlerts";

type Activity = {
	timestamp: string;
	description: string;
};

const sampleActivity: Activity[] = [
	{ timestamp: "2026-04-27T09:10:00Z", description: "jane.doe logged in from US" },
	{ timestamp: "2026-04-27T09:14:00Z", description: "admin account changed IAM policy" },
	{ timestamp: "2026-04-27T09:20:00Z", description: "svc-account called security-sensitive API" }
];

export default function Dashboard() {
	const { alerts, loading, error } = useAlerts();
	const [query, setQuery] = useState("");
	const [severity, setSeverity] = useState("all");

	const filteredAlerts = useMemo(() => {
		return alerts.filter((alert) => {
			const matchesUser = alert.user_id.toLowerCase().includes(query.toLowerCase());
			const matchesSeverity = severity === "all" || alert.severity === severity;
			return matchesUser && matchesSeverity;
		});
	}, [alerts, query, severity]);

	return (
		<div className="container">
			<div className="header">
				<h1>Cloud Security Dashboard</h1>
				<small>{alerts.length} total alerts</small>
			</div>

			<div className="controls">
				<input
					placeholder="Filter by user"
					value={query}
					onChange={(e) => setQuery(e.target.value)}
				/>
				<select value={severity} onChange={(e) => setSeverity(e.target.value)}>
					<option value="all">All severities</option>
					<option value="high">High</option>
					<option value="medium">Medium</option>
				</select>
			</div>

			{loading && <p>Loading alerts...</p>}
			{error && <p>Failed to load alerts: {error}</p>}

			<div className="grid">
				<section className="card">
					<h2>Recent Alerts</h2>
					<AlertTable alerts={filteredAlerts} />
				</section>
				<section className="card">
					<h2>User Activity</h2>
					<UserActivityTimeline activity={sampleActivity} />
				</section>
			</div>
		</div>
	);
}
