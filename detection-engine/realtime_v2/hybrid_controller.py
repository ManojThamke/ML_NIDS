def apply_hybrid_logic(payload: dict):
    """
    Applies hybrid (ML + rule-based) logic
    to refine ATTACK / BENIGN into:
    BENIGN / SUSPICIOUS / ATTACK
    """

    final_label = payload["finalLabel"]
    confidence = payload["confidence"]
    attack_votes = payload["attackVotes"]
    vote_k = payload["voteK"]
    dst_port = payload["dstPort"]

    # Default severity
    severity = "BENIGN"
    hybrid_label = "BENIGN"
    reason = "Low risk traffic"

    # -------------------------------
    # Hybrid downgrade rules
    # -------------------------------

    if final_label == "ATTACK":

        # Low confidence attack
        if confidence < 0.6:
            hybrid_label = "SUSPICIOUS"
            severity = "LOW"
            reason = "Low confidence ensemble decision"

        # Weak model agreement
        elif attack_votes < (vote_k + 1):
            hybrid_label = "SUSPICIOUS"
            severity = "MEDIUM"
            reason = "Partial model agreement"

        # Browser / DNS traffic safeguard
        elif dst_port in [53, 443] and confidence < 0.7:
            hybrid_label = "SUSPICIOUS"
            severity = "LOW"
            reason = "Likely browser/DNS traffic"

        # True high-confidence attack
        else:
            hybrid_label = "ATTACK"
            severity = "HIGH"
            reason = "High confidence multi-model attack"

    payload["hybridLabel"] = hybrid_label
    payload["severity"] = severity
    payload["hybridReason"] = reason

    return payload
