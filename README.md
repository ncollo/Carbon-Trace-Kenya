# Carbon-Trace-Kenya
AI-powered transport emission disclosure platform for Kenyan institutions.

Features
- Document ingestion (PDF, receipts, exports)
- Cross-source reconciliation & anomaly detection
- GHG Protocol calculation engine with Kenya adjustments
- NSE-compliant XBRL + PDF disclosure generation
- Privacy-preserving federated sector analytics (PySyft)

Project structure (backend)

Modules

M1  |  AI Document Intelligence & Data Ingestion
- ingestion/  — document parsing & normalization
- api/routers/upload.py  — `POST /upload`

M2  |  Cross-Source Reconciliation & Anomaly Detection
- reconciliation/ — anomaly pipelines and rule engine
- api/routers/anomalies.py — `GET /anomalies`

M3  |  GHG Protocol Emission Calculation Engine (Core)
- ghg_engine/ — emission factor registry & calculators
- api/routers/calculate.py — `POST /calculate/{company_id}`

M4  |  NSE-Compliant XBRL Report & PDF Generation
- reporting/ — narrative generator, XBRL and PDF builders
- api/routers/reports.py — `GET /reports/{id}/pdf` · `GET /reports/{id}/xbrl`

M5  |  EPRA Sector Analytics & Federated Learning
- federated/ — PySyft aggregator, consent and anonymiser
- api/routers/epra/ — sector analytics endpoints

Core shared infra
- db/ — SQLAlchemy models & session pool
- api/main.py — FastAPI app & router registration
- config.py, dependencies.py, middleware.py — app wiring

Recommended build order
1. `api/main.py` — FastAPI skeleton
2. `db/models.py` — define DB tables
3. `ghg_engine/emission_factor_registry.py` — pin factors
4. `ghg_engine/scope1_calculator.py` — core engine
5. `reconciliation/isolation_forest.py` — anomaly detection
6. `reporting/xbrl_builder.py` — XBRL output
7. `federated/fl_aggregator.py` — federated aggregation

Contributors
Timothy Gitau Muchiri — Team Lead & Backend AI Engineer
EmitIQ Team — EPRA Hackathon 2026

Background processing & object storage

- Configure S3 and Redis in `.env` or environment variables (`use_s3`, `s3_bucket`, `s3_access_key`, `s3_secret_key`, `s3_region`, `redis_url`).
- Worker: run `python worker.py` to start an RQ worker.
- Uploads: when `use_s3=true`, uploaded files are stored in S3 under `uploads/` and the ingestion job is enqueued in Redis (RQ). Otherwise files are stored locally under `data/uploads` and enqueued.

Local dev quickstart

```bash
python -m pip install -r requirements.txt
# start redis (platform-specific)
# run worker in background
python worker.py
# run app
uvicorn api.main:app --reload
```

Running background ingestion

Prerequisites:
- Redis running and reachable at `REDIS_URL` or configured in `config.py` as `redis_url`.
- (Optional) S3-compatible object storage and credentials configured via environment or `config.py` (`use_s3`, `s3_bucket`, `s3_access_key`, `s3_secret_key`, `s3_endpoint`).

Start an RQ worker (from project root):

```bash
python -m pip install -r requirements.txt
# then in one shell
python worker.py
```

Uploads will be stored locally under `data/uploads/` by default. If `use_s3` is enabled, uploads are pushed to the configured bucket and the ingestion job is enqueued to process the S3 object.


