# detection-engine/realtime_v2/detector_live_capture_v2.py
# =====================================================
# Phase-2 Realtime Live Packet → Flow → Feature Engine
# STEP-1: NO ML, NO HYBRID, NO LOGGING
# =====================================================

from scapy.all import sniff, IP, TCP, UDP
import time
import pandas as pd

from feature_extractor_v2 import FlowStats, REALTIME_FEATURES

# ===============================
# FLOW TABLE
# ===============================

FLOW_TABLE = {}
FLOW_TIMEOUT = 10  # seconds


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
    Flow → Feature Extraction → Print
    """

    features = flow.extract_features()
    feature_df = pd.DataFrame([features], columns=REALTIME_FEATURES)

    print("\n🧬 FINAL FLOW FEATURES")
    print(f"Flow: {flow_key}")
    for col in REALTIME_FEATURES:
        print(f"{col:30s}: {feature_df[col].values[0]}")

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
        direction = "FWD"
    else:
        flow.update_backward(pkt_len)
        direction = "BWD"

    print(
        f"📦 {direction} | "
        f"{flow_key[0]}:{flow_key[2]} → {flow_key[1]}:{flow_key[3]} "
        f"| {flow_key[4]}"
    )

    # Expire old flows
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
    print("🚀 Starting Realtime V2 Live Capture (STEP-1)")
    print("✔ Packet capture enabled")
    print("✔ Flow tracking enabled")
    print("✔ Feature extraction enabled")
    print("❌ ML disabled")
    print("❌ Hybrid disabled")
    print("❌ Logging disabled")
    print("-" * 60)

    sniff(prn=on_packet, store=False)
