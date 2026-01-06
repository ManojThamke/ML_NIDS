import sys
import os
import argparse
import pandas as pd

# --------------------------------------
# ADD PROJECT ROOT TO PYTHON PATH
# --------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ======================================
# IMPORTS
# ======================================
from realtime_v2.model_loader_v2 import load_realtime_models
from realtime_v2.detector_multi_model_v2 import detect_with_all_models
from realtime_v2.detector_threshold_v2 import apply_threshold_and_vote

# ======================================
# ARGUMENT PARSER
# ======================================
parser = argparse.ArgumentParser(
    description="Realtime V2 Global Threshold & Voting Test"
)

parser.add_argument(
    "--threshold",
    type=float,
    help="Single global threshold (deployment mode)"
)

parser.add_argument(
    "--thresholds",
    type=str,
    help="Comma-separated thresholds for analysis mode (e.g. 0.4,0.5,0.6)"
)

parser.add_argument(
    "--vote",
    type=int,
    default=2,
    help="Minimum number of models required to trigger ATTACK"
)

args = parser.parse_args()

# ======================================
# LOAD MODELS
# ======================================
print("\n📦 Loading realtime models (V2)...")
models = load_realtime_models()

# ======================================
# SAMPLE REALTIME INPUT
# ======================================
REALTIME_FEATURES = [
    "Destination Port",
    "Flow Duration",
    "Total Fwd Packets",
    "Total Backward Packets",
    "Total Length of Fwd Packets",
    "Total Length of Bwd Packets",
    "Fwd Packet Length Min",
    "Fwd Packet Length Mean",
    "Packet Length Std",
    "Flow IAT Mean",
    "Fwd IAT Mean",
    "Down/Up Ratio"
]

sample = pd.DataFrame([{
    "Destination Port": 80,
    "Flow Duration": 120000,
    "Total Fwd Packets": 10,
    "Total Backward Packets": 8,
    "Total Length of Fwd Packets": 5000,
    "Total Length of Bwd Packets": 4200,
    "Fwd Packet Length Min": 40,
    "Fwd Packet Length Mean": 500,
    "Packet Length Std": 120,
    "Flow IAT Mean": 15000,
    "Fwd IAT Mean": 8000,
    "Down/Up Ratio": 1.2
}], columns=REALTIME_FEATURES)

# ======================================
# MULTI-MODEL INFERENCE
# ======================================
print("\n🧪 Day 5 – Multi-model inference test\n")

results = detect_with_all_models(sample)

for model, res in results.items():
    print(f"{model:25s} -> {res}")

per_model_probs = {
    model: res["probability"]
    for model, res in results.items()
}

# ======================================
# THRESHOLD & VOTING LOGIC
# ======================================
print("\n🧪 Day 5 – Global threshold & voting logic\n")

# ---- MULTI-THRESHOLD MODE (RESEARCH / ANALYSIS) ----
if args.thresholds:
    thresholds = [float(x.strip()) for x in args.thresholds.split(",")]

    print("Multi-threshold Decision Output:\n")

    for th in thresholds:
        result = apply_threshold_and_vote(
            per_model_probs=per_model_probs,
            threshold=th,
            vote_k=args.vote
        )

        print(f"Threshold = {th}")
        for k, v in result.items():
            print(f"{k}: {v}")
        print("-" * 45)

# ---- SINGLE THRESHOLD MODE (DEPLOYMENT) ----
else:
    threshold = args.threshold if args.threshold is not None else 0.5

    final_result = apply_threshold_and_vote(
        per_model_probs=per_model_probs,
        threshold=threshold,
        vote_k=args.vote
    )

    print("Final Decision Output:\n")
    for k, v in final_result.items():
        print(f"{k}: {v}")

print("\n✅ Day 5 – Part 2 completed successfully")
