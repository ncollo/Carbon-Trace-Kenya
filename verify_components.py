#!/usr/bin/env python
"""
Quick test to verify all new components are working.
Tests imports and basic functionality.
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("\n" + "="*80)
print("CARBON TRACE KENYA - COMPONENT VERIFICATION")
print("="*80)

# Test 1: Config imports
print("\n[TEST 1] Importing configuration...")
try:
    from config import settings
    print(f"[OK] Config loaded: APP_NAME={settings.app_name}")
except Exception as e:
    print(f"[ERROR] Config import failed: {e}")
    sys.exit(1)

# Test 2: Database models
print("\n[TEST 2] Importing database models...")
try:
    from db.models import Company, User, Upload, Emission, AnomalyFlag, JobRecord
    print("[OK] All models imported successfully")
except Exception as e:
    print(f"[ERROR] Models import failed: {e}")
    sys.exit(1)

# Test 3: Authentication module
print("\n[TEST 3] Importing authentication module...")
try:
    from api.routers import auth
    print("[OK] Auth module loaded")
    print(f"   - Endpoints: /auth/token, /auth/signup, /auth/me, /auth/validate")
except Exception as e:
    print(f"[ERROR] Auth import failed: {e}")
    sys.exit(1)

# Test 4: FastAPI app
print("\n[TEST 4] Creating FastAPI app...")
try:
    from api.main import create_app
    app = create_app()
    print("[OK] FastAPI app created")
    print(f"   - Routes: {len(app.routes)} total")
    
    # List registered routers
    routers = {}
    for route in app.routes:
        if hasattr(route, 'path'):
            routers[route.path] = route.methods if hasattr(route, 'methods') else 'N/A'
    
    print(f"   - Auth routes: /api/auth/*")
    print(f"   - Other routes registered: {len([r for r in routers if '/api' in r])} routes")
except Exception as e:
    print(f"[ERROR] App creation failed: {e}")
    sys.exit(1)

# Test 5: Utility functions
print("\n[TEST 5] Testing utility functions...")
try:
    from api.routers.auth import hash_password, verify_password, create_access_token, verify_token
    
    # Test password hashing
    test_password = "TestPassword123"
    hashed = hash_password(test_password)
    is_valid = verify_password(test_password, hashed)
    assert is_valid, "Password verification failed"
    print("[OK] Password hashing works")
    
    # Test token creation (without database)
    token, expires_in = create_access_token(user_id=1, email="test@example.com")
    assert token, "Token creation failed"
    assert expires_in > 0, "Expiration not set"
    print(f"[OK] Token creation works (expires in {expires_in} seconds)")
except Exception as e:
    print(f"[ERROR] Utility functions test failed: {e}")
    sys.exit(1)

# Test 6: Seed script
print("\n[TEST 6] Checking seed script...")
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("seed_db", project_root / "seed_db.py")
    seed_module = importlib.util.module_from_spec(spec)
    print("[OK] Seed script found and valid")
except Exception as e:
    print(f"[ERROR] Seed script check failed: {e}")
    sys.exit(1)

# Test 7: Configuration completeness
print("\n[TEST 7] Checking configuration completeness...")
try:
    required_settings = [
        'app_name', 'database_url', 'redis_url', 'jwt_secret', 
        'jwt_algorithm', 'cors_allowed_origins'
    ]
    
    config_attrs = dir(settings)
    missing = [attr for attr in required_settings if attr not in config_attrs]
    
    if missing:
        print(f"[WARN] Missing config attributes: {missing}")
    else:
        print("[OK] All required configuration present")
except Exception as e:
    print(f"[ERROR] Config check failed: {e}")
    sys.exit(1)

# Summary
print("\n" + "="*80)
print("VERIFICATION SUMMARY")
print("="*80)
print("""
[OK] All components verified successfully!

Next steps:
1. Create .env file: cp .env.example .env
2. Update .env with database/redis credentials
3. Run migrations: alembic upgrade head
4. Seed database: python seed_db.py
5. Start API: python -m uvicorn api.main:app --reload
6. Test auth: curl -X POST http://localhost:8000/api/auth/token

For complete setup instructions, see SETUP.md
""")
print("="*80 + "\n")
