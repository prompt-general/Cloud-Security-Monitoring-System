import os
import json
import logging
from confluent_kafka import Consumer, Producer
from transformer import normalize
from opensearch_client import get_opensearch_client, index_normalized_log

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
RAW_TOPIC = "raw-logs"
NORMALIZED_TOPIC = "normalized-logs"

consumer_conf = {
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': 'normalization-service',
    'auto.offset.reset': 'earliest'
}
producer_conf = {'bootstrap.servers': KAFKA_BROKER}

consumer = Consumer(consumer_conf)
producer = Producer(producer_conf)
consumer.subscribe([RAW_TOPIC])

os_client = get_opensearch_client()

def publish_normalized(normalized: dict):
    producer.produce(NORMALIZED_TOPIC, value=json.dumps(normalized))
    producer.poll(0)

def main():
    logger.info("Normalization Service started")
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                logger.error(f"Consumer error: {msg.error()}")
                continue
            
            raw_log = json.loads(msg.value().decode('utf-8'))
            normalized = normalize(raw_log)
            if normalized:
                publish_normalized(normalized)
                index_normalized_log(os_client, normalized)
                logger.info(f"Normalized and indexed log for user {normalized['user_id']}")
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == "__main__":
    main()