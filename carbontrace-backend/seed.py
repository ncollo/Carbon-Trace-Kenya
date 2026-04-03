"""
Seed the database from the generated CSV datasets.
Loads both train and test splits for all modules.
"""
import pandas as pd
import os, sys
from database import SessionLocal, create_tables
from database import (
    FuelRecord, AnomalyRecord, TravelRecord, CommuteRecord,
    GHGSummary, EmissionFactor, PolicySimulation, EPRASectorAnalytics
)

import pathlib as _pl
_here = _pl.Path(__file__).parent.resolve()
# CSV files are bundled in dataset_csv/ inside the backend folder
CSV_DIR = str(_here / "dataset_csv")

def safe_float(val):
    try:
        f = float(val)
        return None if pd.isna(f) else f
    except:
        return None

def safe_int(val):
    try:
        return int(val)
    except:
        return None

def seed_fuel_records(db):
    print("  Seeding fuel card records...")
    count = 0
    for split in ["train", "test"]:
        df = pd.read_csv(f"{CSV_DIR}/fuel_card_{split}.csv")
        for _, row in df.iterrows():
            existing = db.query(FuelRecord).filter_by(record_id=row["record_id"]).first()
            if existing:
                continue
            db.add(FuelRecord(
                record_id=str(row["record_id"]),
                company_name=str(row["company_name"]),
                nse_code=str(row["nse_code"]),
                sector=str(row["sector"]),
                county=str(row["county"]),
                vehicle_id=str(row["vehicle_id"]),
                vehicle_class=str(row["vehicle_class"]),
                fuel_type=str(row["fuel_type"]),
                transaction_date=str(row["transaction_date"]),
                month=safe_int(row["month"]),
                quarter=safe_int(row["quarter"]),
                fuel_station_brand=str(row["fuel_station_brand"]),
                fuel_station_area=str(row["fuel_station_area"]),
                fuel_litres=safe_float(row["fuel_litres"]),
                fuel_price_ksh_per_l=safe_float(row["fuel_price_ksh_per_l"]),
                fuel_cost_ksh=safe_float(row["fuel_cost_ksh"]),
                gps_km_driven=safe_float(row["gps_km_driven"]),
                defra_ef_kgco2e_per_l=safe_float(row["defra_ef_kgco2e_per_l"]),
                kenya_road_adj=safe_float(row["kenya_road_adj"]),
                emission_kgco2e=safe_float(row["emission_kgco2e"]),
                emission_tco2e=safe_float(row["emission_tco2e"]),
                scope=str(row["scope"]),
                anomaly_flag=safe_int(row["anomaly_flag"]) or 0,
                anomaly_type=str(row["anomaly_type"]),
                fy_year=safe_int(row["fy_year"]),
            ))
            count += 1
        db.commit()
    print(f"    → {count} fuel records seeded")

def seed_anomaly_records(db):
    print("  Seeding anomaly records...")
    count = 0
    for split in ["train", "test"]:
        df = pd.read_csv(f"{CSV_DIR}/anomaly_{split}.csv")
        for _, row in df.iterrows():
            existing = db.query(AnomalyRecord).filter_by(anomaly_record_id=row["anomaly_record_id"]).first()
            if existing:
                continue
            db.add(AnomalyRecord(
                anomaly_record_id=str(row["anomaly_record_id"]),
                company_name=str(row["company_name"]),
                nse_code=str(row["nse_code"]),
                vehicle_id=str(row["vehicle_id"]),
                vehicle_class=str(row["vehicle_class"]),
                transaction_date=str(row["transaction_date"]),
                fuel_declared_l=safe_float(row["fuel_declared_l"]),
                gps_km_logged=safe_float(row["gps_km_logged"]),
                expected_fuel_l=safe_float(row["expected_fuel_l"]),
                delta_fuel_l=safe_float(row["delta_fuel_l"]),
                anomaly_flag=safe_int(row["anomaly_flag"]) or 1,
                anomaly_type=str(row["anomaly_type"]),
                anomaly_confidence=safe_float(row["anomaly_confidence"]),
                impact_tco2e=safe_float(row["impact_tco2e"]),
                isolation_score=safe_float(row["isolation_score"]),
                resolution_status=str(row["resolution_status"]),
            ))
            count += 1
        db.commit()
    print(f"    → {count} anomaly records seeded")

def seed_travel_records(db):
    print("  Seeding travel records...")
    count = 0
    for split in ["train", "test"]:
        df = pd.read_csv(f"{CSV_DIR}/travel_{split}.csv")
        for _, row in df.iterrows():
            existing = db.query(TravelRecord).filter_by(travel_record_id=row["travel_record_id"]).first()
            if existing:
                continue
            db.add(TravelRecord(
                travel_record_id=str(row["travel_record_id"]),
                company_name=str(row["company_name"]),
                nse_code=str(row["nse_code"]),
                sector=str(row["sector"]),
                travel_date=str(row["travel_date"]),
                month=safe_int(row["month"]),
                quarter=safe_int(row["quarter"]),
                origin_airport=str(row["origin_airport"]),
                destination_airport=str(row["destination_airport"]),
                flight_type=str(row["flight_type"]),
                cabin_class=str(row["cabin_class"]),
                passengers=safe_int(row["passengers"]),
                distance_km=safe_int(row["distance_km"]),
                ef_kgco2e_per_pkm=safe_float(row["ef_kgco2e_per_pkm"]),
                rfi_factor=safe_float(row["rfi_factor"]),
                emission_kgco2e=safe_float(row["emission_kgco2e"]),
                emission_tco2e=safe_float(row["emission_tco2e"]),
                scope=str(row["scope"]),
                category=str(row["category"]),
                cost_ksh=safe_float(row["cost_ksh"]),
                fy_year=safe_int(row["fy_year"]),
            ))
            count += 1
        db.commit()
    print(f"    → {count} travel records seeded")

def seed_commute_records(db):
    print("  Seeding commute records...")
    count = 0
    for split in ["train", "test"]:
        df = pd.read_csv(f"{CSV_DIR}/commute_{split}.csv")
        for _, row in df.iterrows():
            existing = db.query(CommuteRecord).filter_by(commute_record_id=row["commute_record_id"]).first()
            if existing:
                continue
            db.add(CommuteRecord(
                commute_record_id=str(row["commute_record_id"]),
                company_name=str(row["company_name"]),
                nse_code=str(row["nse_code"]),
                sector=str(row["sector"]),
                employee_id=str(row["employee_id"]),
                county_residence=str(row["county_residence"]),
                commute_mode=str(row["commute_mode"]),
                one_way_km=safe_float(row["one_way_km"]),
                working_days_pa=safe_int(row["working_days_pa"]),
                annual_commute_km=safe_float(row["annual_commute_km"]),
                ef_kgco2e_per_km=safe_float(row["ef_kgco2e_per_km"]),
                emission_kgco2e=safe_float(row["emission_kgco2e"]),
                emission_tco2e=safe_float(row["emission_tco2e"]),
                scope=str(row["scope"]),
                category=str(row["category"]),
                fy_year=safe_int(row["fy_year"]),
            ))
            count += 1
        db.commit()
    print(f"    → {count} commute records seeded")

def seed_ghg_summary(db):
    print("  Seeding GHG summaries...")
    count = 0
    for split in ["train", "test"]:
        df = pd.read_csv(f"{CSV_DIR}/ghg_summary_{split}.csv")
        for _, row in df.iterrows():
            existing = db.query(GHGSummary).filter_by(company_id=row["company_id"]).first()
            if existing:
                continue
            db.add(GHGSummary(
                company_id=str(row["company_id"]),
                company_name=str(row["company_name"]),
                nse_code=str(row["nse_code"]),
                sector=str(row["sector"]),
                county_hq=str(row["county_hq"]),
                fy_year=safe_int(row["fy_year"]),
                revenue_ksh_millions=safe_float(row["revenue_ksh_millions"]),
                fleet_size_vehicles=safe_int(row["fleet_size_vehicles"]),
                scope1_tco2e=safe_float(row["scope1_tco2e"]),
                s3_cat6_tco2e=safe_float(row["s3_cat6_tco2e"]),
                s3_cat7_tco2e=safe_float(row["s3_cat7_tco2e"]),
                total_tco2e=safe_float(row["total_tco2e"]),
                fy23_total_tco2e=safe_float(row["fy23_total_tco2e"]),
                yoy_change_pct=safe_float(row["yoy_change_pct"]),
                intensity_tco2e_per_ksh_m=safe_float(row["intensity_tco2e_per_ksh_m"]),
                uncertainty_pct_95ci=safe_float(row["uncertainty_pct_95ci"]),
                ci_low_tco2e=safe_float(row["ci_low_tco2e"]),
                ci_high_tco2e=safe_float(row["ci_high_tco2e"]),
                defra_ef_version=str(row["defra_ef_version"]),
                ipcc_gwp_version=str(row["ipcc_gwp_version"]),
                ketraco_grid_ef=safe_float(row["ketraco_grid_ef"]),
                kenya_road_adj=safe_float(row["kenya_road_adj"]),
                tier_scope1=str(row["tier_scope1"]),
                tier_s3c6=str(row["tier_s3c6"]),
                tier_s3c7=str(row["tier_s3c7"]),
                nse_compliant=safe_int(row["nse_compliant"]),
                xbrl_taxonomy=str(row["xbrl_taxonomy"]),
                gri_305_aligned=safe_int(row["gri_305_aligned"]),
                consent_federated=safe_int(row["consent_federated"]),
            ))
            count += 1
        db.commit()
    print(f"    → {count} GHG summaries seeded")

def seed_emission_factors(db):
    print("  Seeding emission factors...")
    df = pd.read_csv(f"{CSV_DIR}/emission_factor_register.csv")
    count = 0
    for _, row in df.iterrows():
        existing = db.query(EmissionFactor).filter_by(ef_id=row["ef_id"]).first()
        if existing:
            continue
        db.add(EmissionFactor(
            ef_id=str(row["ef_id"]),
            category=str(row["category"]),
            vehicle_class=str(row["vehicle_class"]),
            ef_kgco2e_per_l=safe_float(row.get("ef_kgco2e_per_l")),
            ef_kgco2e_per_kwh=safe_float(row.get("ef_kgco2e_per_kwh")),
            ef_kgco2e_per_pkm=safe_float(row.get("ef_kgco2e_per_pkm")),
            kenya_adj_factor=safe_float(row["kenya_adj_factor"]),
            adjusted_ef=safe_float(row["adjusted_ef"]),
            source=str(row["source"]),
            ipcc_gwp=str(row["ipcc_gwp"]),
            scope=str(row["scope"]),
            tier=str(row["tier"]),
        ))
        count += 1
    db.commit()
    print(f"    → {count} emission factors seeded")

def seed_policy_simulations(db):
    print("  Seeding policy simulation data...")
    count = 0
    for split in ["train", "test"]:
        df = pd.read_csv(f"{CSV_DIR}/policy_sim_{split}.csv")
        for _, row in df.iterrows():
            existing = db.query(PolicySimulation).filter_by(sim_id=row["sim_id"]).first()
            if existing:
                continue
            db.add(PolicySimulation(
                sim_id=str(row["sim_id"]),
                ev_mandate_pct=safe_float(row["ev_mandate_pct"]),
                fuel_economy_std_pct=safe_float(row["fuel_economy_std_pct"]),
                remote_work_pct=safe_float(row["remote_work_pct"]),
                sector_baseline_tco2e=safe_float(row["sector_baseline_tco2e"]),
                projected_reduction_tco2e=safe_float(row["projected_reduction_tco2e"]),
                projected_total_tco2e=safe_float(row["projected_total_tco2e"]),
                reduction_pct=safe_float(row["reduction_pct"]),
                ndc_2025_target=safe_float(row["ndc_2025_target"]),
                ndc_gap_tco2e=safe_float(row["ndc_gap_tco2e"]),
                ndc_met=safe_int(row["ndc_met"]),
                label_ndc_met=str(row["label_ndc_met"]),
            ))
            count += 1
        db.commit()
    print(f"    → {count} policy simulations seeded")

def seed_epra_analytics(db):
    print("  Seeding EPRA sector analytics...")
    df = pd.read_csv(f"{CSV_DIR}/epra_sector_analytics.csv")
    count = 0
    for _, row in df.iterrows():
        existing = db.query(EPRASectorAnalytics).filter_by(sector=row["sector"]).first()
        if existing:
            continue
        db.add(EPRASectorAnalytics(
            sector=str(row["sector"]),
            n_companies=safe_int(row["n_companies"]),
            total_tco2e=safe_float(row["total_tco2e"]),
            avg_intensity=safe_float(row["avg_intensity"]),
            min_intensity=safe_float(row["min_intensity"]),
            max_intensity=safe_float(row["max_intensity"]),
            median_intensity=safe_float(row["median_intensity"]),
            avg_fleet_size=safe_float(row["avg_fleet_size"]),
            avg_yoy_change_pct=safe_float(row["avg_yoy_change_pct"]),
            sector_pct_of_national=safe_float(row["sector_pct_of_national"]),
            ndc_2025_target_tco2e=safe_float(row["ndc_2025_target_tco2e"]),
            ndc_gap_tco2e=safe_float(row["ndc_gap_tco2e"]),
        ))
        count += 1
    db.commit()
    print(f"    → {count} EPRA sector records seeded")

def run_seed():
    print("Creating tables...")
    create_tables()
    db = SessionLocal()
    try:
        print("Seeding from CSV datasets...")
        seed_emission_factors(db)
        seed_fuel_records(db)
        seed_anomaly_records(db)
        seed_travel_records(db)
        seed_commute_records(db)
        seed_ghg_summary(db)
        seed_policy_simulations(db)
        seed_epra_analytics(db)
        print("\n✓ Database seeded successfully.")
    finally:
        db.close()

if __name__ == "__main__":
    run_seed()
