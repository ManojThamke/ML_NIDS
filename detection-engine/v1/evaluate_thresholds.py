import csv
import os
import shutil
import pandas as pd
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix

# Paths
HERE = os.path.dirname(__file__)
LOG = os.path.abspath(os.path.join(HERE, "..", "logs", "realtime_predictions.csv"))
OUT_MD = os.path.abspath(os.path.join(HERE, "..", "docs", "threshold_tuning_notes.md"))
OUT_CSV = OUT_MD.replace(".md", ".csv")

if not os.path.exists(LOG):
    raise SystemExit(f"Log not found: {LOG}")

# Backup the original log first
backup_path = LOG + ".bak"
shutil.copy2(LOG, backup_path)
print(f"Backup created: {backup_path}")

# Read & repair CSV rows so every row has same number of fields as the header
clean_rows = []
with open(LOG, newline='', encoding='utf-8') as fh:
    reader = csv.reader(fh)
    try:
        header = next(reader)
    except StopIteration:
        raise SystemExit("CSV is empty.")
    expected = len(header)
    clean_rows.append(header)

    line_no = 1
    for row in reader:
        line_no += 1
        if len(row) == expected:
            clean_rows.append(row)
        elif len(row) > expected:
            # Too many fields: join the extras into the last column (conservative repair)
            fixed = row[: expected - 1] + [",".join(row[expected - 1:])]
            clean_rows.append(fixed)
        else:
            # Too few fields: pad with empty strings
            fixed = row + [""] * (expected - len(row))
            clean_rows.append(fixed)

# Create a temporary cleaned CSV in memory (DataFrame) and continue
df = pd.DataFrame(clean_rows[1:], columns=clean_rows[0])

# Normalize common column names: ensure pred_prob column exists
# The log writer used column name 'pred_prob' (if different, try a few common variants)
prob_cols = [c for c in df.columns if c.lower() in ('pred_prob','prob','predprob','pred_probability')]
if prob_cols:
    prob_col = prob_cols[0]
    df.rename(columns={prob_col: 'pred_prob'}, inplace=True)
else:
    # if no probability column found, try to infer from columns names, else error
    possible = [c for c in df.columns if 'prob' in c.lower() or 'probability' in c.lower()]
    if possible:
        df.rename(columns={possible[0]: 'pred_prob'}, inplace=True)
    else:
        raise SystemExit("Could not find a probability column in log (e.g. 'pred_prob').")

# Convert pred_prob to numeric
df['pred_prob'] = pd.to_numeric(df['pred_prob'], errors='coerce').fillna(0.0)

# If 'final_label' present, ensure numeric
if 'final_label' in df.columns:
    df['final_label'] = pd.to_numeric(df['final_label'], errors='coerce').fillna(0).astype(int)

# ready to evaluate thresholds
thresholds = [0.01, 0.05, 0.1, 0.5, 0.6, 0.7, 0.8, 0.9]
results = []
has_truth = 'true_label' in df.columns

for t in thresholds:
    pred_col = f'final_{t}'
    df[pred_col] = (df['pred_prob'] >= t).astype(int)
    alerts = int(df[pred_col].sum())
    alert_rate = alerts / len(df) if len(df) > 0 else 0.0
    row = {'threshold': float(t), 'alerts': int(alerts), 'alert_rate': float(alert_rate)}
    if has_truth:
        y_true = pd.to_numeric(df['true_label'], errors='coerce').fillna(0).astype(int)
        y_pred = df[pred_col]
        prec, rec, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='binary', zero_division=0)
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        row.update({'precision': float(prec), 'recall': float(rec), 'f1': float(f1),
                    'tp': int(tp), 'fp': int(fp), 'tn': int(tn), 'fn': int(fn)})
    results.append(row)

res_df = pd.DataFrame(results)
# Save results CSV
os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
res_df.to_csv(OUT_CSV, index=False)

# Write a short markdown notes file
with open(OUT_MD, 'w', encoding='utf-8') as fh:
    fh.write("# Threshold tuning notes\n\n")
    fh.write("This file contains results for different probability thresholds computed from your realtime predictions log.\n\n")
    fh.write(f"- Source log (backup): `{backup_path}`\n")
    fh.write(f"- Cleaned rows read: {len(df)}\n\n")
    fh.write("## Results table\n\n")
    fh.write(res_df.to_markdown(index=False))
    fh.write("\n\n")
    if not has_truth:
        fh.write("**Note:** No ground-truth (`true_label`) column found in the log. To compute precision/recall, label attack rows (e.g. by dst_port) and add `true_label` column to the log or produce a labeled copy.\n")

print("Saved:", OUT_MD)
print("Saved CSV:", OUT_CSV)
