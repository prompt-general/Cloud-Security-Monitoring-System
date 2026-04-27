-- Users table (managed by API service, but schema defined here)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255),
    role VARCHAR(20) DEFAULT 'viewer',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Alert history
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    risk_score FLOAT,
    reason TEXT,
    details JSONB,
    timestamp TIMESTAMPTZ NOT NULL,
    acknowledged BOOLEAN DEFAULT FALSE
);

-- Rule configurations (for rule-engine service)
CREATE TABLE IF NOT EXISTS detection_rules (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    rule_definition JSONB NOT NULL,   -- e.g., {"failed_logins_threshold": 5, "time_window_minutes": 10}
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert a default rule (optional)
INSERT INTO detection_rules (name, description, rule_definition)
VALUES ('Failed Login Burst', 'Alert when >5 failed logins in 10 minutes', 
        '{"event_type": "login", "status": "failure", "threshold": 5, "window_minutes": 10}')
ON CONFLICT (name) DO NOTHING;