-- Step 1: Create a temporary staging table
CREATE TEMP TABLE staging_customer_requests (
    request_id VARCHAR(64),
    created_at TIMESTAMPTZ,
    last_updated TIMESTAMPTZ,
    customer_email TEXT,
    category TEXT,
    priority VARCHAR(16),
    subject TEXT,
    body TEXT,
    status VARCHAR(32),
    source_file TEXT,
    row_hash VARCHAR(64),
    ingested_at TIMESTAMPTZ
);

-- Step 2: Copy data from CSV into staging table
COPY staging_customer_requests (
    request_id,
    created_at,
    last_updated,
    customer_email,
    category,
    priority,
    subject,
    body,
    status,
    source_file,
    row_hash,
    ingested_at
)
FROM '/opt/airflow/data/processed/cleaned_customer_requests.csv'
DELIMITER ',' CSV HEADER;

-- Step 3: Insert into main table only if not already present
INSERT INTO support.customer_requests (
    request_id,
    created_at,
    last_updated,
    customer_email,
    category,
    priority,
    subject,
    body,
    status,
    source_file,
    row_hash,
    ingested_at
)
SELECT 
    s.request_id,
    s.created_at,
    s.last_updated,
    s.customer_email,
    s.category,
    s.priority,
    s.subject,
    s.body,
    s.status,
    s.source_file,
    s.row_hash,
    COALESCE(s.ingested_at, NOW())  -- fallback to current timestamp
FROM staging_customer_requests s
ON CONFLICT (request_id) DO NOTHING;
