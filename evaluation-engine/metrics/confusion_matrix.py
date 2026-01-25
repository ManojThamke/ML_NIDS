import pandas as pd


def compute_confusion_matrix(df: pd.DataFrame) -> dict:
    """
    Compute proxy confusion matrix using ensemble voting logic.

    Proxy Ground Truth:
    - ATTACK if attackVotes >= ceil(totalModels / 2)
    - BENIGN otherwise
    """

    if df.empty:
        raise ValueError("Empty DataFrame passed to confusion matrix")

    tp = fp = tn = fn = 0

    for _, row in df.iterrows():
        # Proxy ground truth
        expected_label = (
            "ATTACK"
            if row["attackVotes"] >= (row["totalModels"] / 2)
            else "BENIGN"
        )

        predicted_label = row["finalLabel"]

        if expected_label == "ATTACK" and predicted_label == "ATTACK":
            tp += 1
        elif expected_label == "BENIGN" and predicted_label == "ATTACK":
            fp += 1
        elif expected_label == "BENIGN" and predicted_label == "BENIGN":
            tn += 1
        elif expected_label == "ATTACK" and predicted_label == "BENIGN":
            fn += 1

    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0

    return {
        "TP": tp,
        "FP": fp,
        "TN": tn,
        "FN": fn,
        "False Positive Rate": round(fpr, 4),
        "False Negative Rate": round(fnr, 4),
    }
