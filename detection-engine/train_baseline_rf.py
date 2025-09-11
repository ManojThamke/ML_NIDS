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

# Load Data
print("Loading Train/Test data...")
train = pd.read_csv(train_file)
test = pd.read_csv(test_file)

# Features and Label
label = "Label"
feature_cols = [c for c in train.columns if c != label]

x_train = train[feature_cols]
y_train = train[label]
x_test = test[feature_cols]
y_test = test[label]

# Scale features (random Forest dosen't require it, but safe)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(x_train)
X_test_scaled = scaler.transform(x_test)

# Train Random Forest
print("Training Random Forest Classifier...")
rf = RandomForestClassifier(n_estimators=100, n_jobs=1, random_state=42)
rf.fit(X_train_scaled, y_train)

# Predict
y_pred = rf.predict(X_test_scaled)
y_proba = rf.predict_proba(X_test_scaled)[:, 1] if hasattr(rf, "predict_proba") else None

# Metrics
acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred, zero_division=0)
rec = recall_score(y_test, y_pred, zero_division=0)
f1 = f1_score(y_test, y_pred, zero_division=0)
cm = confusion_matrix(y_test, y_pred)
report = classification_report(y_test, y_pred, zero_division=0)

print("\n=== Evaluation ===")
print(f"Accuracy : {acc:.4f}")
print(f"Precision : {prec:.4f}")
print(f"Recall : {rec:.4f}")
print(f"F1-score : {f1:.4f}")
print("Confusion matrix:")
print(cm)
print("\nClassification report:\n", report)

# Save model + scaler together as a dict
print(f"Saving model to {model_path}...")
joblib.dump({"model":rf, "scaler":scaler, "feature_cols":feature_cols}, model_path)

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

print(f"Metrics saved to {metrics_path}")
print("Training complete.")