from __future__ import annotations
import os
import hashlib
import pandas as pd
from datetime import datetime, timezone

def process_customer_requests(manifest: dict, src: dict, val: dict):
    # Configs
    xform = manifest.get("transformations", {})
    csv_folder = src["path"]
    file_pattern = src.get("file_pattern", "*.csv")

    # Get latest CSV file
    latest_file = find_latest_csv("/opt/airflow/data/sharepoint/customer_requests", "*.csv")
    

    # Load CSV
    df = pd.read_csv(latest_file)

    # ✅ Required columns (real dataset schema)
    req_cols = ["request_id", "created_at", "customer_email", "status"]
    missing = [c for c in req_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # ✅ Drop rows missing key identifiers
    non_nullable = ["request_id", "customer_email"]
    for c in non_nullable:
        if c in df.columns:
            df = df[df[c].notna()]

    # ✅ Date parsing
    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce", utc=True)
        df = df[df["created_at"].notna()]
    if "last_updated" in df.columns:
        df["last_updated"] = pd.to_datetime(df["last_updated"], errors="coerce", utc=True)

    # ✅ Keep only "done" status (case-insensitive)
    if "status" in df.columns:
        df["status"] = df["status"].astype(str)
        df = df[df["status"].str.lower() == "done"]

    # ✅ Trims / lowercase
    trims = xform.get("trims", [])
    for c in trims:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()
    lower = xform.get("lowercase", [])
    for c in lower:
        if c in df.columns:
            df[c] = df[c].astype(str).str.lower()

    # ✅ Fill defaults
    coalesce = xform.get("coalesce_nulls", {})
    for c, default in coalesce.items():
        if c in df.columns:
            df[c] = df[c].fillna(default)

    # ✅ Add audit columns
    df["source_file"] = os.path.basename(latest_file)
    df["ingested_at"] = datetime.now(timezone.utc)

    # ✅ Optional row hash
    rh = xform.get("row_hash", {})
    if rh.get("enabled"):
        cols = rh.get("columns", [])
        def md5_row(row):
            items = [str(row[c]) if c in row else "" for c in cols]
            return hashlib.md5("|".join(items).encode("utf-8")).hexdigest()
        df["row_hash"] = df.apply(md5_row, axis=1)

    # ✅ Save cleaned file
    out_dir = "/opt/airflow/data/processed"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"cleaned_{os.path.basename(latest_file)}")
    df.to_csv(out_file, index=False)

    return out_file
