from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

# In-memory store for sliding window counts (MVP: use Redis later)
failed_login_windows = defaultdict(list)  # user_id -> list of timestamps

def evaluate_failed_login_burst(event: Dict[str, Any], threshold: int = 5, window_minutes: int = 10) -> bool:
    """Return True if user has > threshold failed logins in the last window_minutes."""
    if event["event_type"] != "login" or event["status"] != "failure":
        return False
    
    user = event["user_id"]
    now = datetime.fromisoformat(event["timestamp"].replace('Z', '+00:00'))
    
    # Clean old entries
    cutoff = now - timedelta(minutes=window_minutes)
    failed_login_windows[user] = [ts for ts in failed_login_windows[user] if ts > cutoff]
    
    failed_login_windows[user].append(now)
    count = len(failed_login_windows[user])
    
    if count >= threshold:
        logger.info(f"Failed login burst for {user}: {count} failures in {window_minutes} min")
        return True
    return False

def evaluate_new_country(event: Dict[str, Any], user_history: Dict[str, set]) -> bool:
    """Simple new country detection if geo_location present."""
    # For MVP, always false unless we have geo data
    return False

def evaluate_high_risk_api(event: Dict[str, Any]) -> bool:
    """Example: alert on API calls to sensitive resources."""
    sensitive_resources = ["iam", "security", "admin"]
    resource = event.get("resource", "").lower()
    if any(s in resource for s in sensitive_resources):
        return True
    return False