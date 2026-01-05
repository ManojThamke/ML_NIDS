import os
import json
import joblib
import numpy as np
import pandas as pd

from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)
from sklearn.model_selection import train_test_split

# ================================
# CONFIG
# ================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_PATH = os.path.join(
    BASE_DIR, "..", "data", "final", "cicids2017_final_scaled.csv"
)

METRICS_DIR = os.path.join(BASE_DIR, "..", "docs", "metrics")
MODELS_DIR = os.path.join(BASE_DIR, "..", "models", "phase1")

os.makedirs(METRICS_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

LABEL_COL = "Label"
RANDOM_STATE = 42

# KNN settings
K_VALUES = range(1, 11)
TRAIN_SIZES = [0.4, 0.5, 0.6, 0.7]
SUBSET_SIZE = 200_000
MODEL_NAME = "KNN"

# ================================
# LOAD & SUBSET DATASET
# ================================
print("📥 Loading frozen scaled dataset...")
df = pd.read_csv(DATASET_PATH)

print(f"✅ Full dataset shape: {df.shape}")

# Stratified subset
df_subset, _ = train_test_split(
    df,
    train_size=SUBSET_SIZE,
    stratify=df[LABEL_COL],
    random_state=RANDOM_STATE
)

print(f"📉 Using subset for KNN: {df_subset.shape}")

X = df_subset.drop(columns=[LABEL_COL])
y = df_subset[LABEL_COL]

# ================================
# TRAIN LOOP
# ================================
for k in K_VALUES:
    for train_size in TRAIN_SIZES:
        train_pct = int(train_size * 100)

        print(f"\n🚀 Training {MODEL_NAME} | k={k} | Train {train_pct}%")

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            train_size=train_size,
            stratify=y,
            random_state=RANDOM_STATE
        )

        model = KNeighborsClassifier(
            n_neighbors=k,
            n_jobs=-1
        )

        model.fit(X_train, y_train)

        # ----------------------------
        # SAVE MODEL
        # ----------------------------
        model_path = os.path.join(
            MODELS_DIR,
            f"knn_k{k}_train{train_pct}.pkl"
        )
        joblib.dump(model, model_path)

        # ----------------------------
        # EVALUATION
        # ----------------------------
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        metrics = {
            "model": MODEL_NAME,
            "k": k,
            "train_percentage": train_pct,
            "test_percentage": 100 - train_pct,
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred),
            "f1": f1_score(y_test, y_pred),
            "roc_auc": roc_auc_score(y_test, y_prob),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "subset_size": SUBSET_SIZE,
            "model_path": model_path
        }

        metrics_path = os.path.join(
            METRICS_DIR,
            f"knn_k{k}_train{train_pct}.json"
        )

        with open(metrics_path, "w") as f:
            json.dump(metrics, f, indent=4)

        print(f"✅ Saved model & metrics for k={k}, train={train_pct}%")
