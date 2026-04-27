import json
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

def normalize_aws_log(raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Transform AWS CloudTrail log to unified SecurityEvent."""
    try:
        # Map status: Success/Failure -> success/failure
        status = "success" if raw.get("status", "").lower() == "success" else "failure"
        # Map event_type: Login, API_Call, AdminAction -> login, api_call, admin_action
        event_type_raw = raw.get("event_type", "").lower()
        if "login" in event_type_raw:
            event_type = "login"
        elif "api" in event_type_raw:
            event_type = "api_call"
        else:
            event_type = "admin_action"
        
        return {
            "timestamp": raw["timestamp"],
            "user_id": raw["user"],
            "source_ip": raw["ip"],
            "geo_location": None,  # Could be enriched via IP-to-geo later
            "event_type": event_type,
            "cloud_provider": "aws",
            "status": status,
            "resource": raw.get("resource"),
            "raw_log_ref": f"aws_{raw.get('timestamp')}_{raw.get('user')}"  # simplistic
        }
    except Exception as e:
        logger.error(f"Failed to normalize AWS log: {e}, raw: {raw}")
        return None

def normalize_azure_log(raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        status = "success" if raw.get("status", "").lower() == "succeeded" else "failure"
        event_type_raw = raw.get("event_type", "").lower()
        if "login" in event_type_raw:
            event_type = "login"
        elif "write" in event_type_raw or "delete" in event_type_raw:
            event_type = "admin_action"
        else:
            event_type = "api_call"
        
        return {
            "timestamp": raw["timestamp"],
            "user_id": raw["user"],
            "source_ip": raw["ip"],
            "geo_location": None,
            "event_type": event_type,
            "cloud_provider": "azure",
            "status": status,
            "resource": raw.get("resource"),
            "raw_log_ref": f"azure_{raw.get('timestamp')}"
        }
    except Exception as e:
        logger.error(f"Failed to normalize Azure log: {e}")
        return None

def normalize_gcp_log(raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        status = "success" if raw.get("status", "").upper() == "SUCCESS" else "failure"
        event_type_raw = raw.get("event_type", "").lower()
        if "login" in event_type_raw:
            event_type = "login"
        elif "create" in event_type_raw or "update" in event_type_raw:
            event_type = "admin_action"
        else:
            event_type = "api_call"
        
        return {
            "timestamp": raw["timestamp"],
            "user_id": raw["user"],
            "source_ip": raw["ip"],
            "geo_location": None,
            "event_type": event_type,
            "cloud_provider": "gcp",
            "status": status,
            "resource": raw.get("resource"),
            "raw_log_ref": f"gcp_{raw.get('timestamp')}"
        }
    except Exception as e:
        logger.error(f"Failed to normalize GCP log: {e}")
        return None

def normalize(raw_log: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    source = raw_log.get("source", "").lower()
    if "aws" in source:
        return normalize_aws_log(raw_log)
    elif "azure" in source:
        return normalize_azure_log(raw_log)
    elif "gcp" in source:
        return normalize_gcp_log(raw_log)
    else:
        logger.warning(f"Unknown source: {source}")
        return None