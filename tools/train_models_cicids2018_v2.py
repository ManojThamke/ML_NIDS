# ==========================================================
# TRAIN MODELS – CICIDS 2018 (V2 REALTIME FEATURES)
# 70 / 30 Split | No SVM (time-efficient)
# ==========================================================

import pandas as pd
import numpy as np
import json
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier

# -------------------------------
# PATHS
# -------------------------------
DATASET = "data/final/cicids2018_v2_realtime_clean.csv"
MODEL_DIR = "models/cicids2018_v2"
SCALER_PATH = "scalers/cicids2018_realtime_scaler.pkl"
DOCS_DIR = "docs/cicids2018_v2"

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs("scalers", exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

# -------------------------------
# REALTIME FEATURES (V2)
# -------------------------------
REALTIME_FEATURES = [
    "Destination Port",
    "Flow Duration",
    "Total Fwd Packets",
    "Total Backward Packets",
    "Total Length of Fwd Packets",
    "Total Length of Bwd Packets",
    "Fwd Packet Length Min",
    "Fwd Packet Length Mean",
    "Packet Length Std",
    "Flow IAT Mean",
    "Fwd IAT Mean",
    "Down/Up Ratio"
]

print("📥 Loading CICIDS-2018 V2 dataset...")
df = pd.read_csv(DATASET, low_memory=False)

# -------------------------------
# FEATURE SELECTION
# -------------------------------
X = df[REALTIME_FEATURES].copy()
y = df["Label"].map({"BENIGN": 0, "ATTACK": 1})

# Ensure numeric
for col in REALTIME_FEATURES:
    X[col] = pd.to_numeric(X[col], errors="coerce")

X.dropna(inplace=True)
y = y.loc[X.index]

print(f"📊 Dataset shape after cleaning: {X.shape}")
print("⚖️ Label distribution:")
print(y.value_counts())

# -------------------------------
# TRAIN / TEST SPLIT (70 / 30)
# -------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.30,      # ✅ 70 / 30
    random_state=42,
    stratify=y
)

# -------------------------------
# SCALING
# -------------------------------
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

joblib.dump(scaler, SCALER_PATH)
print("💾 Scaler saved")

# -------------------------------
# MODELS (NO SVM)
# -------------------------------
models = {
    "LogisticRegression": LogisticRegression(
        max_iter=1000,
        n_jobs=-1
    ),
    "RandomForest": RandomForestClassifier(
        n_estimators=150,
        n_jobs=-1,
        random_state=42
    ),
    "GradientBoosting": GradientBoostingClassifier(
        random_state=42
    ),
    "KNN": KNeighborsClassifier(
        n_neighbors=5,
        n_jobs=-1
    ),
    "MLP": MLPClassifier(
        hidden_layer_sizes=(64, 32),
        max_iter=300,
        random_state=42
    )
}

metrics = {}

# -------------------------------
# TRAINING LOOP
# -------------------------------
for name, model in models.items():
    print(f"\n🚀 Training {name}")
    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)

    metrics[name] = {
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred), 4),
        "recall": round(recall_score(y_test, y_pred), 4),
        "f1_score": round(f1_score(y_test, y_pred), 4)
    }

    joblib.dump(model, f"{MODEL_DIR}/{name}.pkl")
    print(f"✅ {name} trained & saved")

# -------------------------------
# SAVE METRICS (FOR CHARTS)
# -------------------------------
with open(f"{DOCS_DIR}/model_metrics.json", "w") as f:
    json.dump(metrics, f, indent=4)

# -------------------------------
# BEST MODELS
# -------------------------------
sorted_models = sorted(
    metrics.items(),
    key=lambda x: x[1]["f1_score"],
    reverse=True
)

best_models_json = {
    "best_f1_model": sorted_models[0],
    "top_3_models": sorted_models[:3]
}

with open(f"{DOCS_DIR}/best_models.json", "w") as f:
    json.dump(best_models_json, f, indent=4)

# -------------------------------
# DONE
# -------------------------------
print("\n🎉 TRAINING COMPLETE")
print("📊 docs/cicids2018_v2/model_metrics.json created")
print("🏆 docs/cicids2018_v2/best_models.json created")
print("🚫 SVM skipped (will be added later with subsampling)")
