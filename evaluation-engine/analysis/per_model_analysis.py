import pandas as pd
from collections import defaultdict


def per_model_analysis(
    df: pd.DataFrame,
    threshold: float = 0.6,
    margin: float = 0.05
) -> dict:
    """
    Analyze individual model behavior from ensemble logs.
    - Average confidence per model
    - Dominant model frequency
    - Model ranking by dominance
    - Threshold proximity analysis (risk decisions)
    """

    if df.empty:
        raise ValueError("Empty DataFrame passed for model analysis")

    model_confidence_sum = defaultdict(float)
    model_count = defaultdict(int)
    dominant_model_count = defaultdict(int)

    near_threshold_count = 0
    total_predictions = 0

    for _, row in df.iterrows():
        probs = row.get("modelProbabilities", {})
        confidence = row.get("confidence")

        if not probs:
            continue

        total_predictions += 1

        # ---------- Threshold Proximity ----------
        if confidence is not None:
            if abs(confidence - threshold) <= margin:
                near_threshold_count += 1

        # ---------- Dominant Model ----------
        dominant_model = max(probs, key=probs.get)
        dominant_model_count[dominant_model] += 1

        # ---------- Average Confidence ----------
        for model, prob in probs.items():
            model_confidence_sum[model] += prob
            model_count[model] += 1

    # Compute average confidence per model
    avg_confidence = {
        model: round(model_confidence_sum[model] / model_count[model], 6)
        for model in model_confidence_sum
        if model_count[model] > 0
    }

    # Rank models by dominance
    model_ranking = sorted(
        dominant_model_count.items(),
        key=lambda x: x[1],
        reverse=True
    )

    threshold_proximity = {
        "near_threshold_count": near_threshold_count,
        "total_predictions": total_predictions,
        "percentage": round(
            (near_threshold_count / total_predictions) * 100, 2
        ) if total_predictions > 0 else 0
    }

    return {
        "Average Confidence Per Model": avg_confidence,
        "Dominant Model Frequency": dict(dominant_model_count),
        "Model Ranking (by dominance)": model_ranking,
        "Threshold Proximity": threshold_proximity
    }
