# detector_live_capture_v2.py
# ===============================
# IMPORTS
# ===============================

# Scapy for live packet capture
from scapy.all import sniff, IP, TCP, UDP

# Data handling
import pandas as pd
import time
import argparse

# ===============================
# LOCAL PROJECT IMPORTS (V2)
# ===============================

# Flow-based feature extraction
from feature_extractor_v2 import FlowStats, REALTIME_FEATURES

# Multi-model inference
from detector_multi_model_v2 import detect_with_all_models

# Threshold + voting aggregation logic
from detector_threshold_v2 import apply_threshold_and_vote

# Model registry
from model_loader_v2 import MODEL_FILES

# Logger
from detector_logger_v2 import log_detection

# Hybrid logic + alert
from hybrid_controller import apply_hybrid_logic
from alert_manager import trigger_alert


# ===============================
# CLI ARGUMENTS
# ===============================

parser = argparse.ArgumentParser(
    description="Realtime Live Detection Engine (V2)"
)

parser.add_argument("--models", type=str, default="all")
parser.add_argument("--threshold", type=float, default=0.5)
parser.add_argument("--vote", type=int, default=2)
parser.add_argument("--timeout", type=int, default=10)

args = parser.parse_args()


# ===============================
# RESOLVE MODELS
# ===============================

if args.models.lower() == "all":
    SELECTED_MODELS = list(MODEL_FILES.keys())
else:
    SELECTED_MODELS = [m.strip() for m in args.models.split(",")]

GLOBAL_THRESHOLD = args.threshold
VOTE_K = args.vote
FLOW_TIMEOUT = args.timeout


# ===============================
# FLOW TABLE
# ===============================

FLOW_TABLE = {}


# ===============================
# FLOW HELPERS
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
# FLOW PROCESSING
# ===============================

def process_flow(flow_key, flow):
    """
    Flow → ML → Hybrid → Alert → Log
    """

    # 1️⃣ Feature extraction
    feature_values = flow.extract_features()
    feature_df = pd.DataFrame([feature_values], columns=REALTIME_FEATURES)

    # 2️⃣ Multi-model inference
    model_results = detect_with_all_models(
        feature_df,
        selected_models=SELECTED_MODELS
    )

    per_model_probs = {
        model: res["probability"]
        for model, res in model_results.items()
    }

    # 3️⃣ Voting decision
    decision = apply_threshold_and_vote(
    per_model_probs=per_model_probs,
    threshold=GLOBAL_THRESHOLD,
    vote_k=VOTE_K
    )


    # 4️⃣ Mean confidence
    mean_probability = sum(per_model_probs.values()) / len(per_model_probs)

    # 5️⃣ Base ML payload
    decision_payload = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),

        "sourceIP": flow_key[0],
        "destinationIP": flow_key[1],
        "srcPort": flow_key[2],
        "dstPort": flow_key[3],
        "protocol": flow_key[4],

        "finalLabel": decision["final_label"],
        "confidence": mean_probability,

        "modelProbabilities": per_model_probs,
        "attackVotes": decision["attack_votes"],
        "totalModels": len(per_model_probs),
        "threshold": GLOBAL_THRESHOLD,
        "voteK": VOTE_K,
        "aggMethod": "voting+mean"
    }

    # 6️⃣ Hybrid refinement
    decision_payload = apply_hybrid_logic(decision_payload)

    # 🔔 7️⃣ ALERT (ONLY HIGH SEVERITY ATTACK)
    trigger_alert(decision_payload)

    # 8️⃣ Log decision
    log_detection(decision_payload)

    # 9️⃣ Console output
    print("\n🚨 FLOW ANALYSIS RESULT")
    print(f"Flow           : {flow_key}")
    print(f"ML Decision    : {decision['final_label']}")
    print(f"Hybrid Decision: {decision_payload['hybridLabel']}")
    print(f"Severity       : {decision_payload['severity']}")
    print(f"Confidence     : {round(decision_payload['confidence'], 4)}")
    print(f"Attack Votes   : {decision_payload['attackVotes']}")
    print(f"Reason         : {decision_payload['hybridReason']}")
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
        print(f"\n🆕 New Flow: {flow_key}")

    entry = FLOW_TABLE[flow_key]
    flow = entry["flow"]
    entry["last_seen"] = now

    pkt_len = len(pkt)

    if is_forward(flow_key, pkt):
        flow.update_forward(pkt_len)
        direction = "FWD"
    else:
        flow.update_backward(pkt_len)
        direction = "BWD"

    print(
        f"📊 {direction} | "
        f"{flow_key[0]}:{flow_key[2]} → {flow_key[1]}:{flow_key[3]} "
        f"| {flow_key[4]}"
    )

    # Flow expiry
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
    print("🚀 Starting live detection engine (Day-6 Part-4)")
    print(f"Models    : {SELECTED_MODELS}")
    print(
        f"Threshold : {GLOBAL_THRESHOLD} | "
        f"Vote K    : {VOTE_K} | "
        f"Timeout   : {FLOW_TIMEOUT}s"
    )

    sniff(prn=on_packet, store=False)
