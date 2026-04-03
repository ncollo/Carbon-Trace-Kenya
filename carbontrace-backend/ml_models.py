"""
ML Models for CarbonTrace Kenya
- Isolation Forest: trained on real anomaly + fuel card data from CSVs
- GHG Calculator: deterministic engine using DEFRA 2024 / KETRACO factors
- Emission factor lookup: from database
"""
import numpy as np
import pandas as pd
import pickle, os, pathlib as _pl
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder

# Resolve paths cross-platform (Windows + Linux + Mac)
_here = _pl.Path(__file__).parent.resolve()

MODEL_PATH   = str(_here / "models" / "isolation_forest.pkl")
ENCODER_PATH = str(_here / "models" / "label_encoder.pkl")

# CSV files are bundled in dataset_csv/ inside the backend folder
CSV_DIR = str(_here / "dataset_csv")

# ── GHG Protocol constants (from proposal + DEFRA 2024 + KETRACO) ─────────────
DEFRA_EF = {
    "diesel_truck":  2.640, "diesel_van":    2.640,
    "petrol_saloon": 2.311, "petrol_suv":    2.311,
    "petrol_4wd":    2.640, "petrol_bike":   2.296,
    "diesel_bus":    2.640, "lpg_van":       1.630,
    "cng_van":       2.040, "ev":            0.0,
}
KETRACO_EF    = 0.392   # kgCO2e per kWh
KENYA_ROAD_ADJ = 1.18   # NTSA +18%
GWP = {"CO2": 1.0, "CH4": 27.9, "N2O": 273.0}

# Rated L/100km (manufacturer, pre-Kenya adjustment)
RATED_L100KM = {
    "diesel_truck":  28.0, "diesel_van":    10.5,
    "petrol_saloon":  8.2, "petrol_suv":   12.5,
    "petrol_4wd":    14.0, "petrol_bike":   4.0,
    "diesel_bus":    18.0, "lpg_van":      12.0,
    "cng_van":       11.0,
}

def get_expected_fuel(gps_km: float, vehicle_class: str) -> float:
    """Expected fuel given GPS km and vehicle class, Kenya-adjusted."""
    l100 = RATED_L100KM.get(vehicle_class, 10.0) * KENYA_ROAD_ADJ
    return round((gps_km / 100.0) * l100, 3)

def calc_emission_tco2e(fuel_litres: float, vehicle_class: str, ev_kwh: float = 0.0) -> float:
    """Calculate tCO2e from fuel quantity using DEFRA 2024 + Kenya calibration."""
    if vehicle_class == "ev":
        return round(ev_kwh * KETRACO_EF / 1000, 6)
    ef = DEFRA_EF.get(vehicle_class, 2.311)
    return round(fuel_litres * ef / 1000, 6)

def train_isolation_forest():
    """Train Isolation Forest on the real CSV training data."""
    print("Training Isolation Forest on CSV data...")

    # Load clean fuel records (anomaly_flag=0)
    fuel_df = pd.read_csv(f"{CSV_DIR}/fuel_card_train.csv")
    clean = fuel_df[fuel_df["anomaly_flag"] == 0].copy()

    # Load anomaly records (anomaly_flag=1)
    ano_df = pd.read_csv(f"{CSV_DIR}/anomaly_train.csv")

    # Build feature matrix from clean records
    le = LabelEncoder()
    all_classes = list(set(clean["vehicle_class"].tolist() + ano_df["vehicle_class"].tolist()))
    le.fit(all_classes)

    def build_features_fuel(df):
        df = df.copy()
        df["vehicle_class_enc"] = le.transform(df["vehicle_class"])
        df["expected_fuel"] = df.apply(
            lambda r: get_expected_fuel(r["gps_km_driven"], r["vehicle_class"]), axis=1
        )
        df["delta_fuel"] = df["fuel_litres"] - df["expected_fuel"]
        df["delta_pct"]  = df["delta_fuel"] / (df["expected_fuel"] + 0.001)
        features = ["fuel_litres", "gps_km_driven", "expected_fuel", "delta_fuel",
                    "delta_pct", "vehicle_class_enc"]
        return df[features].fillna(0).values

    def build_features_ano(df):
        df = df.copy()
        # Re-encode safely
        known = set(le.classes_)
        df["vehicle_class_safe"] = df["vehicle_class"].apply(lambda x: x if x in known else "petrol_saloon")
        df["vehicle_class_enc"] = le.transform(df["vehicle_class_safe"])
        df["delta_pct"] = df["delta_fuel_l"] / (df["expected_fuel_l"] + 0.001)
        features_map = {
            "fuel_litres": "fuel_declared_l",
            "gps_km_driven": "gps_km_logged",
            "expected_fuel": "expected_fuel_l",
            "delta_fuel": "delta_fuel_l",
        }
        out = pd.DataFrame()
        for feat, col in features_map.items():
            out[feat] = df[col]
        out["delta_pct"] = df["delta_pct"]
        out["vehicle_class_enc"] = df["vehicle_class_enc"]
        return out.fillna(0).values

    X_clean = build_features_fuel(clean)

    # Train on clean data (unsupervised — learns the normal distribution)
    model = IsolationForest(
        n_estimators=200,
        contamination=0.05,
        max_samples="auto",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_clean)

    # Evaluate on anomaly records
    X_ano = build_features_ano(ano_df)
    preds = model.predict(X_ano)
    # -1 = anomaly, +1 = normal
    detected = sum(1 for p in preds if p == -1)
    print(f"  Detection rate on anomaly test: {detected}/{len(preds)} = {detected/len(preds):.1%}")

    # Save
    os.makedirs(_here / "models", exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    with open(ENCODER_PATH, "wb") as f:
        pickle.dump(le, f)
    print(f"  Model saved → {MODEL_PATH}")
    return model, le

def load_model():
    if os.path.exists(MODEL_PATH) and os.path.exists(ENCODER_PATH):
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        with open(ENCODER_PATH, "rb") as f:
            le = pickle.load(f)
        return model, le
    return train_isolation_forest()

def predict_anomaly(fuel_litres: float, gps_km: float, vehicle_class: str) -> dict:
    """Run the Isolation Forest model on a single record."""
    model, le = load_model()
    known = set(le.classes_)
    vc_safe = vehicle_class if vehicle_class in known else "petrol_saloon"
    vc_enc = le.transform([vc_safe])[0]

    expected = get_expected_fuel(gps_km, vehicle_class)
    delta = fuel_litres - expected
    delta_pct = delta / (expected + 0.001)

    X = np.array([[fuel_litres, gps_km, expected, delta, delta_pct, vc_enc]])
    score = model.score_samples(X)[0]
    pred  = model.predict(X)[0]

    is_anomaly = pred == -1
    # Determine type
    if gps_km == 0 and fuel_litres > 0:
        anomaly_type = "zero_gps_nonzero_fuel"
    elif delta_pct > 0.5:
        anomaly_type = "impossible_consumption"
    elif delta_pct > 0.3:
        anomaly_type = "over_capacity"
    else:
        anomaly_type = "clean" if not is_anomaly else "suspicious"

    impact = calc_emission_tco2e(abs(delta), vehicle_class) if is_anomaly else 0.0

    return {
        "is_anomaly": is_anomaly,
        "anomaly_type": anomaly_type if is_anomaly else "clean",
        "isolation_score": round(float(score), 4),
        "confidence": round(min(0.99, abs(score) * 3), 4) if is_anomaly else 0.0,
        "expected_fuel_l": round(expected, 3),
        "delta_fuel_l": round(delta, 3),
        "impact_tco2e": round(impact, 6),
    }

def calculate_ghg(fuel_records: list, travel_records: list, commute_records: list) -> dict:
    """
    Full GHG Protocol calculation from lists of records.
    Returns scope breakdown, total, intensity, uncertainty.
    """
    scope1 = sum(r.get("emission_tco2e", 0) or 0 for r in fuel_records)
    s3c6   = sum(r.get("emission_tco2e", 0) or 0 for r in travel_records)
    s3c7   = sum(r.get("emission_tco2e", 0) or 0 for r in commute_records)
    total  = scope1 + s3c6 + s3c7

    # Bayesian uncertainty approximation (±5% EF, ±2.1% activity, ±3% road adj)
    # Combined in quadrature
    uncertainty_pct = round((0.05**2 + 0.021**2 + 0.03**2)**0.5 * 100, 2)
    ci_low  = round(total * (1 - uncertainty_pct / 100), 2)
    ci_high = round(total * (1 + uncertainty_pct / 100), 2)

    return {
        "scope1_tco2e": round(scope1, 2),
        "s3_cat6_tco2e": round(s3c6, 2),
        "s3_cat7_tco2e": round(s3c7, 2),
        "total_tco2e": round(total, 2),
        "uncertainty_pct_95ci": uncertainty_pct,
        "ci_low_tco2e": ci_low,
        "ci_high_tco2e": ci_high,
        "defra_ef_version": "DEFRA 2024",
        "ipcc_gwp_version": "AR6 100-year",
        "ketraco_grid_ef": KETRACO_EF,
        "kenya_road_adj": KENYA_ROAD_ADJ,
    }

def simulate_policy(ev_pct: float, fe_pct: float, rw_pct: float,
                    baseline_tco2e: float = 218000.0) -> dict:
    """
    Policy simulation using coefficients derived from training data regression.
    ev_pct: EV mandate adoption %
    fe_pct: Fuel economy standard % above baseline
    rw_pct: Remote work policy % of workforce
    """
    # Load training data to fit actual coefficients
    df = pd.read_csv(f"{CSV_DIR}/policy_sim_train.csv")
    # Simple linear model from training data
    from numpy.linalg import lstsq
    X = df[["ev_mandate_pct","fuel_economy_std_pct","remote_work_pct"]].values
    y = df["projected_reduction_tco2e"].values
    coeffs, _, _, _ = lstsq(
        np.column_stack([X, np.ones(len(X))]), y, rcond=None
    )
    ev_coeff, fe_coeff, rw_coeff, intercept = coeffs

    reduction = float(ev_pct * ev_coeff + fe_pct * fe_coeff + rw_pct * rw_coeff + intercept)
    reduction = max(0, min(reduction, baseline_tco2e * 0.95))
    projected = baseline_tco2e - reduction
    ndc_target = 200000.0
    ndc_gap = max(0, projected - ndc_target)

    return {
        "baseline_tco2e": baseline_tco2e,
        "projected_reduction_tco2e": round(reduction, 1),
        "projected_total_tco2e": round(projected, 1),
        "reduction_pct": round(reduction / baseline_tco2e * 100, 2),
        "ndc_2025_target": ndc_target,
        "ndc_gap_tco2e": round(ndc_gap, 1),
        "ndc_met": ndc_gap == 0,
        "model": "linear regression on 400 training simulations",
    }

if __name__ == "__main__":
    train_isolation_forest()
