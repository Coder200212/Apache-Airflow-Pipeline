from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timezone, timedelta
import pandas as pd
import os
import hashlib


BASE_DIR = os.path.dirname(__file__)
DAG_ID = "customer_requests_pipeline"
EXTRACTION_PATH = os.path.join(BASE_DIR, "extraction/customer_requests")

default_args = {
    "owner": "emmanuel",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# Updated config for actual dataset schema
manifest = {
    "transformations": {
        "trims": [],
        "lowercase": ["status"],
        "coalesce_nulls": {"priority": "medium"},
        "row_hash": {"enabled": True, "columns": ["status"]}
    }
}

val = {
    "required_columns": ["request_id", "created_at", "customer_email", "status"],
    "non_nullable": ["request_id", "customer_email"],
    "allowed_values": {"status": ["done"]}
}

src = {
    "path": "/opt/airflow/data/raw",
    "file_pattern": "*.csv"
}

def find_latest_csv(folder, pattern):
    import glob
    files = glob.glob(os.path.join(folder, pattern))
    return max(files, key=os.path.getctime)

def process_customer_requests():
    xform = manifest.get("transformations", {})
    csv_folder = src["path"]
    file_pattern = src.get("file_pattern", "*.csv")
    latest_file = find_latest_csv(csv_folder, file_pattern)

    df = pd.read_csv(latest_file)

    # Required columns
    req_cols = val.get("required_columns", [])
    missing = [c for c in req_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Non-nullable
    non_nullable = val.get("non_nullable", [])
    for c in non_nullable:
        if c in df.columns:
            df = df[df[c].notna()]

    # Dtypes
    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce", utc=True)
        df = df[df["created_at"].notna()]
    if "last_updated" in df.columns:
        df["last_updated"] = pd.to_datetime(df["last_updated"], errors="coerce", utc=True)

    # Status filter
    allowed_status = set([s.lower() for s in val.get("allowed_values", {}).get("status", [])])
    if "status" in df.columns:
        df["status"] = df["status"].astype(str)
        df = df[df["status"].str.lower() == "done"]

    # Trims / lowercase
    trims = xform.get("trims", [])
    for c in trims:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()
    lower = xform.get("lowercase", [])
    for c in lower:
        if c in df.columns:
            df[c] = df[c].astype(str).str.lower()

    # Coalesce defaults
    coalesce = xform.get("coalesce_nulls", {})
    for c, default in coalesce.items():
        if c in df.columns:
            df[c] = df[c].fillna(default)

    # Audit columns
    df["source_file"] = os.path.basename(latest_file)
    df["ingested_at"] = datetime.now(timezone.utc)

    # Row hash
    rh = xform.get("row_hash", {})
    if rh.get("enabled"):
        cols = rh.get("columns", [])
        def md5_row(row):
            items = [str(row[c]) if c in row else "" for c in cols]
            return hashlib.md5("|".join(items).encode("utf-8")).hexdigest()
        df["row_hash"] = df.apply(md5_row, axis=1)

    # Output cleaned file
    out_dir = "/opt/airflow/data/processed"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "cleaned_customer_requests.csv")
    df.to_csv(out_path, index=False)

# Define the DAG
with DAG(
    dag_id=DAG_ID,
    default_args=default_args,
    description="Customer Requests Pipeline",
    schedule_interval=None,
    start_date=datetime(2025, 1, 1),
    catchup=False,
    template_searchpath=[os.path.join(BASE_DIR, "extraction/customer_requests")],
) as dag:

    import logging

    try:
        with open("/opt/airflow/dags/extraction/customer_requests/ddl.sql", "r") as file:
            ddl_sql = file.read()
    except Exception as e:
        logging.error(f"Failed to read DDL file: {e}")
        ddl_sql = "SELECT 1;"  # fallback dummy SQL

    create_table = PostgresOperator(
        task_id="create_table",
        postgres_conn_id="postgres_default",
        sql="ddl.sql",
    )

    validate_and_transform = PythonOperator(
        task_id="validate_and_transform",
        python_callable=process_customer_requests
    )

    load_to_postgres = PostgresOperator(
        task_id="load_to_postgres",
        postgres_conn_id="postgres_default",
        sql="load.sql",
    )

    # 👇 Define task dependencies
    create_table >> validate_and_transform >> load_to_postgres
