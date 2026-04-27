import json
import logging
import os
from confluent_kafka import Consumer, Producer
from opensearchpy import OpenSearch, RequestsHttpConnection
from prometheus_client import Counter, start_http_server
from pythonjsonlogger import jsonlogger
from transformer import normalize


def configure_json_logging() -> logging.Logger:
	logger = logging.getLogger("normalization-service")
	logger.handlers.clear()
	handler = logging.StreamHandler()
	handler.setFormatter(jsonlogger.JsonFormatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
	logger.addHandler(handler)
	logger.setLevel(logging.INFO)
	return logger


logger = configure_json_logging()

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
RAW_TOPIC = "raw-logs"
NORMALIZED_TOPIC = "normalized-logs"
METRICS_PORT = int(os.getenv("METRICS_PORT", "8001"))

KAFKA_CONSUMER_GROUP = os.getenv("KAFKA_CONSUMER_GROUP", "normalization-service")
KAFKA_AUTO_OFFSET_RESET = os.getenv("KAFKA_AUTO_OFFSET_RESET", "earliest")

OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST", "opensearch")
OPENSEARCH_PORT = int(os.getenv("OPENSEARCH_PORT", "9200"))

# Metrics
NORMALIZATION_ERRORS_TOTAL = Counter(
	"normalization_errors_total",
	"Total normalization errors",
)
NORMALIZED_LOGS_TOTAL = Counter(
	"normalization_normalized_logs_total",
	"Total normalized logs emitted",
	["cloud_provider"],
)


def get_opensearch_client() -> OpenSearch:
	return OpenSearch(
		hosts=[{"host": OPENSEARCH_HOST, "port": OPENSEARCH_PORT}],
		http_compress=True,
		use_ssl=False,
		verify_certs=False,
		connection_class=RequestsHttpConnection,
	)


def index_normalized_log(client: OpenSearch, normalized_log: dict) -> None:
	index_name = f"normalized-logs-{normalized_log['timestamp'][:10]}".replace("-", ".")
	client.index(index=index_name, body=normalized_log)


consumer_conf = {
	"bootstrap.servers": KAFKA_BROKER,
	"group.id": KAFKA_CONSUMER_GROUP,
	"auto.offset.reset": KAFKA_AUTO_OFFSET_RESET,
	"max.poll.interval.ms": 300000,
	"session.timeout.ms": 10000,
	"heartbeat.interval.ms": 3000,
	"max.partition.fetch.bytes": 1048576,
}
producer_conf = {"bootstrap.servers": KAFKA_BROKER}


def publish_normalized(producer: Producer, normalized_event: dict) -> None:
	producer.produce(NORMALIZED_TOPIC, value=json.dumps(normalized_event))
	producer.poll(0)


def main() -> None:
	start_http_server(METRICS_PORT)
	consumer = Consumer(consumer_conf)
	producer = Producer(producer_conf)
	os_client = get_opensearch_client()
	consumer.subscribe([RAW_TOPIC])

	logger.info("Normalization Service started")
	try:
		while True:
			msg = consumer.poll(1.0)
			if msg is None:
				continue
			if msg.error():
				logger.error("Consumer error", extra={"error": str(msg.error())})
				NORMALIZATION_ERRORS_TOTAL.inc()
				continue

			try:
				raw_log = json.loads(msg.value().decode("utf-8"))
				normalized = normalize(raw_log)
				if not normalized:
					NORMALIZATION_ERRORS_TOTAL.inc()
					continue

				publish_normalized(producer, normalized)
				index_normalized_log(os_client, normalized)
				NORMALIZED_LOGS_TOTAL.labels(cloud_provider=normalized.get("cloud_provider", "unknown")).inc()
				logger.info("Normalized log", extra={"user_id": normalized.get("user_id")})
			except Exception as exc:
				NORMALIZATION_ERRORS_TOTAL.inc()
				logger.exception("Normalization processing failure", extra={"error": str(exc)})
	except KeyboardInterrupt:
		logger.info("Normalization Service interrupted")
	finally:
		consumer.close()


if __name__ == "__main__":
	main()
