# =====================================================
# Phase-2 Realtime Live Packet → Flow → Feature → ML
# FINAL STABLE VERSION (Windows + Wi-Fi + VM Ethernet)
# =====================================================

from scapy.all import (
    sniff, IP, IPv6, TCP, UDP, ICMP, ARP,
    get_if_list, conf
)
import time
import pandas as pd
import argparse
import signal
import sys
import os
import requests
import threading
from datetime import datetime, timezone

from feature_extractor_v2 import FlowStats, REALTIME_FEATURES
from detector_multi_model_v2 import detect_with_all_models, SCALER
from detector_threshold_v2 import apply_threshold_and_vote
from hybrid_controller import apply_hybrid_logic
from detector_logger_v2 import log_detection
from alert_manager import trigger_alert

# =====================================================
# BACKEND CONFIG
# =====================================================

BACKEND_URL = os.getenv(
    "ML_NIDS_BACKEND_URL",
    "http://localhost:5000/api/detections"
)

def send_to_backend(payload: dict):
    try:
        requests.post(
            BACKEND_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=2
        )
    except Exception:
        pass


# =====================================================
# CLI ARGUMENTS
# =====================================================

parser = argparse.ArgumentParser(description="Realtime Hybrid ML-NIDS")

parser.add_argument("--iface", type=str, required=True,
                    help="Wi-Fi | Ethernet | Ethernet 2 | VirtualBox")
parser.add_argument("--protocol",
                    choices=["tcp", "udp", "icmp", "arp", "both", "all"],
                    default="both")
parser.add_argument("--models", type=str, default="all")
parser.add_argument("--threshold", type=float, default=0.5)
parser.add_argument("--vote", type=int, default=3)
parser.add_argument("--timeout", type=int, default=10)
parser.add_argument("--run_mode", choices=["cli", "service"], default="cli")

args = parser.parse_args()

USER_IFACE = args.iface.strip()
PROTOCOL_MODE = args.protocol.lower()
GLOBAL_THRESHOLD = args.threshold
VOTE_K = args.vote
FLOW_TIMEOUT = args.timeout
RUN_MODE = args.run_mode

SELECTED_MODELS = None if args.models.lower() == "all" else [
    m.strip() for m in args.models.split(",")
]

# =====================================================
# FLOW TABLE
# =====================================================

FLOW_TABLE = {}
RUNNING = True


# =====================================================
# SIGNAL HANDLING
# =====================================================

def shutdown_handler(signum, frame):
    global RUNNING
    RUNNING = False
    print("\n[INFO] Detector shutting down safely")
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)


# =====================================================
# WINDOWS INTERFACE RESOLUTION (CRITICAL)
# =====================================================

def resolve_windows_iface(user_iface: str):
    """
    Convert Windows UI interface name → Scapy/Npcap interface
    """
    if os.name != "nt":
        return user_iface

    user = user_iface.lower()

    for iface in get_if_list():
        try:
            meta = conf.ifaces[iface]
            desc = (meta.description or "").lower()

            # Wi-Fi
            if user in ["wi-fi", "wifi"]:
                if "wi-fi" in desc or "wireless" in desc:
                    return iface

            # Ethernet (Ethernet / Ethernet 2 / LAN)
            if user.startswith("ethernet"):
                if any(x in desc for x in ["ethernet", "gbe", "realtek", "intel"]):
                    return iface

            # VirtualBox Host-Only / VM
            if any(x in user for x in ["virtualbox", "host-only", "vm"]):
                if "virtualbox" in desc:
                    return iface

        except Exception:
            continue

    raise ValueError(f"Interface '{user_iface}' not found in Scapy/Npcap")


def resolve_interfaces(user_iface: str):
    resolved = []
    for name in user_iface.split(","):
        name = name.strip()
        try:
            resolved.append(resolve_windows_iface(name))
        except Exception as e:
            print(f"[WARN] {e}")
    return list(set(resolved))


# =====================================================
# FLOW HELPERS
# =====================================================

def get_ip_layer(pkt):
    if IP in pkt:
        return pkt[IP]
    if IPv6 in pkt:
        return pkt[IPv6]
    return None


def get_flow_key(pkt):
    ip = get_ip_layer(pkt)
    if ip is None:
        return None

    if TCP in pkt:
        return (ip.src, ip.dst, pkt[TCP].sport, pkt[TCP].dport, "TCP")
    if UDP in pkt:
        return (ip.src, ip.dst, pkt[UDP].sport, pkt[UDP].dport, "UDP")
    if ICMP in pkt:
        return (ip.src, ip.dst, 0, 0, "ICMP")
    if ARP in pkt:
        return (pkt[ARP].psrc, pkt[ARP].pdst, 0, 0, "ARP")

    return None


def is_forward(flow_key, pkt):
    proto = flow_key[4]
    if proto == "TCP":
        return pkt[TCP].sport == flow_key[2]
    if proto == "UDP":
        return pkt[UDP].sport == flow_key[2]
    return True


# =====================================================
# APPLICATION PROTOCOL DETECTION
# =====================================================

def detect_app_protocol(flow_key):
    _, _, _, dport, proto = flow_key

    if proto == "TCP":
        return {
            80: "HTTP",
            443: "HTTPS",
            22: "SSH",
            21: "FTP"
        }.get(dport, "OTHER")

    if proto == "UDP" and dport == 53:
        return "DNS"

    return "OTHER"


# =====================================================
# FLOW FINALIZATION
# =====================================================

def process_flow(flow_key, flow, iface_name):

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
        "appProtocol": detect_app_protocol(flow_key),
        "interface": iface_name,   # ✅ REQUIRED BY NEW SCHEMA

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
        print(
            f"[FLOW] {flow_key[0]} → {flow_key[1]} | "
            f"{payload['protocol']}/{payload['appProtocol']} | "
            f"{payload['finalLabel']} | {round(mean_confidence, 3)}"
        )


# =====================================================
# PACKET HANDLER
# =====================================================

def on_packet(pkt, iface_name):
    if not RUNNING:
        return

    if PROTOCOL_MODE != "all":
        if PROTOCOL_MODE == "tcp" and TCP not in pkt:
            return
        if PROTOCOL_MODE == "udp" and UDP not in pkt:
            return
        if PROTOCOL_MODE == "icmp" and ICMP not in pkt:
            return
        if PROTOCOL_MODE == "arp" and ARP not in pkt:
            return
        if PROTOCOL_MODE == "both" and not (TCP in pkt or UDP in pkt):
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

    entry = FLOW_TABLE[flow_key]
    entry["last_seen"] = now

    if is_forward(flow_key, pkt):
        entry["flow"].update_forward(len(pkt))
    else:
        entry["flow"].update_backward(len(pkt))

    # Timeout-based flush (Wi-Fi safe)
    expired = [
        k for k, v in FLOW_TABLE.items()
        if now - v["last_seen"] > FLOW_TIMEOUT
    ]

    for k in expired:
        process_flow(k, FLOW_TABLE[k]["flow"], iface_name)
        del FLOW_TABLE[k]


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    interfaces = resolve_interfaces(USER_IFACE)

    if not interfaces:
        print("[ERROR] No valid interfaces resolved for Scapy")
        sys.exit(1)

    print("[INFO] Realtime Detector Started")
    print(f"[INFO] Mode={RUN_MODE} | Protocol={PROTOCOL_MODE}")
    print(f"[INFO] Scapy Interfaces={interfaces}")
    print("-" * 60)

    for iface in interfaces:
        threading.Thread(
            target=sniff,
            kwargs={
                "iface": iface,
                "prn": lambda pkt, i=iface: on_packet(pkt, i),
                "store": False
            },
            daemon=True
        ).start()

    while RUNNING:
        time.sleep(1)
