import pandas as pd


def ensemble_comparison(df: pd.DataFrame) -> dict:
    """
    Compare ensemble behavior with individual model outputs.
    """

    if df.empty:
        raise ValueError("Empty DataFrame passed for ensemble comparison")

    ensemble_confidence = []
    best_model_confidence = []
    agreement_count = 0

    total_rows = len(df)

    for _, row in df.iterrows():
        probs = row["modelProbabilities"]

        if not probs:
            continue

        # Best single model confidence
        best_single = max(probs.values())
        best_model_confidence.append(best_single)

        # Ensemble confidence
        ensemble_confidence.append(row["confidence"])

        # Safe threshold handling
        threshold = row.get("threshold", 0.5)

        dominant_model = max(probs, key=probs.get)
        dominant_vote = (
            "ATTACK"
            if probs[dominant_model] >= threshold
            else "BENIGN"
        )

        if dominant_vote == row["finalLabel"]:
            agreement_count += 1

    avg_ensemble_conf = round(sum(ensemble_confidence) / len(ensemble_confidence), 6)
    avg_best_model_conf = round(sum(best_model_confidence) / len(best_model_confidence), 6)
    agreement_rate = round(agreement_count / total_rows, 4)

    return {
        "Average Ensemble Confidence": avg_ensemble_conf,
        "Average Best Model Confidence": avg_best_model_conf,
        "Ensemble vs Model Confidence Gain": round(avg_ensemble_conf - avg_best_model_conf, 6),
        "Voting Agreement Rate": agreement_rate
    }
