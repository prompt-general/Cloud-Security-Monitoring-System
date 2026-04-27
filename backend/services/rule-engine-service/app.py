import os
import json
import uuid
import logging
from datetime import datetime
from confluent_kafka import Consumer, Producer
from prometheus_client import Counter, start_http_server
from pythonjsonlogger import jsonlogger
from rules.base_rules import evaluate_failed_login_burst, evaluate_high_risk_api


def configure_json_logging() -> logging.Logger:
	logger = logging.getLogger("rule-engine-service")
	logger.handlers.clear()
	handler = logging.StreamHandler()
	handler.setFormatter(jsonlogger.JsonFormatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
	logger.addHandler(handler)
	logger.setLevel(logging.INFO)
	return logger


logger = configure_json_logging()

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
NORMALIZED_TOPIC = "normalized-logs"
ALERTS_TOPIC = "security-alerts"
METRICS_PORT = int(os.getenv("METRICS_PORT", "8001"))
KAFKA_CONSUMER_GROUP = os.getenv("KAFKA_CONSUMER_GROUP", "rule-engine-service")
KAFKA_AUTO_OFFSET_RESET = os.getenv("KAFKA_AUTO_OFFSET_RESET", "earliest")

consumer_conf = {
	'bootstrap.servers': KAFKA_BROKER,
	'group.id': KAFKA_CONSUMER_GROUP,
	'auto.offset.reset': KAFKA_AUTO_OFFSET_RESET,
	'max.poll.interval.ms': 300000,
	'session.timeout.ms': 10000,
	'heartbeat.interval.ms': 3000,
	'max.partition.fetch.bytes': 1048576,
}
producer_conf = {'bootstrap.servers': KAFKA_BROKER}

consumer = Consumer(consumer_conf)
producer = Producer(producer_conf)
consumer.subscribe([NORMALIZED_TOPIC])

RULE_EVALUATIONS_TOTAL = Counter(
	"rule_evaluations_total",
	"Total rule evaluations",
	["rule_name", "triggered"],
)


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
	start_http_server(METRICS_PORT)
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
			failed_burst = evaluate_failed_login_burst(event)
			RULE_EVALUATIONS_TOTAL.labels(rule_name="FailedLoginBurst", triggered=str(failed_burst).lower()).inc()
			if failed_burst:
				alert = create_alert(event, "More than 5 failed logins in 10 minutes", 0.85, "FailedLoginBurst")
				alerts.append(alert)

			# Rule 2: high-risk API access
			high_risk_api = evaluate_high_risk_api(event)
			RULE_EVALUATIONS_TOTAL.labels(rule_name="HighRiskApiAccess", triggered=str(high_risk_api).lower()).inc()
			if high_risk_api:
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
