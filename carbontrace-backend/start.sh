#!/bin/bash
# CarbonTrace Kenya — Backend startup script
set -e

echo "================================================"
echo "  CarbonTrace Kenya — Backend API"
echo "  EPRA Hackathon 2026 · Team EmitIQ"
echo "================================================"

# Install dependencies
echo ""
echo "[1/4] Installing Python dependencies..."
pip install -r requirements.txt --break-system-packages -q

# Seed database from CSVs
echo "[2/4] Seeding database from CSV datasets..."
python seed.py

# Train ML models
echo "[3/4] Training Isolation Forest model..."
python ml_models.py

# Start API
echo "[4/4] Starting FastAPI server on http://localhost:8000"
echo ""
echo "  API docs:  http://localhost:8000/docs"
echo "  Health:    http://localhost:8000/api/health"
echo ""
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
