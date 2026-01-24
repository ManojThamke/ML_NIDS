import os
import json
import time
import joblib

import lightgbm as lgb
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)

from utils_split import get_train_test_split

# ================================
# PATH CONFIG
# ================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
METRICS_DIR = os.path.join(BASE_DIR, "..", "docs", "metrics")
MODELS_DIR = os.path.join(BASE_DIR, "..", "models", "phase1")

os.makedirs(METRICS_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

# ================================
# TRAINING CONFIG
# ================================
TRAIN_SIZES = [0.4, 0.5, 0.6, 0.7]
MODEL_NAME = "LightGBM"

# ================================
# LIGHTGBM PARAMETERS (CPU SAFE)
# ================================
LGB_PARAMS = {
    "n_estimators": 200,
    "learning_rate": 0.1,
    "num_leaves": 127,
    "max_depth": -1,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "objective": "binary",
    "metric": "binary_logloss",
    "n_jobs": -1,
    "random_state": 42
}

# ================================
# TRAIN & EVALUATE
# ================================
for train_size in TRAIN_SIZES:
    train_pct = int(train_size * 100)
    print(f"\n🚀 Training {MODEL_NAME} (Train {train_pct}%)")

    start_time = time.time()

    # 🔹 SAME SPLIT UTILITY AS ALL MODELS
    X_train, X_test, y_train, y_test = get_train_test_split(train_size)

    print(f"Train samples: {len(X_train)}")
    print(f"Test samples : {len(X_test)}")
    print(f"Features     : {X_train.shape[1]}")

    model = lgb.LGBMClassifier(**LGB_PARAMS)
    model.fit(X_train, y_train)

    # ----------------------------
    # SAVE MODEL
    # ----------------------------
    model_path = os.path.join(
        MODELS_DIR,
        f"lightgbm_train{train_pct}.pkl"
    )
    joblib.dump(model, model_path)

    # ----------------------------
    # EVALUATION
    # ----------------------------
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    metrics = {
        "model": MODEL_NAME,
        "train_percentage": train_pct,
        "test_percentage": 100 - train_pct,
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
        "roc_auc": roc_auc_score(y_test, y_prob),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "training_time_seconds": round(time.time() - start_time, 2),
        "model_path": model_path
    }

    metrics_path = os.path.join(
        METRICS_DIR,
        f"lightgbm_train{train_pct}.json"
    )

    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=4)

    print(f"✅ Model saved  : {model_path}")
    print(f"✅ Metrics saved: {metrics_path}")

print("\n🎉 LIGHTGBM TRAINING COMPLETED FOR ALL SPLITS")
