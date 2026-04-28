import os
import json
import time
import logging
import hashlib
from typing import Any

from confluent_kafka import Consumer, Producer, KafkaError
from prometheus_client import Counter, Histogram, start_http_server
from pythonjsonlogger import jsonlogger

from baseline_engine import BaselineEngine
from redis_client import get_redis_client


# Logging
logger = logging.getLogger("anomaly-service")
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(name)s %(levelname)s %(message)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)


# Prometheus metrics
ANOMALY_PROCESSED = Counter(
    "anomaly_processed_events_total", "Total number of events processed by anomaly service"
)
ANOMALY_ALERTS = Counter(
    "anomaly_alerts_total", "Total number of anomaly alerts produced"
)
ANOMALY_SCORES = Histogram("anomaly_scores", "Observed anomaly scores")


BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
INPUT_TOPIC = os.getenv("NORMALIZED_TOPIC", "normalized-logs")
OUTPUT_TOPIC = os.getenv("ALERTS_TOPIC", "security-alerts")
GROUP_ID = os.getenv("ANOMALY_GROUP", "anomaly-service-group")
METRICS_PORT = int(os.getenv("METRICS_PORT", "8003"))
ANOMALY_THRESHOLD = float(os.getenv("ANOMALY_THRESHOLD", "0.8"))
DEDUP_TTL = int(os.getenv("ANOMALY_DEDUP_TTL", "300"))


def make_consumer() -> Consumer:
    conf = {
        "bootstrap.servers": BOOTSTRAP_SERVERS,
        "group.id": GROUP_ID,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": True,
        "session.timeout.ms": 6000,
        "max.poll.interval.ms": 300000,
    }
    return Consumer(conf)


def make_producer() -> Producer:
    return Producer({"bootstrap.servers": BOOTSTRAP_SERVERS})


def alert_dedupe_key(event: dict, score: float) -> str:
    uid = str(event.get("user_id") or event.get("user", "unknown"))
    payload = f"{uid}:{score}:{event.get('event_id', '')}"
    return hashlib.sha1(payload.encode()).hexdigest()


def main():
    start_http_server(METRICS_PORT)
    logger.info("metrics_server_started", extra={"port": METRICS_PORT})

    redis_client = get_redis_client()
    engine = BaselineEngine()

    consumer = make_consumer()
    consumer.subscribe([INPUT_TOPIC])
    producer = make_producer()

    logger.info("anomaly_service_started", extra={"input_topic": INPUT_TOPIC, "output_topic": OUTPUT_TOPIC})

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                time.sleep(0.1)
                continue
            if msg.error():
                logger.error("kafka_error", extra={"error": str(msg.error())})
                continue

            try:
                payload = msg.value().decode("utf-8")
                event = json.loads(payload)
            except Exception as e:
                logger.exception("invalid_message", extra={"error": str(e)})
                continue

            ANOMALY_PROCESSED.inc()

            try:
                score = engine.score(event)
                ANOMALY_SCORES.observe(score)
            except Exception as e:
                logger.exception("scoring_error", extra={"error": str(e)})
                continue

            try:
                if score >= ANOMALY_THRESHOLD:
                    dedupe = alert_dedupe_key(event, score)
                    dedupe_key = f"anomaly_alert:{dedupe}"
                    if redis_client.exists(dedupe_key):
                        logger.info("duplicate_alert_skipped", extra={"dedupe_key": dedupe_key})
                    else:
                        alert = {
                            "source": "anomaly-service",
                            "user_id": event.get("user_id") or event.get("user"),
                            "score": score,
                            "event": event,
                            "timestamp": int(time.time() * 1000),
                        }
                        producer.produce(OUTPUT_TOPIC, json.dumps(alert).encode("utf-8"))
                        producer.flush()
                        redis_client.setex(dedupe_key, DEDUP_TTL, "1")
                        ANOMALY_ALERTS.inc()
                        logger.info("anomaly_alert_produced", extra={"user_id": alert.get("user_id"), "score": score})
                else:
                    logger.debug("no_anomaly", extra={"score": score})
            except Exception as e:
                logger.exception("alert_production_error", extra={"error": str(e)})

    except KeyboardInterrupt:
        logger.info("shutting_down")
    finally:
        try:
            consumer.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
