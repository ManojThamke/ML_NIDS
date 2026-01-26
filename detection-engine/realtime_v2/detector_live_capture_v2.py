# =====================================================
# Phase-2 Realtime Live Packet → Flow → Feature → ML
# STEP-4: MULTI-MODEL + VOTING + HYBRID + LOGGING
# =====================================================

from scapy.all import sniff, IP, TCP, UDP
import time
import pandas as pd
import argparse
import signal
import sys
import os
import requests
from datetime import datetime, timezone

from feature_extractor_v2 import FlowStats, REALTIME_FEATURES
from detector_multi_model_v2 import detect_with_all_models, SCALER
from detector_threshold_v2 import apply_threshold_and_vote
from hybrid_controller import apply_hybrid_logic
from detector_logger_v2 import log_detection
from alert_manager import trigger_alert

# ===============================
# BACKEND CONFIG
# ===============================

BACKEND_URL = os.getenv(
    "ML_NIDS_BACKEND_URL",
    "http://localhost:5000/api/detections"
)

def send_to_backend(payload: dict):
    """Send detection payload to backend (never crash detector)"""
    try:
        requests.post(
            BACKEND_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=2
        )
    except Exception:
        pass

# ===============================
# CLI ARGUMENTS
# ===============================

parser = argparse.ArgumentParser(
    description="Realtime Hybrid ML-NIDS (Phase-2)"
)

parser.add_argument("--iface", type=str, required=True)
parser.add_argument("--models", type=str, default="all")
parser.add_argument("--threshold", type=float, default=0.5)
parser.add_argument("--vote", type=int, default=3)
parser.add_argument("--timeout", type=int, default=10)

# 🔥 NEW: protocol selection (like v1)
parser.add_argument(
    "--protocol",
    choices=["tcp", "udp", "both"],
    default="both",
    help="Protocol to monitor (tcp | udp | both)"
)

parser.add_argument(
    "--run_mode",
    choices=["cli", "service"],
    default="cli",
    help="cli = verbose, service = backend controlled"
)

args = parser.parse_args()

INTERFACE = args.iface
GLOBAL_THRESHOLD = args.threshold
VOTE_K = args.vote
FLOW_TIMEOUT = args.timeout
RUN_MODE = args.run_mode
PROTOCOL_MODE = args.protocol

SELECTED_MODELS = None if args.models.lower() == "all" else [
    m.strip() for m in args.models.split(",")
]

# ===============================
# FLOW TABLE
# ===============================

FLOW_TABLE = {}
RUNNING = True

# ===============================
# SIGNAL HANDLING
# ===============================

def shutdown_handler(signum, frame):
    global RUNNING
    RUNNING = False
    if RUN_MODE == "cli":
        print("\n[INFO] Detector shutting down safely")
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

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
    return pkt[TCP].sport == sport if proto == "TCP" else pkt[UDP].sport == sport

# ===============================
# PROTOCOL FILTER (NEW)
# ===============================

def build_bpf_filter(protocol_mode: str):
    if protocol_mode == "tcp":
        return "tcp"
    elif protocol_mode == "udp":
        return "udp"
    return "tcp or udp"

# ===============================
# FLOW FINALIZATION
# ===============================

def process_flow(flow_key, flow):

    features = flow.extract_features()
    flow_duration = round(features[1], 6)

    feature_df = pd.DataFrame([features], columns=REALTIME_FEATURES)
    feature_df = feature_df[list(SCALER.feature_names_in_)]

    model_results = detect_with_all_models(
        feature_df,
        selected_models=SELECTED_MODELS
    )

    per_model_probs = {
        model: res["probability"]
        for model, res in model_results.items()
    }

    vote_result = apply_threshold_and_vote(
        per_model_probs,
        threshold=GLOBAL_THRESHOLD,
        vote_k=VOTE_K
    )

    mean_confidence = sum(per_model_probs.values()) / len(per_model_probs)

    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),

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
        "aggregationMethod": "global-threshold-voting",

        "flowDuration": flow_duration,
        "modelProbabilities": per_model_probs
    }

    payload = apply_hybrid_logic(payload)

    trigger_alert(payload)
    log_detection(payload)
    send_to_backend(payload)

    if RUN_MODE == "cli":
        print("\n[FLOW RESULT]")
        print(f"Flow: {flow_key}")
        print(f"ML Decision: {payload['finalLabel']}")
        print(f"Hybrid Decision: {payload['hybridLabel']}")
        print(f"Severity: {payload['severity']}")
        print(f"Confidence: {round(mean_confidence, 4)}")
        print(f"Attack Votes: {payload['attackVotes']}")
        print(f"Flow Duration: {flow_duration}s")
        print(f"Reason: {payload['hybridReason']}")
        print("-" * 60)

# ===============================
# PACKET HANDLER
# ===============================

def on_packet(pkt):
    if not RUNNING or IP not in pkt:
        return

    # 🔒 Protocol safety check
    if PROTOCOL_MODE == "tcp" and TCP not in pkt:
        return
    if PROTOCOL_MODE == "udp" and UDP not in pkt:
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

        if RUN_MODE == "cli":
            print(f"[NEW FLOW] {flow_key}")

    entry = FLOW_TABLE[flow_key]
    entry["last_seen"] = now

    if is_forward(flow_key, pkt):
        entry["flow"].update_forward(len(pkt))
    else:
        entry["flow"].update_backward(len(pkt))

    expired = [
        k for k, v in FLOW_TABLE.items()
        if now - v["last_seen"] > FLOW_TIMEOUT
    ]

    for k in expired:
        process_flow(k, FLOW_TABLE[k]["flow"])
        del FLOW_TABLE[k]

# ===============================
# MAIN
# ===============================

if __name__ == "__main__":

    if RUN_MODE == "cli":
        print("[INFO] Starting Realtime V2 Detector")
        print(
            f"Iface={INTERFACE} | Protocol={PROTOCOL_MODE} | Models={args.models} | "
            f"Threshold={GLOBAL_THRESHOLD} | VoteK={VOTE_K} | "
            f"Timeout={FLOW_TIMEOUT}s | Mode={RUN_MODE}"
        )
        print("-" * 60)

    BPF_FILTER = build_bpf_filter(PROTOCOL_MODE)

    sniff(
        iface=INTERFACE,
        filter=BPF_FILTER,
        prn=on_packet,
        store=False
    )
