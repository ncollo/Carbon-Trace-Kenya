#!/usr/bin/env python3
"""
Matatu Fleet Data Ingestion Script for Carbon Trace Kenya
Loads CSV datasets into the database using SQLAlchemy models
"""

import pandas as pd
import sys
import os
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from sqlalchemy.dialects import postgresql
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
class DatabaseConfig:
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    
    @staticmethod
    def get_connection_url(db_type: str, **kwargs):
        """Get database connection URL based on type"""
        if db_type == DatabaseConfig.SQLITE:
            return kwargs.get('sqlite_url', "sqlite:///carbon_trace.db")
        elif db_type == DatabaseConfig.POSTGRESQL:
            user = kwargs.get('user', 'postgres')
            password = kwargs.get('password', 'password')
            host = kwargs.get('host', 'localhost')
            port = kwargs.get('port', '5432')
            database = kwargs.get('database', 'carbon_trace')
            return f"postgresql://{user}:{password}@{host}:{port}/{database}"
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    @staticmethod
    def get_engine_kwargs(db_type: str):
        """Get engine-specific arguments"""
        if db_type == DatabaseConfig.SQLITE:
            return {
                'echo': False,
                'connect_args': {'check_same_thread': False}
            }
        elif db_type == DatabaseConfig.POSTGRESQL:
            return {
                'echo': False,
                'pool_size': 10,
                'max_overflow': 20,
                'pool_pre_ping': True,
                'pool_recycle': 3600
            }
        else:
            return {}

def test_database_connection(engine, db_type: str):
    """Test database connection and compatibility"""
    try:
        with engine.connect() as conn:
            # Test basic connection
            result = conn.execute(text("SELECT 1")).scalar()
            logger.info(f"Database connection test successful: {result}")
            
            # Test database-specific features
            if db_type == DatabaseConfig.POSTGRESQL:
                # Test PostgreSQL-specific features
                version = conn.execute(text("SELECT version()")).scalar()
                logger.info(f"PostgreSQL version: {version}")
                
                # Test JSON support
                test_json = conn.execute(text("SELECT '{\"test\": \"value\"}'::jsonb")).scalar()
                logger.info(f"PostgreSQL JSON support: {test_json}")
            
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False

def load_matatu_datasets(db_type: str = DatabaseConfig.SQLITE, **kwargs):
    """Load Matatu fleet datasets into the database"""
    
    logger.info(f"Starting Matatu fleet data ingestion for {db_type}...")
    
    # Get connection URL and engine arguments
    db_url = DatabaseConfig.get_connection_url(db_type, **kwargs)
    engine_kwargs = DatabaseConfig.get_engine_kwargs(db_type)
    
    logger.info(f"Database URL: {db_url}")
    
    # Create database engine
    engine = create_engine(db_url, **engine_kwargs)
    
    # Test database connection
    if not test_database_connection(engine, db_type):
        logger.error("Database connection test failed. Aborting ingestion.")
        return False
    
    # Create tables if they don't exist
    try:
        Base.metadata.create_all(engine)
        logger.info("Database tables created/verified successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        return False
    
    # Load CSV datasets
    try:
        saccos_df = pd.read_csv("dataset_csv/matatu_saccos.csv")
        vehicles_df = pd.read_csv("dataset_csv/matatu_vehicles.csv")
        inspections_df = pd.read_csv("dataset_csv/ntsa_inspections.csv")
        
        logger.info(f"Loaded {len(saccos_df)} SACCOS, {len(vehicles_df)} vehicles, {len(inspections_df)} inspections")
        
    except FileNotFoundError as e:
        logger.error(f"Error: CSV file not found - {e}")
        logger.error("Please run generate_matatu_dataset.py first to create the datasets")
        return False
    
    # Create session
    with Session(engine) as session:
        try:
            # Clear existing data to avoid duplicates
            session.query(NtsaInspection).delete()
            session.query(MatatuVehicle).delete()
            session.query(MatatuSacco).delete()
            session.commit()
            logger.info("Cleared existing Matatu data")
            
            # Insert SACCOS
            sacco_records = []
            for _, row in saccos_df.iterrows():
                sacco = MatatuSacco(
                    id=row['id'],
                    name=row['name'],
                    registration_number=row['registration_number'],
                    contact_phone=row['contact_phone'],
                    contact_email=row['contact_email'],
                    office_location=row['office_location'],
                    fleet_size=row['fleet_size'],
                    established_year=row['established_year'],
                    ntsa_compliance_rating=row['ntsa_compliance_rating'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at'])
                )
                sacco_records.append(sacco)
            
            session.add_all(sacco_records)
            session.commit()
            logger.info(f"Inserted {len(sacco_records)} SACCOS")
            
            # Insert Vehicles
            vehicle_records = []
            for _, row in vehicles_df.iterrows():
                vehicle = MatatuVehicle(
                    id=row['id'],
                    sacco_id=row['sacco_id'],
                    registration_number=row['registration_number'],
                    make=row['make'],
                    model=row['model'],
                    year_of_manufacture=row['year_of_manufacture'],
                    vehicle_type=row['vehicle_type'],
                    engine_capacity=row['engine_capacity'],
                    fuel_type=row['fuel_type'],
                    seating_capacity=row['seating_capacity'],
                    route_number=row['route_number'],
                    ntsa_inspection_expiry=datetime.fromisoformat(row['ntsa_inspection_expiry']) if pd.notna(row['ntsa_inspection_expiry']) else None,
                    insurance_expiry=datetime.fromisoformat(row['insurance_expiry']) if pd.notna(row['insurance_expiry']) else None,
                    road_license_expiry=datetime.fromisoformat(row['road_license_expiry']) if pd.notna(row['road_license_expiry']) else None,
                    emission_rating=row['emission_rating'],
                    last_service_date=datetime.fromisoformat(row['last_service_date']) if pd.notna(row['last_service_date']) else None,
                    mileage=row['mileage'],
                    is_active=row['is_active'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at'])
                )
                vehicle_records.append(vehicle)
            
            session.add_all(vehicle_records)
            session.commit()
            logger.info(f"Inserted {len(vehicle_records)} vehicles")
            
            # Insert Inspections
            inspection_records = []
            for _, row in inspections_df.iterrows():
                inspection = NtsaInspection(
                    id=row['id'],
                    vehicle_id=row['vehicle_id'],
                    inspection_date=datetime.fromisoformat(row['inspection_date']),
                    inspector_id=row['inspector_id'],
                    inspection_type=row['inspection_type'],
                    roadworthiness_score=row['roadworthiness_score'],
                    safety_score=row['safety_score'],
                    emissions_score=row['emissions_score'],
                    overall_rating=row['overall_rating'],
                    violations_found=row['violations_found'],
                    recommendations=row['recommendations'],
                    next_inspection_date=datetime.fromisoformat(row['next_inspection_date']),
                    created_at=datetime.fromisoformat(row['created_at'])
                )
                inspection_records.append(inspection)
            
            session.add_all(inspection_records)
            session.commit()
            logger.info(f"Inserted {len(inspection_records)} inspections")
            
            logger.info("Matatu fleet data ingestion completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Error during data ingestion: {e}")
            session.rollback()
            return False

def generate_summary_report(db_type: str = DatabaseConfig.SQLITE, **kwargs):
    """Generate a summary report of the ingested Matatu data"""
    
    db_url = DatabaseConfig.get_connection_url(db_type, **kwargs)
    engine_kwargs = DatabaseConfig.get_engine_kwargs(db_type)
    engine = create_engine(db_url, **engine_kwargs)
    
    with Session(engine) as session:
        # SACCO summary
        total_saccos = session.query(MatatuSacco).count()
        avg_compliance = session.query(func.avg(MatatuSacco.ntsa_compliance_rating)).scalar()
        
        # Vehicle summary
        total_vehicles = session.query(MatatuVehicle).count()
        active_vehicles = session.query(MatatuVehicle).filter(MatatuVehicle.is_active == True).count()
        
        # Inspection summary
        total_inspections = session.query(NtsaInspection).count()
        passed_inspections = session.query(NtsaInspection).filter(NtsaInspection.overall_rating == 'Pass').count()
        failed_inspections = session.query(NtsaInspection).filter(NtsaInspection.overall_rating == 'Fail').count()
        
        print("\n" + "="*50)
        print("MATATU FLEET SUMMARY REPORT")
        print("="*50)
        print(f"Total SACCOS: {total_saccos}")
        print(f"Average NTSA Compliance Rating: {avg_compliance:.2f}/5.0")
        print(f"Total Vehicles: {total_vehicles}")
        print(f"Active Vehicles: {active_vehicles} ({active_vehicles/total_vehicles*100:.1f}%)")
        print(f"Total Inspections: {total_inspections}")
        print(f"Passed Inspections: {passed_inspections} ({passed_inspections/total_inspections*100:.1f}%)")
        print(f"Failed Inspections: {failed_inspections} ({failed_inspections/total_inspections*100:.1f}%)")
        print("="*50)

def test_model_compatibility(db_type: str = DatabaseConfig.SQLITE, **kwargs):
    """Test model compatibility with the specified database"""
    logger.info(f"Testing model compatibility with {db_type}...")
    
    db_url = DatabaseConfig.get_connection_url(db_type, **kwargs)
    engine_kwargs = DatabaseConfig.get_engine_kwargs(db_type)
    engine = create_engine(db_url, **engine_kwargs)
    
    try:
        # Test table creation
        Base.metadata.create_all(engine)
        logger.info("✓ Table creation successful")
        
        # Test data insertion
        with Session(engine) as session:
            # Create test SACCO
            test_sacco = MatatuSacco(
                name="Test SACCO",
                registration_number="TEST/001/01",
                contact_phone="+254123456789",
                contact_email="test@test.com",
                office_location="Test Location",
                fleet_size=5,
                established_year=2020,
                ntsa_compliance_rating=4.5
            )
            session.add(test_sacco)
            session.commit()
            
            # Create test vehicle
            test_vehicle = MatatuVehicle(
                sacco_id=test_sacco.id,
                registration_number="KAT123A",
                make="Toyota",
                model="Hiace",
                year_of_manufacture=2020,
                vehicle_type="14-seater",
                engine_capacity=2000,
                fuel_type="diesel",
                seating_capacity=14,
                route_number="11",
                emission_rating="EURO 4",
                mileage=50000,
                is_active=True
            )
            session.add(test_vehicle)
            session.commit()
            
            # Create test inspection
            test_inspection = NtsaInspection(
                vehicle_id=test_vehicle.id,
                inspection_date=datetime.now(),
                inspector_id="TEST-001",
                inspection_type="annual",
                roadworthiness_score=85.0,
                safety_score=90.0,
                emissions_score=80.0,
                overall_rating="Pass",
                violations_found=json.dumps(["No violations"]),
                recommendations=json.dumps(["Continue regular maintenance"]),
                next_inspection_date=datetime.now()
            )
            session.add(test_inspection)
            session.commit()
            
            # Test queries
            sacco_count = session.query(MatatuSacco).count()
            vehicle_count = session.query(MatatuVehicle).count()
            inspection_count = session.query(NtsaInspection).count()
            
            # Clean up test data
            session.query(NtsaInspection).delete()
            session.query(MatatuVehicle).delete()
            session.query(MatatuSacco).delete()
            session.commit()
            
        logger.info(f"✓ Data insertion/query successful: {sacco_count} SACCOS, {vehicle_count} vehicles, {inspection_count} inspections")
        logger.info(f"✓ Model compatibility test passed for {db_type}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Model compatibility test failed for {db_type}: {e}")
        return False

if __name__ == "__main__":
    # Add the parent directory to the path so we can import db.models
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from db.models import Base, MatatuSacco, MatatuVehicle, NtsaInspection
    from sqlalchemy import func
    
    import argparse
    parser = argparse.ArgumentParser(description="Matatu Fleet Data Ingestion")
    parser.add_argument("--db-type", choices=[DatabaseConfig.SQLITE, DatabaseConfig.POSTGRESQL], 
                       default=DatabaseConfig.SQLITE, help="Database type")
    parser.add_argument("--test-only", action="store_true", help="Only run compatibility tests")
    
    # PostgreSQL connection arguments
    parser.add_argument("--user", default="postgres", help="PostgreSQL username")
    parser.add_argument("--password", default="password", help="PostgreSQL password")
    parser.add_argument("--host", default="localhost", help="PostgreSQL host")
    parser.add_argument("--port", default="5432", help="PostgreSQL port")
    parser.add_argument("--database", default="carbon_trace", help="PostgreSQL database name")
    parser.add_argument("--sqlite-url", default="sqlite:///carbon_trace.db", help="SQLite database URL")
    
    args = parser.parse_args()
    
    # Prepare connection arguments
    db_kwargs = {
        'user': args.user,
        'password': args.password,
        'host': args.host,
        'port': args.port,
        'database': args.database,
        'sqlite_url': args.sqlite_url
    }
    
    # Run compatibility tests
    logger.info("Running model compatibility tests...")
    if test_model_compatibility(args.db_type, **db_kwargs):
        logger.info("✓ Compatibility tests passed")
    else:
        logger.error("✗ Compatibility tests failed")
        sys.exit(1)
    
    if not args.test_only:
        # Run data ingestion
        if load_matatu_datasets(args.db_type, **db_kwargs):
            generate_summary_report(args.db_type, **db_kwargs)
        else:
            logger.error("Data ingestion failed!")
            sys.exit(1)
