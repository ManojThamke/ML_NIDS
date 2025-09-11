import pandas as pd
import glob
import os

# Path to CSV files
path = "../data/cicids2017"

# Collect all CSV files in data folder
all_files = glob.glob(os.path.join(path, "*.csv"))

print("Files to merge: ")
for f in all_files:
    print(f)

if not all_files:
    raise FileNotFoundError("No CSV files found in the specified directory.")

# Read and merge all CSVs
df_list = [pd.read_csv(f, low_memory=False) for f in all_files]
df = pd.concat(df_list, ignore_index=True)

# Save as one goant dataset
output_file = os.path.join(path, "cicids2017_full.csv")
df.to_csv(output_file, index=False)

print(f" Full dataset saved as: {output_file}")
print("Total rows: ", len(df))