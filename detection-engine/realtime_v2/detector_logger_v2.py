# =====================================================
# Phase-2 Realtime Detection Logger (V2)
# Thread-safe CSV logger for ML-NIDS
# =====================================================

import csv
import os
import threading

# ===============================
# PATH CONFIG (SAFE)
# ===============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "realtime_v2_1_log.csv")

os.makedirs(LOG_DIR, exist_ok=True)

# ===============================
# CSV HEADER (CICIDS + V2 + HYBRID)
# ===============================

CSV_HEADER = [
    "timestamp",

    "source_ip",
    "destination_ip",
    "src_port",
    "dst_port",
    "protocol",

    "final_label",
    "confidence",

    "attack_votes",
    "total_models",
    "threshold",
    "vote_k",
    "aggregation_method",

    "hybrid_label",
    "severity",
    "hybrid_reason",

    "flow_duration",

    "model_probabilities"
]

# Thread lock for realtime sniffing
_lock = threading.Lock()

# ===============================
# INITIALIZE LOG FILE
# ===============================

def _initialize_log_file():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADER)

_initialize_log_file()

# ===============================
# MAIN LOGGER FUNCTION
# ===============================

def log_detection(payload: dict):
    """
    Persist a single flow detection result (thread-safe)

    Expected payload keys:
    - timestamp
    - sourceIP
    - destinationIP
    - srcPort
    - dstPort
    - protocol
    - finalLabel
    - confidence
    - attackVotes
    - totalModels
    - threshold
    - voteK
    - aggMethod
    - hybridLabel
    - severity
    - hybridReason
    - flowDuration (optional)
    - modelProbabilities
    """

    with _lock:
        with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            writer.writerow([
                payload.get("timestamp"),

                payload.get("sourceIP"),
                payload.get("destinationIP"),
                payload.get("srcPort"),
                payload.get("dstPort"),
                payload.get("protocol"),

                payload.get("finalLabel"),
                round(payload.get("confidence", 0.0), 6),

                payload.get("attackVotes"),
                payload.get("totalModels"),
                payload.get("threshold"),
                payload.get("voteK"),
                payload.get("aggMethod"),

                payload.get("hybridLabel"),
                payload.get("severity"),
                payload.get("hybridReason"),

                payload.get("flowDuration"),

                str(payload.get("modelProbabilities"))
            ])
