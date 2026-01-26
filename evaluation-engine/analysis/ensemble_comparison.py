import pandas as pd


def ensemble_comparison(df: pd.DataFrame, noise_conf_threshold: float = 0.6) -> dict:
    """
    Compare ensemble behavior with individual model outputs.
    Adds alert noise ratio to measure low-confidence ATTACK alerts.
    """

    if df.empty:
        raise ValueError("Empty DataFrame passed for ensemble comparison")

    ensemble_confidence = []
    best_model_confidence = []
    agreement_count = 0

    low_conf_attack_count = 0
    total_attack_count = 0

    total_rows = len(df)

    for _, row in df.iterrows():
        probs = row.get("modelProbabilities", {})
        confidence = row.get("confidence")
        final_label = row.get("finalLabel")

        if not probs or confidence is None:
            continue

        # ---------- Best Single Model Confidence ----------
        best_single = max(probs.values())
        best_model_confidence.append(best_single)

        # ---------- Ensemble Confidence ----------
        ensemble_confidence.append(confidence)

        # ---------- Threshold Handling ----------
        threshold = row.get("threshold", 0.5)

        dominant_model = max(probs, key=probs.get)
        dominant_vote = (
            "ATTACK"
            if probs[dominant_model] >= threshold
            else "BENIGN"
        )

        if dominant_vote == final_label:
            agreement_count += 1

        # ---------- Alert Noise Ratio ----------
        if final_label == "ATTACK":
            total_attack_count += 1
            if confidence < noise_conf_threshold:
                low_conf_attack_count += 1

    avg_ensemble_conf = (
        round(sum(ensemble_confidence) / len(ensemble_confidence), 6)
        if ensemble_confidence else 0
    )

    avg_best_model_conf = (
        round(sum(best_model_confidence) / len(best_model_confidence), 6)
        if best_model_confidence else 0
    )

    agreement_rate = round(
        agreement_count / total_rows, 4
    ) if total_rows > 0 else 0

    alert_noise_ratio = (
        round(low_conf_attack_count / total_attack_count, 4)
        if total_attack_count > 0 else 0
    )

    return {
        "Average Ensemble Confidence": avg_ensemble_conf,
        "Average Best Model Confidence": avg_best_model_conf,
        "Ensemble vs Model Confidence Gain": round(
            avg_ensemble_conf - avg_best_model_conf, 6
        ),
        "Voting Agreement Rate": agreement_rate,
        "Alert Noise": {
            "Low Confidence ATTACK Alerts": low_conf_attack_count,
            "Total ATTACK Alerts": total_attack_count,
            "Noise Ratio": alert_noise_ratio
        }
    }
