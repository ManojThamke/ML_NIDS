import pandas as pd
from collections import defaultdict


def per_model_analysis(df: pd.DataFrame) -> dict:
    """
    Analyze individual model behavior from ensemble logs.
    Uses modelProbabilities field.
    """

    if df.empty:
        raise ValueError("Empty DataFrame passed for model analysis")

    model_confidence_sum = defaultdict(float)
    model_count = defaultdict(int)
    dominant_model_count = defaultdict(int)

    for _, row in df.iterrows():
        probs = row["modelProbabilities"]

        if not probs:
            continue

        # Track dominant model (highest probability)
        dominant_model = max(probs, key=probs.get)
        dominant_model_count[dominant_model] += 1

        # Track average confidence
        for model, prob in probs.items():
            model_confidence_sum[model] += prob
            model_count[model] += 1

    # Compute average confidence
    avg_confidence = {
        model: round(model_confidence_sum[model] / model_count[model], 6)
        for model in model_confidence_sum
    }

    # Rank models by dominance
    model_ranking = sorted(
        dominant_model_count.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return {
        "Average Confidence Per Model": avg_confidence,
        "Dominant Model Frequency": dict(dominant_model_count),
        "Model Ranking (by dominance)": model_ranking
    }
