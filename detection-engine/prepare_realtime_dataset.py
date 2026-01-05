import os
import pandas as pd

# ============================================
# PATH CONFIG
# ============================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "..", "data", "final")

INPUT_FILE = os.path.join(
    DATA_DIR,
    "cicids2017_final_scaled.csv"
)

OUTPUT_FILE = os.path.join(
    DATA_DIR,
    "cicids2017_realtime_features.csv"
)

# ============================================
# FINAL REAL-TIME FEATURES (LOCKED)
# ============================================
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

LABEL_COL = "Label"

# ============================================
# LOAD DATASET
# ============================================
print("📂 Loading CICIDS dataset...")
print(f"📄 Input file: {INPUT_FILE}")

if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(f"❌ File not found: {INPUT_FILE}")

df = pd.read_csv(INPUT_FILE)

print(f"📊 Original dataset shape: {df.shape}")

# ============================================
# VALIDATION
# ============================================
missing_features = [f for f in REALTIME_FEATURES if f not in df.columns]

if missing_features:
    raise ValueError(f"❌ Missing features in dataset: {missing_features}")

if LABEL_COL not in df.columns:
    raise ValueError("❌ 'Label' column not found in dataset")

print("✅ All real-time features + Label found")

# ============================================
# CREATE REAL-TIME DATASET
# ============================================
selected_columns = REALTIME_FEATURES + [LABEL_COL]

df_rt = df[selected_columns].copy()

print(f"📊 Shape after feature selection: {df_rt.shape}")

# Clean invalid values
df_rt.replace([float("inf"), float("-inf")], 0, inplace=True)
df_rt.dropna(inplace=True)

print(f"📊 Shape after cleaning: {df_rt.shape}")

# ============================================
# SAVE DATASET
# ============================================
df_rt.to_csv(OUTPUT_FILE, index=False)

print("\n✅ REAL-TIME DATASET CREATED SUCCESSFULLY")
print(f"📁 Saved at: {OUTPUT_FILE}")
