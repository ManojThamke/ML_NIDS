# =====================================================
# Phase-2 Realtime Multi-Model Inference Engine
# STEP-3: ML ONLY (No voting, no hybrid, no logging)
# =====================================================

from model_loader_v2 import load_all_models_and_scaler

# -----------------------------------------------------
# Load all models ONCE (performance-safe)
# -----------------------------------------------------
MODELS, SCALER = load_all_models_and_scaler()

# -----------------------------------------------------
# MODEL NAME NORMALIZATION (CRITICAL FIX)
# -----------------------------------------------------
MODEL_ALIAS_MAP = {
    "rf": "RandomForest",
    "randomforest": "RandomForest",

    "xgb": "XGBoost",
    "xgboost": "XGBoost",

    "lgb": "LightGBM",
    "lightgbm": "LightGBM",

    "knn": "KNN",
    "knearestneighbors": "KNN",

    "nb": "NaiveBayes",
    "naive_bayes": "NaiveBayes",

    "lr": "LogisticRegression",
    "logisticregression": "LogisticRegression",

    "gb": "GradientBoosting",
    "gradientboosting": "GradientBoosting",

    "mlp": "MLP"
}


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

    # -------------------------------------------------
    # Decide which models to use (NORMALIZED)
    # -------------------------------------------------
    if selected_models:
        models_to_use = []
        for m in selected_models:
            normalized = MODEL_ALIAS_MAP.get(m.lower(), m)
            if normalized in MODELS:
                models_to_use.append(normalized)
            else:
                print(f"[WARN] Model not available: {m}")
    else:
        models_to_use = MODELS.keys()

    # -------------------------------------------------
    # Scale features ONCE
    # -------------------------------------------------
    X_scaled = SCALER.transform(features_df)

    # -------------------------------------------------
    # Run inference
    # -------------------------------------------------
    for model_name in models_to_use:
        model = MODELS.get(model_name)
        if model is None:
            continue

        prob_attack = model.predict_proba(X_scaled)[0][1]
        prob_attack = round(float(prob_attack), 6)

        label = "ATTACK" if prob_attack >= 0.5 else "BENIGN"

        results[model_name] = {
            "probability": prob_attack,
            "label": label
        }

    return results
