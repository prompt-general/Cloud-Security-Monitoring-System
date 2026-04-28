from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Any


class BaselineEngine:
	def __init__(self) -> None:
		self.user_logins = defaultdict(list)
		self.user_ips = defaultdict(set)

	def score(self, event: Dict[str, Any]) -> float:
		user_id = event.get("user_id", "unknown")
		timestamp = datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))
		source_ip = event.get("source_ip", "")

		# Keep a rolling one-day window for login frequency.
		day_ago = timestamp - timedelta(hours=24)
		self.user_logins[user_id] = [ts for ts in self.user_logins[user_id] if ts > day_ago]

		freq_spike = min(len(self.user_logins[user_id]) / 30.0, 1.0)
		ip_novelty = 1.0 if source_ip and source_ip not in self.user_ips[user_id] else 0.0
		geo_risk = 0.2 if event.get("geo_location") in (None, "", "unknown") else 0.0

		self.user_logins[user_id].append(timestamp)
		if source_ip:
			self.user_ips[user_id].add(source_ip)

		# anomaly_score = w1*geo_risk + w2*ip_novelty + w3*frequency_spike
		return round((0.2 * geo_risk) + (0.4 * ip_novelty) + (0.4 * freq_spike), 4)
