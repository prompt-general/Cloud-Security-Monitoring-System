import axios from "axios";

export type AlertItem = {
	alert_id: string;
	user_id: string;
	risk_score: number;
	severity: "high" | "medium" | "low";
	reason: string;
	timestamp: string;
};

const api = axios.create({
	baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
	timeout: 5000
});

export async function fetchAlerts(): Promise<AlertItem[]> {
	try {
		const response = await api.get<AlertItem[]>("/alerts");
		return response.data;
	} catch {
		return [
			{
				alert_id: "a1",
				user_id: "jane.doe",
				risk_score: 0.92,
				severity: "high",
				reason: "Login from new country",
				timestamp: "2026-04-27T09:12:00Z"
			},
			{
				alert_id: "a2",
				user_id: "svc-account",
				risk_score: 0.61,
				severity: "medium",
				reason: "Access to sensitive resource",
				timestamp: "2026-04-27T09:18:00Z"
			}
		];
	}
}

