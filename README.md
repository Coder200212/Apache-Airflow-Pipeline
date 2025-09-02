# Airflow Pipeline: Customer Requests Ingestion

This project implements an Apache Airflow pipeline that ingests **customer request data** from CSV files, processes them, and loads them into a **PostgreSQL database** for downstream analytics.

## 📌 Features
- Airflow DAG for **extract → transform → load (ETL)** of customer requests.
- Source data: CSV files (raw → processed → cleaned).
- Target database: PostgreSQL (`support.customer_requests` table).
- Configurable schema and manifest YAML files for flexibility.

## 📂 Repository Structure

airflow-pipeline/
│── dags/
│    └── extraction/customer_requests/
│        ├── customer_requests_pipeline.py
│        ├── ddl.sql
│        ├── load.sql
│        ├── schema.sql
│        ├── schema.yaml
│        └── dataset_manifest.yaml
│── data/
│    └── raw/          # Drop raw CSVs here
│    └── processed/    # Cleaned CSVs land here
│── docker-compose.yaml
│── logs
│── .env
│── .gitignore
│── README.md


## ⚡ Prerequisites
- [Docker](https://docs.docker.com/get-docker/) & Docker Compose
- Git
- (Optional) [pgAdmin](https://www.pgadmin.org/) or any Postgres client

## 🚀 Quickstart
```bash
# Clone the repository
git clone https://github.com/Glynac-AI/airflow-pipeline.git
cd airflow-pipeline

# Start the Airflow + Postgres stack
docker-compose up -d

Then follow instructions in the RUNBOOK.md to run the pipeline