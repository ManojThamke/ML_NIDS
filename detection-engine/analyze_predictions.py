import pandas as pd
import os
from datetime import datetime

LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "logs", "realtime_predictions.csv")

if not os.path.exists(LOG_PATH):
    raise SystemExit("No prediction log found! Run realtime_detector_log.py first.")

df = pd.read_csv(LOG_PATH)

# parse timestamp
df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
print("Loaded rows:", len(df))

# totals
total = len(df)
attacks = df[df['pred_label'] == 1].shape[0] if 'pred_label' in df.columns else df[df['pred_label']=='ATTACK 🚨'].shape[0] if 'pred_label' in df.columns else None

# some logs might store label as numeric; handle both
if 'pred_label' in df.columns:
    attack_count = df['pred_label'].astype(str).isin(['1', 'ATTACK 🚨']).sum()
else:
    attack_count = (df['pred_label'] == 1).sum() if 'pres_label' in df.columns else df['pred_label'].astype(str).isin(['1','ATTACK 🚨']).sum()


print(f"Total predictions: {total}")
print(f"Alerts (prediction attack): {attack_count} (rate: {attack_count/total:.3f})")

# top destination ports in logged flows
if 'Destination Port' in df.columns:
    print("\nTop Destination Ports:")
    print(df['Destination Port'].value_counts().head(10).to_string())

# basic time-series: per minute prediction count
if df['timestamp'].notna().any():
    per_min = df.set_index('timestamp').resample('1T').size()
    print("\nPredictions per minute:")
    print(per_min.tail(10).to_string())

# simple csv summary output
summary_path = os.path.join(os.path.dirname(__file__), "..", "logs", "predictions_summary.csv")
summary ={
    'total': total,
    'alerts': int(attack_count),
    "alert_rate": float(attack_count/total) if total>0 else 0.0
}
pd.DataFrame([summary]).to_csv(summary_path, index=False)
print(f"\n Summary saved to {summary_path}")