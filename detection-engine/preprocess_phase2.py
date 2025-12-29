# detection-engine/preprocess_phase2.py
"""
Preprocess Phase-2 training data and save preprocessing bundle.

Saves:
  models/preprocess_phase2_bundle.joblib
Contents:
  {"pipeline": fitted_pipeline, "feature_order": [col1, col2, ...]}

Usage:
  python detection-engine/preprocess_phase2.py
  python detection-engine/preprocess_phase2.py --data data/final_train_phase2.csv --out models/preprocess_phase2_bundle.joblib
"""

import os
import argparse
import joblib
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DATA = os.path.join(ROOT, "data", "final_train_phase2.csv")
DEFAULT_OUT = os.path.join(ROOT, "models", "preprocess_phase2_bundle.joblib")

def build_preprocess(data_path: str, out_path: str):
    print("[*] Loading training CSV:", data_path)
    if not os.path.isfile(data_path):
        raise FileNotFoundError(f"Training CSV not found: {data_path}")

    df = pd.read_csv(data_path)
    print("[*] Raw shape:", df.shape)

    # If label is present, drop it for preprocessing fit
    if "label" in df.columns:
        X = df.drop(columns=["label"])
    else:
        X = df.copy()

    # Drop any completely-empty columns
    X = X.loc[:, X.notna().any()]

    # If there are non-numeric columns, attempt to coerce them to numeric
    print("[*] Converting columns to numeric (coerce invalid -> NaN)...")
    X_numeric = X.apply(pd.to_numeric, errors="coerce")

    # Check we have at least one numeric column
    if X_numeric.shape[1] == 0:
        raise ValueError("No numeric feature columns found after coercion.")

    # Fill NaNs temporarily for info (pipeline will handle imputation)
    n_missing = X_numeric.isna().sum().sum()
    print(f"[*] Feature matrix shape: {X_numeric.shape}  Total missing values (will be imputed): {n_missing}")

    # Build pipeline: imputer (constant 0) + standard scaler
    pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value=0.0)),
        ("scaler", StandardScaler())
    ])

    print("[*] Fitting preprocessing pipeline...")
    pipe.fit(X_numeric)

    feature_order = list(X_numeric.columns)
    bundle = {"pipeline": pipe, "feature_order": feature_order}

    # Ensure output directory exists
    out_dir = os.path.dirname(out_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    print("[*] Saving preprocess bundle to:", out_path)
    joblib.dump(bundle, out_path)
    print("[*] Saved. Feature order (first 20):", feature_order[:20])
    print("[*] Bundle contains pipeline and feature_order.")

def main():
    parser = argparse.ArgumentParser(description="Build preprocess bundle for Phase-2")
    parser.add_argument("--data", default=DEFAULT_DATA, help="Path to training CSV (default: data/final_train_phase2.csv)")
    parser.add_argument("--out", default=DEFAULT_OUT, help="Output joblib path (default: models/preprocess_phase2_bundle.joblib)")
    args = parser.parse_args()

    try:
        build_preprocess(args.data, args.out)
    except Exception as e:
        print("[ERROR] Preprocess failed:", e)
        raise

if __name__ == "__main__":
    main()
