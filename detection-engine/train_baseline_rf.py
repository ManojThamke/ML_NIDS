import os
import joblib
import json
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)
from sklearn.preprocessing import StandardScaler

# paths
train_file = "../data/baseline_train.csv"
test_file = "../data/baseline_test.csv"
model_dir = "models"
model_path = os.path.join(model_dir, "realtime_rf.pkl")
metrics_path = os.path.join(model_dir, "realtime_rf_metrics.json")

# Create models dir
os.makedirs(model_dir, exist_ok=True)

print("📥 Loading Train/Test data...")
train = pd.read_csv(train_file)
test  = pd.read_csv(test_file)

label = "Label"
feature_cols = [c for c in train.columns if c != label]

X_train = train[feature_cols]
y_train = train[label]
X_test  = test[feature_cols]
y_test  = test[label]

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

# Train Random Forest
print("🌲 Training Random Forest...")
rf = RandomForestClassifier(
    n_estimators=300,
    max_depth=20,
    min_samples_split=2,
    min_samples_leaf=1,
    random_state=42,
    n_jobs=4
)
rf.fit(X_train_scaled, y_train)

# Predictions
y_pred = rf.predict(X_test_scaled)
y_proba = rf.predict_proba(X_test_scaled)[:, 1]

# Metrics
acc  = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred, zero_division=0)
rec  = recall_score(y_test, y_pred, zero_division=0)
f1   = f1_score(y_test, y_pred, zero_division=0)
cm   = confusion_matrix(y_test, y_pred)

print("\n📊 === Evaluation ===")
print(f"Accuracy : {acc:.4f}")
print(f"Precision: {prec:.4f}")
print(f"Recall   : {rec:.4f}")
print(f"F1-score : {f1:.4f}")
print("\nConfusion matrix:\n", cm)
print("\nClassification Report:\n", classification_report(y_test, y_pred, zero_division=0))

# Save model bundle
bundle = {
    "model": rf,
    "scaler": scaler,
    "feature_cols": feature_cols,
    "dataset": "baseline_train"
}

print(f"\n💾 Saving model to {model_path} ...")
joblib.dump(bundle, model_path)

# Save metrics
metrics = {
    "accuracy": acc,
    "precision": prec,
    "recall": rec,
    "f1-score": f1,
    "confusion_matrix": cm.tolist()
}

with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)

print(f"📁 Metrics saved to {metrics_path}")
print("✅ Training complete.")
