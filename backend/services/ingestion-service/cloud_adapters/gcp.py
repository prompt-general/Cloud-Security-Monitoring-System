import random
import datetime
from typing import List, Dict, Any

def fetch_gcp_logs() -> List[Dict[str, Any]]:
    events = []
    for _ in range(random.randint(0, 2)):
        event = {
            "source": "gcp.audit",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "user": f"user-{random.randint(1,10)}@example.com",
            "ip": f"34.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}",
            "event_type": random.choice(["Login", "Create", "Update"]),
            "status": random.choice(["SUCCESS", "FAILURE"]),
            "resource": f"projects/project-{random.randint(100,999)}/global/{random.choice(['buckets','instances'])}/resource-{random.randint(1,20)}"
        }
        events.append(event)
    return events