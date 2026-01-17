# tools/clean_cicids2018.py
# ======================================================
# CICIDS-2018 CLEANING (V2 – PRE-SPLIT MASTER DATASET)
# This script performs ONLY data cleaning.
# Train-test split and scaling are done later.
# ======================================================

import pandas as pd
import numpy as np
import glob
import os

# ---------------- CONFIG ----------------
DATA_DIR = "data/cicids2018"
OUTPUT_FILE = "data/final/cicids2018_v2_clean_master.csv"
CHUNK_SIZE = 1_000_000  # memory-safe

os.makedirs("data/final", exist_ok=True)

# Selected realtime-compatible features + label
COLUMN_MAP = {
    "Dst Port": "Destination Port",
    "Flow Duration": "Flow Duration",
    "Tot Fwd Pkts": "Total Fwd Packets",
    "Tot Bwd Pkts": "Total Backward Packets",
    "TotLen Fwd Pkts": "Total Length of Fwd Packets",
    "TotLen Bwd Pkts": "Total Length of Bwd Packets",
    "Fwd Pkt Len Min": "Fwd Packet Length Min",
    "Fwd Pkt Len Mean": "Fwd Packet Length Mean",
    "Pkt Len Std": "Packet Length Std",
    "Flow IAT Mean": "Flow IAT Mean",
    "Fwd IAT Mean": "Fwd IAT Mean",
    "Down/Up Ratio": "Down/Up Ratio",
    "Label": "Label"
}

FEATURE_COLUMNS = [col for col in COLUMN_MAP.values() if col != "Label"]
LABEL_COLUMN = "Label"
# ----------------------------------------

csv_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
print(f"📂 Found {len(csv_files)} CICIDS-2018 CSV files")

first_write = True
total_rows = 0

for file in csv_files:
    print(f"\n➡️ Processing: {os.path.basename(file)}")

    for chunk in pd.read_csv(
        file,
        usecols=COLUMN_MAP.keys(),
        chunksize=CHUNK_SIZE,
        low_memory=False
    ):
        # Rename columns to standard names
        chunk.rename(columns=COLUMN_MAP, inplace=True)

        # Replace infinite values
        chunk.replace([np.inf, -np.inf], np.nan, inplace=True)

        # Convert feature columns to numeric
        for col in FEATURE_COLUMNS:
            chunk[col] = pd.to_numeric(chunk[col], errors="coerce")

        # Drop rows with missing values (features or label)
        chunk.dropna(inplace=True)

        # Normalize labels (binary classification)
        chunk[LABEL_COLUMN] = (
            chunk[LABEL_COLUMN]
            .astype(str)
            .str.upper()
            .apply(lambda x: "BENIGN" if x == "BENIGN" else "ATTACK")
        )

        # Save cleaned chunk
        chunk.to_csv(
            OUTPUT_FILE,
            mode="w" if first_write else "a",
            header=first_write,
            index=False
        )

        total_rows += len(chunk)
        first_write = False

print("\n✅ CLEANING COMPLETE (PRE-SPLIT)")
print(f"📊 Total cleaned rows: {total_rows}")
print(f"📁 Master dataset saved at: {OUTPUT_FILE}")
