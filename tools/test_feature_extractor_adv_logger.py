# tools/test_feature_extractor_adv_logger.py
import sys, os, csv, signal, time, pprint, traceback
from datetime import datetime

# add project root + detection-engine path (handles hyphen folder)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
sys.path.append(os.path.join(PROJECT_ROOT, "detection-engine"))

from feature_extractor_adv import FeatureExtractorAdv

from scapy.all import sniff

# --- Configuration ---
IFACE = "Wi-Fi"   # change if needed
OUT_PATH = os.path.join(PROJECT_ROOT, "logs", "realtime_features_phase2.csv")
FLUSH_ON_EXIT_TIMEOUT = 5  # seconds idle threshold for flush on exit

# Final fixed Feature Order (must match extractor keys)
FEATURE_ORDER = [
    "flow_duration",
    "total_fwd_packets",
    "total_bwd_packets",
    "total_length_fwd",
    "total_length_bwd",
    "pkt_len_mean",
    "pkt_len_std",
    "fwd_pkt_len_min",
    "bwd_pkt_len_min",
    "flow_iat_mean",
    "flow_iat_std",
    "fwd_iat_mean",
    "bwd_iat_mean",
    "fin_count",
    "syn_count",
    "rst_count",
    "psh_count",
    "ack_count",
    "bytes_per_sec",
    "pkts_per_sec",
    "payload_entropy",
    "ttl",
    "window_size",
    "is_tcp",
    "is_udp",
    "unique_dst_ports_in_flow"
]

os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

# CSV writer setup (create file with header if not exists)
write_header = not os.path.exists(OUT_PATH)
csv_file = open(OUT_PATH, "a", newline="", encoding="utf-8")
csv_writer = csv.writer(csv_file)
if write_header:
    csv_writer.writerow(["timestamp"] + FEATURE_ORDER + ["src", "dst", "sport", "dport", "proto"])

# create extractor (report_once True gives one snapshot per flow at maturity)
fe = FeatureExtractorAdv(report_once=True, report_every=0, idle_timeout=60)

def write_feature_row(feats, pkt_info=None):
    """Write one CSV row for a feature snapshot (feats dict must contain FEATURE_ORDER keys)."""
    ts = datetime.utcnow().isoformat()
    row = [ts]
    for k in FEATURE_ORDER:
        row.append(feats.get(k, ""))

    # optionally add packet/flow identity info if provided
    if pkt_info:
        row.extend([pkt_info.get("src",""), pkt_info.get("dst",""), pkt_info.get("sport",""),
                    pkt_info.get("dport",""), pkt_info.get("proto","")])
    else:
        row.extend(["", "", "", "", ""])

    csv_writer.writerow(row)
    csv_file.flush()

def on_packet(pkt):
    try:
        feats = fe.process(pkt)
        if not feats:
            return

        # print to console (optional)
        print("\n================ FEATURE SAMPLE ================")
        for k in sorted(feats.keys()):
            print(f"{k:30}: {feats[k]}")

        # derive simple pkt_info
        pkt_info = {}
        try:
            if hasattr(pkt, "haslayer") and pkt.haslayer(IP):
                ip = pkt[IP]
                pkt_info["src"] = getattr(ip, "src", "")
                pkt_info["dst"] = getattr(ip, "dst", "")
            if pkt.haslayer(TCP):
                pkt_info["sport"] = getattr(pkt[TCP], "sport", "")
                pkt_info["dport"] = getattr(pkt[TCP], "dport", "")
                pkt_info["proto"] = "TCP"
            elif pkt.haslayer(UDP):
                pkt_info["sport"] = getattr(pkt[UDP], "sport", "")
                pkt_info["dport"] = getattr(pkt[UDP], "dport", "")
                pkt_info["proto"] = "UDP"
        except Exception:
            pass

        write_feature_row(feats, pkt_info=pkt_info)

    except Exception as e:
        print("❌ Error processing packet:", e)
        traceback.print_exc()

def flush_and_exit(signum=None, frame=None):
    print("\n[!] Signal received — flushing idle flows to CSV...")
    flushed = fe.clear_older_than_flush(seconds=FLUSH_ON_EXIT_TIMEOUT)
    for key, feats in flushed:
        # key is (src,dst,sport,dport,proto) — pass as pkt_info for logging
        src, dst, sport, dport, proto = key
        pkt_info = {"src": src, "dst": dst, "sport": sport, "dport": dport, "proto": proto}
        write_feature_row(feats, pkt_info=pkt_info)
    csv_file.close()
    print("[!] Flush complete — exiting.")
    sys.exit(0)

# hook Ctrl+C
signal.signal(signal.SIGINT, flush_and_exit)
signal.signal(signal.SIGTERM, flush_and_exit)

if __name__ == "__main__":
    print(f"[*] Starting extractor logger on interface: {IFACE}")
    print(f"[*] Writing feature snapshots to: {OUT_PATH}")
    sniff(prn=on_packet, store=False, filter="tcp or udp", iface=IFACE)
