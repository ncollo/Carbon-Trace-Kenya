#!/usr/bin/env python
"""
Database seeding script for Carbon Trace Kenya.
Populates the database with sample companies, users, and emissions data for testing.

Usage:
    python seed.py
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import hashlib
import random

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from db.session import SessionLocal, engine
from db.models import Base, Company, User, Upload, Emission, AnomalyFlag

# ============================================================================
# CONFIGURATION
# ============================================================================

SECTORS = [
    "Agriculture",
    "Banking & Finance",
    "Construction",
    "Education",
    "Energy & Petroleum",
    "Healthcare",
    "Hospitality",
    "Insurance",
    "Logistics",
    "Manufacturing",
    "Media",
    "Real Estate",
    "Retail & FMCG",
    "Technology",
    "Telecommunications"
]

SAMPLE_COMPANIES = [
    {"name": "Evans Group", "sector": "Logistics"},
    {"name": "Harding Ltd", "sector": "Manufacturing"},
    {"name": "Bray Group", "sector": "Energy & Petroleum"},
    {"name": "Francis Taylor and Lowe", "sector": "Agriculture"},
    {"name": "Tech Solutions Kenya", "sector": "Technology"},
    {"name": "Kenya Finance Bank", "sector": "Banking & Finance"},
    {"name": "Nairobi Construction Co", "sector": "Construction"},
    {"name": "East African Healthcare", "sector": "Healthcare"},
    {"name": "Safari Hotels Ltd", "sector": "Hospitality"},
    {"name": "Kenya Insurance Corp", "sector": "Insurance"},
]

SCOPES = ["Scope 1", "Scope 2", "Scope 3"]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def hash_password(password: str) -> str:
    """Hash a password (same as in auth.py)."""
    salt = os.getenv("PASSWORD_SALT", "default-salt-change-me")
    return hashlib.sha256((password + salt).encode()).hexdigest()


def seed_companies_and_users(session):
    """Create sample companies and users."""
    print("[*] Seeding companies and users...")
    
    companies = []
    for i, company_data in enumerate(SAMPLE_COMPANIES):
        company = Company(name=company_data["name"])
        session.add(company)
        session.flush()  # Get the ID
        companies.append(company)
        
        # Create admin user for each company
        user = User(
            email=f"admin.{company.name.lower().replace(' ', '.')}@carbontrace.ke",
            password_hash=hash_password("DemoPassword123"),
            company_id=company.id,
            role="admin",
            is_active=True
        )
        session.add(user)
        
        # Create additional users
        for j in range(2):
            user = User(
                email=f"user{j+1}.{company.name.lower().replace(' ', '.')}@carbontrace.ke",
                password_hash=hash_password("DemoPassword123"),
                company_id=company.id,
                role="user",
                is_active=True
            )
            session.add(user)
    
    session.commit()
    print(f"[OK] Created {len(SAMPLE_COMPANIES)} companies with {len(SAMPLE_COMPANIES) * 3} users")
    
    return companies


def seed_uploads(session, companies):
    """Create sample upload records."""
    print("[*] Seeding uploads...")
    
    for company in companies[:5]:  # Add uploads for first 5 companies
        for i in range(random.randint(2, 5)):
            upload = Upload(
                company_id=company.id,
                filename=f"quarterly_report_{i+1}_fy2024.pdf",
                uploaded_at=datetime.now() - timedelta(days=random.randint(1, 90))
            )
            session.add(upload)
    
    session.commit()
    print(f"[OK] Created sample uploads")


def seed_emissions(session, companies):
    """Create sample emission records."""
    print("[*] Seeding emissions data...")
    
    for company in companies:
        # Create Scope 1, 2, 3 emissions for each company
        for scope in SCOPES:
            # Generate realistic emission values (in tCO2e)
            base_value = random.uniform(500, 25000)
            
            for month in range(1, 13):  # 12 months of data
                variance = base_value * random.uniform(0.8, 1.2)
                emission = Emission(
                    company_id=company.id,
                    scope=scope,
                    value=round(variance, 2)
                )
                session.add(emission)
    
    session.commit()
    print(f"[OK] Created {len(companies) * 3 * 12} emission records")


def seed_anomaly_flags(session):
    """Create sample anomaly flags."""
    print("[*] Seeding anomaly flags...")
    
    # Get all uploads
    uploads = session.query(Upload).all()
    
    for upload in uploads[:10]:  # Add flags to first 10 uploads
        if random.random() < 0.3:  # 30% chance of anomaly
            flag = AnomalyFlag(
                upload_id=upload.id,
                resolved=random.choice([True, False])
            )
            session.add(flag)
    
    session.commit()
    print(f"[OK] Created sample anomaly flags")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Execute database seeding."""
    print("\n" + "="*80)
    print("CARBON TRACE KENYA - DATABASE SEEDING")
    print("="*80)
    
    # Create all tables
    print("\n[*] Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("[OK] Tables created")
    
    # Initialize session
    session = SessionLocal()
    
    try:
        # Check if data already exists
        company_count = session.query(Company).count()
        if company_count > 0:
            print(f"\n[WARN] Database already contains {company_count} companies")
            response = input("Do you want to clear existing data? (yes/no): ").lower()
            
            if response == "yes":
                print("[*] Clearing existing data...")
                session.query(AnomalyFlag).delete()
                session.query(Emission).delete()
                session.query(Upload).delete()
                session.query(User).delete()
                session.query(Company).delete()
                session.commit()
                print("[OK] Data cleared")
            else:
                print("[*] Skipping seeding")
                return
        
        # Seed data
        companies = seed_companies_and_users(session)
        seed_uploads(session, companies)
        seed_emissions(session, companies)
        seed_anomaly_flags(session)
        
        # Print summary
        print("\n" + "-"*80)
        print("SEEDING SUMMARY")
        print("-"*80)
        print(f"Companies: {session.query(Company).count()}")
        print(f"Users: {session.query(User).count()}")
        print(f"Uploads: {session.query(Upload).count()}")
        print(f"Emissions: {session.query(Emission).count()}")
        print(f"Anomaly Flags: {session.query(AnomalyFlag).count()}")
        
        # Print test credentials
        print("\n" + "-"*80)
        print("TEST CREDENTIALS")
        print("-"*80)
        test_user = session.query(User).first()
        if test_user:
            print(f"Email: {test_user.email}")
            print(f"Password: DemoPassword123")
            print(f"\nAPI Endpoint: http://localhost:8000/api/auth/token")
            print(f"Docs: http://localhost:8000/docs")
        
        print("\n" + "="*80)
        print("[OK] Database seeding completed successfully!")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n[ERROR] Seeding failed: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
