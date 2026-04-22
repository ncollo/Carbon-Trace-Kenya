#!/usr/bin/env python3
"""
Test script for Carbon Trace Kenya AI Models
Run this to verify the ML models work before deployment
"""
import sys
import os
sys.path.append('carbontrace-backend')

from ml_models_new import predict_carbon_emissions, optimize_fleet_assignments

def test_carbon_prediction():
    """Test the carbon prediction model"""
    print("=== Testing Carbon Prediction Model ===")
    
    # Test case 1: Diesel truck in urban traffic
    test_case_1 = {
        "distance_km": 25.5,
        "vehicle_type": "diesel_truck", 
        "road_type": "urban",
        "traffic_density": "high"
    }
    
    result1 = predict_carbon_emissions(test_case_1)
    print(f"Test 1 - Diesel Truck Urban: {result1}")
    
    # Test case 2: Electric vehicle on highway
    test_case_2 = {
        "distance_km": 50.0,
        "vehicle_type": "ev",
        "road_type": "highway", 
        "traffic_density": "low"
    }
    
    result2 = predict_carbon_emissions(test_case_2)
    print(f"Test 2 - EV Highway: {result2}")
    
    return result1 and result2

def test_fleet_optimization():
    """Test the fleet optimization model"""
    print("\n=== Testing Fleet Optimization Model ===")
    
    fleet_data = [
        {"id": "truck1", "efficiency": 0.8, "emission_factor": 2.64, "distance": 100},
        {"id": "ev1", "efficiency": 0.95, "emission_factor": 0.0, "distance": 80},
        {"id": "van1", "efficiency": 0.7, "emission_factor": 2.31, "distance": 60}
    ]
    
    result = optimize_fleet_assignments(fleet_data)
    print(f"Fleet Optimization Result: {result}")
    
    return result

def main():
    """Run all AI model tests"""
    print("Carbon Trace Kenya - AI Model Test Suite")
    print("=" * 50)
    
    try:
        # Test carbon prediction
        carbon_ok = test_carbon_prediction()
        
        # Test fleet optimization  
        fleet_ok = test_fleet_optimization()
        
        print("\n=== Test Results ===")
        print(f"Carbon Prediction: {'PASS' if carbon_ok else 'FAIL'}")
        print(f"Fleet Optimization: {'PASS' if fleet_ok else 'FAIL'}")
        
        if carbon_ok and fleet_ok:
            print("\nAll AI models working correctly! Ready for deployment.")
            return True
        else:
            print("\nSome models failed. Check the output above.")
            return False
            
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
