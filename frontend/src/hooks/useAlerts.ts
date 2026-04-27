import { useEffect, useState } from "react";
import { AlertItem, fetchAlerts } from "../services/api";

export function useAlerts() {
	const [alerts, setAlerts] = useState<AlertItem[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");

	useEffect(() => {
		let mounted = true;

		async function load() {
			try {
				const data = await fetchAlerts();
				if (mounted) {
					setAlerts(data);
				}
			} catch (err) {
				if (mounted) {
					setError(err instanceof Error ? err.message : "Unknown error");
				}
			} finally {
				if (mounted) {
					setLoading(false);
				}
			}
		}

		load();
		return () => {
			mounted = false;
		};
	}, []);

	return { alerts, loading, error };
}

