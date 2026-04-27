import random
import datetime
from typing import List, Dict, Any

def fetch_aws_logs() -> List[Dict[str, Any]]:
    """Simulate AWS CloudTrail events."""
    # In real implementation, you'd use boto3 to pull from S3 or CloudWatch.
    # For MVP, generate 0-3 random events per poll.
    events = []
    for _ in range(random.randint(0, 3)):
        event = {
            "source": "aws.cloudtrail",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "user": f"user_{random.randint(1,10)}@example.com",
            "ip": f"192.168.{random.randint(1,254)}.{random.randint(1,254)}",
            "event_type": random.choice(["Login", "API_Call", "AdminAction"]),
            "status": random.choice(["Success", "Failure"]),
            "region": random.choice(["us-east-1", "eu-west-1"]),
            "resource": f"arn:aws:ec2:us-east-1:123456789012:instance/i-{random.randint(1000,9999)}"
        }
        events.append(event)
    return events