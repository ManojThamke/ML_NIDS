import os
import json
import time
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier

# ================================
# PATH CONFIG
# ================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(
    BASE_DIR, "..", "data", "final", "cicids2017_realtime_features.csv"
)

MODELS_DIR = os.path.join(BASE_DIR, "..", "models", "realtime")
METRICS_DIR = os.path.join(BASE_DIR, "..", "docs", "metrics")

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(METRICS_DIR, exist_ok=True)

# ================================
# LOAD DATASET
# ================================
print("📂 Loading realtime dataset...")
df = pd.read_csv(DATA_FILE)

X = df.drop(columns=["Label"])
y = df["Label"]

print(f"Dataset shape : {df.shape}")
print(f"Features used : {list(X.columns)}")

# ================================
# GLOBAL 70 / 30 SPLIT (FULL DATA)
# ================================
X_train_full, X_test_full, y_train_full, y_test_full = train_test_split(
    X,
    y,
    test_size=0.30,
    stratify=y,
    random_state=42
)

print(f"Full Train samples: {X_train_full.shape[0]}")
print(f"Full Test samples : {X_test_full.shape[0]}")

# ================================
# SVM SUBSET CONFIG
# ================================
SVM_SUBSET_SIZE = 300_000  # 3 lakh (SAFE & PRACTICAL)

print(f"\n🔽 Creating SVM stratified subset: {SVM_SUBSET_SIZE}")

X_svm, _, y_svm, _ = train_test_split(
    X,
    y,
    train_size=SVM_SUBSET_SIZE,
    stratify=y,
    random_state=42
)

X_train_svm, X_test_svm, y_train_svm, y_test_svm = train_test_split(
    X_svm,
    y_svm,
    test_size=0.30,
    stratify=y_svm,
    random_state=42
)

print(f"SVM Train samples: {X_train_svm.shape[0]}")
print(f"SVM Test samples : {X_test_svm.shape[0]}")

# ================================
# MODEL DEFINITIONS
# ================================
models = {
    "SupportVectorMachine": {
        "model": SVC(
            kernel="rbf",
            probability=True,
            class_weight="balanced",
            cache_size=4096
        ),
        "X_train": X_train_svm,
        "X_test": X_test_svm,
        "y_train": y_train_svm,
        "y_test": y_test_svm,
        "subset": True
    },

    "KNN": {
        "model": KNeighborsClassifier(n_neighbors=5),
        "X_train": X_train_full,
        "X_test": X_test_full,
        "y_train": y_train_full,
        "y_test": y_test_full,
        "subset": False
    },

    "DecisionTree": {
        "model": DecisionTreeClassifier(random_state=42),
        "X_train": X_train_full,
        "X_test": X_test_full,
        "y_train": y_train_full,
        "y_test": y_test_full,
        "subset": False
    },

    "RandomForest": {
        "model": RandomForestClassifier(
            n_estimators=100,
            n_jobs=-1,
            random_state=42
        ),
        "X_train": X_train_full,
        "X_test": X_test_full,
        "y_train": y_train_full,
        "y_test": y_test_full,
        "subset": False
    },

    "GradientBoosting": {
        "model": GradientBoostingClassifier(random_state=42),
        "X_train": X_train_full,
        "X_test": X_test_full,
        "y_train": y_train_full,
        "y_test": y_test_full,
        "subset": False
    },

    "MultiLayerPerceptron": {
        "model": MLPClassifier(
            hidden_layer_sizes=(64, 32),
            max_iter=50,
            early_stopping=True,
            random_state=42
        ),
        "X_train": X_train_full,
        "X_test": X_test_full,
        "y_train": y_train_full,
        "y_test": y_test_full,
        "subset": False
    }
}

# ================================
# TRAIN & SAVE
# ================================
for name, cfg in models.items():
    print(f"\n🚀 Training {name}")
    if cfg["subset"]:
        print("⚠ Using 3-lakh stratified subset")

    start = time.time()

    model = cfg["model"]
    model.fit(cfg["X_train"], cfg["y_train"])

    y_pred = model.predict(cfg["X_test"])
    y_prob = model.predict_proba(cfg["X_test"])[:, 1]

    metrics = {
        "model": name,
        "training_split": "70/30",
        "subset_used": cfg["subset"],
        "accuracy": accuracy_score(cfg["y_test"], y_pred),
        "precision": precision_score(cfg["y_test"], y_pred),
        "recall": recall_score(cfg["y_test"], y_pred),
        "f1": f1_score(cfg["y_test"], y_pred),
        "roc_auc": roc_auc_score(cfg["y_test"], y_prob),
        "train_samples": len(cfg["X_train"]),
        "test_samples": len(cfg["X_test"]),
        "training_time_sec": round(time.time() - start, 2)
    }

    model_path = os.path.join(MODELS_DIR, f"{name}_realtime.pkl")
    joblib.dump(model, model_path)

    metrics_path = os.path.join(METRICS_DIR, f"{name}_realtime.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=4)

    print(f"✅ Model saved   : {model_path}")
    print(f"✅ Metrics saved : {metrics_path}")

print("\n🎉 ALL REALTIME MODELS TRAINED SUCCESSFULLY")
