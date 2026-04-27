import random
import datetime
from typing import List, Dict, Any

def fetch_azure_logs() -> List[Dict[str, Any]]:
    events = []
    for _ in range(random.randint(0, 2)):
        event = {
            "source": "azure.activity",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "user": f"user{random.randint(1,10)}@onmicrosoft.com",
            "ip": f"10.0.{random.randint(1,254)}.{random.randint(1,254)}",
            "event_type": random.choice(["Login", "Write", "Delete"]),
            "status": random.choice(["Succeeded", "Failed"]),
            "resource": f"/subscriptions/xxx/resourceGroups/rg1/providers/Microsoft.Compute/virtualMachines/vm{random.randint(1,5)}"
        }
        events.append(event)
    return events