# detection-engine/realtime_v2/model_loader_v2.py
# ==================================================
# Phase-2 Dynamic Model Loader (Metadata Driven)
# ==================================================

import os
import json
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODELS_BASE_DIR = os.path.join(BASE_DIR, "..", "..", "models", "phase2_offline_v2")
METADATA_FILE = os.path.join(MODELS_BASE_DIR, "model_metadata.json")
SCALER_FILE = "scaler_v2.pkl"


def load_model_and_scaler():
    print("📦 Loading model using evaluation metadata...")

    # ---------------- LOAD METADATA ----------------
    if not os.path.exists(METADATA_FILE):
        raise FileNotFoundError(f"❌ Metadata file missing: {METADATA_FILE}")

    with open(METADATA_FILE, "r") as f:
        metadata = json.load(f)

    model_file = metadata["selected_model"]

    model_path = os.path.join(MODELS_BASE_DIR, model_file)
    scaler_path = os.path.join(MODELS_BASE_DIR, SCALER_FILE)

    # ---------------- SAFETY CHECKS ----------------
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"❌ Model not found: {model_path}")

    if not os.path.exists(scaler_path):
        raise FileNotFoundError(f"❌ Scaler not found: {scaler_path}")

    # ---------------- LOAD ----------------
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)

    # ---------------- VALIDATION ----------------
    if not hasattr(model, "predict") or not hasattr(model, "predict_proba"):
        raise AttributeError("❌ Loaded model missing required methods")

    print("✅ Model & scaler loaded successfully")
    print(f"🏆 Selected Model: {model_file}")
    print(f"📊 Selection Basis: {metadata['selection_criteria']}")
    print(f"📈 Avg F1: {metadata['metrics']['avg_f1']}")
    print(f"📈 Avg ROC–AUC: {metadata['metrics']['avg_roc_auc']}")

    return model, scaler


# ---------------- SELF TEST ----------------
if __name__ == "__main__":
    print("🧪 Running metadata-driven model loader test...")
    model, scaler = load_model_and_scaler()
    print("🎯 Model loader test PASSED")
