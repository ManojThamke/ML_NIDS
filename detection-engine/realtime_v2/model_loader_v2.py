# detection-engine/realtime_v2/model_loader_v2.py

import os
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODELS_DIR = os.path.join(
    BASE_DIR, "..", "..", "models", "realtime"
)

MODEL_FILES = {
    "LogisticRegression": "LogisticRegression_realtime.pkl",
    "NaiveBayes": "NaiveBayes_realtime.pkl",
    "SupportVectorMachine": "SupportVectorMachine_realtime.pkl",
    "KNN": "KNN_realtime.pkl",
    "DecisionTree": "DecisionTree_realtime.pkl",
    "RandomForest": "RandomForest_realtime.pkl",
    "GradientBoosting": "GradientBoosting_realtime.pkl",
    "MultiLayerPerceptron": "MultiLayerPerceptron_realtime.pkl",
}

def load_realtime_models():
    models = {}

    print("📦 Loading realtime models (V2)...")

    for name, filename in MODEL_FILES.items():
        path = os.path.join(MODELS_DIR, filename)

        if not os.path.exists(path):
            raise FileNotFoundError(f"❌ Model not found: {path}")

        model = joblib.load(path)

        # Safety check for thresholding
        if not hasattr(model, "predict_proba"):
            raise AttributeError(
                f"❌ {name} does not support predict_proba()"
            )

        models[name] = model
        print(f"✅ Loaded: {name}")

    print("🎉 All realtime models loaded successfully")
    return models
