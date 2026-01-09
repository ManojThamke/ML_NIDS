import csv
import os
import threading

# ===============================
# LOG FILE CONFIG
# ===============================

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "realtime_v2_log.csv")

# Ensure logs directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# ===============================
# CSV HEADER (V1 + V2 + HYBRID)
# ===============================

CSV_HEADER = [
    "timestamp",
    "source_ip",
    "destination_ip",
    "src_port",
    "dst_port",
    "protocol",

    # V1-compatible fields
    "final_label",
    "confidence",

    # V2 ensemble fields
    "attack_votes",
    "total_models",
    "threshold",
    "vote_k",
    "agg_method",

    # 🔥 NEW: Hybrid intelligence fields
    "hybrid_label",
    "severity",
    "hybrid_reason",

    # Per-model probabilities
    "model_probabilities"
]

# Thread lock (important for realtime sniffing)
_lock = threading.Lock()


# ===============================
# INITIALIZE CSV FILE
# ===============================

def _initialize_log_file():
    """
    Create CSV file with header if it doesn't exist
    """
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
    Persist a single flow detection result.

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

                # 🔥 Hybrid fields
                payload.get("hybridLabel"),
                payload.get("severity"),
                payload.get("hybridReason"),

                str(payload.get("modelProbabilities"))
            ])
