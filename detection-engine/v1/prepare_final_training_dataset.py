import os
import glob
import pandas as pd
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT, "data")
CICIDS_DIR = os.path.join(DATA_DIR, "cicids2017")
OUT_FILE = os.path.join(DATA_DIR, "final_train.csv")
REPORT = os.path.join(DATA_DIR, "final_train_report.txt")

# canonical full CICIDS filename (adjust if your file name differs)
CICIDS_FULL = "cicids2017_full.csv"

# 1) collect files
data_csvs = [p for p in glob.glob(os.path.join(DATA_DIR, "*.csv")) if not p.endswith("final_train.csv")]
cicids_csvs = [p for p in glob.glob(os.path.join(CICIDS_DIR, "*.csv"))]
all_csvs = list(dict.fromkeys([os.path.abspath(p) for p in (data_csvs + cicids_csvs)]))

# ensure canonical file exists
canonical_path = os.path.abspath(os.path.join(CICIDS_DIR, CICIDS_FULL))
if not os.path.exists(canonical_path):
    raise SystemExit(f"❌ Canonical CICIDS full file not found at: {canonical_path}\nPlease ensure {CICIDS_FULL} is present in data/cicids2017/")

# order: canonical first, then others (excluding canonical)
csv_files = [canonical_path] + [p for p in all_csvs if os.path.abspath(p) != os.path.abspath(canonical_path)]

print("Files to merge (canonical first):")
for f in csv_files:
    print(" -", os.path.relpath(f, ROOT))

# helper to read CSV robustly
def read_csv_safe(path):
    try:
        return pd.read_csv(path, low_memory=False)
    except Exception:
        return pd.read_csv(path, low_memory=False, engine="python", encoding="utf-8", errors="replace")

# 2) load canonical to establish schema
print("\nLoading canonical CICIDS (full) ...")
df0 = read_csv_safe(csv_files[0])
df0.columns = [c.strip() for c in df0.columns]
canonical_cols = list(df0.columns)
dfs = [df0]

# 3) load remaining files (if any)
for p in csv_files[1:]:
    print("Loading", os.path.relpath(p, ROOT))
    df = read_csv_safe(p)
    df.columns = [c.strip() for c in df.columns]
    dfs.append(df)

# 4) align/merge: canonical columns first, then union with others (iterative union)
all_index = pd.Index(canonical_cols)
for df in dfs:
    all_index = all_index.union(df.columns)
all_columns = list(all_index)

aligned = [df.reindex(columns=all_columns) for df in dfs]
merged = pd.concat(aligned, axis=0, ignore_index=True, sort=False)
print("Merged shape before cleaning:", merged.shape)

# 5) label normalization
if "Label" not in merged.columns:
    alt = [c for c in merged.columns if c.lower() in ("label", "class", "category", "attack/benign")]
    if alt:
        merged = merged.rename(columns={alt[0]: "Label"})
        print(f"Renamed column '{alt[0]}' -> 'Label'")
    else:
        raise KeyError("❌ No 'Label' column found in merged data. Columns: " + ", ".join(merged.columns[:20]))

def to_binary(lbl):
    s = str(lbl).strip().upper()
    if s in ("BENIGN", "NORMAL", "0"):
        return 0
    if s in ("", "NAN", "NONE"):
        return pd.NA
    return 1

merged["Label"] = merged["Label"].apply(to_binary)

# 6) drop rows without label
before = len(merged)
merged = merged.dropna(subset=["Label"])
after = len(merged)
print(f"Rows dropped (no label): {before - after}")

# 7) drop non-training identifier columns if present
drop_candidates = ["Flow ID", "Source IP", "Destination IP", "Timestamp"]
to_drop = [c for c in drop_candidates if c in merged.columns]
if to_drop:
    merged = merged.drop(columns=to_drop)
    print("Dropped ID columns:", to_drop)

# 8) coerce numeric-like columns (heuristic) to maximize numeric features
for c in merged.columns:
    if c == "Label":
        continue
    col = merged[c]
    sample = col.dropna().astype(str).head(500)
    if len(sample) == 0:
        continue
    num_like = sample.str.replace(r"[.\-0-9eE+]", "", regex=True).str.strip().eq("").sum()
    if num_like / len(sample) >= 0.5:
        merged[c] = pd.to_numeric(col, errors="coerce")

# 9) optional: drop columns with >90% missing values (keeps feature quality)
thresh = int(0.1 * len(merged))  # require at least 10% non-NA
cols_before = merged.shape[1]
merged = merged.dropna(axis=1, thresh=thresh)
cols_after = merged.shape[1]
if cols_before != cols_after:
    print(f"Dropped {cols_before - cols_after} columns with >90% missing values")

# 10) replace inf and drop remaining rows with NaN (conservative)
merged = merged.replace([np.inf, -np.inf], np.nan).dropna()

# 11) finalize types
merged = merged.reset_index(drop=True)
merged["Label"] = merged["Label"].astype(int)

# 12) save outputs
os.makedirs(DATA_DIR, exist_ok=True)
merged.to_csv(OUT_FILE, index=False)
print("✅ Final dataset saved:", os.path.relpath(OUT_FILE, ROOT))
print("Final shape:", merged.shape)
print("Label distribution:\n", merged["Label"].value_counts())

with open(REPORT, "w", encoding="utf-8") as fh:
    fh.write(f"Final train created: {OUT_FILE}\n")
    fh.write(f"Rows: {merged.shape[0]}  Columns: {merged.shape[1]}\n\n")
    fh.write("Top columns:\n")
    for c in merged.columns[:80]:
        fh.write(" - " + c + "\n")
    fh.write("\nClass counts:\n")
    for k, v in merged["Label"].value_counts().items():
        fh.write(f" {k}: {v}\n")
print("Report written to:", os.path.relpath(REPORT, ROOT))
