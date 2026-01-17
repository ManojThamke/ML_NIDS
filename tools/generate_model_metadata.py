# ==================================================
# Generate Model Metadata (Phase-2)
# Select best model based on evaluation results
# ==================================================

import json
import os
from statistics import mean
from datetime import datetime

EVAL_FILE = "results/offline_evaluation_v2.json"
OUTPUT_FILE = "models/phase2_offline_v2/model_metadata.json"

os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

with open(EVAL_FILE, "r") as f:
    results = json.load(f)

model_scores = {}

for model_name, runs in results.items():
    f1_scores = []
    roc_scores = []

    for _, metrics in runs.items():
        if metrics["f1_score"] is not None:
            f1_scores.append(metrics["f1_score"])
        if metrics["roc_auc"] is not None:
            roc_scores.append(metrics["roc_auc"])

    model_scores[model_name] = {
        "avg_f1": round(mean(f1_scores), 4),
        "avg_roc_auc": round(mean(roc_scores), 4)
    }

# Select best model (highest F1, tie-breaker ROC-AUC)
best_model = max(
    model_scores.items(),
    key=lambda x: (x[1]["avg_f1"], x[1]["avg_roc_auc"])
)

metadata = {
    "selected_model": f"{best_model[0]}_v2.pkl",
    "selection_criteria": "Highest average F1-score with ROC–AUC as tie-breaker",
    "metrics": best_model[1],
    "evaluated_models": model_scores,
    "generated_on": datetime.now().isoformat()
}

with open(OUTPUT_FILE, "w") as f:
    json.dump(metadata, f, indent=4)

print("✅ Model metadata generated successfully")
print(f"🏆 Selected Model: {metadata['selected_model']}")
print(f"📊 Metrics: {metadata['metrics']}")
