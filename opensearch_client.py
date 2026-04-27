import os
from opensearchpy import OpenSearch, RequestsHttpConnection
import logging

logger = logging.getLogger(__name__)

OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST", "opensearch")
OPENSEARCH_PORT = int(os.getenv("OPENSEARCH_PORT", "9200"))

def get_opensearch_client():
    return OpenSearch(
        hosts=[{"host": OPENSEARCH_HOST, "port": OPENSEARCH_PORT}],
        http_compress=True,
        use_ssl=False,
        verify_certs=False,
        connection_class=RequestsHttpConnection
    )

def index_normalized_log(client, log: dict):
    """Index log into OpenSearch with index name 'normalized-logs-YYYY.MM.DD'."""
    index_name = f"normalized-logs-{log['timestamp'][:10]}".replace("-", ".")
    try:
        response = client.index(index=index_name, body=log)
        logger.debug(f"Indexed log: {response['_id']}")
    except Exception as e:
        logger.error(f"Failed to index log: {e}")