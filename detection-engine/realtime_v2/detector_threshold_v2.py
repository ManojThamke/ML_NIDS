# detection-engine/realtime_v2/detector_threshold_v2.py
# =====================================================
# Global Threshold + Multi-Threshold Voting Engine (V2)
# =====================================================

def apply_threshold_and_vote(
    per_model_probs: dict,
    threshold: float = None,
    thresholds: list = None,
    vote_k: int = 1
):
    """
    Apply global threshold(s) to all models and perform voting.

    Parameters:
    - per_model_probs : dict
        {model_name: probability}
    - threshold : float | None
        Single global threshold (DEPLOYMENT MODE)
    - thresholds : list[float] | None
        Multiple thresholds (ANALYSIS MODE)
    - vote_k : int
        Minimum number of models required to classify ATTACK

    Returns:
    --------
    DEPLOYMENT MODE (single threshold):
    {
        "final_label": "ATTACK" | "BENIGN",
        "per_model_decision": {model: 0/1},
        "triggered_models": [...],
        "attack_votes": int,
        "threshold": float,
        "vote_k": int
    }

    ANALYSIS MODE (multi-threshold):
    {
        threshold_value: {
            "final_label": "ATTACK" | "BENIGN",
            "attack_votes": int,
            "triggered_models": [...]
        }
    }
    """

    # ==================================================
    # MULTI-THRESHOLD MODE (OFFLINE / ANALYSIS)
    # ==================================================
    if thresholds is not None:
        results = {}

        for th in thresholds:
            triggered_models = [
                model for model, prob in per_model_probs.items()
                if prob >= th
            ]

            attack_votes = len(triggered_models)
            final_label = (
                "ATTACK" if attack_votes >= vote_k else "BENIGN"
            )

            results[th] = {
                "final_label": final_label,
                "attack_votes": attack_votes,
                "triggered_models": triggered_models
            }

        return results

    # ==================================================
    # SINGLE THRESHOLD MODE (REALTIME / DEPLOYMENT)
    # ==================================================
    if threshold is None:
        threshold = 0.5  # safe default

    per_model_decision = {}
    triggered_models = []

    for model, prob in per_model_probs.items():
        decision = 1 if prob >= threshold else 0
        per_model_decision[model] = decision

        if decision == 1:
            triggered_models.append(model)

    attack_votes = len(triggered_models)
    final_label = (
        "ATTACK" if attack_votes >= vote_k else "BENIGN"
    )

    return {
        "final_label": final_label,
        "per_model_decision": per_model_decision,
        "triggered_models": triggered_models,
        "attack_votes": attack_votes,
        "threshold": threshold,
        "vote_k": vote_k
    }
