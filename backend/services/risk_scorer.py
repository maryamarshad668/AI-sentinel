import os
import numpy as np
import pickle
from xgboost import XGBRegressor
from sklearn.preprocessing import MinMaxScaler
from typing import Dict, List


MODEL_PATH = "models/xgboost_model.pkl"
SCALER_PATH = "models/scaler.pkl"


def generate_training_data(n_samples: int = 2000):
    """
    Generate synthetic training data based on software engineering research.
    High complexity + high churn + low maintainability = high risk score.
    """
    np.random.seed(42)

    loc             = np.random.randint(10, 500, n_samples).astype(float)
    cc_avg          = np.random.uniform(1, 15, n_samples)
    cc_max          = cc_avg + np.random.uniform(0, 8, n_samples)
    halstead_effort = np.random.uniform(0, 10000, n_samples)
    maintainability = np.random.uniform(0, 100, n_samples)
    churn_rate      = np.random.uniform(0, 20, n_samples)

    # Risk score formula — denominators match new ranges
    risk = (
        0.30 * (cc_avg / 15) +
        0.20 * (cc_max / 23) +
        0.15 * (churn_rate / 20) +
        0.15 * (loc / 500) +
        0.10 * (halstead_effort / 10000) +
        0.10 * (1 - maintainability / 100)  # low MI = high risk
    )

    # Add noise and scale to 0-100
    noise = np.random.normal(0, 0.03, n_samples)
    risk_score = np.clip((risk + noise) * 100, 0, 100)

    X = np.column_stack([loc, cc_avg, cc_max, halstead_effort, maintainability, churn_rate])
    y = risk_score
    return X, y


def train_and_save_model():
    """Train the XGBoost model and save it to disk."""
    os.makedirs("models", exist_ok=True)

    print("🔄 Generating training data...")
    X, y = generate_training_data()

    print("🔄 Training XGBoost model...")
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    model = XGBRegressor(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        verbosity=0
    )
    model.fit(X_scaled, y)

    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
    with open(SCALER_PATH, 'wb') as f:
        pickle.dump(scaler, f)

    print("✅ Model trained and saved to models/")


def load_model():
    """Load the trained model and scaler from disk."""
    if not os.path.exists(MODEL_PATH):
        print("⚠️  Model not found. Training now...")
        train_and_save_model()

    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    with open(SCALER_PATH, 'rb') as f:
        scaler = pickle.load(f)

    return model, scaler


def get_risk_tier(score: float) -> str:
    """Convert a numeric risk score to a tier label."""
    if score >= 75:
        return "Critical"
    elif score >= 50:
        return "High"
    elif score >= 25:
        return "Moderate"
    else:
        return "Low"


def compute_hotspot_score(cc_avg: float, churn_rate: float, loc: int,
                           max_cc: float = 15, max_churn: float = 20, max_loc: float = 500) -> float:
    """Hotspot = weighted combo of complexity, churn, and size."""
    norm_cc    = min(cc_avg / max_cc, 1.0)
    norm_churn = min(churn_rate / max_churn, 1.0)
    norm_loc   = min(loc / max_loc, 1.0)
    return round(0.5 * norm_cc + 0.3 * norm_churn + 0.2 * norm_loc, 4)


def compute_tdc(risk_score: float, hourly_rate: float = 75.0) -> float:
    """Technical Debt Cost = (risk/100) * hourly_rate * remediation_hours."""
    if risk_score >= 75:
        remediation_hours = 40
    elif risk_score >= 50:
        remediation_hours = 20
    elif risk_score >= 25:
        remediation_hours = 8
    else:
        remediation_hours = 2
    return round((risk_score / 100) * hourly_rate * remediation_hours, 2)


def score_files(file_metrics: List[Dict], hourly_rate: float = 75.0) -> List[Dict]:
    """
    Take a list of file metrics dicts (from analyzer.py)
    and return them enriched with risk scores, tiers, hotspot flags, and TDC.
    """
    model, scaler = load_model()

    results = []
    for m in file_metrics:
        loc             = m.get("loc", 0)
        cc_avg          = m.get("cc_avg", 1.0)
        cc_max          = m.get("cc_max", 1.0)
        halstead_effort = m.get("halstead_effort", 0.0)
        maintainability = m.get("maintainability_index", 50.0)
        churn_rate      = m.get("churn_rate", 0.0)

        features = np.array([[loc, cc_avg, cc_max, halstead_effort, maintainability, churn_rate]])
        features_scaled = scaler.transform(features)
        risk_score = float(np.clip(model.predict(features_scaled)[0], 0, 100))

        hotspot_score = compute_hotspot_score(cc_avg, churn_rate, loc)
        is_hotspot    = hotspot_score >= 0.75
        risk_tier     = get_risk_tier(risk_score)
        tdc_annual    = compute_tdc(risk_score, hourly_rate)

        results.append({
            **m,
            "risk_score":    round(risk_score, 2),
            "risk_tier":     risk_tier,
            "hotspot_score": hotspot_score,
            "is_hotspot":    is_hotspot,
            "tdc_annual":    tdc_annual,
        })

    results.sort(key=lambda x: x["risk_score"], reverse=True)
    return results