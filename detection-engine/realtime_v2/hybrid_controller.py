def apply_hybrid_logic(payload: dict):
    """
    Hybrid Decision Engine (V2)

    Combines:
    - ML ensemble output
    - Voting strength
    - Confidence score
    - Protocol / port awareness
    - Network context

    Final labels:
    - BENIGN
    - SUSPICIOUS
    - ATTACK
    """

    # -------------------------------
    # Extract required fields
    # -------------------------------
    final_label = payload.get("finalLabel")
    confidence = payload.get("confidence", 0.0)
    attack_votes = payload.get("attackVotes", 0)
    vote_k = payload.get("voteK", 1)

    dst_port = payload.get("dstPort")
    dst_ip = payload.get("destinationIP")

    # Optional (future-safe)
    flow_duration = payload.get("flowDuration", None)

    # -------------------------------
    # Default decision
    # -------------------------------
    hybrid_label = "BENIGN"
    severity = "BENIGN"
    reason = "Low risk traffic"

    # ==========================================================
    # APPLY HYBRID LOGIC ONLY IF ML SAYS ATTACK
    # ==========================================================
    if final_label == "ATTACK":

        # ------------------------------------------------------
        # RULE 1: Very low confidence → downgrade
        # ------------------------------------------------------
        if confidence < 0.55:
            hybrid_label = "SUSPICIOUS"
            severity = "LOW"
            reason = "Very low ensemble confidence"

        # ------------------------------------------------------
        # RULE 2: Weak model agreement
        # (Barely crossing vote threshold)
        # ------------------------------------------------------
        elif attack_votes < (vote_k + 1):
            hybrid_label = "SUSPICIOUS"
            severity = "MEDIUM"
            reason = "Partial model agreement"

        # ------------------------------------------------------
        # RULE 3: Multicast traffic safeguard
        # (SSDP, routing, discovery)
        # ------------------------------------------------------
        elif dst_ip and dst_ip.startswith(("224.", "239.")):
            hybrid_label = "BENIGN"
            severity = "LOW"
            reason = "Multicast control / discovery traffic"

        # ------------------------------------------------------
        # RULE 4: SSDP (UPnP discovery)
        # ------------------------------------------------------
        elif dst_port == 1900:
            hybrid_label = "BENIGN"
            severity = "LOW"
            reason = "SSDP multicast discovery traffic"

        # ------------------------------------------------------
        # RULE 5: mDNS (Apple / Linux service discovery)
        # ------------------------------------------------------
        elif dst_port == 5353:
            hybrid_label = "BENIGN"
            severity = "LOW"
            reason = "mDNS local service discovery"

        # ------------------------------------------------------
        # RULE 6: Windows NetBIOS discovery
        # ------------------------------------------------------
        elif dst_port in [137, 138]:
            hybrid_label = "BENIGN"
            severity = "LOW"
            reason = "Windows network discovery traffic"

        # ------------------------------------------------------
        # RULE 7: Browser / DNS / HTTPS safeguard
        # ------------------------------------------------------
        elif dst_port in [53, 443] and confidence < 0.7:
            hybrid_label = "SUSPICIOUS"
            severity = "LOW"
            reason = "Likely browser or DNS-related traffic"

        # ------------------------------------------------------
        # RULE 8: Short-lived flows (anti false-positive)
        # ------------------------------------------------------
        elif flow_duration is not None and flow_duration < 2 and confidence < 0.7:
            hybrid_label = "BENIGN"
            severity = "LOW"
            reason = "Short-lived low-volume flow"

        # ------------------------------------------------------
        # RULE 9: TRUE HIGH-CONFIDENCE ATTACK
        # ------------------------------------------------------
        else:
            hybrid_label = "ATTACK"
            severity = "HIGH"
            reason = "High confidence multi-model attack"

    # -------------------------------
    # Update payload
    # -------------------------------
    payload["hybridLabel"] = hybrid_label
    payload["severity"] = severity
    payload["hybridReason"] = reason

    return payload
