#!/usr/bin/env python3
"""
Comprehensive system test for Carbon Trace Kenya
Tests all API endpoints, AI models, and system components
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8002"

def test_endpoint(endpoint, method="GET", data=None, description=""):
    """Test a single API endpoint"""
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json=data, timeout=5)
        elif method == "PATCH":
            response = requests.patch(f"{BASE_URL}{endpoint}", timeout=5)
        
        if response.status_code == 200:
            print(f"  {method} {endpoint} - PASS {description}")
            return True, response.json()
        else:
            print(f"  {method} {endpoint} - FAIL ({response.status_code}) {description}")
            return False, response.text
    except Exception as e:
        print(f"  {method} {endpoint} - ERROR ({e}) {description}")
        return False, str(e)

def test_ai_models():
    """Test AI model endpoints"""
    print("\n=== AI Model Tests ===")
    
    # Test carbon prediction
    carbon_data = {
        "distance_km": 25.5,
        "vehicle_type": "diesel_truck",
        "road_type": "urban",
        "traffic_density": "high"
    }
    success, _ = test_endpoint("/api/predict/carbon-emissions", "POST", carbon_data, "Carbon Prediction")
    
    # Test fleet optimization
    fleet_data = {
        "fleet_data": [
            {"id": "truck1", "efficiency": 0.8, "emission_factor": 2.64, "distance": 100},
            {"id": "ev1", "efficiency": 0.95, "emission_factor": 0.0, "distance": 80}
        ]
    }
    success, _ = test_endpoint("/api/optimize/fleet", "POST", fleet_data, "Fleet Optimization")
    
    # Test demo endpoints
    test_endpoint("/api/demo/carbon-prediction", "GET", description="Carbon Prediction Demo")
    test_endpoint("/api/demo/fleet-optimization", "GET", description="Fleet Optimization Demo")
    test_endpoint("/api/models/new-features", "GET", description="New ML Features Info")

def test_dashboard_endpoints():
    """Test all dashboard endpoints"""
    print("\n=== Dashboard API Tests ===")
    
    # Health and basic endpoints
    test_endpoint("/", "GET", description="Home")
    test_endpoint("/api/health", "GET", description="Health Check")
    
    # Overview endpoints
    test_endpoint("/api/overview/kpis", "GET", description="Overview KPIs")
    test_endpoint("/api/overview/quarterly-trend", "GET", description="Quarterly Trend")
    test_endpoint("/api/overview/scope-breakdown", "GET", description="Scope Breakdown")
    test_endpoint("/api/overview/fleet-by-class", "GET", description="Fleet by Class")
    test_endpoint("/api/overview/companies", "GET", description="Companies")
    test_endpoint("/api/overview/intensity-trend", "GET", description="Intensity Trend")
    
    # Ingestion endpoints
    test_endpoint("/api/ingestion/files", "GET", description="Files List")
    test_endpoint("/api/ingestion/extraction-stats", "GET", description="Extraction Stats")
    
    # Reconciliation endpoints
    test_endpoint("/api/reconcile/flags", "GET", description="Anomaly Flags")
    test_endpoint("/api/reconcile/quality", "GET", description="Data Quality")
    test_endpoint("/api/reconcile/validation-log", "GET", description="Validation Log")
    
    # Calculator endpoints
    test_endpoint("/api/calculator/results", "GET", description="GHG Results")
    test_endpoint("/api/calculator/emission-factors", "GET", description="Emission Factors")
    test_endpoint("/api/calculator/intensity-trend", "GET", description="Calculator Intensity Trend")
    test_endpoint("/api/calculator/scope-by-vehicle", "GET", description="Scope by Vehicle")
    
    # Report endpoints
    test_endpoint("/api/report/summary", "GET", description="Report Summary")
    test_endpoint("/api/report/narrative-samples", "GET", description="Narrative Samples")
    
    # EPRA endpoints
    test_endpoint("/api/epra/kpis", "GET", description="EPRA KPIs")
    test_endpoint("/api/epra/ndc-trajectory", "GET", description="NDC Trajectory")
    test_endpoint("/api/epra/sector-breakdown", "GET", description="Sector Breakdown")
    test_endpoint("/api/epra/league-table", "GET", description="League Table")
    test_endpoint("/api/epra/county-distribution", "GET", description="County Distribution")

def test_frontend_connectivity():
    """Test if frontend can reach backend"""
    print("\n=== Frontend Connectivity Test ===")
    
    try:
        # Test the exact endpoints the frontend uses
        response = requests.get(f"{BASE_URL}/api/health", timeout=3)
        if response.status_code == 200:
            print("  Frontend-Backend Connectivity - PASS")
            return True
        else:
            print(f"  Frontend-Backend Connectivity - FAIL ({response.status_code})")
            return False
    except Exception as e:
        print(f"  Frontend-Backend Connectivity - ERROR ({e})")
        return False

def test_data_integrity():
    """Test data integrity and completeness"""
    print("\n=== Data Integrity Tests ===")
    
    # Test KPIs data structure
    success, kpis_data = test_endpoint("/api/overview/kpis", "GET", description="KPIs Data Structure")
    if success:
        required_fields = ["scope1_tco2e", "total_tco2e", "n_companies", "avg_intensity"]
        missing_fields = [field for field in required_fields if field not in kpis_data]
        if missing_fields:
            print(f"  KPIs Data Integrity - FAIL (Missing: {missing_fields})")
        else:
            print("  KPIs Data Integrity - PASS")
    
    # Test companies data
    success, companies_data = test_endpoint("/api/overview/companies", "GET", description="Companies Data Structure")
    if success and isinstance(companies_data, list):
        if len(companies_data) > 0:
            company = companies_data[0]
            required_fields = ["nse_code", "name", "total_emissions", "intensity"]
            missing_fields = [field for field in required_fields if field not in company]
            if missing_fields:
                print(f"  Companies Data Integrity - FAIL (Missing: {missing_fields})")
            else:
                print("  Companies Data Integrity - PASS")
        else:
            print("  Companies Data Integrity - FAIL (Empty data)")

def main():
    """Run comprehensive system test"""
    print("Carbon Trace Kenya - Comprehensive System Test")
    print("=" * 60)
    print(f"Testing against: {BASE_URL}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test basic connectivity first
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code != 200:
            print(f"ERROR: Backend not responding at {BASE_URL}")
            return False
    except Exception as e:
        print(f"ERROR: Cannot connect to backend at {BASE_URL} - {e}")
        return False
    
    # Run all test suites
    test_ai_models()
    test_dashboard_endpoints()
    test_frontend_connectivity()
    test_data_integrity()
    
    print("\n" + "=" * 60)
    print("System Test Complete!")
    print("If all tests show PASS, the system is ready for deployment.")
    print("If any tests show FAIL, check the backend logs and fix issues.")

if __name__ == "__main__":
    main()
