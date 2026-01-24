import pandas as pd
import os
# input and output paths
input_file = "../data/cicids2017/cicids2017_full.csv"
output_file = "../data/cicids2017/cicids2017_cleaned.csv"

print(" Loading dataset...")
df = pd.read_csv(input_file, low_memory=False)
print("Loaded. Shape:", df.shape)

# Drop columns not useful for baseline model
drop_cols = ['Flow ID', 'Source IP', 'Destination IP', 'Timestamp']
drop_existing = [c for c in drop_cols if c in df.columns]
df.drop(columns=drop_existing, inplace=True, errors='ignore')
print("Dropped columns:", drop_existing)

# Detect label column automatically
label_col = None
for c in df.columns:
    if "label" in c.lower():
        label_col = c
        break

if label_col is None:
    raise KeyError("No label column found in dataset.")

print("Label column detected:", label_col)

# convert lables: BENIGN=0, all ATTACK=1
df[label_col] = df[label_col].apply(lambda x: 0 if str(x).strip().upper() == "BENIGN" else 1)

# Rename column to 'Label' for consistency
df.rename(columns={label_col: 'Label'}, inplace=True)
print("labels normalized and column renamed to 'Label'.")

# Remove invalid rows(NaN, Inf values)
before_rows = len(df)
df = df.replace([float('inf'), -float('inf')], pd.NA).dropna()
after_rows = len(df)
print("Removed: {before_rows - after_rows} bad rows")

# Save cleaned dataset
df.to_csv(output_file, index=False)
print("Saved cleaned dataset to:", output_file)
print("Final shape:", df.shape )