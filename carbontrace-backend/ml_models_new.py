"""
New ML Models for CarbonTrace Kenya Demo
- Real-time Carbon Prediction Model
- Fleet Efficiency Optimizer
- Route-based Emission Calculator
"""
import numpy as np
import pandas as pd
import pickle, os, pathlib as _pl
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Resolve paths cross-platform
_here = _pl.Path(__file__).parent.resolve()
MODEL_PATH = str(_here / "models" / "carbon_predictor.pkl")

class CarbonPredictor:
    """Real-time carbon emission prediction model for hackathon demo"""
    
    def __init__(self):
        self.model = None
        self.feature_columns = [
            'distance_km', 'vehicle_type', 'fuel_type', 
            'road_type', 'traffic_density', 'time_of_day'
        ]
        self.load_model()
    
    def load_model(self):
        """Load trained model or create dummy for demo"""
        try:
            if os.path.exists(MODEL_PATH):
                with open(MODEL_PATH, 'rb') as f:
                    self.model = pickle.load(f)
            else:
                # Create a simple rule-based model for demo
                self.model = self._create_demo_model()
        except Exception as e:
            print(f"Model loading error: {e}")
            self.model = self._create_demo_model()
    
    def _create_demo_model(self):
        """Create a simple demo model"""
        return {
            'base_emissions': {
                'diesel_truck': 2.64,
                'petrol_saloon': 2.31,
                'ev': 0.0,
                'diesel_van': 2.64,
                'petrol_suv': 2.31
            },
            'road_multipliers': {
                'highway': 0.9,
                'urban': 1.2,
                'rural': 1.0,
                'mixed': 1.1
            },
            'traffic_multipliers': {
                'low': 0.8,
                'medium': 1.0,
                'high': 1.3
            }
        }
    
    def predict_emissions(self, features: Dict) -> Dict:
        """Predict carbon emissions for given route/vehicle"""
        try:
            vehicle_type = features.get('vehicle_type', 'petrol_saloon')
            distance_km = float(features.get('distance_km', 0))
            road_type = features.get('road_type', 'mixed')
            traffic_density = features.get('traffic_density', 'medium')
            
            # Base emission calculation
            base_rate = self.model['base_emissions'].get(vehicle_type, 2.31)
            road_mult = self.model['road_multipliers'].get(road_type, 1.0)
            traffic_mult = self.model['traffic_multipliers'].get(traffic_density, 1.0)
            
            # Calculate emissions
            emissions_kg = distance_km * base_rate * road_mult * traffic_mult
            emissions_co2 = emissions_kg  # Simplified for demo
            
            return {
                'predicted_emissions_kg': round(emissions_kg, 3),
                'predicted_emissions_co2': round(emissions_co2, 3),
                'efficiency_score': max(0, min(100, 100 - (emissions_kg / distance_km * 10))),
                'recommendations': self._get_recommendations(vehicle_type, emissions_kg, distance_km),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': f'Prediction failed: {str(e)}'}
    
    def _get_recommendations(self, vehicle_type: str, emissions: float, distance: float) -> List[str]:
        """Generate eco-driving recommendations"""
        recommendations = []
        
        if emissions / distance > 0.3:  # High emission rate
            recommendations.append("Consider route optimization to reduce distance")
            recommendations.append("Check tire pressure and vehicle maintenance")
        
        if vehicle_type != 'ev':
            recommendations.append("Consider transitioning to electric vehicles")
        
        if emissions > 10:
            recommendations.append("Look into carbon offsetting options")
        
        return recommendations

class FleetOptimizer:
    """Fleet efficiency optimization for hackathon demo"""
    
    def __init__(self):
        self.vehicles = []
        self.routes = []
    
    def optimize_fleet(self, fleet_data: List[Dict]) -> Dict:
        """Optimize fleet assignment for minimal emissions"""
        try:
            # Simple optimization: assign most efficient vehicles to longest routes
            sorted_vehicles = sorted(fleet_data, key=lambda x: x.get('efficiency', 0), reverse=True)
            sorted_routes = sorted(fleet_data, key=lambda x: x.get('distance', 0), reverse=True)
            
            assignments = []
            total_emissions = 0
            
            for i, route in enumerate(sorted_routes):
                if i < len(sorted_vehicles):
                    vehicle = sorted_vehicles[i]
                    emission_estimate = route['distance'] * vehicle.get('emission_factor', 2.31)
                    total_emissions += emission_estimate
                    
                    assignments.append({
                        'vehicle_id': vehicle.get('id', f'veh_{i}'),
                        'route_id': route.get('id', f'route_{i}'),
                        'estimated_emissions': round(emission_estimate, 3),
                        'distance': route['distance']
                    })
            
            return {
                'assignments': assignments,
                'total_emissions': round(total_emissions, 3),
                'optimization_score': min(100, (total_emissions / sum(r['distance'] for r in sorted_routes)) * 10),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': f'Optimization failed: {str(e)}'}

# Global instances
carbon_predictor = CarbonPredictor()
fleet_optimizer = FleetOptimizer()

def predict_carbon_emissions(features: Dict) -> Dict:
    """Main prediction function for API"""
    return carbon_predictor.predict_emissions(features)

def optimize_fleet_assignments(fleet_data: List[Dict]) -> Dict:
    """Main fleet optimization function for API"""
    return fleet_optimizer.optimize_fleet(fleet_data)
