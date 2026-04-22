#!/usr/bin/env python
"""Test script to verify imports work correctly."""
import sys
from pathlib import Path

project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print("[TEST] Testing imports...")

try:
    from ingestion.ingest_job import process_upload
    print("[OK] ingestion.ingest_job imported successfully")
except Exception as e:
    print(f"[ERROR] Failed to import ingest_job: {e}")
    sys.exit(1)

try:
    from ingestion.dataset_loader import DatasetLoader
    print("[OK] ingestion.dataset_loader imported successfully")
except Exception as e:
    print(f"[ERROR] Failed to import dataset_loader: {e}")
    sys.exit(1)

try:
    from db.models import JobRecord
    print("[OK] db.models imported successfully")
except Exception as e:
    print(f"[ERROR] Failed to import db.models: {e}")
    sys.exit(1)

print("\n[SUCCESS] All core imports working!")
