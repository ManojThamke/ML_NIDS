def compute_classification_metrics(confusion: dict) -> dict:
    """
    Compute classification metrics from confusion matrix.
    Input dictionary must contain TP, FP, TN, FN.
    """

    tp = confusion["TP"]
    fp = confusion["FP"]
    tn = confusion["TN"]
    fn = confusion["FN"]

    accuracy = (tp + tn) / (tp + tn + fp + fn)
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
