import os
import json
import time
from typing import Dict, Any
from confluent_kafka import Producer
from cloud_adapters.aws import fetch_aws_logs
from cloud_adapters.azure import fetch_azure_logs
from cloud_adapters.gcp import fetch_gcp_logs
import logging
from prometheus_client import Counter, start_http_server
from pythonjsonlogger import jsonlogger


def configure_json_logging() -> logging.Logger:
    logger = logging.getLogger("ingestion-service")
    logger.handlers.clear()
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter("%(asctime)s %(name)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


logger = configure_json_logging()

# Kafka configuration
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
RAW_LOGS_TOPIC = "raw-logs"
METRICS_PORT = int(os.getenv("METRICS_PORT", "8001"))

# Metrics
INGESTION_RAW_LOGS_TOTAL = Counter(
    "ingestion_raw_logs_total",
    "Total raw logs produced by ingestion service",
    ["cloud_provider"],
)

producer_conf = {'bootstrap.servers': KAFKA_BROKER}
producer = Producer(producer_conf)

def delivery_report(err, msg):
    """Callback for Kafka produce."""
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def publish_raw_log(log_entry: Dict[str, Any]):
    """Publish a raw log (as JSON string) to Kafka."""
    producer.produce(
        RAW_LOGS_TOPIC,
        key=log_entry.get("source_id", "unknown"),
        value=json.dumps(log_entry),
        callback=delivery_report
    )
    producer.poll(0)
    source = str(log_entry.get("source", "unknown")).lower()
    provider = "aws" if "aws" in source else "azure" if "azure" in source else "gcp" if "gcp" in source else "unknown"
    INGESTION_RAW_LOGS_TOTAL.labels(cloud_provider=provider).inc()

def main_loop():
    """Main loop: fetch logs from each cloud adapter and publish."""
    # For MVP, we run a continuous loop with mock data.
    # In production, each adapter would use its own stream (e.g., SQS, EventHub).
    start_http_server(METRICS_PORT)
    logger.info("Starting Ingestion Service...")
    while True:
        # AWS
        for log in fetch_aws_logs():
            publish_raw_log(log)
        # Azure
        for log in fetch_azure_logs():
            publish_raw_log(log)
        # GCP
        for log in fetch_gcp_logs():
            publish_raw_log(log)
        
        time.sleep(10)  # Poll every 10 seconds for demo

if __name__ == "__main__":
    main_loop()