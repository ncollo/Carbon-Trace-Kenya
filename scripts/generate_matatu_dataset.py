#!/usr/bin/env python3
"""
Matatu Fleet Dataset Generator for Carbon Trace Kenya
Generates realistic Matatu SACCO and vehicle data based on NTSA standards and Kenyan transport patterns
"""

import pandas as pd
import random
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict
import json

class MatatuDatasetGenerator:
    def __init__(self):
        # Real Kenyan Matatu SACCO names (sample)
        self.sacco_names = [
            "Citi Hoppa", "KBS", "Forward Travellers", "Mombasa Road Line",
            "Kenya Bus Service", "Nairobi Bus Service", "Easy Coach", "Modern Coast",
            "Guardian Coach", "Transline", "Prestige Shuttle", "Mololine",
            "KBS SACCO", "Nairobi Commuter", "Ushirika", "Embassava",
            "Zuri Bus", "Pioneer", "Royal Express", "Goldline", "Naboka"
        ]
        
        # Common vehicle makes in Kenyan Matatu industry
        self.vehicle_makes = ["Toyota", "Nissan", "Isuzu", "Mitsubishi", "Hino", "Mercedes-Benz"]
        self.vehicle_models = {
            "Toyota": ["Hiace", "Coaster", "Noah", "Voxy"],
            "Nissan": ["Caravan", "Urvan", "Civilian"],
            "Isuzu": ["NPR", "NQR", "Elf"],
            "Mitsubishi": ["Rosa", "L300", "Canter"],
            "Hino": ["300 Series", "500 Series"],
            "Mercedes-Benz": ["Sprinter", "Vario", "Bus"]
        }
        
        # Common Nairobi route numbers
        self.route_numbers = [
            "11", "23", "33", "44", "45", "46", "48", "49", "52", "58", "69", "70",
            "102", "103", "104", "105", "106", "107", "108", "110", "111", "112",
            "114", "115", "116", "119", "120", "121", "125", "126", "127", "128",
            "130", "135", "145", "150", "158", "165", "168", "195", "196", "197"
        ]
        
        # Nairobi areas for office locations
        self.office_locations = [
            "Nairobi CBD", "Kenyatta Avenue", "Moi Avenue", "River Road", "Kirinyaga Road",
            "Accra Road", "Tom Mboya Street", "Koinange Street", "Haile Selassie Avenue",
            "Mombasa Road", "Thika Road", "Waiyaki Way", "Langata Road", "Ngong Road"
        ]

    def generate_saccos(self, count: int = 20) -> List[Dict]:
        """Generate Matatu SACCO data"""
        saccos = []
        used_names = set()
        
        for i in range(count):
            # Ensure unique names
            available_names = [name for name in self.sacco_names if name not in used_names]
            if not available_names:
                # Generate unique names if we run out
                name = f"SACCO {i+1}"
            else:
                name = random.choice(available_names)
                used_names.add(name)
            
            sacco = {
                "id": i + 1,
                "name": name,
                "registration_number": f"SACCO/{random.randint(1000, 9999)}/{random.randint(10, 99)}",
                "contact_phone": f"+254{random.randint(700000000, 799999999)}",
                "contact_email": f"info@{name.lower().replace(' ', '')}.co.ke",
                "office_location": random.choice(self.office_locations),
                "fleet_size": random.randint(5, 150),
                "established_year": random.randint(1990, 2020),
                "ntsa_compliance_rating": round(random.uniform(2.5, 5.0), 1),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            saccos.append(sacco)
        return saccos

    def generate_vehicles(self, sacco_id: int, vehicle_count: int) -> List[Dict]:
        """Generate vehicle data for a specific SACCO"""
        vehicles = []
        for i in range(vehicle_count):
            make = random.choice(self.vehicle_makes)
            model = random.choice(self.vehicle_models[make])
            year = random.randint(2005, 2023)
            
            # Determine vehicle type based on model
            if "Hiace" in model or "Caravan" in model:
                vehicle_type = "14-seater"
                seating_capacity = 14
            elif "Coaster" in model or "Civilian" in model:
                vehicle_type = "33-seater"
                seating_capacity = 33
            elif "Bus" in model or "Rosa" in model:
                vehicle_type = "bus"
                seating_capacity = random.choice([45, 51, 62])
            else:
                vehicle_type = "25-seater"
                seating_capacity = 25
            
            vehicle = {
                "id": len(vehicles) + 1,  # Will be adjusted later
                "sacco_id": sacco_id,
                "registration_number": f"K{random.choice(['A', 'B', 'C', 'D', 'E'])}{random.randint(100, 999)}{random.choice(['A', 'B', 'C', 'D', 'E'])}",
                "make": make,
                "model": model,
                "year_of_manufacture": year,
                "vehicle_type": vehicle_type,
                "engine_capacity": random.choice([2000, 2400, 2700, 3000, 3500]),
                "fuel_type": random.choice(["diesel", "diesel", "diesel", "petrol", "hybrid"]),
                "seating_capacity": seating_capacity,
                "route_number": random.choice(self.route_numbers),
                "ntsa_inspection_expiry": (datetime.now() + timedelta(days=random.randint(30, 365))).isoformat(),
                "insurance_expiry": (datetime.now() + timedelta(days=random.randint(1, 365))).isoformat(),
                "road_license_expiry": (datetime.now() + timedelta(days=random.randint(1, 365))).isoformat(),
                "emission_rating": random.choice(["EURO 2", "EURO 3", "EURO 4", "EURO 5"]),
                "last_service_date": (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat(),
                "mileage": random.randint(50000, 500000),
                "is_active": random.choice([True, True, True, False]),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            vehicles.append(vehicle)
        return vehicles

    def generate_inspections(self, vehicle_id: int, inspection_count: int = 3) -> List[Dict]:
        """Generate NTSA inspection data for a vehicle"""
        inspections = []
        for i in range(inspection_count):
            # Generate inspection dates going backwards
            inspection_date = datetime.now() - timedelta(days=random.randint(30, 365) * (i + 1))
            
            # Generate realistic scores
            roadworthiness_score = random.uniform(60, 100)
            safety_score = random.uniform(50, 100)
            emissions_score = random.uniform(40, 100)
            
            # Determine overall rating based on scores
            avg_score = (roadworthiness_score + safety_score + emissions_score) / 3
            if avg_score >= 80:
                overall_rating = "Pass"
            elif avg_score >= 60:
                overall_rating = "Conditional"
            else:
                overall_rating = "Fail"
            
            # Generate violations
            violations = []
            if roadworthiness_score < 70:
                violations.extend(["Worn tires", "Faulty brakes", "Poor lighting"])
            if safety_score < 70:
                violations.extend(["Missing fire extinguisher", "No first aid kit", "Broken seats"])
            if emissions_score < 60:
                violations.append("Excessive emissions")
            
            if not violations:
                violations = ["No violations found"]
            
            inspection = {
                "id": len(inspections) + 1,  # Will be adjusted later
                "vehicle_id": vehicle_id,
                "inspection_date": inspection_date.isoformat(),
                "inspector_id": f"NTSA-{random.randint(1000, 9999)}",
                "inspection_type": random.choice(["annual", "quarterly", "special"]),
                "roadworthiness_score": round(roadworthiness_score, 1),
                "safety_score": round(safety_score, 1),
                "emissions_score": round(emissions_score, 1),
                "overall_rating": overall_rating,
                "violations_found": json.dumps(violations),
                "recommendations": json.dumps([
                    "Regular maintenance schedule",
                    "Driver safety training",
                    "Emission system check"
                ]),
                "next_inspection_date": (inspection_date + timedelta(days=random.randint(180, 365))).isoformat(),
                "created_at": datetime.now().isoformat()
            }
            inspections.append(inspection)
        return inspections

    def generate_full_dataset(self, num_saccos: int = 20) -> Dict[str, pd.DataFrame]:
        """Generate complete dataset with SACCOS, vehicles, and inspections"""
        print(f"Generating dataset for {num_saccos} Matatu SACCOS...")
        
        # Generate SACCOS
        saccos = self.generate_saccos(num_saccos)
        saccos_df = pd.DataFrame(saccos)
        
        # Generate vehicles for each SACCO
        all_vehicles = []
        all_inspections = []
        
        for sacco in saccos:
            vehicle_count = sacco["fleet_size"]
            vehicles = self.generate_vehicles(sacco["id"], vehicle_count)
            
            # Adjust vehicle IDs
            for i, vehicle in enumerate(vehicles):
                vehicle["id"] = len(all_vehicles) + i + 1
            
            all_vehicles.extend(vehicles)
            
            # Generate inspections for each vehicle
            for vehicle in vehicles:
                inspection_count = random.randint(1, 4)
                inspections = self.generate_inspections(vehicle["id"], inspection_count)
                
                # Adjust inspection IDs
                for i, inspection in enumerate(inspections):
                    inspection["id"] = len(all_inspections) + i + 1
                
                all_inspections.extend(inspections)
        
        vehicles_df = pd.DataFrame(all_vehicles)
        inspections_df = pd.DataFrame(all_inspections)
        
        print(f"Generated {len(saccos)} SACCOS, {len(all_vehicles)} vehicles, {len(all_inspections)} inspections")
        
        return {
            "matatu_saccos": saccos_df,
            "matatu_vehicles": vehicles_df,
            "ntsa_inspections": inspections_df
        }

    def save_datasets(self, datasets: Dict[str, pd.DataFrame], output_dir: str = "dataset_csv"):
        """Save datasets to CSV files"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        for name, df in datasets.items():
            filename = f"{output_dir}/{name}.csv"
            df.to_csv(filename, index=False)
            print(f"Saved {filename} with {len(df)} records")
        
        # Generate summary statistics
        summary = {
            "total_saccos": len(datasets["matatu_saccos"]),
            "total_vehicles": len(datasets["matatu_vehicles"]),
            "total_inspections": len(datasets["ntsa_inspections"]),
            "average_fleet_size": datasets["matatu_vehicles"].groupby("sacco_id").size().mean(),
            "vehicle_types": datasets["matatu_vehicles"]["vehicle_type"].value_counts().to_dict(),
            "fuel_types": datasets["matatu_vehicles"]["fuel_type"].value_counts().to_dict(),
            "inspection_ratings": datasets["ntsa_inspections"]["overall_rating"].value_counts().to_dict()
        }
        
        summary_df = pd.DataFrame([summary])
        summary_df.to_csv(f"{output_dir}/matatu_fleet_summary.csv", index=False)
        print(f"Saved {output_dir}/matatu_fleet_summary.csv")

if __name__ == "__main__":
    generator = MatatuDatasetGenerator()
    datasets = generator.generate_full_dataset(num_saccos=20)
    generator.save_datasets(datasets)
