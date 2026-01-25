import json
from datetime import datetime


def export_metrics_for_backend(
    confusion_matrix: dict,
    classification_metrics: dict,
    per_model_analysis: dict,
    ensemble_comparison: dict,
    output_path: str = "export/evaluation_metrics.json",
):
    """
    Export evaluation metrics into a backend-safe JSON file.
    """

    payload = {
        "generatedAt": datetime.utcnow().isoformat(),
        "confusionMatrix": confusion_matrix,
        "classificationMetrics": classification_metrics,
        "perModelAnalysis": per_model_analysis,
        "ensembleComparison": ensemble_comparison,
    }

    with open(output_path, "w") as f:
        json.dump(payload, f, indent=4)

    print(f"📦 Metrics exported successfully → {output_path}")
