import os
import json
import joblib
from sklearn.linear_model import LogisticRegression
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

# ================================
# TRAIN & EVALUATE
# ================================
for train_size in TRAIN_SIZES:
    train_pct = int(train_size * 100)
    print(f"\n🚀 Training Logistic Regression (Train {train_pct}%)")

    X_train, X_test, y_train, y_test = get_train_test_split(train_size)

    model = LogisticRegression(
        max_iter=1000,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    # ----------------------------
    # SAVE MODEL
    # ----------------------------
    model_path = os.path.join(
        MODELS_DIR,
        f"logreg_train{train_pct}.pkl"
    )
    joblib.dump(model, model_path)

    # ----------------------------
    # EVALUATION
    # ----------------------------
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    metrics = {
        "model": "LogisticRegression",
        "train_percentage": train_pct,
        "test_percentage": 100 - train_pct,
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
        "roc_auc": roc_auc_score(y_test, y_prob),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "model_path": model_path
    }

    metrics_path = os.path.join(
        METRICS_DIR,
        f"logreg_train{train_pct}.json"
    )

    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=4)

    print(f"✅ Model saved: {model_path}")
    print(f"✅ Metrics saved: {metrics_path}")
