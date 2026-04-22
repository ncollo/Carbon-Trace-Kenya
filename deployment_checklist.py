#!/usr/bin/env python3
"""
Final deployment checklist for Carbon Trace Kenya
Verifies all components are ready for production deployment
"""
import requests
import json
import subprocess
import os
from datetime import datetime

def check_backend_health():
    """Check if backend is running and healthy"""
    try:
        response = requests.get("http://localhost:8002/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return True, f"Backend healthy - {data.get('model', 'Unknown')}"
        else:
            return False, f"Backend returned status {response.status_code}"
    except Exception as e:
        return False, f"Backend connection failed: {e}"

def check_ai_models():
    """Test AI model functionality"""
    try:
        # Test carbon prediction
        carbon_data = {
            "distance_km": 25.5,
            "vehicle_type": "diesel_truck", 
            "road_type": "urban",
            "traffic_density": "high"
        }
        response = requests.post("http://localhost:8002/api/predict/carbon-emissions", 
                               json=carbon_data, timeout=5)
        if response.status_code != 200:
            return False, "Carbon prediction model failed"
        
        # Test fleet optimization
        fleet_data = {
            "fleet_data": [
                {"id": "truck1", "efficiency": 0.8, "emission_factor": 2.64, "distance": 100},
                {"id": "ev1", "efficiency": 0.95, "emission_factor": 0.0, "distance": 80}
            ]
        }
        response = requests.post("http://localhost:8002/api/optimize/fleet", 
                               json=fleet_data, timeout=5)
        if response.status_code != 200:
            return False, "Fleet optimization model failed"
            
        return True, "All AI models working correctly"
    except Exception as e:
        return False, f"AI model test failed: {e}"

def check_dashboard_data():
    """Verify dashboard data is available"""
    try:
        # Test key dashboard endpoints
        endpoints = [
            "/api/overview/kpis",
            "/api/overview/companies", 
            "/api/reconcile/flags",
            "/api/epra/kpis"
        ]
        
        for endpoint in endpoints:
            response = requests.get(f"http://localhost:8002{endpoint}", timeout=5)
            if response.status_code != 200:
                return False, f"Dashboard endpoint {endpoint} failed"
        
        return True, "Dashboard data available"
    except Exception as e:
        return False, f"Dashboard data check failed: {e}"

def check_deployment_files():
    """Check if required deployment files exist"""
    required_files = [
        "docker-compose.yml",
        "Dockerfile", 
        "requirements.txt",
        ".env.example",
        "deployment-setup.md",
        "HACKATHON_DEPLOYMENT_GUIDE.md",
        ".github/workflows/deploy.yml"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        return False, f"Missing deployment files: {missing_files}"
    
    return True, "All deployment files present"

def check_ml_models():
    """Check if ML model files exist"""
    ml_files = [
        "carbontrace-backend/ml_models.py",
        "carbontrace-backend/ml_models_new.py"
    ]
    
    missing_files = []
    for file in ml_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        return False, f"Missing ML model files: {missing_files}"
    
    return True, "ML model files present"

def main():
    """Run deployment checklist"""
    print("Carbon Trace Kenya - Deployment Checklist")
    print("=" * 50)
    print(f"Check time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    checks = [
        ("Backend Health", check_backend_health),
        ("AI Models", check_ai_models),
        ("Dashboard Data", check_dashboard_data),
        ("Deployment Files", check_deployment_files),
        ("ML Model Files", check_ml_models)
    ]
    
    all_passed = True
    results = []
    
    for check_name, check_func in checks:
        passed, message = check_func()
        status = "PASS" if passed else "FAIL"
        print(f"{check_name}: {status} - {message}")
        results.append((check_name, passed, message))
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("DEPLOYMENT READY! All checks passed.")
        print("\nNext steps:")
        print("1. Create production repository on GitHub")
        print("2. Generate SSH keys for DigitalOcean")
        print("3. Create DigitalOcean Droplet")
        print("4. Deploy using HACKATHON_DEPLOYMENT_GUIDE.md")
        
        # Create deployment summary
        summary = {
            "status": "ready",
            "checks": results,
            "timestamp": datetime.now().isoformat(),
            "backend_url": "http://localhost:8002",
            "frontend_url": "http://localhost:5173"
        }
        
        with open("deployment_status.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        print("\nDeployment status saved to deployment_status.json")
        
    else:
        print("DEPLOYMENT NOT READY. Fix failed checks above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
