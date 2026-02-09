def apply_hybrid_logic(payload: dict):
    """
    Hybrid Decision Engine (V2.1 – CICIDS2018 Aligned)

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

    flow_duration = payload.get("flowDuration")

    # --------------------------------------------------
    # DEFAULT OUTPUT
    # --------------------------------------------------
    hybrid_label = "BENIGN"
    severity = "LOW"
    reason = "Low risk traffic"

    # ==================================================
    # HARD SAFETY RULES (APPLY FIRST)
    # ==================================================

    # 1️⃣ Non TCP/UDP traffic
    if protocol not in ["TCP", "UDP"]:
        payload.update({
            "hybridLabel": "BENIGN",
            "severity": "LOW",
            "hybridReason": "Non TCP/UDP traffic (out of CICIDS scope)"
        })
        return payload

    # 2️⃣ Multicast traffic
    if dst_ip and dst_ip.startswith(("224.", "239.")):
        payload.update({
            "hybridLabel": "BENIGN",
            "severity": "LOW",
            "hybridReason": "Multicast discovery/control traffic"
        })
        return payload

    # 3️⃣ Service discovery protocols
    if dst_port in [1900, 5353, 137, 138]:
        payload.update({
            "hybridLabel": "BENIGN",
            "severity": "LOW",
            "hybridReason": "Local service discovery traffic"
        })
        return payload

    # ==================================================
    # APPLY HYBRID LOGIC ONLY IF ML FLAGS ATTACK
    # ==================================================
    if final_label == "ATTACK":

        # --------------------------------------------------
        # 1️⃣ Very weak signal → LOW
        # --------------------------------------------------
        if confidence < 0.55:
            hybrid_label = "SUSPICIOUS"
            severity = "LOW"
            reason = "Very low ensemble confidence"

        # --------------------------------------------------
        # 2️⃣ Moderate confidence + weak agreement → MEDIUM
        # --------------------------------------------------
        elif confidence < 0.75 and attack_votes < vote_k:
            hybrid_label = "SUSPICIOUS"
            severity = "MEDIUM"
            reason = "Moderate confidence with weak multi-model agreement"

        # --------------------------------------------------
        # 3️⃣ DNS / HTTPS false-positive protection
        # --------------------------------------------------
        elif dst_port in [53, 443] and confidence < 0.80:
            hybrid_label = "SUSPICIOUS"
            severity = "LOW"
            reason = "Likely benign DNS/HTTPS traffic"

        # --------------------------------------------------
        # 4️⃣ Short-lived flows
        # --------------------------------------------------
        elif flow_duration is not None and flow_duration < 2 and confidence < 0.80:
            hybrid_label = "BENIGN"
            severity = "LOW"
            reason = "Short-lived low-volume flow"

        # --------------------------------------------------
        # 5️⃣ TRUE HIGH CONFIDENCE ATTACK
        # --------------------------------------------------
        else:
            hybrid_label = "ATTACK"
            severity = "HIGH"
            reason = "High confidence multi-model attack"

    # --------------------------------------------------
    # Update payload
    # --------------------------------------------------
    payload.update({
        "hybridLabel": hybrid_label,
        "severity": severity,
        "hybridReason": reason
    })

    return payload
