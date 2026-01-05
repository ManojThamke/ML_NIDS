import os
import pandas as pd
from sklearn.preprocessing import StandardScaler
import joblib

# ================================
# PATH CONFIG
# ================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_FILE = os.path.join(
    BASE_DIR, "..", "data", "final", "cicids2017_final_cleaned.csv"
)

OUTPUT_DATA_DIR = os.path.join(BASE_DIR, "..", "data", "final")
MODEL_DIR = os.path.join(BASE_DIR, "..", "models")
DOCS_DIR = os.path.join(BASE_DIR, "..", "docs")

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

# ================================
# LOAD DATASET
# ================================
print("📥 Loading final cleaned dataset...")
df = pd.read_csv(INPUT_FILE)

print(f"✅ Dataset shape: {df.shape}")

# ================================
# SEPARATE FEATURES & LABEL
# ================================
LABEL_COL = "Label"

X = df.drop(columns=[LABEL_COL])
y = df[LABEL_COL]

print(f"🧮 Features count: {X.shape[1]}")
print(f"🏷 Label distribution:\n{y.value_counts()}")

# ================================
# SAVE FEATURE LIST (FREEZE)
# ================================
feature_file = os.path.join(DOCS_DIR, "final_features.txt")
with open(feature_file, "w") as f:
    for col in X.columns:
        f.write(col + "\n")

print(f"📄 Feature list saved: {feature_file}")

# ================================
# FEATURE SCALING
# ================================
print("⚙ Applying StandardScaler...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ================================
# SAVE SCALER
# ================================
scaler_path = os.path.join(MODEL_DIR, "final_scaler.joblib")
joblib.dump(scaler, scaler_path)

print(f"💾 Scaler saved: {scaler_path}")

# ================================
# SAVE SCALED DATASET
# ================================
scaled_df = pd.DataFrame(X_scaled, columns=X.columns)
scaled_df[LABEL_COL] = y.values

output_scaled_file = os.path.join(
    OUTPUT_DATA_DIR, "cicids2017_final_scaled.csv"
)

scaled_df.to_csv(output_scaled_file, index=False)

print(f"✅ Final scaled dataset saved at:")
print(output_scaled_file)

print("\n🎯 PREPROCESSING COMPLETE — DATASET FROZEN")
