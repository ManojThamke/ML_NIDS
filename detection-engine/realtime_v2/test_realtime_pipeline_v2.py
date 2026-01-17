"""
🧪 Realtime V2 Pipeline Test Script
----------------------------------
Tests:
✔ Feature Extractor
✔ Scaler (schema-safe, order enforced)
✔ Metadata-driven Model Loader
✔ Prediction + Probability
NO live traffic involved
"""

import time
import numpy as np
import pandas as pd

from feature_extractor_v2 import FlowStats, REALTIME_FEATURES
from model_loader_v2 import load_model_and_scaler


def run_pipeline_test():
    print("\n🧪 STARTING REALTIME V2 PIPELINE TEST\n")

    # --------------------------------------------------
    # Step 1: Load best model + scaler (metadata-driven)
    # --------------------------------------------------
    model, scaler = load_model_and_scaler()

    print("🏆 Loaded Model & Scaler successfully")

    # --------------------------------------------------
    # Step 2: Simulate a network flow
    # --------------------------------------------------
    print("\n📡 Simulating network flow...")

    flow = FlowStats(dst_port=443)

    flow.update_forward(150)
    time.sleep(0.01)

    flow.update_forward(300)
    time.sleep(0.01)

    flow.update_backward(200)
    time.sleep(0.01)

    flow.update_forward(500)

    # --------------------------------------------------
    # Step 3: Extract features
    # --------------------------------------------------
    features = flow.extract_features()

    print("\n🧬 Extracted Features:")
    for name, val in zip(REALTIME_FEATURES, features):
        print(f"  {name:30s}: {val}")

    # Safety check
    assert len(features) == len(REALTIME_FEATURES), \
        "❌ Feature count mismatch!"

    # --------------------------------------------------
    # Step 4: Schema-safe scaling (CRITICAL FIX)
    # --------------------------------------------------
    # Create DataFrame using realtime feature names
    X = pd.DataFrame([features], columns=REALTIME_FEATURES)

    # 🔒 Enforce EXACT feature order used during training
    expected_order = list(scaler.feature_names_in_)
    X = X[expected_order]

    # Scale
    X_scaled = scaler.transform(X)

    print("\n📐 Features scaled successfully (order enforced)")

    # --------------------------------------------------
    # Step 5: Prediction
    # --------------------------------------------------
    proba = model.predict_proba(X_scaled)[0][1]
    prediction = "ATTACK" if proba >= 0.5 else "BENIGN"

    print("\n🤖 MODEL OUTPUT")
    print(f"   Probability (Attack): {proba:.4f}")
    print(f"   Final Prediction     : {prediction}")

    print("\n✅ REALTIME V2 PIPELINE TEST PASSED")


# --------------------------------------------------
# Run test
# --------------------------------------------------
if __name__ == "__main__":
    run_pipeline_test()
