
# Runbook: Airflow Pipeline for Customer Requests

This runbook provides step-by-step instructions to operate the Airflow ETL pipeline.

---

## ✅ Prerequisites
- Airflow stack running via `docker-compose`
- CSV files available in `data/raw/`

---

## ▶️ Starting & Stopping the Stack
```bash
# Start services (Airflow, Postgres, Scheduler, Webserver, etc.)
docker-compose up -d

# Stop services
docker-compose down

Access Airflow UI: http://localhost:8080

Default credentials: airflow / airflow

## Placing CSV Files

- Place raw CSV files into:

airflow-pipeline/data/raw/


Example:

data/raw/customer_requests_2025-08-25.csv


- The pipeline processes raw files → saves cleaned files in:

data/processed/cleaned_customer_requests.csv


## 🏃 Running the DAG

- Open Airflow UI → DAGs

- Enable customer_requests_ingestion

- Trigger DAG manually or wait for schedule


## 🔍 Verifying Data Load

Inside the Postgres container:

docker exec -it airflow-pipeline-postgres-1 psql -U airflow -d airflow


Then run:

SELECT COUNT(*) FROM support.customer_requests;
SELECT * FROM support.customer_requests LIMIT 10;

## 🛠️ Troubleshooting

- Container not starting:
Check logs:

docker-compose logs airflow-webserver
docker-compose logs airflow-scheduler


- CSV not found error:
Ensure file is in data/raw/ and volume is mounted correctly in docker-compose.yaml.

- DAG not appearing:
Check file path inside container:

docker exec -it airflow-pipeline-airflow-scheduler-1 ls /opt/airflow/dags/extraction/customer_requests/


## Postgres permission issues:
- Confirm schema exists:

CREATE SCHEMA IF NOT EXISTS support;

## 📌 Notes

- All SQL scripts (ddl.sql, schema.sql, load.sql) live under:

dags/extraction/customer_requests/


- Modify dataset_manifest.yaml or schema.yaml to adapt schema.




👉 Do you want me to also **add both files (`README.md` + `RUNBOOK.md`) into your local repo paths** so you can just `git add . && git commit -m "docs: add readme and runbook"`?
