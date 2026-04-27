from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class EventType(str, Enum):
    login = "login"
    api_call = "api_call"
    admin_action = "admin_action"

class CloudProvider(str, Enum):
    aws = "aws"
    azure = "azure"
    gcp = "gcp"

class Status(str, Enum):
    success = "success"
    failure = "failure"

class SecurityEvent(BaseModel):
    timestamp: datetime
    user_id: str
    source_ip: str
    geo_location: Optional[str] = None
    event_type: EventType
    cloud_provider: CloudProvider
    status: Status
    resource: Optional[str] = None
    raw_log_ref: Optional[str] = None

class AlertEvent(BaseModel):
    alert_id: str   # UUID
    user_id: str
    risk_score: float = Field(ge=0, le=1)
    severity: str = "medium"
    reason: str
    timestamp: datetime
    triggering_events: list[str] = []
    rule_name: Optional[str] = None