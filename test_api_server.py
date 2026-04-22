#!/usr/bin/env python3
"""
Simple FastAPI test server to demonstrate AI responses
Run this locally to test the API before deploying
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
sys.path.append('carbontrace-backend')

from ml_models_new import predict_carbon_emissions, optimize_fleet_assignments
from typing import Dict, List
from pydantic import BaseModel

app = FastAPI(title="Carbon Trace Kenya - Test Server", version="2.0")

# Enable CORS for frontend testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CarbonPredictionRequest(BaseModel):
    distance_km: float
    vehicle_type: str
    fuel_type: str = None
    road_type: str = "mixed"
    traffic_density: str = "medium"
    time_of_day: str = None

class FleetOptimizationRequest(BaseModel):
    fleet_data: List[dict]

@app.get("/")
def home():
    return {
        "message": "Carbon Trace Kenya - AI Test Server",
        "status": "Running",
        "models": ["CarbonPredictor", "FleetOptimizer"],
        "endpoints": [
            "/api/predict/carbon-emissions",
            "/api/optimize/fleet",
            "/api/models/new-features",
            "/docs"
        ]
    }

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "database": "Test Mode - No Database Required",
        "fuel_records": "Demo Data",
        "model": "CarbonPredictor + FleetOptimizer v2.0",
        "ai_features": "Real-time prediction and optimization"
    }

@app.post("/api/predict/carbon-emissions")
def predict_carbon(request: CarbonPredictionRequest):
    """Predict carbon emissions for a given route and vehicle"""
    try:
        features = {
            "distance_km": request.distance_km,
            "vehicle_type": request.vehicle_type,
            "fuel_type": request.fuel_type,
            "road_type": request.road_type,
            "traffic_density": request.traffic_density,
            "time_of_day": request.time_of_day
        }
        result = predict_carbon_emissions(features)
        return {
            "success": True,
            "data": result,
            "input": features
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Prediction failed: {str(e)}"
        }

@app.post("/api/optimize/fleet")
def optimize_fleet(request: FleetOptimizationRequest):
    """Optimize fleet assignments for minimal emissions"""
    try:
        result = optimize_fleet_assignments(request.fleet_data)
        return {
            "success": True,
            "data": result,
            "input_count": len(request.fleet_data)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Optimization failed: {str(e)}"
        }

@app.get("/api/models/new-features")
def get_new_model_features():
    """Get information about new ML model features"""
    return {
        "features": [
            {
                "name": "Real-time Carbon Prediction",
                "endpoint": "/api/predict/carbon-emissions",
                "description": "Predict CO2 emissions for specific routes and vehicles",
                "parameters": ["distance_km", "vehicle_type", "road_type", "traffic_density"],
                "demo_input": {"distance_km": 25.5, "vehicle_type": "diesel_truck", "road_type": "urban", "traffic_density": "high"}
            },
            {
                "name": "Fleet Optimization",
                "endpoint": "/api/optimize/fleet", 
                "description": "Optimize fleet assignments for minimal emissions",
                "parameters": ["fleet_data"],
                "demo_input": [{"id": "truck1", "efficiency": 0.8, "emission_factor": 2.64, "distance": 100}]
            }
        ],
        "models": ["CarbonPredictor", "FleetOptimizer"],
        "version": "2.0",
        "status": "Ready for hackathon demo"
    }

@app.get("/api/demo/carbon-prediction")
def demo_carbon_prediction():
    """Demo endpoint with pre-filled data"""
    demo_request = {
        "distance_km": 25.5,
        "vehicle_type": "diesel_truck",
        "road_type": "urban",
        "traffic_density": "high"
    }
    result = predict_carbon_emissions(demo_request)
    return {
        "demo_input": demo_request,
        "prediction": result,
        "explanation": "This shows how a diesel truck in heavy urban traffic produces higher emissions"
    }

@app.get("/api/demo/fleet-optimization")
def demo_fleet_optimization():
    """Demo endpoint with pre-filled fleet data"""
    demo_fleet = [
        {"id": "truck1", "efficiency": 0.8, "emission_factor": 2.64, "distance": 100},
        {"id": "ev1", "efficiency": 0.95, "emission_factor": 0.0, "distance": 80},
        {"id": "van1", "efficiency": 0.7, "emission_factor": 2.31, "distance": 60}
    ]
    result = optimize_fleet_assignments(demo_fleet)
    return {
        "demo_fleet": demo_fleet,
        "optimization": result,
        "explanation": "The AI assigns the most efficient vehicles to longest routes to minimize total emissions"
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting Carbon Trace Kenya Test Server...")
    print("Access the demo at: http://localhost:8000")
    print("API docs at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
