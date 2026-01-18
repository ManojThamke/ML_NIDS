# detection-engine/realtime_v2/model_loader_v2.py
# ==================================================
# Phase-2 Dynamic Model Loader (Metadata + Multi-Model)
# ==================================================

import os
import json
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODELS_BASE_DIR = os.path.join(
    BASE_DIR, "..", "..", "models", "phase2_offline_v2"
)

METADATA_FILE = os.path.join(MODELS_BASE_DIR, "model_metadata.json")
SCALER_FILE = os.path.join(MODELS_BASE_DIR, "scaler_v2.pkl")


# ==================================================
# MODE 1: Load BEST model (metadata driven)
# ==================================================
def load_model_and_scaler():
    print("📦 Loading BEST model using evaluation metadata...")

    if not os.path.exists(METADATA_FILE):
        raise FileNotFoundError("❌ model_metadata.json not found")

    with open(METADATA_FILE, "r") as f:
        metadata = json.load(f)

    model_file = metadata["selected_model"]

    model_path = os.path.join(MODELS_BASE_DIR, model_file)

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"❌ Model not found: {model_file}")

    model = joblib.load(model_path)
    scaler = joblib.load(SCALER_FILE)

    print("✅ Model & scaler loaded")
    print(f"🏆 Selected Model: {model_file}")
    print(f"📊 Criteria: {metadata['selection_criteria']}")
    print(f"📈 Avg F1: {metadata['metrics']['avg_f1']}")
    print(f"📈 Avg ROC–AUC: {metadata['metrics']['avg_roc_auc']}")

    return model, scaler


# ==================================================
# MODE 2: Load ALL models (for ensemble / voting)
# ==================================================
def load_all_models_and_scaler():
    print("📦 Loading ALL trained models for ensemble...")

    if not os.path.exists(METADATA_FILE):
        raise FileNotFoundError("❌ model_metadata.json not found")

    with open(METADATA_FILE, "r") as f:
        metadata = json.load(f)

    evaluated_models = metadata["evaluated_models"]

    models = {}

    for model_name in evaluated_models.keys():
        model_file = f"{model_name}_v2.pkl"
        model_path = os.path.join(MODELS_BASE_DIR, model_file)

        if not os.path.exists(model_path):
            print(f"⚠️ Skipping missing model: {model_file}")
            continue

        model = joblib.load(model_path)

        if not hasattr(model, "predict_proba"):
            print(f"⚠️ Skipping non-probabilistic model: {model_name}")
            continue

        models[model_name] = model
        print(f"✅ Loaded: {model_name}")

    scaler = joblib.load(SCALER_FILE)

    print(f"🎯 Total models loaded: {len(models)}")
    return models, scaler


# ==================================================
# SELF TEST
# ==================================================
if __name__ == "__main__":
    print("\n🧪 Testing BEST model loader")
    load_model_and_scaler()

    print("\n🧪 Testing MULTI-model loader")
    load_all_models_and_scaler()

    print("\n🎉 Model loader tests PASSED")
