#!/usr/bin/env python3
"""
SQLite Setup & Verification Script
Ensures SQLite database is properly initialized with all tables and sample data
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

print("[INFO] ============================================")
print("[INFO] SQLite Setup & Verification")
print("[INFO] ============================================\n")

# Step 1: Verify .env file exists
print("[INFO] Step 1: Checking .env configuration...")
if not os.path.exists('.env'):
    print("[FAIL] .env file not found!")
    sys.exit(1)

from config import settings
print(f"[OK] DATABASE_URL: {settings.database_url}")
print(f"[OK] DEBUG: {settings.app_name}\n")

if not settings.database_url.startswith("sqlite"):
    print("[WARN] Not using SQLite!")
    sys.exit(1)

# Step 2: Create database and run migrations
print("[INFO] Step 2: Initializing database...")
try:
    from db.session import init_db, SessionLocal, engine
    from db.models import Base, Company, User
    
    # Create all tables
    init_db()
    print("[OK] Database tables created successfully\n")
except Exception as e:
    print(f"[FAIL] Database initialization failed: {e}")
    sys.exit(1)

# Step 3: Verify tables exist
print("[INFO] Step 3: Verifying tables...")
try:
    from sqlalchemy import inspect, text
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    expected_tables = ['companies', 'users']
    
    for table in expected_tables:
        if table in tables:
            # Get column info
            columns = inspector.get_columns(table)
            col_names = [col['name'] for col in columns]
            print(f"[OK] Table '{table}' exists with columns: {', '.join(col_names)}")
        else:
            print(f"[WARN] Table '{table}' not found")
    
    print()
except Exception as e:
    print(f"[FAIL] Table verification failed: {e}\n")

# Step 4: Test database connection
print("[INFO] Step 4: Testing database connection...")
try:
    db = SessionLocal()
    
    # Check if it's an existing database with data
    company_count = db.query(Company).count()
    user_count = db.query(User).count()
    
    print(f"[OK] Connected successfully!")
    print(f"[INFO] Companies in database: {company_count}")
    print(f"[INFO] Users in database: {user_count}\n")
    
    db.close()
except Exception as e:
    print(f"[FAIL] Connection test failed: {e}")
    sys.exit(1)

# Step 5: Seed sample data if empty
print("[INFO] Step 5: Checking if sample data needed...")
if company_count == 0:
    print("[INFO] Database is empty. Loading sample data...")
    try:
        from seed_db import seed_database
        seed_database()
        print("[OK] Sample data loaded successfully\n")
    except Exception as e:
        print(f"[WARN] Sample data loading failed: {e}")
        print("[INFO] You can run: python seed_db.py\n")
else:
    print(f"[OK] Database already has {company_count} companies\n")

# Step 6: Display database info
print("[INFO] Step 6: Database Summary")
print("=" * 50)
db = SessionLocal()
try:
    companies = db.query(Company).all()
    if companies:
        print(f"[INFO] Sample Companies:")
        for comp in companies[:3]:
            user_list = db.query(User).filter(User.company_id == comp.id).all()
            print(f"  - {comp.name} ({len(user_list)} users)")
        if len(companies) > 3:
            print(f"  ... and {len(companies) - 3} more")
finally:
    db.close()

print("\n[OK] ============================================")
print("[OK] SQLite is properly configured and ready!")
print("[OK] ============================================")
print("\nNext steps:")
print("1. Start the API: python -m uvicorn api.main:app --reload")
print("2. Test auth: curl -X POST http://localhost:8000/api/auth/token \\")
print("   -H 'Content-Type: application/json' \\")
print("   -d '{\"email\":\"admin.evans.group@carbontrace.ke\",\"password\":\"DemoPassword123\"}'")
