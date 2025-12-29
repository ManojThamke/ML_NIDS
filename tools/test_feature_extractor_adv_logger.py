# tools/test_feature_extractor_adv_logger.py
"""
Robust Phase-2 extractor logger (FINAL, CLI):
- Auto-detects extractor class (detection-engine or detection_engine)
- Supports --out (file or directory). If directory given, writes realtime_features_phase2.csv inside it
- Supports --iface and --filter CLI options
- Writes header once (frozen Phase-2 order when available)
- Flushes idle flows on Ctrl+C if extractor provides clear_older_than_flush()
- Safe and verbose
"""
import sys
import os
import csv
import signal
import traceback
import argparse
from datetime import datetime
from scapy.all import sniff, IP, TCP, UDP

# -------------------------
# Path setup (project root)
# -------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

# Support both folder names
for candidate in ("detection-engine", "detection_engine"):
    cand_path = os.path.join(PROJECT_ROOT, candidate)
    if os.path.isdir(cand_path):
        sys.path.append(cand_path)

# -------------------------
# Import extractor class robustly
# -------------------------
ExtractorClass = None
fe_mod = None
try:
    import feature_extractor_adv as fe_mod
    ExtractorClass = getattr(fe_mod, "FeatureExtractorAdv", None) or getattr(fe_mod, "FeatureExtractor", None)
except Exception:
    fe_mod = None

if ExtractorClass is None:
    try:
        import feature_extractor as fe_mod2
        ExtractorClass = getattr(fe_mod2, "FeatureExtractor", None) or getattr(fe_mod2, "FlowStats", None)
    except Exception:
        fe_mod2 = None

if ExtractorClass is None:
    raise ImportError("No extractor class found in detection-engine folder. Make sure detection-engine/feature_extractor_adv.py or detection-engine/feature_extractor.py exists.")

# -------------------------
# Phase-2 frozen order (preferred)
# -------------------------
PHASE2_ORDER = [
    "flow_duration","total_fwd_packets","total_bwd_packets","total_length_fwd","total_length_bwd",
    "pkt_len_mean","pkt_len_std","fwd_pkt_len_min","bwd_pkt_len_min","flow_iat_mean",
    "flow_iat_std","fwd_iat_mean","bwd_iat_mean","fin_count","syn_count",
    "rst_count","psh_count","ack_count","bytes_per_sec","pkts_per_sec",
    "payload_entropy","ttl","window_size","is_tcp","is_udp","unique_dst_ports_in_flow"
]

# -------------------------
# Globals (will be initialized later)
# -------------------------
csv_file = None
csv_writer = None
have_header = False
detected_keys = None
frozen_order = None
fe = None  # extractor instance

# -------------------------
# Helper: instantiate extractor with tolerant signatures
# -------------------------
def make_extractor():
    # try various common constructor signatures
    candidates = [
        {"report_once": True},
        {"report_once": True, "report_every": 0},
        {"enable_unique_dp_track": True},
        {}
    ]
    for kwargs in candidates:
        try:
            return ExtractorClass(**kwargs)
        except TypeError:
            continue
        except Exception as e:
            # if the constructor raises unexpected error, re-raise
            raise
    # fallback: try no-arg
    return ExtractorClass()

# -------------------------
# Header & writing helpers
# -------------------------
def write_header(keys):
    global frozen_order, have_header
    if set(PHASE2_ORDER).issubset(set(keys)):
        frozen_order = PHASE2_ORDER
    else:
        # preserve detected order
        frozen_order = list(keys)
    if not have_header:
        header = ["timestamp"] + frozen_order + ["src", "dst", "sport", "dport", "proto"]
        csv_writer.writerow(header)
        csv_file.flush()
        have_header = True

def write_row(feats, pkt_info):
    ts = datetime.utcnow().isoformat()
    row = [ts]
    for k in frozen_order:
        row.append(feats.get(k, ""))
    row += [
        pkt_info.get("src", ""),
        pkt_info.get("dst", ""),
        pkt_info.get("sport", ""),
        pkt_info.get("dport", ""),
        pkt_info.get("proto", "")
    ]
    csv_writer.writerow(row)
    csv_file.flush()

# -------------------------
# Packet callback
# -------------------------
def on_packet(pkt):
    global detected_keys, frozen_order
    try:
        # call extractor method robustly
        if hasattr(fe, "process"):
            feats = fe.process(pkt)
        elif hasattr(fe, "process_packet"):
            feats = fe.process_packet(pkt)
        else:
            return

        if not feats:
            return

        if not isinstance(feats, dict):
            try:
                feats = dict(feats)
            except Exception:
                # cannot convert -> skip
                return

        # detect keys on first sample
        if detected_keys is None:
            detected_keys = list(feats.keys())
            write_header(detected_keys)

        # pretty-print a sample to console
        print("\n===== FEATURE SAMPLE =====")
        for k in frozen_order:
            print(f"{k:28}: {feats.get(k)}")

        # build pkt_info
        pkt_info = {}
        try:
            if IP in pkt:
                pkt_info["src"] = pkt[IP].src
                pkt_info["dst"] = pkt[IP].dst
            if TCP in pkt:
                pkt_info["sport"] = getattr(pkt[TCP], "sport", "")
                pkt_info["dport"] = getattr(pkt[TCP], "dport", "")
                pkt_info["proto"] = "TCP"
            elif UDP in pkt:
                pkt_info["sport"] = getattr(pkt[UDP], "sport", "")
                pkt_info["dport"] = getattr(pkt[UDP], "dport", "")
                pkt_info["proto"] = "UDP"
        except Exception:
            pass

        write_row(feats, pkt_info)

    except Exception as e:
        print("❌ Error processing packet:", e)
        traceback.print_exc()

# -------------------------
# Flush idle flows on exit (if supported)
# -------------------------
def flush_and_exit(signum=None, frame=None):
    print("\n[!] Ctrl+C detected — attempting to flush idle flows...")
    try:
        if hasattr(fe, "clear_older_than_flush"):
            flushed = fe.clear_older_than_flush(seconds=5)
            for key, feats in flushed:
                try:
                    src, dst, sport, dport, proto = key
                except Exception:
                    src = dst = sport = dport = proto = ""
                pkt_info = {"src": src, "dst": dst, "sport": sport, "dport": dport, "proto": proto}
                if frozen_order is None:
                    write_header(list(feats.keys()))
                write_row(feats, pkt_info)
    except Exception as e:
        print("Flush error:", e)
        traceback.print_exc()
    finally:
        try:
            csv_file.close()
        except:
            pass
        print("[!] Logger stopped cleanly.")
        sys.exit(0)

# -------------------------
# Main entry: CLI + init
# -------------------------
def main():
    global csv_file, csv_writer, have_header, detected_keys, frozen_order, fe

    parser = argparse.ArgumentParser(description="Phase-2 feature logger (supports --out path).")
    parser.add_argument("--out", help="Output file path or directory (default ./logs/realtime_features_phase2.csv)", default=None)
    parser.add_argument("--iface", help="Interface to sniff on (default: Wi-Fi)", default="Wi-Fi")
    parser.add_argument("--filter", help="BPF filter (default: \"tcp or udp\")", default="tcp or udp")
    args = parser.parse_args()

    # decide output path
    if args.out:
        out_candidate = args.out
        # if directory, create and use default filename inside it
        if os.path.isdir(out_candidate) or out_candidate.endswith(os.sep):
            os.makedirs(out_candidate, exist_ok=True)
            out_path = os.path.join(out_candidate, "realtime_features_phase2.csv")
        else:
            # if ends with path separator, treat as dir
            parent = os.path.dirname(out_candidate) or "."
            if parent and not os.path.isdir(parent):
                os.makedirs(parent, exist_ok=True)
            out_path = out_candidate
    else:
        # default
        logs_dir = os.path.join(PROJECT_ROOT, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        out_path = os.path.join(logs_dir, "realtime_features_phase2.csv")

    # open csv (append)
    csv_file = open(out_path, "a", newline="", encoding="utf-8")
    csv_writer = csv.writer(csv_file)
    have_header = os.path.getsize(out_path) > 0

    # instantiate extractor
    fe = make_extractor()

    # register signals
    signal.signal(signal.SIGINT, flush_and_exit)
    signal.signal(signal.SIGTERM, flush_and_exit)

    print(f"[*] Using extractor class: {ExtractorClass.__name__}")
    print(f"[*] Sniffing on interface: {args.iface}")
    print(f"[*] BPF filter: {args.filter}")
    print(f"[*] Logging to: {out_path}")
    print("[*] Press Ctrl+C to stop and flush idle flows (if supported).")

    # start sniffing
    sniff(prn=on_packet, store=False, filter=args.filter, iface=args.iface)

if __name__ == "__main__":
    import argparse
    main()
