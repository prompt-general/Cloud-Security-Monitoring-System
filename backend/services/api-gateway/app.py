from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from opensearchpy import OpenSearch, RequestsHttpConnection
from auth import get_current_user  # we'll implement simple auth

app = FastAPI(title="Cloud Security Monitor API")

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React default
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_NAME = os.getenv("DB_NAME", "cloudsec_metadata")
DB_USER = os.getenv("DB_USER", "cloudsec")
DB_PASSWORD = os.getenv("DB_PASSWORD", "cloudsec123")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        cursor_factory=RealDictCursor
    )

# OpenSearch connection
OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST", "opensearch")
OPENSEARCH_PORT = int(os.getenv("OPENSEARCH_PORT", "9200"))

def get_os_client():
    return OpenSearch(
        hosts=[{"host": OPENSEARCH_HOST, "port": OPENSEARCH_PORT}],
        http_compress=True,
        use_ssl=False,
        verify_certs=False,
        connection_class=RequestsHttpConnection
    )

# Pydantic models for responses
class AlertResponse(BaseModel):
    id: int
    user_id: str
    risk_score: float
    reason: str
    severity: str
    timestamp: datetime
    acknowledged: bool
    details: dict

class LogEntry(BaseModel):
    timestamp: datetime
    user_id: str
    source_ip: str
    geo_location: Optional[str]
    event_type: str
    cloud_provider: str
    status: str
    resource: Optional[str]

# -------------------- Alert endpoints --------------------
@app.get("/api/alerts", response_model=List[AlertResponse])
def get_alerts(
    user_id: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    # current_user: dict = Depends(get_current_user)  # uncomment when auth ready
):
    conn = get_db_connection()
    cur = conn.cursor()
    query = "SELECT * FROM alerts WHERE 1=1"
    params = []
    if user_id:
        query += " AND user_id = %s"
        params.append(user_id)
    if severity:
        query += " AND severity = %s"
        params.append(severity)
    query += " ORDER BY timestamp DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@app.get("/api/alerts/{alert_id}")
def get_alert(alert_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM alerts WHERE id = %s", (alert_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Alert not found")
    return row

@app.patch("/api/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE alerts SET acknowledged = TRUE WHERE id = %s", (alert_id,))
    conn.commit()
    updated = cur.rowcount > 0
    cur.close()
    conn.close()
    if not updated:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"status": "acknowledged"}

# -------------------- Log search endpoints --------------------
@app.get("/api/logs", response_model=List[LogEntry])
def search_logs(
    user_id: Optional[str] = None,
    event_type: Optional[str] = None,
    cloud_provider: Optional[str] = None,
    status: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 100
):
    os_client = get_os_client()
    must_conditions = []
    if user_id:
        must_conditions.append({"term": {"user_id": user_id}})
    if event_type:
        must_conditions.append({"term": {"event_type": event_type}})
    if cloud_provider:
        must_conditions.append({"term": {"cloud_provider": cloud_provider}})
    if status:
        must_conditions.append({"term": {"status": status}})
    if start_time or end_time:
        time_range = {}
        if start_time:
            time_range["gte"] = start_time.isoformat()
        if end_time:
            time_range["lte"] = end_time.isoformat()
        must_conditions.append({"range": {"timestamp": time_range}})
    
    query_body = {
        "query": {"bool": {"must": must_conditions}} if must_conditions else {"match_all": {}},
        "size": limit,
        "sort": [{"timestamp": {"order": "desc"}}]
    }
    # Search across all normalized-logs indices
    response = os_client.search(index="normalized-logs-*", body=query_body)
    hits = response["hits"]["hits"]
    logs = [hit["_source"] for hit in hits]
    return logs

# -------------------- User risk summary --------------------
@app.get("/api/users/{user_id}/risk")
def get_user_risk(user_id: str):
    conn = get_db_connection()
    cur = conn.cursor()
    # Get count of high severity alerts for this user in last 24h
    cur.execute("""
        SELECT COUNT(*) as high_risk_alerts 
        FROM alerts 
        WHERE user_id = %s AND severity = 'high' AND timestamp > NOW() - INTERVAL '24 hours'
    """, (user_id,))
    high_count = cur.fetchone()["high_risk_alerts"]
    cur.close()
    conn.close()
    # Simple risk score: if any high alerts => high risk
    risk_level = "high" if high_count > 0 else "low"
    return {"user_id": user_id, "risk_level": risk_level, "alert_count_24h": high_count}

# -------------------- Health check --------------------
@app.get("/health")
def health():
    return {"status": "ok"}