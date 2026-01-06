from scapy.all import sniff, IP, TCP, UDP
import pandas as pd
import time
import argparse

# Local imports
from feature_extractor_v2 import FlowStats, REALTIME_FEATURES
from detector_multi_model_v2 import detect_with_all_models
from detector_threshold_v2 import apply_threshold_and_vote
from model_loader_v2 import MODEL_FILES


# ===============================
# CLI ARGUMENTS
# ===============================
parser = argparse.ArgumentParser(
    description="Realtime Live Detection Engine (V2)"
)

parser.add_argument(
    "--models",
    type=str,
    default="all",
    help="Comma-separated model names or 'all'"
)

parser.add_argument(
    "--threshold",
    type=float,
    default=0.5,
    help="Global probability threshold"
)

parser.add_argument(
    "--vote",
    type=int,
    default=2,
    help="Minimum number of models required to trigger ATTACK"
)

parser.add_argument(
    "--timeout",
    type=int,
    default=10,
    help="Flow timeout in seconds"
)

args = parser.parse_args()


# ===============================
# RESOLVE SELECTED MODELS
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


def process_flow(flow_key, flow):
    """
    Flow → Features → Selected Models → Threshold → Decision
    """
    feature_values = flow.extract_features()

    feature_df = pd.DataFrame(
        [feature_values],
        columns=REALTIME_FEATURES
    )

    # 1️⃣ Multi-model inference (CLI-selected)
    model_results = detect_with_all_models(
        feature_df,
        selected_models=SELECTED_MODELS
    )

    per_model_probs = {
        model: res["probability"]
        for model, res in model_results.items()
    }

    # 2️⃣ Threshold + voting
    decision = apply_threshold_and_vote(
        per_model_probs=per_model_probs,
        threshold=GLOBAL_THRESHOLD,
        vote_k=VOTE_K
    )

    print("\n🚨 FLOW ANALYSIS RESULT")
    print(f"Flow: {flow_key}")
    print(f"Final Decision: {decision['final_label']}")
    print(f"Attack Votes: {decision['attack_votes']}")
    print(f"Triggered Models: {decision['triggered_models']}")
    print("-" * 60)


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

    # Expire flows
    expired = []
    for key, entry in FLOW_TABLE.items():
        if now - entry["last_seen"] > FLOW_TIMEOUT:
            expired.append(key)

    for key in expired:
        process_flow(key, FLOW_TABLE[key]["flow"])
        del FLOW_TABLE[key]


if __name__ == "__main__":
    print("🚀 Starting live detection engine (Day 6 – Part 3)")
    print(f"Models: {SELECTED_MODELS}")
    print(
        f"Threshold={GLOBAL_THRESHOLD} | "
        f"Vote K={VOTE_K} | "
        f"Timeout={FLOW_TIMEOUT}s"
    )
    sniff(prn=on_packet, store=False)
