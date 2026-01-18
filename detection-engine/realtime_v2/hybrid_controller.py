def apply_hybrid_logic(payload: dict):
    """
    Hybrid Decision Engine (V2 – CICIDS2018 Aligned)

    Combines:
    - Multi-model ML decision
    - Voting strength
    - Confidence score
    - Protocol & port awareness
    - Flow context

    Final labels:
    - BENIGN
    - SUSPICIOUS
    - ATTACK
    """

    # --------------------------------------------------
    # Extract required fields (SAFE)
    # --------------------------------------------------
    final_label = payload.get("finalLabel", "BENIGN")
    confidence = payload.get("confidence", 0.0)
    attack_votes = payload.get("attackVotes", 0)
    vote_k = payload.get("voteK", 1)

    dst_port = payload.get("dstPort")
    dst_ip = payload.get("destinationIP")
    protocol = payload.get("protocol")

    flow_duration = payload.get("flowDuration", None)

    # --------------------------------------------------
    # DEFAULT OUTPUT
    # --------------------------------------------------
    hybrid_label = "BENIGN"
    severity = "BENIGN"
    reason = "Low risk traffic"

    # ==================================================
    # HARD SAFETY RULES (APPLY FIRST)
    # ==================================================

    # 1️⃣ Non TCP/UDP traffic (not part of CICIDS)
    if protocol not in ["TCP", "UDP"]:
        payload["hybridLabel"] = "BENIGN"
        payload["severity"] = "LOW"
        payload["hybridReason"] = "Non TCP/UDP traffic (out of CICIDS scope)"
        return payload

    # 2️⃣ Multicast traffic
    if dst_ip and dst_ip.startswith(("224.", "239.")):
        payload["hybridLabel"] = "BENIGN"
        payload["severity"] = "LOW"
        payload["hybridReason"] = "Multicast discovery/control traffic"
        return payload

    # 3️⃣ Service discovery protocols
    if dst_port in [1900, 5353, 137, 138]:
        payload["hybridLabel"] = "BENIGN"
        payload["severity"] = "LOW"
        payload["hybridReason"] = "Local service discovery traffic"
        return payload

    # ==================================================
    # APPLY HYBRID LOGIC ONLY IF ML FLAGS ATTACK
    # ==================================================
    if final_label == "ATTACK":

        # --------------------------------------------------
        # Very low confidence → downgrade
        # --------------------------------------------------
        if confidence < 0.60:
            hybrid_label = "SUSPICIOUS"
            severity = "LOW"
            reason = "Very low ensemble confidence"

        # --------------------------------------------------
        # Weak ensemble agreement
        # --------------------------------------------------
        elif attack_votes < (vote_k + 1):
            hybrid_label = "SUSPICIOUS"
            severity = "MEDIUM"
            reason = "Weak multi-model agreement"

        # --------------------------------------------------
        # DNS / HTTPS false-positive protection
        # --------------------------------------------------
        elif dst_port in [53, 443] and confidence < 0.75:
            hybrid_label = "SUSPICIOUS"
            severity = "LOW"
            reason = "Likely benign DNS/HTTPS traffic"

        # --------------------------------------------------
        # Short-lived flows
        # --------------------------------------------------
        elif flow_duration is not None and flow_duration < 2 and confidence < 0.75:
            hybrid_label = "BENIGN"
            severity = "LOW"
            reason = "Short-lived low-volume flow"

        # --------------------------------------------------
        # TRUE HIGH CONFIDENCE ATTACK
        # --------------------------------------------------
        else:
            hybrid_label = "ATTACK"
            severity = "HIGH"
            reason = "High confidence multi-model attack"

    # --------------------------------------------------
    # Update payload
    # --------------------------------------------------
    payload["hybridLabel"] = hybrid_label
    payload["severity"] = severity
    payload["hybridReason"] = reason

    return payload
