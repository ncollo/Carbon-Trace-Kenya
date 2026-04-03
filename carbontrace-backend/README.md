# CarbonTrace Kenya — Backend API

FastAPI backend with SQLite database seeded from CSV datasets.
No hardcoded data — all figures derived from 12,657 CSV records.

## Quick start

```bash
cd carbontrace-backend
./start.sh          # installs, seeds DB, trains model, starts API
```

## What this runs

1. Seeds SQLite (`carbontrace.db`) from `/home/claude/dataset/csv/`
2. Trains Isolation Forest on 2,400 fuel card records
3. Starts FastAPI on `http://localhost:8000`

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/health | Health + DB record counts |
| GET | /api/overview/kpis | Aggregated KPIs from DB |
| GET | /api/overview/quarterly-trend | Quarterly emissions from fuel records |
| GET | /api/overview/scope-breakdown | Scope 1/3 split from DB |
| GET | /api/overview/fleet-by-class | Fleet emissions by vehicle class |
| GET | /api/overview/companies | All 67 GHG company summaries |
| GET | /api/ingestion/files | Uploaded file log |
| GET | /api/ingestion/extraction-stats | Record counts by type |
| POST | /api/ingestion/upload | Upload CSV/Excel file → ingest to DB |
| GET | /api/reconcile/flags | Pending anomaly flags from DB |
| PATCH | /api/reconcile/flags/{id}/resolve | Resolve an anomaly flag |
| GET | /api/reconcile/quality | Data quality stats |
| GET | /api/reconcile/validation-log | Full validation log |
| POST | /api/reconcile/run-model | Run Isolation Forest on single record |
| GET | /api/calculator/results | GHG calculation from DB records |
| GET | /api/calculator/emission-factors | EF register from DB |
| GET | /api/calculator/intensity-trend | Intensity trend from GHG summaries |
| GET | /api/calculator/scope-by-vehicle | Scope 1 by vehicle class |
| GET | /api/report/summary | Full report summary |
| GET | /api/report/narrative-samples | Real narrative samples from training CSV |
| GET | /api/epra/kpis | EPRA sector KPIs |
| GET | /api/epra/ndc-trajectory | Year-on-year vs NDC pathway |
| GET | /api/epra/sector-breakdown | All 10 EPRA sectors |
| GET | /api/epra/league-table | Company intensity ranking |
| GET | /api/epra/county-distribution | Emissions by county |
| POST | /api/epra/simulate | Run policy simulation (ML model) |

## Database

SQLite · `carbontrace.db` · 9 tables · seeded from 20 CSV files

| Table | Records |
|-------|---------|
| fuel_records | 3,015 |
| anomaly_records | 500 |
| travel_records | 1,340 |
| commute_records | 4,020 |
| ghg_summary | 67 |
| emission_factors | 13 |
| policy_simulations | 500 |
| epra_sector_analytics | 10 |
| uploaded_files | 0 (grows with uploads) |
