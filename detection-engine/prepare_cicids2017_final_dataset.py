import os
import glob
import pandas as pd
import numpy as np

# ================================
# PATH CONFIG
# ================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data", "cicids2017")
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "data", "final")
OUTPUT_FILE = "cicids2017_final_cleaned.csv"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ================================
# STEP 1: LOAD & MERGE RAW CSVs
# ================================
IGNORE_FILES = ["cicids2017_cleaned.csv", "cicids2017_full.csv"]

csv_files = [
    f for f in glob.glob(os.path.join(DATA_DIR, "*.csv"))
    if os.path.basename(f) not in IGNORE_FILES
]

print(f"📂 Found {len(csv_files)} RAW CICIDS CSV files")

df_list = []
for file in csv_files:
    print(f"➡ Loading: {os.path.basename(file)}")
    temp_df = pd.read_csv(file, low_memory=False)
    df_list.append(temp_df)

df = pd.concat(df_list, ignore_index=True)
print(f"✅ Merged dataset shape: {df.shape}")

# ================================
# STEP 2: CLEAN COLUMN NAMES
# ================================
df.columns = df.columns.str.strip()
print("🧹 Column names stripped of extra spaces")

# ================================
# STEP 3: DROP DUPLICATES
# ================================
before = len(df)
df.drop_duplicates(inplace=True)
print(f"🧹 Removed duplicate rows: {before - len(df)}")

# ================================
# STEP 4: DROP IDENTIFIER COLUMNS
# ================================
DROP_COLS_KEYWORDS = [
    "flow id", "timestamp",
    "src ip", "dst ip",
    "source ip", "destination ip"
]

drop_cols = [
    col for col in df.columns
    if any(key in col.lower() for key in DROP_COLS_KEYWORDS)
]

df.drop(columns=drop_cols, inplace=True, errors="ignore")
print(f"🧹 Dropped identifier columns: {len(drop_cols)}")

# ================================
# STEP 5: HANDLE NaN & INF
# ================================
df.replace([np.inf, -np.inf], np.nan, inplace=True)
before = len(df)
df.dropna(inplace=True)
print(f"🧹 Removed rows with NaN/Inf: {before - len(df)}")

# ================================
# STEP 6: AUTO-DETECT LABEL COLUMN
# ================================
possible_labels = ["label", "attack", "class"]

label_col = None
for col in df.columns:
    if col.lower() in possible_labels:
        label_col = col
        break

if label_col is None:
    raise ValueError(f"❌ No label column found! Available columns: {df.columns.tolist()}")

print(f"🏷 Detected label column: '{label_col}'")

# Rename label column to standard name
df.rename(columns={label_col: "Label"}, inplace=True)

# ================================
# STEP 7: LABEL ENCODING
# ================================
df["Label"] = df["Label"].astype(str)
df["Label"] = df["Label"].apply(
    lambda x: 0 if x.strip().upper() == "BENIGN" else 1
)

print("🏷 Label encoded: BENIGN → 0 | ATTACK → 1")

# ================================
# STEP 8: DROP CONSTANT FEATURE COLUMNS
# ================================
constant_cols = [
    col for col in df.columns
    if col != "Label" and df[col].nunique() <= 1
]

df.drop(columns=constant_cols, inplace=True)
print(f"🧹 Dropped constant feature columns: {len(constant_cols)}")

# ================================
# STEP 9: FINAL DATASET SUMMARY
# ================================
print("\n📊 Final label distribution:")
print(df["Label"].value_counts())

print("📐 Final dataset shape:", df.shape)

# ================================
# STEP 10: SAVE FINAL DATASET
# ================================
output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
df.to_csv(output_path, index=False)

print("\n✅ FINAL CLEANED DATASET SAVED AT:")
print(output_path)
