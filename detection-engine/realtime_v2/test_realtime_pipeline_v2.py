"""
🧪 Realtime V2 Pipeline Validation Test
----------------------------------
Purpose:
✔ Feature Extractor validation
✔ Feature schema & order validation
✔ Scaler compatibility check
✔ Metadata-driven model loading
✔ Prediction sanity check

⚠ NO live traffic involved
"""

import time
import numpy as np
import pandas as pd

from feature_extractor_v2 import FlowStats, REALTIME_FEATURES
from model_loader_v2 import load_model_and_scaler


def run_pipeline_test():
    print("\n🧪 STARTING REALTIME V2 PIPELINE VALIDATION TEST\n")

    # ==================================================
    # STEP 1: Load best model + scaler
    # ==================================================
    model, scaler = load_model_and_scaler()
    print("🏆 Model & Scaler loaded successfully")

    # ==================================================
    # STEP 2: Simulate a network flow
    # ==================================================
    print("\n📡 Simulating network flow...")

    flow = FlowStats(dst_port=443)

    flow.update_forward(150)
    time.sleep(0.01)

    flow.update_forward(300)
    time.sleep(0.01)

    flow.update_backward(200)
    time.sleep(0.01)

    flow.update_forward(500)

    # ==================================================
    # STEP 3: Feature extraction
    # ==================================================
    features = flow.extract_features()

    print("\n🧬 Extracted Features:")
    for name, val in zip(REALTIME_FEATURES, features):
        print(f"  {name:30s}: {val}")

    # --- HARD SAFETY CHECKS ---
    assert len(features) == len(REALTIME_FEATURES), \
        "❌ Feature count mismatch!"

    # ==================================================
    # STEP 4: Schema-safe scaling (CRITICAL)
    # ==================================================
    X = pd.DataFrame([features], columns=REALTIME_FEATURES)

    # Enforce exact training order
    expected_order = list(scaler.feature_names_in_)
    X = X[expected_order]

    # Check schema match
    assert list(X.columns) == expected_order, \
        "❌ Feature order mismatch with training schema!"

    # Scale
    X_scaled = scaler.transform(X)

    # Check numeric stability
    assert not np.isnan(X_scaled).any(), "❌ NaN values after scaling!"
    assert not np.isinf(X_scaled).any(), "❌ Infinite values after scaling!"

    print("\n📐 Scaling successful (schema & order validated)")

    # ==================================================
    # STEP 5: Prediction sanity test
    # ==================================================
    proba = model.predict_proba(X_scaled)[0][1]

    assert 0.0 <= proba <= 1.0, \
        "❌ Invalid probability output!"

    prediction = "ATTACK" if proba >= 0.5 else "BENIGN"

    print("\n🤖 MODEL OUTPUT")
    print(f"   Probability (Attack): {proba:.4f}")
    print(f"   Final Prediction     : {prediction}")

    # ==================================================
    # FINAL RESULT
    # ==================================================
    print("\n✅ REALTIME V2 PIPELINE VALIDATION PASSED")
    print("✔ Safe to proceed with live capture integration")


if __name__ == "__main__":
    run_pipeline_test()
