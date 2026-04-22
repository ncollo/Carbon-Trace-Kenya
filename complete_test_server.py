#!/usr/bin/env python3
"""
Complete FastAPI test server with all endpoints needed for the dashboard
This includes both original endpoints and new ML models
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
sys.path.append('carbontrace-backend')

from ml_models_new import predict_carbon_emissions, optimize_fleet_assignments
from typing import Dict, List
from pydantic import BaseModel
import json
from datetime import datetime

app = FastAPI(title="Carbon Trace Kenya - Complete Test Server", version="2.0")

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

# Mock data for dashboard endpoints
MOCK_DATA = {
    "kpis": {
        "scope1_tco2e": 15420.50,
        "s3_cat6_tco2e": 8920.30,
        "s3_cat7_tco2e": 3210.80,
        "total_tco2e": 27551.60,
        "n_companies": 42,
        "avg_intensity": 0.0042,
        "pending_anomalies": 8,
        "total_fuel_records": 15847,
        "flagged_records": 234,
        "uncertainty_pct": 4.8
    },
    "quarterly_trend": [
        {"label": "Q1 2024", "value": 6234.10},
        {"label": "Q2 2024", "value": 7123.50},
        {"label": "Q3 2024", "value": 6891.20},
        {"label": "Q4 2024", "value": 7302.80}
    ],
    "scope_breakdown": [
        {"scope": "Scope 1", "value": 15420.50, "percentage": 56.0},
        {"scope": "Scope 3 Cat 6", "value": 8920.30, "percentage": 32.4},
        {"scope": "Scope 3 Cat 7", "value": 3210.80, "percentage": 11.6}
    ],
    "fleet_by_class": [
        {"class": "diesel_truck", "count": 234, "emissions": 8923.40},
        {"class": "petrol_saloon", "count": 567, "emissions": 4521.80},
        {"class": "ev", "count": 89, "emissions": 0.00},
        {"class": "petrol_suv", "count": 345, "emissions": 1975.30}
    ],
    "companies": [
        {"nse_code": "SAFARICOM", "name": "Safaricom PLC", "total_emissions": 3420.50, "intensity": 0.0032},
        {"nse_code": "EQUITY", "name": "Equity Group", "total_emissions": 2891.20, "intensity": 0.0041},
        {"nse_code": "KCB", "name": "KCB Group", "total_emissions": 2156.80, "intensity": 0.0038}
    ],
    "intensity_trend": [
        {"month": "Jan", "value": 0.0045},
        {"month": "Feb", "value": 0.0043},
        {"month": "Mar", "value": 0.0041},
        {"month": "Apr", "value": 0.0042}
    ],
    "flags": [
        {
            "anomaly_record_id": "ANOM-001",
            "nse_code": "SAFARICOM",
            "anomaly_type": "high_consumption",
            "anomaly_confidence": 0.92,
            "resolution_status": "pending",
            "description": "Unusual fuel consumption spike detected"
        },
        {
            "anomaly_record_id": "ANOM-002", 
            "nse_code": "EQUITY",
            "anomaly_type": "missing_data",
            "anomaly_confidence": 0.78,
            "resolution_status": "pending",
            "description": "Missing GPS data for fuel transactions"
        }
    ],
    "quality": {
        "total_records": 15847,
        "validated_records": 15613,
        "flagged_records": 234,
        "validation_rate": 98.5,
        "data_quality_score": 94.2
    },
    "validation_log": [
        {"timestamp": "2024-04-22T10:30:00", "rule": "fuel_range_check", "status": "passed", "count": 142},
        {"timestamp": "2024-04-22T10:25:00", "rule": "gps_validation", "status": "failed", "count": 8}
    ],
    "ghg_results": [
        {"nse_code": "SAFARICOM", "scope1": 1920.50, "s3_cat6": 1200.00, "s3_cat7": 300.00, "total": 3420.50},
        {"nse_code": "EQUITY", "scope1": 1591.20, "s3_cat6": 1000.00, "s3_cat7": 300.00, "total": 2891.20}
    ],
    "emission_factors": [
        {"vehicle_class": "diesel_truck", "factor": 2.64, "source": "DEFRA 2024"},
        {"vehicle_class": "petrol_saloon", "factor": 2.31, "source": "DEFRA 2024"},
        {"vehicle_class": "ev", "factor": 0.00, "source": "DEFRA 2024"}
    ],
    "epra_kpis": {
        "total_companies": 156,
        "total_emissions": 125420.50,
        "avg_intensity": 0.0038,
        "compliance_rate": 87.3
    },
    "ndc_trajectory": [
        {"year": 2020, "actual": 180000, "target": 185000},
        {"year": 2025, "actual": 125420, "target": 150000},
        {"year": 2030, "actual": None, "target": 100000}
    ],
    "sector_breakdown": [
        {"sector": "Banking", "emissions": 45230.80, "companies": 28},
        {"sector": "Telecom", "emissions": 34210.50, "companies": 8},
        {"sector": "Manufacturing", "emissions": 28940.20, "companies": 42}
    ],
    "league_table": [
        {"rank": 1, "nse_code": "SAFARICOM", "name": "Safaricom PLC", "intensity": 0.0032, "grade": "A"},
        {"rank": 2, "nse_code": "KCB", "name": "KCB Group", "intensity": 0.0038, "grade": "B"},
        {"rank": 3, "nse_code": "EQUITY", "name": "Equity Group", "intensity": 0.0041, "grade": "B"}
    ],
    "county_dist": [
        {"county": "Nairobi", "emissions": 45230.80, "companies": 89},
        {"county": "Mombasa", "emissions": 23410.50, "companies": 34},
        {"county": "Kisumu", "emissions": 15670.20, "companies": 23}
    ]
}

# Original endpoints needed by the frontend
@app.get("/")
def home():
    return {
        "message": "Carbon Trace Kenya - Complete Test Server",
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
        "database": "Test Mode - Mock Data",
        "fuel_records": "Demo Data",
        "model": "CarbonPredictor + FleetOptimizer v2.0",
        "ai_features": "Real-time prediction and optimization"
    }

# Overview endpoints
@app.get("/api/overview/kpis")
def get_kpis():
    return MOCK_DATA["kpis"]

@app.get("/api/overview/quarterly-trend")
def get_quarterly_trend():
    return MOCK_DATA["quarterly_trend"]

@app.get("/api/overview/scope-breakdown")
def get_scope_breakdown():
    return MOCK_DATA["scope_breakdown"]

@app.get("/api/overview/fleet-by-class")
def get_fleet_by_class():
    return MOCK_DATA["fleet_by_class"]

@app.get("/api/overview/companies")
def get_companies():
    return MOCK_DATA["companies"]

@app.get("/api/overview/intensity-trend")
def get_intensity_trend():
    return MOCK_DATA["intensity_trend"]

# Ingestion endpoints
@app.get("/api/ingestion/files")
def get_files():
    return [
        {"filename": "fuel_data_2024.csv", "file_type": "CSV", "records_extracted": 234, "status": "done"},
        {"filename": "receipt_001.jpg", "file_type": "IMG", "records_extracted": 1, "status": "done"}
    ]

@app.get("/api/ingestion/extraction-stats")
def get_extraction_stats():
    return {
        "total_files": 156,
        "records_extracted": 8234,
        "success_rate": 94.2,
        "last_updated": datetime.utcnow().isoformat()
    }

@app.post("/api/ingestion/upload")
async def upload_file():
    return {"filename": "test.csv", "records_extracted": 25, "status": "done", "method": "Schema-match + Pandas"}

@app.post("/api/ingestion/upload-image")
async def upload_image():
    return {"filename": "receipt.jpg", "records_extracted": 1, "status": "done", "method": "Gemini Vision OCR"}

# Reconcile endpoints
@app.get("/api/reconcile/flags")
def get_flags(status: str = "pending", limit: int = 50):
    return MOCK_DATA["flags"]

@app.patch("/api/reconcile/flags/{anomaly_id}/resolve")
def resolve_flag(anomaly_id: str):
    return {"status": "resolved", "anomaly_id": anomaly_id}

@app.get("/api/reconcile/quality")
def get_quality():
    return MOCK_DATA["quality"]

@app.get("/api/reconcile/validation-log")
def get_validation_log(limit: int = 20):
    return MOCK_DATA["validation_log"]

@app.post("/api/reconcile/run-model")
def run_anomaly_detection(payload: dict):
    return {"status": "completed", "anomalies_detected": 8, "model_version": "2.0"}

# Calculator endpoints
@app.get("/api/calculator/results")
def get_ghg_results(nse_code: str = ""):
    return MOCK_DATA["ghg_results"]

@app.get("/api/calculator/emission-factors")
def get_emission_factors():
    return MOCK_DATA["emission_factors"]

@app.get("/api/calculator/intensity-trend")
def get_intensity_trend_calc():
    return MOCK_DATA["intensity_trend"]

@app.get("/api/calculator/scope-by-vehicle")
def get_scope_by_vehicle():
    return MOCK_DATA["fleet_by_class"]

# Report endpoints
@app.get("/api/report/summary")
def get_report_summary(nse_code: str = ""):
    return {
        "total_emissions": 27551.60,
        "scope_breakdown": MOCK_DATA["scope_breakdown"],
        "key_insights": [
            "Scope 1 emissions represent 56% of total footprint",
            "Electric vehicle adoption shows 0% direct emissions",
            "Data quality score of 94.2% exceeds industry average"
        ]
    }

@app.get("/api/report/narrative-samples")
def get_narrative_samples(n: int = 5):
    return [
        {"category": "executive_summary", "text": "Our carbon footprint decreased by 12% YoY..."},
        {"category": "methodology", "text": "Emissions calculated using DEFRA 2024 factors..."},
        {"category": "targets", "text": "We aim to reduce emissions by 30% by 2030..."}
    ]

# EPRA endpoints
@app.get("/api/epra/kpis")
def get_epra_kpis():
    return MOCK_DATA["epra_kpis"]

@app.get("/api/epra/ndc-trajectory")
def get_ndc_trajectory():
    return MOCK_DATA["ndc_trajectory"]

@app.get("/api/epra/sector-breakdown")
def get_sector_breakdown():
    return MOCK_DATA["sector_breakdown"]

@app.get("/api/epra/league-table")
def get_league_table():
    return MOCK_DATA["league_table"]

@app.get("/api/epra/county-distribution")
def get_county_distribution():
    return MOCK_DATA["county_dist"]

@app.post("/api/epra/simulate")
def run_policy_simulation(payload: dict):
    ev_pct = float(payload.get("ev_pct", 30))
    reduction = ev_pct * 0.8  # Simple simulation
    return {
        "scenario": f"EV adoption at {ev_pct}%",
        "projected_reduction": reduction,
        "baseline_emissions": 125420.50,
        "projected_emissions": 125420.50 - reduction
    }

# Chat endpoint
@app.post("/api/chat")
async def chat_endpoint(payload: dict):
    message = payload.get("message", "")
    history = payload.get("history", [])
    
    # Simple mock responses
    if "carbon" in message.lower():
        response = "Current carbon emissions are 27,551.60 tCO2e across all scopes."
    elif "emission" in message.lower():
        response = "Emission factors are based on DEFRA 2024 guidelines for Kenya."
    else:
        response = "I can help you with carbon footprint analysis and emission calculations."
    
    return {"response": response, "timestamp": datetime.utcnow().isoformat()}

# New ML Model endpoints
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
    print("Starting Carbon Trace Kenya Complete Test Server...")
    print("Access the demo at: http://localhost:8002")
    print("API docs at: http://localhost:8002/docs")
    print("All dashboard endpoints are now available!")
    uvicorn.run(app, host="0.0.0.0", port=8002)
