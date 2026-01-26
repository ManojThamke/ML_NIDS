import numpy as np


def compute_classification_metrics(confusion: dict) -> dict:
    """
    Compute classification metrics from a confusion matrix.
    Input dictionary must contain: TP, FP, TN, FN
    """

    tp = confusion.get("TP", 0)
    fp = confusion.get("FP", 0)
    tn = confusion.get("TN", 0)
    fn = confusion.get("FN", 0)

    total = tp + tn + fp + fn

    accuracy = (tp + tn) / total if total > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1_score = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0
    )

    return {
        "Accuracy": round(accuracy, 4),
        "Precision": round(precision, 4),
        "Recall": round(recall, 4),
        "F1-Score": round(f1_score, 4),
        "Support": {
            "ATTACK": tp + fn,
            "BENIGN": tn + fp
        }
    }


def compute_confidence_stability(confidences: list) -> dict:
    """
    Compute confidence stability metrics for ensemble predictions.
    Measures how consistent real-time confidence scores are.
    """

    if not confidences:
        return {
            "mean": 0,
            "std": 0,
            "variance": 0
        }

    confidences = np.array(confidences)

    return {
        "mean": round(float(np.mean(confidences)), 4),
        "std": round(float(np.std(confidences)), 4),
        "variance": round(float(np.var(confidences)), 4)
    }
