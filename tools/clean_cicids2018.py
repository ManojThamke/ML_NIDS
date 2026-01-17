# tools/clean_cicids2018.py
# =====================================
# CICIDS-2018 CLEANING (V2 REALTIME)
# =====================================

import pandas as pd
import numpy as np
import glob
import os

DATA_DIR = "data/cicids2018"
OUTPUT_FILE = "data/final/cicids2018_v2_realtime_clean.csv"

# CICIDS → Realtime feature mapping
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

CHUNK_SIZE = 1_000_000  # safe for 24GB RAM

os.makedirs("data/final", exist_ok=True)

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
        # Rename columns to realtime standard
        chunk.rename(columns=COLUMN_MAP, inplace=True)

        # Replace inf and NaN
        chunk.replace([np.inf, -np.inf], np.nan, inplace=True)
        chunk.dropna(inplace=True)

        # Convert all features to numeric
        for col in chunk.columns:
            if col != "Label":
                chunk[col] = pd.to_numeric(chunk[col], errors="coerce")

        chunk.dropna(inplace=True)

        # Normalize labels
        chunk["Label"] = chunk["Label"].astype(str).str.upper().apply(
            lambda x: "BENIGN" if x == "BENIGN" else "ATTACK"
        )

        # Append cleaned data
        chunk.to_csv(
            OUTPUT_FILE,
            mode="w" if first_write else "a",
            header=first_write,
            index=False
        )

        total_rows += len(chunk)
        first_write = False

print("\n✅ CLEANING COMPLETE")
print(f"📊 Total cleaned rows: {total_rows}")
print(f"📁 Saved file: {OUTPUT_FILE}")
