import pandas as pd
from typing import Dict, Any, List

# Local import (same folder)
from model_loader_v2 import load_realtime_models


# ================================
# LOAD ALL REALTIME MODELS (ONCE)
# ================================
MODELS = load_realtime_models()


# ================================
# REALTIME FEATURE LIST (LOCKED)
# ================================
REALTIME_FEATURES = [
    "Destination Port",
    "Flow Duration",
    "Total Fwd Packets",
    "Total Backward Packets",
    "Total Length of Fwd Packets",
    "Total Length of Bwd Packets",
    "Fwd Packet Length Min",
    "Fwd Packet Length Mean",
    "Packet Length Std",
    "Flow IAT Mean",
    "Fwd IAT Mean",
    "Down/Up Ratio"
]


# ================================
# MULTI-MODEL REALTIME DETECTOR
# ================================
def detect_with_all_models(
    feature_row: pd.DataFrame,
    selected_models: List[str]
) -> Dict[str, Dict[str, Any]]:
    """
    Run inference using SELECTED realtime ML models.

    Parameters
    ----------
    feature_row : pd.DataFrame
        Single-row dataframe with locked realtime features
    selected_models : list
        List of model names to use

    Returns
    -------
    dict
        {
            "ModelName": {
                "prediction": 0/1,
                "probability": float
            }
        }
    """

    # -------------------------------
    # 1️⃣ Safety checks
    # -------------------------------
    if not isinstance(feature_row, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")

    if feature_row.shape[0] != 1:
        raise ValueError("Feature dataframe must contain exactly ONE row")

    missing = set(REALTIME_FEATURES) - set(feature_row.columns)
    if missing:
        raise ValueError(f"Missing required features: {missing}")

    # Ensure correct order
    feature_row = feature_row[REALTIME_FEATURES]

    results = {}

    # -------------------------------
    # 2️⃣ Run inference on selected models
    # -------------------------------
    for model_name in selected_models:
        if model_name not in MODELS:
            results[model_name] = {
                "prediction": 0,
                "probability": 0.0,
                "error": "Model not loaded"
            }
            continue

        model = MODELS[model_name]

        try:
            pred = int(model.predict(feature_row)[0])
            prob = float(model.predict_proba(feature_row)[0][1])

            results[model_name] = {
                "prediction": pred,
                "probability": round(prob, 6)
            }

        except Exception as e:
            results[model_name] = {
                "prediction": 0,
                "probability": 0.0,
                "error": str(e)
            }

    return results
