# realtime_sniffer.py
"""
Usage examples:
  # log features, show features, with debug and min packets=2 (default)
  sudo python realtime_sniffer.py --show-features --log-features logs/realtime_features.csv --debug

  # only capture tcp/udp (less console noise)
  sudo python realtime_sniffer.py -f "tcp or udp" --log-features logs/realtime_features.csv

  # disable background cleanup (cleanup interval 0)
  sudo python realtime_sniffer.py --log-features logs/realtime_features.csv --cleanup-interval 0
"""
from scapy.all import sniff, IP, TCP, UDP, ICMP
import datetime
import argparse
import os
import sys
import threading
import time

# allow running from project root or detection engine dir:
HERE = os.path.dirname(__file__)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# local import (feature_extractor.py)
from feature_extractor import FeatureExtractor

def pretty_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def pkt_summary(pkt):
    ts = pretty_time()

    proto = ""
    sport = ""
    dport = ""
    src = ""
    dst = ""

    if IP in pkt:
        ip = pkt[IP]
        src = ip.src or ""
        dst = ip.dst or ""

        if TCP in pkt:
            proto = "TCP"
            sport = getattr(pkt[TCP], 'sport', "") or ""
            dport = getattr(pkt[TCP], 'dport', "") or ""
        elif UDP in pkt:
            proto = "UDP"
            sport = getattr(pkt[UDP], 'sport', "") or ""
            dport = getattr(pkt[UDP], 'dport', "") or ""
        elif ICMP in pkt:
            proto = "ICMP"
        else:
            proto = str(getattr(ip, 'proto', "")) or ""
    else:
        proto = getattr(pkt, "name", "NON-IP")
        src = getattr(pkt, 'src', "") or ""
        dst = getattr(pkt, 'dst', "") or ""

    # Ensure all are strings
    proto_s = str(proto)
    sport_s = str(sport)
    dport_s = str(dport)
    src_s = str(src)
    dst_s = str(dst)

    # Align/protect fields using ljust
    proto_field = proto_s.ljust(5)[:5]
    src_field = src_s
    dst_field = dst_s

    # Build a compact printable line
    line = f"[{ts}] {proto_field} {src_field}:{sport_s} -> {dst_field}:{dport_s}"
    return line

# Instance of FeatureExtractor (your feature_extractor.py)
extractor = FeatureExtractor()

# per-flow packet counters to support --min-packets
flows_seen = {}   # key -> count

def make_flow_key(pkt):
    """Return a stable key for a flow or None for non-IP packets."""
    if IP not in pkt:
        return None
    ip = pkt[IP]
    proto = "TCP" if TCP in pkt else ("UDP" if UDP in pkt else str(getattr(ip, 'proto', 'OTHER')))
    sport = ""
    dport = ""
    if TCP in pkt:
        sport = getattr(pkt[TCP], "sport", "") or ""
        dport = getattr(pkt[TCP], "dport", "") or ""
    elif UDP in pkt:
        sport = getattr(pkt[UDP], "sport", "") or ""
        dport = getattr(pkt[UDP], "dport", "") or ""
    return (str(ip.src), str(sport), str(ip.dst), str(dport), str(proto))

def ensure_csv_header(path, header_line):
    """Create file and write header if file doesn't exist or is empty."""
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        with open(path, "w") as fh:
            fh.write(header_line + "\n")

def safe_get(features, key, default=None):
    if not features:
        return default
    return features.get(key, default)

def background_cleanup(interval_seconds):
    """Background thread target that periodically calls extractor.clear_older_than()."""
    if interval_seconds <= 0:
        return
    while True:
        try:
            time.sleep(interval_seconds)
            try:
                extractor.clear_older_than(seconds=interval_seconds * 2 if interval_seconds > 1 else 300)
            except Exception:
                # keep loop alive on errors
                pass
        except Exception:
            # in unlikely event of sleep interrupted, continue
            continue

def on_packet(pkt, show_features=False, log_features=None, min_packets=2, debug=False):
    try:
        # Always print packet summary for visibility
        print(pkt_summary(pkt))

        # Extract features once and reuse for printing/logging
        features = None
        try:
            features = extractor.process_packet(pkt)
        except Exception as e:
            print(f"[{pretty_time()}] WARN extracting features: {e}")
            features = None

        # Optionally show features
        if features and show_features:
            try:
                feat_str = ", ".join(f"{k}={v}" for k, v in features.items())
                print(f"   >> Features: {feat_str}")
            except Exception:
                pass

        # Logging: only if log_features provided
        if log_features:
            # only consider TCP/UDP packets for logging (consistent with desired behavior)
            if not (TCP in pkt or UDP in pkt):
                return

            # enforce min_packets per-flow before logging
            key = make_flow_key(pkt)
            if key:
                flows_seen[key] = flows_seen.get(key, 0) + 1
                seen = flows_seen[key]
            else:
                seen = 0

            if seen < (min_packets or 1):
                # skip logging until flow has been observed at least min_packets times
                return

            # ensure directory and header present
            ensure_csv_header(log_features, "timestamp,Destination Port,Flow Duration,Fwd Packet Length Min,Packet Length Std")

            # prefer extractor values but fallback to packet-layer when possible
            dest_port = safe_get(features, "Destination Port", "")
            if dest_port in (None, ""):
                if TCP in pkt:
                    dest_port = getattr(pkt[TCP], "dport", "") or ""
                elif UDP in pkt:
                    dest_port = getattr(pkt[UDP], "dport", "") or ""
                else:
                    dest_port = ""

            # flow duration (float seconds)
            try:
                flow_duration = float(safe_get(features, "Flow Duration", 0.0) or 0.0)
            except Exception:
                flow_duration = 0.0

            # forward packet length min
            try:
                fwd_min = int(safe_get(features, "Fwd Packet Length Min", 0) or 0)
            except Exception:
                fwd_min = 0

            # packet length std
            try:
                pkt_std = float(safe_get(features, "Packet Length Std", 0.0) or 0.0)
            except Exception:
                pkt_std = 0.0

            # format row
            ts = pretty_time()
            flow_duration_s = f"{flow_duration:.6f}"
            pkt_std_s = f"{pkt_std:.6f}"
            fwd_min_s = str(fwd_min)
            dest_port_s = str(dest_port) if dest_port is not None else ""

            # debug print before writing if requested
            if debug:
                print(f"[DEBUG] writing row: {ts},{dest_port_s},{flow_duration_s},{fwd_min_s},{pkt_std_s}")

            # append to CSV
            try:
                with open(log_features, "a") as fh:
                    fh.write(f"{ts},{dest_port_s},{flow_duration_s},{fwd_min_s},{pkt_std_s}\n")
            except Exception as e:
                print(f"[{pretty_time()}] ERROR writing log features: {e}")

    except Exception as e:
        print(f"[{pretty_time()}] ERROR processing packet: {e}")

def main(interface=None, count=0, bpf_filter=None, show_features=True, log_features=None,
         min_packets=2, debug=False, cleanup_interval=60):
    print("Starting sniffer...")
    print(f"interface: {interface or 'default'} Filter: {bpf_filter or 'none'} Show-features: {show_features} Min-packets: {min_packets} Debug: {debug} Cleanup-interval: {cleanup_interval}")
    print("Press Ctrl+C to stop. \n")

    # start background cleanup thread if requested
    if cleanup_interval and cleanup_interval > 0:
        t = threading.Thread(target=background_cleanup, args=(cleanup_interval,), daemon=True)
        t.start()

    try:
        sniff(iface=interface,
              prn=lambda pkt: on_packet(pkt, show_features=show_features, log_features=log_features, min_packets=min_packets, debug=debug),
              store=False,
              count=count,
              filter=bpf_filter)
    except KeyboardInterrupt:
        print("\nStopping sniffing (KeyboardInterrupt).")
    except Exception as e:
        print(f"[{pretty_time()}] ERROR in sniffing: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Real-time Network Sniffer with Feature Extraction")
    parser.add_argument("-i", "--iface", help="Interface name to sniff on.")
    parser.add_argument("-c", "--count", type=int, default=0, help="Number of packets to capture (0 = infinite).")
    parser.add_argument("-f", "--filter", help="BPF filter string (e.g., 'tcp or udp').", default=None)
    parser.add_argument("--show-features", action="store_true", help="Print extracted feature dict for each packet.")
    parser.add_argument("--log-features", help="Append extractor features to CSV files (e.g., logs/realtime_features.csv)")
    parser.add_argument("--min-packets", type=int, default=2, help="Minimum packets seen in a flow before logging (default 2).")
    parser.add_argument("--debug", action="store_true", help="Print debug info about CSV rows before writing.")
    parser.add_argument("--cleanup-interval", type=int, default=60, help="Background cleanup interval in seconds (0 disables).")
    args = parser.parse_args()

    main(interface=args.iface, count=args.count, bpf_filter=args.filter,
         show_features=args.show_features, log_features=args.log_features,
         min_packets=args.min_packets, debug=args.debug, cleanup_interval=args.cleanup_interval)
