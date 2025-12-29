# detection-engine/prepare_final_dataset_phase2.py
"""
Robust Phase-2 dataset assembler (single-file, run-and-check).
- Finds CSVs under logs/ and logs/* subfolders
- Detects header and feature columns, drops metadata (timestamp, src,dst,sport,dport,proto)
- Adds label column using path heuristic (attack vs benign)
- Shuffles and splits into train/test (default 80/20)
- Writes:
    data/final_phase2_full.csv
    data/final_train_phase2.csv
    data/final_test_phase2.csv
Usage:
    python detection-engine/prepare_final_dataset_phase2.py
"""

import os, glob, argparse, pandas as pd, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_GLOB = os.path.join(ROOT, "logs", "**", "*.csv")
OUT_DIR = os.path.join(ROOT, "data")
os.makedirs(OUT_DIR, exist_ok=True)

def is_attack_path(path):
    p = path.lower()
    keywords = ("attack", "attacks", "malware", "ddos", "syn", "scan", "exploit")
    return any(k in p for k in keywords)

def collect_csv_files():
    files = sorted(glob.glob(LOGS_GLOB, recursive=True))
    # ignore files created by editor swap/temporary patterns
    files = [f for f in files if not os.path.basename(f).startswith(".")]
    return files

def read_and_label(file_path):
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"[WARN] Skipping '{file_path}' (read error): {e}")
        return None
    if df.shape[0] == 0:
        print(f"[INFO] Skipping empty file: {file_path}")
        return None

    label = 1 if is_attack_path(file_path) else 0
    # keep source info for debugging, will drop later
    df["__source_file"] = os.path.relpath(file_path, ROOT)
    df["label"] = label
    return df

def unify_columns_and_concat(dfs):
    # find union of columns
    all_cols = []
    for df in dfs:
        for c in df.columns:
            if c not in all_cols:
                all_cols.append(c)
    # align all dfs to same columns (columns missing -> NaN)
    aligned = []
    for df in dfs:
        aligned.append(df.reindex(columns=all_cols))
    full = pd.concat(aligned, ignore_index=True, sort=False)
    return full

def cleanup_dataframe(df):
    # drop obvious metadata columns if present
    drop_candidates = ["timestamp","src","dst","sport","dport","proto"]
    drop_cols = [c for c in drop_candidates if c in df.columns]
    if drop_cols:
        df = df.drop(columns=drop_cols)
    # keep label and features; ensure label column exists
    if "label" not in df.columns:
        df["label"] = 0
    # drop columns that are all-NaN
    df = df.loc[:, df.notna().any()]
    # Move label to last column
    cols = [c for c in df.columns if c != "label"] + ["label"]
    df = df[cols]
    return df

def save_splits(df, test_frac=0.2, seed=42):
    # shuffle
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    n = len(df)
    n_test = int(n * test_frac)
    test_df = df.iloc[:n_test].reset_index(drop=True)
    train_df = df.iloc[n_test:].reset_index(drop=True)
    out_full = os.path.join(OUT_DIR, "final_phase2_full.csv")
    out_train = os.path.join(OUT_DIR, "final_train_phase2.csv")
    out_test = os.path.join(OUT_DIR, "final_test_phase2.csv")
    df.to_csv(out_full, index=False)
    train_df.to_csv(out_train, index=False)
    test_df.to_csv(out_test, index=False)
    print(f"[SAVED] Full: {out_full}   Train: {out_train}   Test: {out_test}")
    print(f"[STATS] Rows total={n}  train={len(train_df)}  test={len(test_df)}")

def main(test_frac=0.2):
    files = collect_csv_files()
    if not files:
        print("[ERROR] No CSV files found under logs/. Run logger first.")
        sys.exit(1)
    print(f"[FOUND] {len(files)} CSV files under logs/ (scanning...).")
    dfs = []
    for f in files:
        df = read_and_label(f)
        if df is not None:
            dfs.append(df)
    if not dfs:
        print("[ERROR] No readable CSV data found in logs/ (after filtering).")
        sys.exit(1)

    print(f"[INFO] Aligning columns and concatenating {len(dfs)} files...")
    full = unify_columns_and_concat(dfs)
    print(f"[INFO] Combined shape: {full.shape}")

    full = cleanup_dataframe(full)
    print(f"[INFO] After cleanup shape: {full.shape}")
    # quick sanity check: require at least one numeric column (besides label)
    non_label_cols = [c for c in full.columns if c != "label"]
    if not non_label_cols:
        print("[ERROR] No feature columns found after cleanup.")
        sys.exit(1)

    save_splits(full, test_frac=test_frac)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-frac", type=float, default=0.2)
    args = parser.parse_args()
    main(test_frac=args.test_frac)
