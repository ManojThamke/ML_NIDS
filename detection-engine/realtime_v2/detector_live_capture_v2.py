# detection-engine/realtime_v2/detector_live_capture_v2.py
# =====================================================
# Phase-2 Realtime Live Packet → Flow → Feature → ML
# STEP-4: MULTI-MODEL + VOTING + HYBRID + LOGGING
# =====================================================

from scapy.all import sniff, IP, TCP, UDP
import time
import pandas as pd
import argparse

from feature_extractor_v2 import FlowStats, REALTIME_FEATURES
from detector_multi_model_v2 import detect_with_all_models, SCALER
from detector_threshold_v2 import apply_threshold_and_vote
from hybrid_controller import apply_hybrid_logic
from detector_logger_v2 import log_detection
from alert_manager import trigger_alert

# ===============================
# CLI ARGUMENTS
# ===============================

parser = argparse.ArgumentParser(
    description="Realtime Hybrid ML-NIDS (Phase-2)"
)

parser.add_argument(
    "--iface",
    type=str,
    required=True,
    help="Network interface to sniff on (mandatory for Windows / hotspot)"
)

parser.add_argument(
    "--models",
    type=str,
    default="all",
    help="Models to use: all OR comma-separated list"
)

parser.add_argument("--threshold", type=float, default=0.5)
parser.add_argument("--vote", type=int, default=3)
parser.add_argument("--timeout", type=int, default=10)

args = parser.parse_args()

INTERFACE = args.iface
GLOBAL_THRESHOLD = args.threshold
VOTE_K = args.vote
FLOW_TIMEOUT = args.timeout

# Resolve models
if args.models.lower() == "all":
    SELECTED_MODELS = None
else:
    SELECTED_MODELS = [m.strip() for m in args.models.split(",")]

# ===============================
# FLOW TABLE
# ===============================

FLOW_TABLE = {}

# ===============================
# FLOW KEY HELPERS
# ===============================

def get_flow_key(pkt):
    ip = pkt[IP]
    if TCP in pkt:
        return (ip.src, ip.dst, pkt[TCP].sport, pkt[TCP].dport, "TCP")
    elif UDP in pkt:
        return (ip.src, ip.dst, pkt[UDP].sport, pkt[UDP].dport, "UDP")
    return None


def is_forward(flow_key, pkt):
    _, _, sport, _, proto = flow_key
    if proto == "TCP":
        return pkt[TCP].sport == sport
    elif proto == "UDP":
        return pkt[UDP].sport == sport
    return False

# ===============================
# FLOW FINALIZATION
# ===============================

def process_flow(flow_key, flow):
    """
    Flow → Feature → Multi-Model → Voting → Hybrid → Log
    """

    # 1️⃣ Extract features
    features = flow.extract_features()

    # ✅ Flow Duration is ALREADY at index 1 (LOCKED FEATURE ORDER)
    flow_duration = round(features[1], 6)

    feature_df = pd.DataFrame([features], columns=REALTIME_FEATURES)

    # 🔒 Enforce training feature order
    feature_df = feature_df[list(SCALER.feature_names_in_)]

    # 2️⃣ Multi-model inference
    model_results = detect_with_all_models(
        feature_df,
        selected_models=SELECTED_MODELS
    )

    per_model_probs = {
        model: res["probability"]
        for model, res in model_results.items()
    }

    # 3️⃣ Threshold + voting
    vote_result = apply_threshold_and_vote(
        per_model_probs=per_model_probs,
        threshold=GLOBAL_THRESHOLD,
        vote_k=VOTE_K
    )

    # 4️⃣ Mean confidence
    mean_confidence = sum(per_model_probs.values()) / len(per_model_probs)

    # 5️⃣ Build payload
    payload = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),

        "sourceIP": flow_key[0],
        "destinationIP": flow_key[1],
        "srcPort": flow_key[2],
        "dstPort": flow_key[3],
        "protocol": flow_key[4],

        "finalLabel": vote_result["final_label"],
        "confidence": mean_confidence,

        "attackVotes": vote_result["attack_votes"],
        "totalModels": len(per_model_probs),
        "threshold": GLOBAL_THRESHOLD,
        "voteK": VOTE_K,
        "aggMethod": "global-threshold-voting",

        "flowDuration": flow_duration,
        "modelProbabilities": per_model_probs
    }

    # 6️⃣ Hybrid logic
    payload = apply_hybrid_logic(payload)

    # 7️⃣ Alert (only if HIGH)
    trigger_alert(payload)

    # 8️⃣ Logging
    log_detection(payload)

    # 9️⃣ Console output
    print("\n🚨 FLOW ANALYSIS RESULT")
    print(f"Flow           : {flow_key}")
    print(f"ML Decision    : {vote_result['final_label']}")
    print(f"Hybrid Decision: {payload['hybridLabel']}")
    print(f"Severity       : {payload['severity']}")
    print(f"Confidence     : {round(mean_confidence, 4)}")
    print(f"Attack Votes   : {payload['attackVotes']}")
    print(f"Flow Duration  : {flow_duration}s")
    print(f"Reason         : {payload['hybridReason']}")
    print("-" * 60)

# ===============================
# PACKET HANDLER
# ===============================

def on_packet(pkt):
    if IP not in pkt:
        return

    flow_key = get_flow_key(pkt)
    if flow_key is None:
        return

    now = time.time()

    if flow_key not in FLOW_TABLE:
        FLOW_TABLE[flow_key] = {
            "flow": FlowStats(dst_port=flow_key[3]),
            "last_seen": now
        }
        print(f"\n🆕 New Flow Detected: {flow_key}")

    entry = FLOW_TABLE[flow_key]
    flow = entry["flow"]
    entry["last_seen"] = now

    pkt_len = len(pkt)

    if is_forward(flow_key, pkt):
        flow.update_forward(pkt_len)
    else:
        flow.update_backward(pkt_len)

    # ⏱️ Timeout-based expiry
    expired = []
    for key, entry in FLOW_TABLE.items():
        if now - entry["last_seen"] > FLOW_TIMEOUT:
            expired.append(key)

    for key in expired:
        process_flow(key, FLOW_TABLE[key]["flow"])
        del FLOW_TABLE[key]

# ===============================
# MAIN
# ===============================

if __name__ == "__main__":
    print("🚀 Starting Realtime V2 Live Capture (STEP-4)")
    print("✔ Packet capture enabled")
    print("✔ Flow tracking enabled")
    print("✔ Feature extraction enabled")
    print("✔ Multi-model ML enabled")
    print("✔ Threshold voting enabled")
    print("✔ Hybrid logic enabled")
    print("✔ Logging enabled")
    print(
        f"Iface={INTERFACE} | "
        f"Models={args.models} | "
        f"Threshold={GLOBAL_THRESHOLD} | "
        f"VoteK={VOTE_K} | "
        f"Timeout={FLOW_TIMEOUT}s"
    )
    print("-" * 60)

    sniff(
        iface=INTERFACE,
        prn=on_packet,
        store=False
    )
