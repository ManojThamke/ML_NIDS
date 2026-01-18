# =====================================================
# Phase-2 Realtime Multi-Model Inference Engine
# STEP-3: ML ONLY (No voting, no hybrid, no logging)
# =====================================================

from model_loader_v2 import load_all_models_and_scaler


# -----------------------------------------------------
# Load all models ONCE (performance-safe)
# -----------------------------------------------------
MODELS, SCALER = load_all_models_and_scaler()


def detect_with_all_models(features_df, selected_models=None):
    """
    Run inference using multiple ML models on realtime features

    Args:
        features_df (pd.DataFrame): Single-row feature dataframe
        selected_models (list | None): Models to run (default = all)

    Returns:
        dict: Per-model probability & label
    """

    results = {}

    # Decide which models to use
    models_to_use = (
        selected_models if selected_models else MODELS.keys()
    )

    # Scale features ONCE
    X_scaled = SCALER.transform(features_df)

    for model_name in models_to_use:
        if model_name not in MODELS:
            print(f"⚠️ Model not found: {model_name}")
            continue

        model = MODELS[model_name]

        # Predict probability
        prob_attack = model.predict_proba(X_scaled)[0][1]

        # Simple label (TEMPORARY, for visibility)
        label = "ATTACK" if prob_attack >= 0.5 else "BENIGN"

        results[model_name] = {
            "probability": round(float(prob_attack), 6),
            "label": label
        }

    return results
