"""
=====================================================
Threshold Tuning Using Realtime CSV Logs (Phase-2)
=====================================================

Purpose:
- Tune GLOBAL threshold using real traffic logs
- No model re-execution
- Uses ensemble confidence from CSV
"""

import pandas as pd
import os

# ===============================
# RESOLVE PROJECT PATHS SAFELY
# ===============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

LOG_DIR = os.path.join(
    PROJECT_ROOT,
    "detection-engine",
    "realtime_v2",
    "logs"
)

# Thresholds to evaluate
THRESHOLDS = [0.2, 0.3, 0.4, 0.5, 0.6]

# ===============================
# AUTO-DETECT LOG FILE
# ===============================

if not os.path.exists(LOG_DIR):
    raise FileNotFoundError(f"❌ Log directory not found: {LOG_DIR}")

candidates = [
    f for f in os.listdir(LOG_DIR)
    if f.startswith("realtime") and f.endswith(".csv")
]

if not candidates:
    raise FileNotFoundError("❌ No realtime log file found in logs/")

LOG_FILE = os.path.join(LOG_DIR, sorted(candidates)[-1])

print(f"\n📂 Using log file: {LOG_FILE}")

# ===============================
# LOAD LOG FILE
# ===============================

df = pd.read_csv(LOG_FILE)
print(f"✔ Total flows loaded: {len(df)}")

required_columns = ["final_label", "confidence"]

for col in required_columns:
    if col not in df.columns:
        raise ValueError(f"❌ Missing required column: {col}")

print("✔ Required columns verified")

# ===============================
# THRESHOLD SIMULATION
# ===============================

print("\n🧪 Starting threshold simulation...")

results = []

for threshold in THRESHOLDS:
    for _, row in df.iterrows():

        actual = row["final_label"]
        confidence = row["confidence"]

        predicted = (
            "ATTACK" if confidence >= threshold else "BENIGN"
        )

        results.append({
            "threshold": threshold,
            "actual": actual,
            "predicted": predicted
        })

results_df = pd.DataFrame(results)

# ===============================
# METRIC CALCULATION
# ===============================

summary = []

print("\n📊 Calculating metrics per threshold...")

for threshold in THRESHOLDS:
    sub = results_df[results_df["threshold"] == threshold]

    TP = len(sub[(sub.actual == "ATTACK") & (sub.predicted == "ATTACK")])
    FP = len(sub[(sub.actual == "BENIGN") & (sub.predicted == "ATTACK")])
    TN = len(sub[(sub.actual == "BENIGN") & (sub.predicted == "BENIGN")])
    FN = len(sub[(sub.actual == "ATTACK") & (sub.predicted == "BENIGN")])

    fpr = FP / (FP + TN + 1e-6)
    fnr = FN / (FN + TP + 1e-6)

    summary.append({
        "threshold": threshold,
        "TP": TP,
        "FP": FP,
        "TN": TN,
        "FN": FN,
        "false_positive_rate": round(fpr, 4),
        "false_negative_rate": round(fnr, 4),
        "total_error": FP + FN
    })

summary_df = pd.DataFrame(summary)

# ===============================
# DISPLAY RESULTS
# ===============================

print("\n================ THRESHOLD TUNING RESULTS ================\n")
print(summary_df.to_string(index=False))

# ===============================
# RECOMMENDATION
# ===============================

best = summary_df.loc[summary_df["total_error"].idxmin()]

print("\n🏆 RECOMMENDED DEPLOYMENT THRESHOLD")
print("----------------------------------")
print(f"Threshold           : {best['threshold']}")
print(f"False Positives     : {best['FP']}")
print(f"False Negatives     : {best['FN']}")
print(f"False Positive Rate : {best['false_positive_rate']}")
print(f"False Negative Rate : {best['false_negative_rate']}")

print("\n✅ Threshold tuning completed successfully")
print("📌 Use this threshold in detector_live_capture_v2.py")
