# tools/test_feature_extractor_adv_logger.py
"""
Robust Phase-2 extractor logger (FINAL):
✔ Works with FeatureExtractorAdv or FeatureExtractor
✔ Auto-detects feature keys (first snapshot)
✔ Writes correct CSV header once
✔ Flushes idle flows on Ctrl+C (if extractor supports it)
✔ Supports detection-engine folder with hyphen
✔ ZERO NameError issues now
"""

import sys, os, csv, signal, traceback
from datetime import datetime
from scapy.all import sniff, IP, TCP, UDP

# ---------------------------------------------
# PATH SETUP
# ---------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

# Try both folder names
for folder in ("detection-engine", "detection_engine"):
    path = os.path.join(PROJECT_ROOT, folder)
    if os.path.isdir(path):
        sys.path.append(path)

# ---------------------------------------------
# IMPORT EXTRACTOR CLASS SAFELY
# ---------------------------------------------
ExtractorClass = None

try:
    import feature_extractor_adv as fe_mod
    ExtractorClass = getattr(fe_mod, "FeatureExtractorAdv", None) \
                    or getattr(fe_mod, "FeatureExtractor", None)
except:
    pass

if ExtractorClass is None:
    try:
        import feature_extractor as fe_mod2
        ExtractorClass = getattr(fe_mod2, "FeatureExtractor", None)
    except:
        pass

if ExtractorClass is None:
    raise ImportError("❌ No extractor class found in detection-engine folder.")

# ---------------------------------------------
# CONFIG (FIXED NameError HERE)
# ---------------------------------------------
IFACE = "Wi-Fi"      # <-- change here if needed (Wi-Fi / Ethernet / wlan0)
OUT_DIR = os.path.join(PROJECT_ROOT, "logs")
OUT_PATH = os.path.join(OUT_DIR, "realtime_features_phase2.csv")

os.makedirs(OUT_DIR, exist_ok=True)

# ---------------------------------------------
# CSV INIT
# ---------------------------------------------
csv_file = open(OUT_PATH, "a", newline="", encoding="utf-8")
csv_writer = csv.writer(csv_file)
have_header = os.path.getsize(OUT_PATH) > 0

detected_keys = None
frozen_order = None

PHASE2_ORDER = [
    "flow_duration","total_fwd_packets","total_bwd_packets","total_length_fwd","total_length_bwd",
    "pkt_len_mean","pkt_len_std","fwd_pkt_len_min","bwd_pkt_len_min","flow_iat_mean",
    "flow_iat_std","fwd_iat_mean","bwd_iat_mean","fin_count","syn_count",
    "rst_count","psh_count","ack_count","bytes_per_sec","pkts_per_sec",
    "payload_entropy","ttl","window_size","is_tcp","is_udp","unique_dst_ports_in_flow"
]

# ---------------------------------------------
# EXTRACTOR INSTANCE
# ---------------------------------------------
def make_extractor():
    for args in ({"report_once": True},
                 {"report_once": True, "report_every": 0},
                 {}):
        try:
            return ExtractorClass(**args)
        except TypeError:
            continue
        except Exception as e:
            raise RuntimeError(e)
    return ExtractorClass()

fe = make_extractor()

# ---------------------------------------------
# HEADER HANDLER
# ---------------------------------------------
def write_header(keys):
    global frozen_order, have_header

    # If Phase-2 order fully matches detected keys — use it
    if set(PHASE2_ORDER).issubset(set(keys)):
        frozen_order = PHASE2_ORDER
    else:
        frozen_order = list(keys)

    if not have_header:
        header = ["timestamp"] + frozen_order + ["src","dst","sport","dport","proto"]
        csv_writer.writerow(header)
        csv_file.flush()
        have_header = True

# ---------------------------------------------
# WRITE A ROW TO CSV
# ---------------------------------------------
def write_row(feats, pkt_info):
    ts = datetime.utcnow().isoformat()
    row = [ts]

    for k in frozen_order:
        row.append(feats.get(k, ""))

    row += [
        pkt_info.get("src",""),
        pkt_info.get("dst",""),
        pkt_info.get("sport",""),
        pkt_info.get("dport",""),
        pkt_info.get("proto","")
    ]

    csv_writer.writerow(row)
    csv_file.flush()

# ---------------------------------------------
# PACKET HANDLER
# ---------------------------------------------
def on_packet(pkt):
    global detected_keys, frozen_order

    try:
        # call the right extractor method
        if hasattr(fe, "process"):
            feats = fe.process(pkt)
        else:
            feats = fe.process_packet(pkt)

        if not feats:
            return

        if not isinstance(feats, dict):
            feats = dict(feats)

        # detect keys on first valid sample
        if detected_keys is None:
            detected_keys = list(feats.keys())
            write_header(detected_keys)

        # console output (sorted for neatness)
        print("\n===== FEATURE SAMPLE =====")
        for k in frozen_order:
            print(f"{k:28}: {feats.get(k)}")

        # build pkt_info
        pkt_info = {}
        if IP in pkt:
            pkt_info["src"] = pkt[IP].src
            pkt_info["dst"] = pkt[IP].dst

        if TCP in pkt:
            pkt_info["sport"] = pkt[TCP].sport
            pkt_info["dport"] = pkt[TCP].dport
            pkt_info["proto"] = "TCP"
        elif UDP in pkt:
            pkt_info["sport"] = pkt[UDP].sport
            pkt_info["dport"] = pkt[UDP].dport
            pkt_info["proto"] = "UDP"

        write_row(feats, pkt_info)

    except Exception as e:
        print("❌ Error processing packet:", e)
        traceback.print_exc()

# ---------------------------------------------
# FLUSH ON CTRL+C
# ---------------------------------------------
def flush_and_exit(signum=None, frame=None):
    print("\n[!] Ctrl+C detected — flushing idle flows...")

    try:
        if hasattr(fe, "clear_older_than_flush"):
            flushed = fe.clear_older_than_flush(seconds=5)
            for key, feats in flushed:
                src,dst,sport,dport,proto = key
                pkt_info = {"src":src, "dst":dst, "sport":sport, "dport":dport, "proto":proto}

                if frozen_order is None:
                    write_header(list(feats.keys()))

                write_row(feats, pkt_info)
    except Exception as e:
        print("Flush error:", e)

    csv_file.close()
    print("[!] Logger stopped cleanly.")
    sys.exit(0)

signal.signal(signal.SIGINT, flush_and_exit)
signal.signal(signal.SIGTERM, flush_and_exit)

# ---------------------------------------------
# START SNIFFING
# ---------------------------------------------
if __name__ == "__main__":
    print("[*] Using extractor class:", ExtractorClass.__name__)
    print("[*] Interface:", IFACE)
    print("[*] Logging to:", OUT_PATH)
    sniff(prn=on_packet, store=False, filter="tcp or udp", iface=IFACE)
