import os
import json
import uuid
import logging
from datetime import datetime
from confluent_kafka import Consumer, Producer
from rules.base_rules import evaluate_failed_login_burst, evaluate_high_risk_api

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
NORMALIZED_TOPIC = "normalized-logs"
ALERTS_TOPIC = "security-alerts"

consumer_conf = {
	'bootstrap.servers': KAFKA_BROKER,
	'group.id': 'rule-engine',
	'auto.offset.reset': 'earliest'
}
producer_conf = {'bootstrap.servers': KAFKA_BROKER}

consumer = Consumer(consumer_conf)
producer = Producer(producer_conf)
consumer.subscribe([NORMALIZED_TOPIC])


def create_alert(event: dict, reason: str, risk_score: float, rule_name: str) -> dict:
	return {
		"alert_id": str(uuid.uuid4()),
		"user_id": event["user_id"],
		"risk_score": risk_score,
		"severity": "high" if risk_score > 0.7 else "medium",
		"reason": reason,
		"timestamp": datetime.utcnow().isoformat() + "Z",
		"triggering_events": [event.get("raw_log_ref", "unknown")],
		"rule_name": rule_name
	}


def main():
	logger.info("Rule Engine Service started")
	try:
		while True:
			msg = consumer.poll(1.0)
			if msg is None:
				continue
			if msg.error():
				logger.error(f"Consumer error: {msg.error()}")
				continue

			event = json.loads(msg.value().decode('utf-8'))
			alerts = []

			# Rule 1: failed login burst
			if evaluate_failed_login_burst(event):
				alert = create_alert(event, "More than 5 failed logins in 10 minutes", 0.85, "FailedLoginBurst")
				alerts.append(alert)

			# Rule 2: high-risk API access
			if evaluate_high_risk_api(event):
				alert = create_alert(event, "Access to sensitive resource", 0.6, "HighRiskApiAccess")
				alerts.append(alert)

			for alert in alerts:
				producer.produce(ALERTS_TOPIC, value=json.dumps(alert))
				producer.poll(0)
				logger.info(f"Alert produced: {alert['reason']} for {alert['user_id']}")
	except KeyboardInterrupt:
		pass
	finally:
		consumer.close()


if __name__ == "__main__":
	main()
