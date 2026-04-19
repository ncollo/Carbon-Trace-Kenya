#!/usr/bin/env python3
"""
PostgreSQL Compatibility Test for Carbon Trace Kenya Directory Structure
Tests if the current directory structure and models work with PostgreSQL
"""

import sys
import os
import logging
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_postgresql_connection():
    """Test PostgreSQL connection using docker-compose settings"""
    
    # Use docker-compose PostgreSQL settings
    pg_url = "postgresql://user:pass@localhost:5432/carbon"
    
    try:
        engine = create_engine(pg_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()")).scalar()
            logger.info(f"✓ PostgreSQL connection successful: {result[:50]}...")
            return True, engine
    except Exception as e:
        logger.error(f"✗ PostgreSQL connection failed: {e}")
        logger.info("Make sure PostgreSQL is running: docker-compose up -d postgres")
        return False, None

def test_model_creation(engine):
    """Test if all models can be created in PostgreSQL"""
    
    try:
        from db.models import Base, MatatuSacco, MatatuVehicle, NtsaInspection
        
        # Create all tables
        Base.metadata.create_all(engine)
        logger.info("✓ All database tables created successfully")
        
        # Inspect created tables
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = ['companies', 'users', 'uploads', 'emissions', 'anomaly_flags', 
                         'job_records', 'matatu_saccos', 'matatu_vehicles', 'ntsa_inspections']
        
        missing_tables = [t for t in expected_tables if t not in tables]
        if missing_tables:
            logger.error(f"✗ Missing tables: {missing_tables}")
            return False
        
        logger.info(f"✓ All expected tables created: {len(tables)} tables")
        
        # Check table structures
        for table_name in ['matatu_saccos', 'matatu_vehicles', 'ntsa_inspections']:
            columns = inspector.get_columns(table_name)
            logger.info(f"✓ Table '{table_name}' has {len(columns)} columns")
            
        return True
        
    except Exception as e:
        logger.error(f"✗ Model creation failed: {e}")
        return False

def test_data_types_compatibility(engine):
    """Test PostgreSQL-specific data types and features"""
    
    try:
        with engine.connect() as conn:
            # Test JSON support
            result = conn.execute(text("SELECT '{\"test\": \"value\"}'::jsonb")).scalar()
            logger.info("✓ PostgreSQL JSON/JSONB support working")
            
            # Test array support
            result = conn.execute(text("SELECT ARRAY[1,2,3]")).scalar()
            logger.info("✓ PostgreSQL array support working")
            
            # Test UUID support
            result = conn.execute(text("SELECT gen_random_uuid()")).scalar()
            logger.info("✓ PostgreSQL UUID support working")
            
            return True
            
    except Exception as e:
        logger.error(f"✗ PostgreSQL data types test failed: {e}")
        return False

def test_constraints_and_indexes(engine):
    """Test constraints and indexes creation"""
    
    try:
        inspector = inspect(engine)
        
        # Check indexes on Matatu tables
        matatu_indexes = inspector.get_indexes('matatu_saccos')
        logger.info(f"✓ matatu_saccos has {len(matatu_indexes)} indexes")
        
        matatu_indexes = inspector.get_indexes('matatu_vehicles')
        logger.info(f"✓ matatu_vehicles has {len(matatu_indexes)} indexes")
        
        matatu_indexes = inspector.get_indexes('ntsa_inspections')
        logger.info(f"✓ ntsa_inspections has {len(matatu_indexes)} indexes")
        
        # Test foreign key constraints
        fks = inspector.get_foreign_keys('matatu_vehicles')
        if fks:
            logger.info("✓ Foreign key constraints working on matatu_vehicles")
        else:
            logger.warning("⚠ No foreign key constraints found on matatu_vehicles")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Constraints/indexes test failed: {e}")
        return False

def test_directory_structure():
    """Test if directory structure supports PostgreSQL operations"""
    
    required_dirs = [
        'api',
        'db',
        'scripts',
        'config',
        'dataset_csv',
        'ingestion',
        'ghg_engine'
    ]
    
    missing_dirs = []
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        logger.error(f"✗ Missing directories: {missing_dirs}")
        return False
    
    logger.info("✓ All required directories present")
    
    # Check for PostgreSQL-specific files
    pg_files = [
        'config/postgresql_config.py',
        'scripts/ingest_matatu_data.py',
        'docker-compose.yml'
    ]
    
    missing_files = []
    for file_path in pg_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        logger.error(f"✗ Missing PostgreSQL files: {missing_files}")
        return False
    
    logger.info("✓ All PostgreSQL-specific files present")
    return True

def main():
    """Run all PostgreSQL compatibility tests"""
    
    logger.info("=" * 60)
    logger.info("POSTGRESQL COMPATIBILITY TEST FOR CARBON TRACE KENYA")
    logger.info("=" * 60)
    
    # Test directory structure
    logger.info("\n1. Testing directory structure...")
    if not test_directory_structure():
        logger.error("Directory structure test failed")
        return False
    
    # Test PostgreSQL connection
    logger.info("\n2. Testing PostgreSQL connection...")
    connected, engine = test_postgresql_connection()
    if not connected:
        logger.error("PostgreSQL connection test failed")
        return False
    
    # Test model creation
    logger.info("\n3. Testing model creation...")
    if not test_model_creation(engine):
        logger.error("Model creation test failed")
        return False
    
    # Test data types compatibility
    logger.info("\n4. Testing PostgreSQL data types...")
    if not test_data_types_compatibility(engine):
        logger.error("Data types compatibility test failed")
        return False
    
    # Test constraints and indexes
    logger.info("\n5. Testing constraints and indexes...")
    if not test_constraints_and_indexes(engine):
        logger.error("Constraints/indexes test failed")
        return False
    
    logger.info("\n" + "=" * 60)
    logger.info("✓ ALL POSTGRESQL COMPATIBILITY TESTS PASSED")
    logger.info("✓ Directory structure is fully compatible with PostgreSQL")
    logger.info("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
