import os
import joblib
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_IN = os.path.join(ROOT, "data", "final_train.csv")
DATA_OUT = os.path.join(ROOT, "data", "preprocessed_train.csv")
BUNDLE_OUT = os.path.join(os.path.dirname(__file__), "models", "preprocess_bundle.joblib")
FEATURES_MD = os.path.join(ROOT, "docs", "features_used.md")

# Preferred features (try these first)
preferred = [
    "Destination Port",
    "Flow Duration",
    "Fwd Packet Length Min",
    "Packet Length Std",
    "Fwd Packet Length Mean",
    "Bwd Packet Length Mean",
    "Total Fwd Packets",
    "Total Length of Fwd Packets"
]

# Desired number of features (min,max)
MIN_FEAT = 6
MAX_FEAT = 8

os.makedirs(os.path.dirname(BUNDLE_OUT), exist_ok=True)
os.makedirs(os.path.dirname(FEATURES_MD), exist_ok=True)

print("Loading final dataset:", DATA_IN)
df = pd.read_csv(DATA_IN)

# Ensure Label exists
if "Label" not in df.columns:
    raise SystemExit("Label column not found in final_train.csv")

# Identify numeric columns
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
# Remove Label from numeric candidates
numeric_cols = [c for c in numeric_cols if c != "Label"]

# Build selected feature list by preferrence, then fallback to numeric_cols
selected = []
for f in preferred:
    if f in df.columns and f not in selected:
        selected.append(f)
    if len(selected) >= MAX_FEAT:
        break

# Fill up with numeric columns if needed (preserve canonical order)
if len(selected) < MIN_FEAT:
    for c in numeric_cols:
        if c not in selected:
            selected.append(c)
        if len(selected) >= MIN_FEAT:
            break

# Ensure we don't exceed MAX_FEAT
selected = selected[:MAX_FEAT]

print("Selected features:", selected)

# Subset DataFrame
cols_to_keep = selected + ["Label"]
data = df[cols_to_keep].copy()

# Impute numeric NaNs with median
imputer = SimpleImputer(strategy="median")
X = data[selected].values
X_imputed = imputer.fit_transform(X)

# Scale
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_imputed)

# Build output DataFrame
df_out = pd.DataFrame(X_scaled, columns=selected)
df_out["Label"] = data["Label"].values

# Save preprocessed CSV
df_out.to_csv(DATA_OUT, index=False)
print("Saved preprocessed data to:", DATA_OUT)
print("Shape:", df_out.shape)

# Save bundle (scaler + imputer + feature list)
bundle = {"features": selected, "imputer": imputer, "scaler": scaler}
joblib.dump(bundle, BUNDLE_OUT)
print("Saved preprocessing bundle to:", BUNDLE_OUT)

# Write docs/features_used.md
with open(FEATURES_MD, "w", encoding="utf-8") as fh:
    fh.write("# Features used — Day 16\n\n")
    fh.write("Selected features (for initial experiments):\n\n")
    for i, f in enumerate(selected, 1):
        fh.write(f"{i}. {f}\n")
    fh.write("\nPreprocessing steps applied:\n\n")
    fh.write("- Missing values imputed using median (SimpleImputer)\n")
    fh.write("- Features standardized with StandardScaler (zero mean, unit variance)\n")
    fh.write("\nNotes:\n- If a preferred feature was not present in final_train.csv, it was replaced with the next available numeric column.\n")

print("Wrote feature list to:", FEATURES_MD)
