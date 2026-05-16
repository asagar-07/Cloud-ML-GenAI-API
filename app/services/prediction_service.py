import joblib
import time
from pathlib import Path
from typing import Any, Dict

import pandas as pd

MODEL_PATH = Path("models/prototype/fraud_model.pkl") 

# Model expects features in a specific order, so we define the list of feature columns accordingly
FEATURE_COLUMNS = [
    "Time",
    "V1", "V2", "V3", "V4", "V5", "V6", "V7",
    "V8", "V9", "V10", "V11", "V12", "V13", "V14",
    "V15", "V16", "V17", "V18", "V19", "V20", "V21",
    "V22", "V23", "V24", "V25", "V26", "V27", "V28",
    "Amount",
]

_model = None

def load_model() -> Any:
    global _model

    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model file not found at: {MODEL_PATH}")

        _model = joblib.load(MODEL_PATH)
        
    return _model


def validate_payload(payload: Dict[str, Any]) -> None:
    missing_fields = [field for field in FEATURE_COLUMNS if field not in payload]

    if missing_fields:
        raise ValueError(f"Missing required feature fields: {missing_fields}")


def build_feature_dataframe(payload: Dict[str, Any]) -> pd.DataFrame:
    validate_payload(payload)

    ordered_features = {
        feature: payload[feature]
        for feature in FEATURE_COLUMNS
    }

    return pd.DataFrame([ordered_features], columns=FEATURE_COLUMNS)


def predict_fraud(payload: Dict[str, Any]) -> Dict[str, Any]:
    start_time = time.perf_counter()

    model = load_model()
    input_df = build_feature_dataframe(payload)

    prediction = int(model.predict(input_df)[0])

    fraud_probability = None
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(input_df)[0]
        fraud_probability = float(probabilities[1])

    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

    return {
        "prediction": prediction,
        "prediction_label": "FRAUD" if prediction == 1 else "NOT_FRAUD",
        "fraud_probability": fraud_probability,
        "target": "Class",
        "model_stage": "Random Forest Classifier - Prototype",
        "model_type": type(model).__name__,
        "latency_ms": latency_ms,
    }