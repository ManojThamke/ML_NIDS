# =====================================================
# V2 OFFLINE TRAINING + EVALUATION ENGINE
# - Uses cleaned CICIDS2018 master dataset
# - 80/20 train-test split (test frozen)
# - Multiple training sizes (40–100% of TRAIN)
# - Accuracy / Precision / Recall / F1
# - SVM intentionally excluded (trained later)
# =====================================================

import pandas as pd
import numpy as np
import json
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

# Models
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier

# Advanced (non-SVM)
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

# ---------------- CONFIG ----------------
DATA_FILE = "data/final/cicids2018_v2_clean_master.csv"
RESULTS_FILE = "results/offline_evaluation_v2.json"

MODEL_DIR = "models/phase2_offline_v2"

RANDOM_STATE = 42
TRAIN_SPLIT = 0.80

# Multiple training sizes (ONLY from TRAIN set)
TRAIN_SIZES = [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

os.makedirs("results", exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
# ---------------------------------------

print("📥 Loading dataset...")
df = pd.read_csv(DATA_FILE)

X = df.drop(columns=["Label"])
y = df["Label"].map({"BENIGN": 0, "ATTACK": 1})

print("✂️ Performing 80/20 train-test split...")
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    train_size=TRAIN_SPLIT,
    stratify=y,
    random_state=RANDOM_STATE
)

print(f"✅ Train size: {len(X_train)} | Test size: {len(X_test)}")

# ---------------- SCALING ----------------
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)   # fit ONLY on train
X_test_scaled = scaler.transform(X_test)

joblib.dump(scaler, f"{MODEL_DIR}/scaler_v2.pkl")
print("💾 Scaler saved")

# ---------------- MODELS (NO SVM) ----------------
models = {
    "LogisticRegression": LogisticRegression(max_iter=1000, n_jobs=-1),

    "DecisionTree": DecisionTreeClassifier(
        random_state=RANDOM_STATE
    ),

    "RandomForest": RandomForestClassifier(
        n_estimators=100,
        n_jobs=-1,
        random_state=RANDOM_STATE
    ),

    "KNN": KNeighborsClassifier(
        n_neighbors=5
    ),

    "NaiveBayes": GaussianNB(),

    "GradientBoosting": GradientBoostingClassifier(
        random_state=RANDOM_STATE
    ),

    "XGBoost": XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="logloss",
        n_jobs=-1,
        random_state=RANDOM_STATE
    ),

    "LightGBM": LGBMClassifier(
        n_estimators=200,
        learning_rate=0.1,
        n_jobs=-1,
        random_state=RANDOM_STATE
    ),

    "MLP": MLPClassifier(
        hidden_layer_sizes=(64, 32),
        max_iter=300,
        random_state=RANDOM_STATE
    )
}

results = {}

# ---------------- TRAIN & EVALUATE ----------------
for model_name, model in models.items():
    print(f"\n🚀 Training model: {model_name}")
    results[model_name] = {}

    for frac in TRAIN_SIZES:
        subset_size = int(len(X_train_scaled) * frac)

        X_sub = X_train_scaled[:subset_size]
        y_sub = y_train.iloc[:subset_size]

        print(f"   ▶ {int(frac*100)}% TRAIN ({subset_size} samples)")

        model.fit(X_sub, y_sub)

        # Predictions
        y_pred = model.predict(X_test_scaled)

        # ROC–AUC (probability-based)
        if hasattr(model, "predict_proba"):
            y_proba = model.predict_proba(X_test_scaled)[:, 1]
            roc_auc = roc_auc_score(y_test, y_proba)
        else:
            roc_auc = None

        results[model_name][f"{int(frac*100)}%"] = {
            "accuracy": round(accuracy_score(y_test, y_pred), 4),
            "precision": round(precision_score(y_test, y_pred), 4),
            "recall": round(recall_score(y_test, y_pred), 4),
            "f1_score": round(f1_score(y_test, y_pred), 4),
            "roc_auc": round(roc_auc, 4) if roc_auc is not None else None
        }

    # Save model trained on 100% TRAIN
    joblib.dump(model, f"{MODEL_DIR}/{model_name}_v2.pkl")


# ---------------- SAVE RESULTS ----------------
with open(RESULTS_FILE, "w") as f:
    json.dump(results, f, indent=4)

print("\n✅ OFFLINE EVALUATION COMPLETE")
print(f"📊 Results saved to: {RESULTS_FILE}")
print(f"📦 Models + scaler saved in: {MODEL_DIR}")
