CREATE SCHEMA IF NOT EXISTS support;

CREATE TABLE IF NOT EXISTS support.customer_requests (
    request_id VARCHAR(64) PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL,
    last_updated TIMESTAMPTZ NULL,
    customer_email TEXT NULL,
    category TEXT NULL,
    priority VARCHAR(16) NULL,
    subject TEXT NULL,
    body TEXT NULL,
    status VARCHAR(32) NOT NULL,
    source_file TEXT NULL,
    row_hash VARCHAR(64) NULL,
    ingested_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast lookups by status
CREATE INDEX IF NOT EXISTS idx_customer_requests_status
    ON support.customer_requests (status);

-- Index for time-based queries (e.g. dashboards, freshness checks)
CREATE INDEX IF NOT EXISTS idx_customer_requests_created_at
    ON support.customer_requests (created_at);

-- Extra index for deduplication or change detection
CREATE INDEX IF NOT EXISTS idx_customer_requests_row_hash
    ON support.customer_requests (row_hash);
