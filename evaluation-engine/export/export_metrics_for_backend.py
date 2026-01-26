import json
from datetime import datetime


def export_metrics_for_backend(
    confusion_matrix: dict,
    classification_metrics: dict,
    confidence_stability: dict,
    per_model_analysis: dict,
    ensemble_comparison: dict,
    time_window: str = "all",
    output_path: str = "export/evaluation_metrics.json",
):
    """
    Export evaluation metrics into a backend-safe unified JSON file.
    This file acts as a contract between Python Evaluation Engine and MERN backend.
    """

    payload = {
        "meta": {
            "generatedAt": datetime.utcnow().isoformat(),
            "timeWindow": time_window,
            "engine": "evaluation-engine",
            "mode": "real-time-log-analysis"
        },
        "confusionMatrix": confusion_matrix,
        "classificationMetrics": classification_metrics,
        "confidenceStability": confidence_stability,
        "perModelAnalysis": per_model_analysis,
        "ensembleComparison": ensemble_comparison
    }

    with open(output_path, "w") as f:
        json.dump(payload, f, indent=4)

    print(f"📦 Evaluation metrics exported successfully → {output_path}")
