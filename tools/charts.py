import json
import numpy as np
import matplotlib.pyplot as plt
import os

# ----------------------------------
# Paths
# ----------------------------------
RESULTS_FILE = "results/offline_evaluation_v2.json"
OUTPUT_DIR = os.path.join("docs", "final_paper_charts")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ----------------------------------
# Load results
# ----------------------------------
with open(RESULTS_FILE, "r") as f:
    results = json.load(f)

train_labels = ["40%", "50%", "60%", "70%", "80%", "90%", "100%"]
models = list(results.keys())

# ----------------------------------
# Compute average F1-score per model
# ----------------------------------
avg_f1_scores = []

for model in models:
    f1_values = [
        results[model][p]["f1_score"] * 100
        for p in train_labels
    ]
    avg_f1_scores.append(np.mean(f1_values))

# ----------------------------------
# Plot FINAL Chart-1
# ----------------------------------
plt.figure(figsize=(12, 5))
bars = plt.bar(models, avg_f1_scores)

plt.xlabel("Machine Learning Models", fontsize=11)
plt.ylabel("Average F1-Score (%)", fontsize=11)
plt.title("Offline F1-Score Comparison of Machine Learning Models", fontsize=12)

plt.xticks(rotation=30, ha="right")
plt.grid(axis="y", linestyle="--", alpha=0.6)

# Dataset note (small & clean)
plt.text(
    0.98, 0.02,
    "Dataset: CICIDS2018\nTrain/Test: 80/20",
    transform=plt.gca().transAxes,
    fontsize=9,
    ha="right",
    va="bottom",
    bbox=dict(boxstyle="round", facecolor="white", alpha=0.85)
)

plt.tight_layout()
plt.savefig(
    os.path.join(OUTPUT_DIR, "Fig1_Offline_F1Score_Comparison.png"),
    dpi=300
)
plt.close()

print("✅ Final Chart-1 (Offline F1-Score) generated successfully.")
