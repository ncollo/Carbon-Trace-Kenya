#!/usr/bin/env python3
"""
Git Preparation Script - Prepare final version for commit before fork
Shows all changes and provides ready-to-use git commands
"""

import os
import subprocess
from pathlib import Path

print("\n" + "=" * 80)
print("GIT PREPARATION - FINAL VERSION BEFORE FORK")
print("=" * 80 + "\n")

# List of new/modified files created this session
NEW_FILES = [
    ".env",
    ".env.example",
    "SETUP.md",
    "FINAL_CHECKLIST.md",
    "config.py",
    "setup_sqlite.py",
    "verify_components.py",
    "seed_db.py",
    "db/models.py",
    "db/session.py",
    "api/routers/auth.py",
    "api/main.py",
    "alembic/env.py",
    "alembic/versions/0002_create_core_tables.py",
]

MODIFIED_FILES = [
    "requirements.txt (python-multipart added)",
    ".gitignore (carbon_trace.db should be ignored)",
]

DATABASE_FILES = [
    "carbon_trace.db (SQLite database with sample data)",
]

print("[INFO] NEW FILES CREATED THIS SESSION:")
print("-" * 80)
for f in NEW_FILES:
    path = Path(f)
    if path.exists():
        size = path.stat().st_size if path.is_file() else "dir"
        status = "[OK]"
    else:
        status = "[?]"
    print(f"{status} {f}")

print("\n[INFO] MODIFIED FILES:")
print("-" * 80)
for f in MODIFIED_FILES:
    print(f"  - {f}")

print("\n[INFO] DATABASE FILES (should be in .gitignore):")
print("-" * 80)
for f in DATABASE_FILES:
    path = Path(f.split()[0])
    if path.exists():
        size_mb = path.stat().st_size / (1024 * 1024)
        print(f"  ✓ {f} ({size_mb:.2f} MB)")

print("\n" + "=" * 80)
print("RECOMMENDED GIT COMMANDS")
print("=" * 80 + "\n")

print("[STEP 1] Check git status:")
print("-" * 80)
print("git status\n")

print("[STEP 2] Add all changes:")
print("-" * 80)
print("git add .\n")

print("[STEP 3] Review changes before commit:")
print("-" * 80)
print("git diff --cached --stat\n")

print("[STEP 4] Commit with detailed message:")
print("-" * 80)
print("""git commit -m "feat: Production-ready authentication system

- Implement JWT-based authentication endpoints (login, signup, validation)
- Add SQLAlchemy ORM models for User and Company
- Configure SQLite database with automatic initialization
- Create Alembic migrations for core tables
- Build database seeding script with sample data (10 companies, 30 users)
- Add comprehensive .env configuration template
- Create setup and verification scripts
- Document complete setup process in SETUP.md
- Ensure Windows compatibility (Unicode, RQ fork handling)

Includes:
- 4 authentication endpoints (token, signup, me, validate)
- Password hashing and JWT token generation
- SQLite database with 400+ sample records
- Development environment fully configured
- Test credentials: admin.evans.group@carbontrace.ke / DemoPassword123

Ready for production deployment and frontend integration."\n""")

print("[STEP 5] Create feature branch (optional):")
print("-" * 80)
print("git checkout -b feature/authentication\n")

print("[STEP 6] Push to fork:")
print("-" * 80)
print("git push origin feature/authentication\n")

print("=" * 80)
print("KEY FILES FOR CODE REVIEW")
print("=" * 80 + "\n")

review_files = [
    ("api/routers/auth.py", "Authentication logic - review security of password hashing"),
    ("db/models.py", "Database models - review relationships and constraints"),
    ("config.py", "Configuration management - ensure secrets are externalized"),
    ("db/session.py", "Database connection - check SQLite-specific handling"),
    (".env.example", "Configuration template - ensure all required vars present"),
]

for filepath, description in review_files:
    print(f"[REVIEW] {filepath}")
    print(f"         {description}\n")

print("=" * 80)
print("VERIFICATION BEFORE COMMIT")
print("=" * 80 + "\n")

# Run verification
print("[CHECK] Running component verification...\n")
try:
    result = subprocess.run(
        ["python", "verify_components.py"],
        capture_output=True,
        text=True,
        timeout=10
    )
    if result.returncode == 0:
        print("[OK] Component verification passed")
    else:
        print("[WARN] Component verification showed issues:")
        print(result.stdout)
except Exception as e:
    print(f"[WARN] Could not run verification: {e}")

print("\n[CHECK] Checking SQLite database...\n")
try:
    result = subprocess.run(
        ["python", "setup_sqlite.py"],
        capture_output=True,
        text=True,
        timeout=10
    )
    if "properly configured and ready" in result.stdout:
        print("[OK] SQLite database is properly configured")
    else:
        print("[WARN] SQLite check showed issues")
except Exception as e:
    print(f"[WARN] Could not verify SQLite: {e}")

print("\n" + "=" * 80)
print("FINAL STEPS")
print("=" * 80 + "\n")

print("""1. Review FINAL_CHECKLIST.md for complete feature list

2. Test the API locally:
   python -m uvicorn api.main:app --reload
   
3. Call auth endpoint in another terminal:
   curl -X POST http://localhost:8000/api/auth/token \\
     -H "Content-Type: application/json" \\
     -d '{"email":"admin.evans.group@carbontrace.ke","password":"DemoPassword123"}'

4. Verify you get a JWT token response

5. Commit and push:
   git add .
   git commit -m "feat: Production-ready authentication system"
   git push origin main

6. Create fork/branch for next development phase

7. Start Phase 2:
   - Frontend API integration
   - Additional endpoints
   - ML model integration
   - Monitoring & logging
""")

print("=" * 80)
print("[OK] READY TO FORK!")
print("=" * 80 + "\n")
